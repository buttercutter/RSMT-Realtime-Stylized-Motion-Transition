#!/usr/bin/env python3
"""
Modified DeepPhase training script that works with the skeleton format
we've created.
"""

import os
import sys
import torch
import numpy as np
import pickle
import argparse
from datetime import datetime
import matplotlib.pyplot as plt

# Add the repository root to the path
sys.path.append('.')

class DeepPhaseModel(torch.nn.Module):
    """DeepPhase model for motion phase learning"""
    def __init__(self, input_dim, hidden_dim=512, latent_dim=32):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        
        # Encoder layers
        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim, hidden_dim // 2),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim // 2, latent_dim)
        )
        
        # Decoder layers
        self.decoder = torch.nn.Sequential(
            torch.nn.Linear(latent_dim, hidden_dim // 2),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim // 2, hidden_dim),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim, input_dim)
        )
        
    def forward(self, x):
        z = self.encoder(x)
        recon_x = self.decoder(z)
        return recon_x, z

def load_data(data_path, batch_size=64, test_batch_size=32):
    """
    Load the motion data from binary files
    """
    print(f"Loading data from {data_path}")
    
    train_path = os.path.join(data_path, 'train_binary.dat')
    test_path = os.path.join(data_path, 'test_binary.dat')
    
    # Check if files exist
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print(f"Data files not found at {train_path} or {test_path}")
        return None, None
    
    try:
        # Load training data
        with open(train_path, 'rb') as f:
            train_data = pickle.load(f)
        
        # Load test data
        with open(test_path, 'rb') as f:
            test_data = pickle.load(f)
        
        print("Data loaded successfully")
        print(f"Training data keys: {list(train_data.keys())}")
        
        # Extract motion data - assuming it's in a specific format
        # Adapt this based on the actual data structure
        if 'motion_data' in train_data:
            train_motions = torch.tensor(train_data['motion_data'], dtype=torch.float32)
            test_motions = torch.tensor(test_data['motion_data'], dtype=torch.float32)
            
            print(f"Train data shape: {train_motions.shape}")
            print(f"Test data shape: {test_motions.shape}")
            
            # Create data loaders
            train_dataset = torch.utils.data.TensorDataset(train_motions)
            test_dataset = torch.utils.data.TensorDataset(test_motions)
            
            train_loader = torch.utils.data.DataLoader(
                train_dataset, batch_size=batch_size, shuffle=True)
            test_loader = torch.utils.data.DataLoader(
                test_dataset, batch_size=test_batch_size, shuffle=False)
            
            return train_loader, test_loader
        else:
            # Try a different approach if 'motion_data' is not found
            print("'motion_data' key not found, trying alternative approach")
            
            # Based on inspection, we know our data has the following structure:
            # {style_name: {'BR': {'quats': array, 'offsets': array, 'hips': array}}}
            
            # We'll collect quaternion data from all styles
            all_train_motions = []
            
            # Check data format by examining the first style
            first_style = list(train_data.keys())[0]
            print(f"Using data from key: {first_style}")
            
            # Try to extract quaternion data from the style
            try:
                motion_type = 'BR'  # This is the motion type we found in our data
                
                # Process each style
                for style_name, style_data in train_data.items():
                    if motion_type in style_data:
                        motion_info = style_data[motion_type]
                        
                        # Check for quaternion data which is what we need for training
                        if 'quats' in motion_info and motion_info['quats'] is not None:
                            # Get quaternion data and convert to tensor
                            quats = motion_info['quats']
                            
                            # Get offsets and hip position data as well
                            offsets = motion_info.get('offsets', None)
                            hips = motion_info.get('hips', None)
                            
                            # Convert to tensors
                            quats_tensor = torch.tensor(quats, dtype=torch.float32)
                            
                            # Reshape to [time_steps, joint_count * 4]
                            # This flattens the quaternion dimensions for each joint into a single vector
                            batch_size, joint_count, quat_dim = quats_tensor.shape
                            flattened = quats_tensor.reshape(batch_size, -1)  # Flatten to [batch, joint_count * 4]
                            
                            # Add to our collection
                            all_train_motions.append(flattened)
                
                # Do the same for test data
                all_test_motions = []
                for style_name, style_data in test_data.items():
                    if motion_type in style_data:
                        motion_info = style_data[motion_type]
                        
                        # Check for quaternion data
                        if 'quats' in motion_info and motion_info['quats'] is not None:
                            # Get quaternion data and convert to tensor
                            quats = motion_info['quats']
                            quats_tensor = torch.tensor(quats, dtype=torch.float32)
                            
                            # Reshape to [time_steps, joint_count * 4]
                            batch_size, joint_count, quat_dim = quats_tensor.shape
                            flattened = quats_tensor.reshape(batch_size, -1)
                            
                            # Add to our collection
                            all_test_motions.append(flattened)
                
                # Check if we have any data
                if len(all_train_motions) > 0 and len(all_test_motions) > 0:
                    print(f"Collected {len(all_train_motions)} training sequences and {len(all_test_motions)} test sequences")
                    print(f"Sample sequence shape: {all_train_motions[0].shape}")
                    
                    # Calculate input dimension from data
                    input_dim = all_train_motions[0].shape[-1]
                    print(f"Input dimension: {input_dim}")
                    
                    # Create custom dataset class
                    class QuatDataset(torch.utils.data.Dataset):
                        def __init__(self, motions):
                            self.motions = motions
                        
                        def __len__(self):
                            return len(self.motions)
                        
                        def __getitem__(self, idx):
                            return self.motions[idx]
                    
                    # Create datasets
                    train_dataset = QuatDataset(all_train_motions)
                    test_dataset = QuatDataset(all_test_motions)
                    
                    # Create data loaders
                    train_loader = torch.utils.data.DataLoader(
                        train_dataset, batch_size=batch_size, shuffle=True)
                    test_loader = torch.utils.data.DataLoader(
                        test_dataset, batch_size=test_batch_size, shuffle=False)
                    
                    return train_loader, test_loader
                try:
                    return train_loader, test_loader
                except Exception as e:
                    print(f"Error creating data loaders: {e}")
                    return None, None
                    
            except Exception as e:
                print(f"Error processing data: {e}")
            
            # Final fallback approach for other data structures
            if isinstance(train_data, dict) and len(train_data) > 0:
                print("Using fallback method for data loading...")
                # Try to determine the data structure
                try:
                    first_key = list(train_data.keys())[0]
                    first_value = train_data[first_key]
                    
                    print(f"First key: {first_key}")
                    print(f"First value type: {type(first_value)}")
                    
                    # If the value is a numpy array
                    if isinstance(first_value, np.ndarray):
                        print(f"First value shape: {first_value.shape}")
                        
                        # Create tensor datasets directly from the values
                        train_tensors = []
                        test_tensors = []
                        
                        for key, value in train_data.items():
                            if isinstance(value, np.ndarray):
                                train_tensors.append(torch.tensor(value, dtype=torch.float32))
                        
                        for key, value in test_data.items():
                            if isinstance(value, np.ndarray):
                                test_tensors.append(torch.tensor(value, dtype=torch.float32))
                        
                        if train_tensors and test_tensors:
                            # Concatenate tensors if they have compatible shapes
                            train_combined = torch.cat(train_tensors, dim=0)
                            test_combined = torch.cat(test_tensors, dim=0)
                            
                            print(f"Combined train shape: {train_combined.shape}")
                            print(f"Combined test shape: {test_combined.shape}")
                            
                            # Create datasets and loaders
                            train_dataset = torch.utils.data.TensorDataset(train_combined)
                            test_dataset = torch.utils.data.TensorDataset(test_combined)
                            
                            train_loader = torch.utils.data.DataLoader(
                                train_dataset, batch_size=batch_size, shuffle=True)
                            test_loader = torch.utils.data.DataLoader(
                                test_dataset, batch_size=test_batch_size, shuffle=False)
                            
                            return train_loader, test_loader
                            
                except Exception as e:
                    print(f"Error in fallback data loading: {e}")
            
            print("Could not determine data format")
            return None, None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def train(model, train_loader, test_loader, device, 
          num_epochs=100, lr=0.001, save_dir="./output/deephase"):
    """
    Train the DeepPhase model
    """
    # Create optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    # Create loss function
    criterion = torch.nn.MSELoss()
    
    # Track metrics
    train_losses = []
    test_losses = []
    best_test_loss = float('inf')
    
    # Create save directory
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"Starting training for {num_epochs} epochs")
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        epoch_loss = 0
        for batch in train_loader:
            x = batch[0].to(device)
            
            # Forward pass
            recon_x, z = model(x)
            
            # Compute loss
            loss = criterion(recon_x, x)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * x.size(0)
        
        train_loss = epoch_loss / len(train_loader.dataset)
        train_losses.append(train_loss)
        
        # Testing
        model.eval()
        test_loss = 0
        with torch.no_grad():
            for batch in test_loader:
                x = batch[0].to(device)
                
                # Forward pass
                recon_x, z = model(x)
                
                # Compute loss
                loss = criterion(recon_x, x)
                
                test_loss += loss.item() * x.size(0)
        
        test_loss = test_loss / len(test_loader.dataset)
        test_losses.append(test_loss)
        
        # Print progress
        print(f"Epoch {epoch+1}/{num_epochs}: "
              f"Train Loss: {train_loss:.6f}, Test Loss: {test_loss:.6f}")
        
        # Save best model
        if test_loss < best_test_loss:
            best_test_loss = test_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': train_loss,
                'test_loss': test_loss,
            }, os.path.join(save_dir, 'best_model.pt'))
        
        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_losses': train_losses,
                'test_losses': test_losses,
            }, os.path.join(save_dir, f'checkpoint_epoch_{epoch+1}.pt'))
    
    # Save final model
    torch.save({
        'epoch': num_epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'train_losses': train_losses,
        'test_losses': test_losses,
    }, os.path.join(save_dir, 'final_model.pt'))
    
    # Plot training and test losses
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(test_losses, label='Test Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(save_dir, 'loss_plot.png'))
    
    print(f"Training complete. Models saved to {save_dir}")
    
    return train_losses, test_losses

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Train the DeepPhase model")
    parser.add_argument("--data_dir", type=str, default="./MotionData/100STYLE",
                        help="Directory containing the motion data")
    parser.add_argument("--output_dir", type=str, default="./output/deephase",
                        help="Directory to save models and outputs")
    parser.add_argument("--epochs", type=int, default=100, 
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=64, 
                        help="Batch size for training")
    parser.add_argument("--lr", type=float, default=0.001, 
                        help="Learning rate")
    parser.add_argument("--hidden_dim", type=int, default=512, 
                        help="Hidden dimension size")
    parser.add_argument("--latent_dim", type=int, default=32, 
                        help="Latent dimension size")
    args = parser.parse_args()
    
    # Create timestamp for output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.output_dir, f"run_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if CUDA is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load data
    train_loader, test_loader = load_data(
        args.data_dir, args.batch_size, args.batch_size // 2)
    
    if train_loader is None or test_loader is None:
        print("Failed to load data. Exiting.")
        return
    
    # Get input dimension from data
    sample_batch = next(iter(train_loader))
    input_dim = sample_batch[0].shape[1]
    print(f"Input dimension: {input_dim}")
    
    # Create model
    model = DeepPhaseModel(
        input_dim, hidden_dim=args.hidden_dim, latent_dim=args.latent_dim)
    model.to(device)
    
    # Print model summary
    print(f"DeepPhase model summary:")
    print(f"  Input dimension: {input_dim}")
    print(f"  Hidden dimension: {args.hidden_dim}")
    print(f"  Latent dimension: {args.latent_dim}")
    print(f"  Total parameters: {sum(p.numel() for p in model.parameters())}")
    
    # Train model
    train_losses, test_losses = train(
        model, train_loader, test_loader, device,
        num_epochs=args.epochs, lr=args.lr, save_dir=output_dir)
    
    print(f"Training complete!")

if __name__ == "__main__":
    main()
