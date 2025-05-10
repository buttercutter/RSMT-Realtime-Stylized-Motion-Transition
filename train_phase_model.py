#!/usr/bin/env python3
"""
Modified training script for the DeepPhase model that works with
the current PyTorch Lightning version
"""

import os
import sys
import torch
import numpy as np
import pickle
import argparse
from torch.utils.data import DataLoader, Dataset

# Add current directory to path
sys.path.append('.')

class Style100Dataset(Dataset):
    """Custom dataset for loading Style100 data"""
    def __init__(self, data_path, is_train=True):
        super().__init__()
        self.data_path = data_path
        self.is_train = is_train
        
        # Load the data
        data_file = os.path.join(data_path, 'train_binary.dat' if is_train else 'test_binary.dat')
        print(f"Loading data from {data_file}")
        
        with open(data_file, 'rb') as f:
            self.data = pickle.load(f)
        
        # Extract features
        self.motion_data = torch.FloatTensor(self.data['motion_data'])
        self.style_labels = torch.LongTensor(self.data['style_labels']) if 'style_labels' in self.data else None
        
        print(f"Loaded {'training' if is_train else 'test'} data with {len(self.motion_data)} samples")
        
    def __len__(self):
        return len(self.motion_data)
    
    def __getitem__(self, idx):
        # For each sample, return motion data and style label (if available)
        sample = {
            'motion': self.motion_data[idx],
        }
        if self.style_labels is not None:
            sample['style'] = self.style_labels[idx]
        return sample

class PhaseNetModel(torch.nn.Module):
    """Simple autoencoder model for learning motion phases"""
    def __init__(self, input_dim, hidden_dim=256, latent_dim=32):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        
        # Encoder
        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, latent_dim * 2)  # Mean and log variance
        )
        
        # Decoder
        self.decoder = torch.nn.Sequential(
            torch.nn.Linear(latent_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, input_dim)
        )
    
    def encode(self, x):
        h = self.encoder(x)
        # Split into mean and log variance
        mu, log_var = torch.chunk(h, 2, dim=-1)
        return mu, log_var
    
    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        z = mu + eps * std
        return z
    
    def decode(self, z):
        return self.decoder(z)
    
    def forward(self, x):
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        recon_x = self.decode(z)
        return recon_x, mu, log_var

def vae_loss(recon_x, x, mu, log_var):
    """Compute VAE loss: reconstruction loss + KL divergence"""
    # Reconstruction loss
    recon_loss = torch.nn.functional.mse_loss(recon_x, x, reduction='sum')
    
    # KL divergence loss
    kl_loss = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    
    # Total loss
    return recon_loss + kl_loss

def train_epoch(model, train_loader, optimizer, device):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    
    for batch in train_loader:
        # Get the motion data
        x = batch['motion'].to(device)
        
        # Forward pass
        recon_x, mu, log_var = model(x)
        
        # Compute loss
        loss = vae_loss(recon_x, x, mu, log_var)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(train_loader.dataset)

def validate(model, val_loader, device):
    """Validate the model"""
    model.eval()
    total_loss = 0
    
    with torch.no_grad():
        for batch in val_loader:
            # Get the motion data
            x = batch['motion'].to(device)
            
            # Forward pass
            recon_x, mu, log_var = model(x)
            
            # Compute loss
            loss = vae_loss(recon_x, x, mu, log_var)
            total_loss += loss.item()
    
    return total_loss / len(val_loader.dataset)

def main():
    parser = argparse.ArgumentParser(description="Train the DeepPhase model")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size")
    parser.add_argument("--learning_rate", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--hidden_dim", type=int, default=256, help="Hidden dimension size")
    parser.add_argument("--latent_dim", type=int, default=32, help="Latent dimension size")
    parser.add_argument("--data_dir", type=str, default="./MotionData/100STYLE", help="Data directory")
    parser.add_argument("--output_dir", type=str, default="./output/phase_model", help="Output directory")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check if CUDA is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load data
    train_dataset = Style100Dataset(args.data_dir, is_train=True)
    test_dataset = Style100Dataset(args.data_dir, is_train=False)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)
    
    # Get a sample batch to determine input dimension
    sample_batch = next(iter(train_loader))
    input_dim = sample_batch['motion'].shape[1]
    print(f"Input dimension: {input_dim}")
    
    # Create model
    model = PhaseNetModel(input_dim, args.hidden_dim, args.latent_dim)
    model.to(device)
    
    # Create optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    
    # Training loop
    best_val_loss = float('inf')
    
    print(f"Starting training for {args.epochs} epochs...")
    
    for epoch in range(args.epochs):
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, device)
        
        # Validate
        val_loss = validate(model, test_loader, device)
        
        # Print progress
        print(f"Epoch {epoch+1}/{args.epochs} - Train loss: {train_loss:.4f}, Val loss: {val_loss:.4f}")
        
        # Save if this is the best model so far
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            checkpoint_path = os.path.join(args.output_dir, "best_model.pt")
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': best_val_loss,
            }, checkpoint_path)
            print(f"Saved best model to {checkpoint_path}")
    
    # Save the final model
    final_path = os.path.join(args.output_dir, "final_model.pt")
    torch.save({
        'epoch': args.epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': val_loss,
    }, final_path)
    print(f"Training complete. Final model saved to {final_path}")

if __name__ == "__main__":
    main()
