#!/usr/bin/env python3
"""
Train the manifold model for the RSMT pipeline using the generated phase vectors.
The manifold model aims to learn a lower-dimensional space where phase vectors 
of similar motions are close together and transitions can be smoothly interpolated.
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

class ManifoldEncoderVAE(torch.nn.Module):
    """
    Variational Autoencoder for phase manifold learning.
    This model encodes phase vectors into a lower-dimensional manifold space
    and decodes back to the phase space.
    """
    def __init__(self, input_dim, latent_dim=8, hidden_dim=128):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        
        # Encoder layers
        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.LeakyReLU(0.2)
        )
        
        # Latent space projection (mean and variance)
        self.fc_mu = torch.nn.Linear(hidden_dim, latent_dim)
        self.fc_var = torch.nn.Linear(hidden_dim, latent_dim)
        
        # Decoder layers
        self.decoder = torch.nn.Sequential(
            torch.nn.Linear(latent_dim, hidden_dim),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim, input_dim)
        )
    
    def encode(self, x):
        """
        Encode input to latent distribution parameters
        """
        hidden = self.encoder(x)
        mu = self.fc_mu(hidden)
        log_var = self.fc_var(hidden)
        return mu, log_var
    
    def reparameterize(self, mu, log_var):
        """
        Reparameterization trick
        """
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        z = mu + eps * std
        return z
    
    def decode(self, z):
        """
        Decode from latent space to phase space
        """
        return self.decoder(z)
    
    def forward(self, x):
        """
        Forward pass through the VAE
        """
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        recon_x = self.decode(z)
        return recon_x, mu, log_var, z

def load_phase_data(phase_path):
    """
    Load phase data from the generated phase vectors
    """
    print(f"Loading phase data from {phase_path}")
    
    try:
        with open(phase_path, 'rb') as f:
            phase_data = pickle.load(f)
        
        print(f"Loaded phase data for {len(phase_data)} styles")
        return phase_data
    
    except Exception as e:
        print(f"Error loading phase data: {e}")
        return None

def prepare_data_loaders(phase_data, batch_size=64, val_ratio=0.1):
    """
    Prepare data loaders for training and validation
    """
    # Extract phase vectors from all styles
    all_phases = []
    
    for style_name, style_data in phase_data.items():
        phase = style_data['phase']
        all_phases.append(phase)
    
    # Concatenate all phases
    all_phases = np.vstack(all_phases)
    print(f"Total phase vectors: {all_phases.shape[0]}")
    
    # Convert to tensor
    phase_tensors = torch.tensor(all_phases, dtype=torch.float32)
    
    # Split into training and validation sets
    val_size = int(phase_tensors.shape[0] * val_ratio)
    train_size = phase_tensors.shape[0] - val_size
    
    train_dataset, val_dataset = torch.utils.data.random_split(
        phase_tensors, [train_size, val_size])
    
    # Create data loaders
    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False)
    
    print(f"Training set: {len(train_dataset)} samples")
    print(f"Validation set: {len(val_dataset)} samples")
    
    return train_loader, val_loader, phase_tensors.shape[1]

def vae_loss_function(recon_x, x, mu, log_var, kld_weight=0.005):
    """
    VAE loss function: reconstruction loss + KL divergence
    """
    # Reconstruction loss (MSE)
    recon_loss = torch.nn.functional.mse_loss(recon_x, x, reduction='sum')
    
    # KL divergence
    kld_loss = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    
    # Total loss
    return recon_loss + kld_weight * kld_loss, recon_loss, kld_loss

def train(model, train_loader, val_loader, device, num_epochs=100, 
          lr=0.001, kld_weight=0.005, save_dir="./output/manifold"):
    """
    Train the manifold encoder
    """
    # Create optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    # For tracking progress
    train_losses = []
    val_losses = []
    train_recon_losses = []
    train_kld_losses = []
    val_recon_losses = []
    val_kld_losses = []
    
    # For saving the best model
    best_val_loss = float('inf')
    
    # Create directory for saving models
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(save_dir, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"Starting training for {num_epochs} epochs")
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0
        train_recon = 0
        train_kld = 0
        
        for batch_idx, x in enumerate(train_loader):
            x = x.to(device)
            
            # Reset gradients
            optimizer.zero_grad()
            
            # Forward pass
            recon_x, mu, log_var, z = model(x)
            
            # Calculate loss
            loss, recon, kld = vae_loss_function(recon_x, x, mu, log_var, kld_weight)
            
            # Backward pass
            loss.backward()
            
            # Update weights
            optimizer.step()
            
            # Accumulate losses
            train_loss += loss.item()
            train_recon += recon.item()
            train_kld += kld.item()
        
        # Average losses
        train_loss /= len(train_loader.dataset)
        train_recon /= len(train_loader.dataset)
        train_kld /= len(train_loader.dataset)
        
        train_losses.append(train_loss)
        train_recon_losses.append(train_recon)
        train_kld_losses.append(train_kld)
        
        # Validation
        model.eval()
        val_loss = 0
        val_recon = 0
        val_kld = 0
        
        with torch.no_grad():
            for batch_idx, x in enumerate(val_loader):
                x = x.to(device)
                
                # Forward pass
                recon_x, mu, log_var, z = model(x)
                
                # Calculate loss
                loss, recon, kld = vae_loss_function(recon_x, x, mu, log_var, kld_weight)
                
                # Accumulate losses
                val_loss += loss.item()
                val_recon += recon.item()
                val_kld += kld.item()
        
        # Average losses
        val_loss /= len(val_loader.dataset)
        val_recon /= len(val_loader.dataset)
        val_kld /= len(val_loader.dataset)
        
        val_losses.append(val_loss)
        val_recon_losses.append(val_recon)
        val_kld_losses.append(val_kld)
        
        # Print progress
        print(f"Epoch {epoch+1}/{num_epochs}: "
              f"Train Loss: {train_loss:.6f} (Recon: {train_recon:.6f}, KLD: {train_kld:.6f}), "
              f"Val Loss: {val_loss:.6f} (Recon: {val_recon:.6f}, KLD: {val_kld:.6f})")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': train_loss,
                'val_loss': val_loss,
                'input_dim': model.input_dim,
                'latent_dim': model.latent_dim,
                'hidden_dim': model.hidden_dim
            }, os.path.join(run_dir, 'best_model.pt'))
            print(f"Best model saved (validation loss: {val_loss:.6f})")
        
        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_losses': train_losses,
                'val_losses': val_losses,
                'train_recon_losses': train_recon_losses,
                'train_kld_losses': train_kld_losses,
                'val_recon_losses': val_recon_losses,
                'val_kld_losses': val_kld_losses,
                'input_dim': model.input_dim,
                'latent_dim': model.latent_dim,
                'hidden_dim': model.hidden_dim
            }, os.path.join(run_dir, f'checkpoint_epoch_{epoch+1}.pt'))
    
    # Save final model
    torch.save({
        'epoch': num_epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_recon_losses': train_recon_losses,
        'train_kld_losses': train_kld_losses,
        'val_recon_losses': val_recon_losses,
        'val_kld_losses': val_kld_losses,
        'input_dim': model.input_dim,
        'latent_dim': model.latent_dim,
        'hidden_dim': model.hidden_dim
    }, os.path.join(run_dir, 'final_model.pt'))
    
    # Plot training and validation losses
    plt.figure(figsize=(12, 8))
    
    # Total loss
    plt.subplot(2, 1, 1)
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Total Loss')
    plt.legend()
    plt.grid(True)
    
    # Component losses
    plt.subplot(2, 2, 3)
    plt.plot(train_recon_losses, label='Training')
    plt.plot(val_recon_losses, label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Reconstruction Loss')
    plt.title('Reconstruction Loss')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 2, 4)
    plt.plot(train_kld_losses, label='Training')
    plt.plot(val_kld_losses, label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('KL Divergence Loss')
    plt.title('KL Divergence Loss')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(run_dir, 'loss_curves.png'))
    
    print(f"Training complete. Models and plots saved to {run_dir}")
    return model, run_dir

def visualize_manifold(model, phase_tensors, run_dir, device, num_samples=1000):
    """
    Visualize the learned manifold space
    """
    print("Visualizing manifold space...")
    
    # Set model to evaluation mode
    model.eval()
    
    # Select a subset of phase vectors for visualization
    if phase_tensors.shape[0] > num_samples:
        indices = np.random.choice(phase_tensors.shape[0], num_samples, replace=False)
        samples = phase_tensors[indices]
    else:
        samples = phase_tensors
    
    # Move samples to device
    samples = samples.to(device)
    
    # Encode samples to manifold space
    with torch.no_grad():
        mu, _ = model.encode(samples)
        z = mu.cpu().numpy()
    
    # Use PCA for visualization if latent dimension > 2
    if model.latent_dim > 2:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        z_2d = pca.fit_transform(z)
        title = "Manifold Space (PCA Projection)"
        explained_var = pca.explained_variance_ratio_.sum()
        title += f" - Explained Variance: {explained_var:.2f}"
    else:
        z_2d = z
        title = "Manifold Space"
    
    # Plot
    plt.figure(figsize=(10, 8))
    plt.scatter(z_2d[:, 0], z_2d[:, 1], alpha=0.5, s=5)
    plt.title(title)
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(run_dir, 'manifold_space.png'))
    
    # Generate samples from manifold
    grid_size = 20
    if model.latent_dim >= 2:
        # Create a grid in the first two dimensions of the latent space
        x = np.linspace(-2, 2, grid_size)
        y = np.linspace(-2, 2, grid_size)
        grid_x, grid_y = np.meshgrid(x, y)
        
        # Create latent vectors with zeros in all other dimensions
        z_grid = np.zeros((grid_size * grid_size, model.latent_dim))
        z_grid[:, 0] = grid_x.flatten()
        z_grid[:, 1] = grid_y.flatten()
        
        # Convert to tensor and move to device
        z_grid_tensor = torch.tensor(z_grid, dtype=torch.float32).to(device)
        
        # Decode to phase space
        with torch.no_grad():
            decoded = model.decode(z_grid_tensor)
            decoded = decoded.cpu().numpy()
        
        # Plot a heatmap of the decoded values (mean across all phase dimensions)
        plt.figure(figsize=(10, 8))
        
        # Calculate the mean of absolute values across phase dimensions
        mean_activation = np.mean(np.abs(decoded), axis=1)
        mean_activation = mean_activation.reshape(grid_size, grid_size)
        
        plt.imshow(mean_activation, extent=[-2, 2, -2, 2], origin='lower', cmap='viridis')
        plt.colorbar(label='Mean Activation')
        plt.title("Manifold Space Activation")
        plt.xlabel("Latent Dimension 1")
        plt.ylabel("Latent Dimension 2")
        plt.savefig(os.path.join(run_dir, 'manifold_activation.png'))
    
    print(f"Manifold visualizations saved to {run_dir}")

def main(args):
    try:
        # Set device
        device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
        print(f"Using device: {device}")
        
        # Print argument values
        print("\nTraining parameters:")
        for arg in vars(args):
            print(f"  {arg}: {getattr(args, arg)}")
        
        # Create output directory
        print(f"\nCreating output directory: {args.output_dir}")
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Load phase data
        phase_data = load_phase_data(args.phase_data)
        
        if phase_data is None:
            print("Failed to load phase data. Exiting.")
            return
        
        # Print sample of the loaded data
        print("\nPhase data sample:")
        first_style = list(phase_data.keys())[0]
        print(f"  First style: {first_style}")
        print(f"  Keys: {list(phase_data[first_style].keys())}")
        if 'phase' in phase_data[first_style]:
            phase = phase_data[first_style]['phase']
            print(f"  Phase shape: {phase.shape}")
            print(f"  Phase min/max: {np.min(phase):.4f}/{np.max(phase):.4f}")
    except Exception as e:
        print(f"Error in setup: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Prepare data loaders
    train_loader, val_loader, input_dim = prepare_data_loaders(
        phase_data, batch_size=args.batch_size, val_ratio=args.val_ratio)
    
    # Create model
    model = ManifoldEncoderVAE(
        input_dim=input_dim, 
        latent_dim=args.latent_dim, 
        hidden_dim=args.hidden_dim
    )
    
    # Move model to device
    model = model.to(device)
    
    # Print model summary
    print("\nManifold model summary:")
    print(f"  Input dimension: {input_dim}")
    print(f"  Hidden dimension: {args.hidden_dim}")
    print(f"  Latent dimension: {args.latent_dim}")
    print(f"  Total parameters: {sum(p.numel() for p in model.parameters())}")
    
    # Train model
    model, run_dir = train(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        num_epochs=args.epochs,
        lr=args.learning_rate,
        kld_weight=args.kld_weight,
        save_dir=args.output_dir
    )
    
    # Visualize manifold
    visualize_manifold(
        model=model,
        phase_tensors=torch.tensor(np.vstack([data['phase'] for _, data in phase_data.items()]), dtype=torch.float32),
        run_dir=run_dir,
        device=device
    )
    
    print("Manifold training complete!")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Train manifold encoder for phase vectors")
    
    parser.add_argument("--phase-data", type=str, default="./output/phases/train_phases.dat",
                        help="Path to the phase data file")
    parser.add_argument("--output-dir", type=str, default="./output/manifold",
                        help="Directory to save trained models and visualizations")
    parser.add_argument("--batch-size", type=int, default=64,
                        help="Batch size for training")
    parser.add_argument("--epochs", type=int, default=100,
                        help="Number of training epochs")
    parser.add_argument("--learning-rate", type=float, default=0.001,
                        help="Learning rate")
    parser.add_argument("--latent-dim", type=int, default=8,
                        help="Dimensionality of latent manifold space")
    parser.add_argument("--hidden-dim", type=int, default=128,
                        help="Dimensionality of hidden layers")
    parser.add_argument("--val-ratio", type=float, default=0.1,
                        help="Ratio of validation data")
    parser.add_argument("--kld-weight", type=float, default=0.005,
                        help="Weight of KL divergence loss term")
    parser.add_argument("--cpu", action="store_true",
                        help="Use CPU instead of GPU")
    
    args = parser.parse_args()
    
    main(args)
