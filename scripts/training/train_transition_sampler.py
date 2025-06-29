#!/usr/bin/env python3
"""
Train the transition sampler network for the RSMT pipeline.
This model learns to sample from the phase manifold to create smooth transitions
between different motion styles.
"""

import os
import sys
import torch
import numpy as np
import pickle
import argparse
from datetime import datetime
import matplotlib.pyplot as plt
from tqdm import tqdm

# Add the repository root to the path
sys.path.append('.')

class TransitionSampler(torch.nn.Module):
    """
    Transition sampler network.
    This model takes two motion styles and generates a smooth transition path
    in the manifold space between them.
    """
    def __init__(self, manifold_dim=8, hidden_dim=128, sequence_length=16):
        super().__init__()
        self.manifold_dim = manifold_dim
        self.hidden_dim = hidden_dim
        self.sequence_length = sequence_length
        
        # Input features: start point, end point, transition progress (normalized to 0-1)
        input_dim = manifold_dim * 2 + 1
        
        # Path generator - autoregressive LSTM-based network
        self.lstm = torch.nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True
        )
        
        # Output projection
        self.output = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim, manifold_dim)
        )
        
        # Additional path refinement network
        self.refine = torch.nn.Sequential(
            torch.nn.Linear(manifold_dim + input_dim, hidden_dim),
            torch.nn.LeakyReLU(0.2),
            torch.nn.Linear(hidden_dim, manifold_dim)
        )
    
    def forward(self, start_points, end_points, num_steps=None):
        """
        Generate a transition path between start and end points.
        
        Args:
            start_points: Tensor of shape [batch_size, manifold_dim]
            end_points: Tensor of shape [batch_size, manifold_dim]
            num_steps: Number of steps in the transition path (default: self.sequence_length)
            
        Returns:
            Tensor of shape [batch_size, num_steps, manifold_dim] representing the transition path
        """
        batch_size = start_points.shape[0]
        
        if num_steps is None:
            num_steps = self.sequence_length
        
        # Create progress values from 0 to 1
        t = torch.linspace(0, 1, num_steps, device=start_points.device)
        t = t.view(1, -1, 1).repeat(batch_size, 1, 1)  # [batch_size, num_steps, 1]
        
        # Expand start and end points
        start_expanded = start_points.unsqueeze(1).repeat(1, num_steps, 1)  # [batch_size, num_steps, manifold_dim]
        end_expanded = end_points.unsqueeze(1).repeat(1, num_steps, 1)    # [batch_size, num_steps, manifold_dim]
        
        # Concatenate inputs
        inputs = torch.cat([start_expanded, end_expanded, t], dim=2)  # [batch_size, num_steps, manifold_dim*2+1]
        
        # Generate initial path through LSTM
        lstm_out, _ = self.lstm(inputs)
        
        # Project to manifold space
        path = self.output(lstm_out)
        
        # Refine the path
        concat_refine = torch.cat([path, inputs], dim=2)
        refined_path = self.refine(concat_refine)
        
        # Add residual connection
        final_path = path + refined_path
        
        return final_path

def load_manifold_model(model_path):
    """
    Load the trained manifold model
    """
    print(f"Loading manifold model from {model_path}")
    
    try:
        # Load checkpoint
        checkpoint = torch.load(model_path)
        
        # Import the manifold model class
        from train_manifold_model import ManifoldEncoderVAE
        
        # Get model parameters
        if 'input_dim' in checkpoint:
            input_dim = checkpoint['input_dim']
        else:
            # Try to infer from the state dict
            # This is a fallback and may not always work
            input_dim = 32  # Default from our previous training
            print(f"Input dimension not found in checkpoint, using default: {input_dim}")
        
        if 'latent_dim' in checkpoint:
            latent_dim = checkpoint['latent_dim']
        else:
            latent_dim = 8
            print(f"Latent dimension not found in checkpoint, using default: {latent_dim}")
        
        if 'hidden_dim' in checkpoint:
            hidden_dim = checkpoint['hidden_dim']
        else:
            hidden_dim = 128
            print(f"Hidden dimension not found in checkpoint, using default: {hidden_dim}")
        
        # Create model
        model = ManifoldEncoderVAE(
            input_dim=input_dim,
            latent_dim=latent_dim,
            hidden_dim=hidden_dim
        )
        
        # Load state dict
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
        
        # Set to eval mode
        model.eval()
        
        print(f"Manifold model loaded successfully")
        print(f"  Input dim: {input_dim}")
        print(f"  Latent dim: {latent_dim}")
        print(f"  Hidden dim: {hidden_dim}")
        
        return model
    
    except Exception as e:
        print(f"Error loading manifold model: {e}")
        import traceback
        traceback.print_exc()
        return None

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

def prepare_transition_dataset(manifold_model, phase_data, device, num_samples=10000, min_frames=20):
    """
    Prepare a dataset for training the transition sampler.
    Creates pairs of start and end points in the manifold space.
    """
    print(f"Preparing transition dataset with {num_samples} samples")
    
    # Extract all phase vectors
    all_phases = []
    style_indices = {}
    current_idx = 0
    
    for style_name, style_data in phase_data.items():
        phase = style_data['phase']
        
        # Skip styles with too few frames
        if phase.shape[0] < min_frames:
            continue
        
        style_indices[style_name] = (current_idx, current_idx + phase.shape[0])
        all_phases.append(phase)
        current_idx += phase.shape[0]
    
    # Concatenate all phases
    all_phases = np.vstack(all_phases)
    print(f"Total phase vectors: {all_phases.shape[0]}")
    
    # Convert to tensor and move to device
    all_phases = torch.tensor(all_phases, dtype=torch.float32).to(device)
    
    # Encode to manifold space
    with torch.no_grad():
        mu, _ = manifold_model.encode(all_phases)
        manifold_points = mu.detach().cpu().numpy()
    
    print(f"Encoded to manifold space: {manifold_points.shape}")
    
    # Create transition pairs
    start_points = []
    end_points = []
    
    # Sample from same and different styles
    for i in range(num_samples):
        if i % 2 == 0:
            # Same style, different frames
            style_name = np.random.choice(list(style_indices.keys()))
            start_idx, end_idx = style_indices[style_name]
            
            # Sample two different frames
            idx1 = np.random.randint(start_idx, end_idx)
            idx2 = np.random.randint(start_idx, end_idx)
            
            # Make sure they're different
            while idx2 == idx1:
                idx2 = np.random.randint(start_idx, end_idx)
        else:
            # Different styles
            style1, style2 = np.random.choice(list(style_indices.keys()), 2, replace=False)
            start_idx1, end_idx1 = style_indices[style1]
            start_idx2, end_idx2 = style_indices[style2]
            
            # Sample a frame from each style
            idx1 = np.random.randint(start_idx1, end_idx1)
            idx2 = np.random.randint(start_idx2, end_idx2)
        
        # Add to dataset
        start_points.append(manifold_points[idx1])
        end_points.append(manifold_points[idx2])
    
    # Convert to tensors
    start_points = torch.tensor(np.array(start_points), dtype=torch.float32)
    end_points = torch.tensor(np.array(end_points), dtype=torch.float32)
    
    print(f"Created transition dataset: {start_points.shape[0]} pairs")
    
    return start_points, end_points, manifold_points

def prepare_data_loaders(start_points, end_points, batch_size=64, val_ratio=0.1):
    """
    Prepare data loaders for training and validation
    """
    # Create TensorDataset
    dataset = torch.utils.data.TensorDataset(start_points, end_points)
    
    # Split into training and validation
    val_size = int(len(dataset) * val_ratio)
    train_size = len(dataset) - val_size
    
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    # Create data loaders
    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False)
    
    print(f"Training set: {len(train_dataset)} samples")
    print(f"Validation set: {len(val_dataset)} samples")
    
    return train_loader, val_loader

def transition_loss(path, start_points, end_points, all_manifold_points=None, knn=100):
    """
    Custom loss function for evaluating transition paths.
    Includes:
    1. Endpoint matching loss (start and end of path should match input points)
    2. Smoothness loss (path should be smooth)
    3. Manifold consistency loss (path should stay on the manifold)
    """
    batch_size, num_steps, manifold_dim = path.shape
    
    # 1. Endpoint matching loss
    start_loss = torch.nn.functional.mse_loss(path[:, 0, :], start_points)
    end_loss = torch.nn.functional.mse_loss(path[:, -1, :], end_points)
    endpoint_loss = start_loss + end_loss
    
    # 2. Smoothness loss - using first and second derivatives
    # First derivative approximation: v[t+1] - v[t]
    first_derivative = path[:, 1:, :] - path[:, :-1, :]
    smoothness_loss_1 = torch.mean(torch.sum(first_derivative**2, dim=2))
    
    # Second derivative approximation: v[t+2] - 2*v[t+1] + v[t]
    if num_steps > 2:
        second_derivative = path[:, 2:, :] - 2 * path[:, 1:-1, :] + path[:, :-2, :]
        smoothness_loss_2 = torch.mean(torch.sum(second_derivative**2, dim=2))
    else:
        smoothness_loss_2 = 0
    
    smoothness_loss = smoothness_loss_1 + 0.5 * smoothness_loss_2
    
    # 3. Manifold consistency loss (optional)
    # This is more expensive and uses nearest neighbor search
    manifold_loss = 0
    if all_manifold_points is not None:
        # Reshape path to [batch_size * num_steps, manifold_dim]
        flat_path = path.reshape(-1, manifold_dim)
        
        # For each point in the path, find the distance to the nearest manifold point
        # This is computationally expensive, so we'll use a simplified approach
        # For a full implementation, you would use a KD-tree or similar data structure
        
        # Convert all manifold points to tensor if it's not already
        if not torch.is_tensor(all_manifold_points):
            all_manifold_points = torch.tensor(all_manifold_points, dtype=torch.float32, device=path.device)
        
        # Simple nearest neighbor search
        # Calculate pairwise distances
        # This can be memory-intensive for large manifold point sets
        distances = torch.cdist(flat_path, all_manifold_points)
        
        # Get the k nearest neighbors
        # This is a simplified version that only uses the closest neighbor
        min_dists, _ = torch.topk(distances, k=1, dim=1, largest=False)
        
        # Manifold loss is the mean distance to nearest neighbor
        manifold_loss = torch.mean(min_dists)
    
    # Combine losses with weighting
    total_loss = endpoint_loss + 0.1 * smoothness_loss + 0.01 * manifold_loss
    
    return total_loss, (endpoint_loss, smoothness_loss, manifold_loss)

def train(model, manifold_model, train_loader, val_loader, device, manifold_points=None,
          num_epochs=50, lr=0.001, save_dir="./output/sampler"):
    """
    Train the transition sampler
    """
    # Create optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    # For tracking progress
    train_losses = []
    val_losses = []
    train_endpoint_losses = []
    train_smoothness_losses = []
    train_manifold_losses = []
    val_endpoint_losses = []
    val_smoothness_losses = []
    val_manifold_losses = []
    
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
        train_endpoint = 0
        train_smoothness = 0
        train_manifold = 0
        
        for batch_idx, (start_points, end_points) in enumerate(tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}")):
            start_points = start_points.to(device)
            end_points = end_points.to(device)
            
            # Reset gradients
            optimizer.zero_grad()
            
            # Forward pass - generate transition path
            path = model(start_points, end_points)
            
            # Calculate loss
            loss, (endpoint_loss, smoothness_loss, manifold_loss) = transition_loss(
                path, start_points, end_points, manifold_points)
            
            # Backward pass
            loss.backward()
            
            # Update weights
            optimizer.step()
            
            # Accumulate losses
            train_loss += loss.item()
            train_endpoint += endpoint_loss.item()
            train_smoothness += smoothness_loss.item()
            train_manifold += manifold_loss.item() if torch.is_tensor(manifold_loss) else manifold_loss
        
        # Average losses
        train_loss /= len(train_loader)
        train_endpoint /= len(train_loader)
        train_smoothness /= len(train_loader)
        train_manifold /= len(train_loader)
        
        train_losses.append(train_loss)
        train_endpoint_losses.append(train_endpoint)
        train_smoothness_losses.append(train_smoothness)
        train_manifold_losses.append(train_manifold)
        
        # Validation
        model.eval()
        val_loss = 0
        val_endpoint = 0
        val_smoothness = 0
        val_manifold = 0
        
        with torch.no_grad():
            for batch_idx, (start_points, end_points) in enumerate(val_loader):
                start_points = start_points.to(device)
                end_points = end_points.to(device)
                
                # Forward pass
                path = model(start_points, end_points)
                
                # Calculate loss
                loss, (endpoint_loss, smoothness_loss, manifold_loss) = transition_loss(
                    path, start_points, end_points, manifold_points)
                
                # Accumulate losses
                val_loss += loss.item()
                val_endpoint += endpoint_loss.item()
                val_smoothness += smoothness_loss.item()
                val_manifold += manifold_loss.item() if torch.is_tensor(manifold_loss) else manifold_loss
        
        # Average losses
        val_loss /= len(val_loader)
        val_endpoint /= len(val_loader)
        val_smoothness /= len(val_loader)
        val_manifold /= len(val_loader)
        
        val_losses.append(val_loss)
        val_endpoint_losses.append(val_endpoint)
        val_smoothness_losses.append(val_smoothness)
        val_manifold_losses.append(val_manifold)
        
        # Print progress
        print(f"Epoch {epoch+1}/{num_epochs}: "
              f"Train Loss: {train_loss:.6f} (Endpoint: {train_endpoint:.6f}, "
              f"Smoothness: {train_smoothness:.6f}, Manifold: {train_manifold:.6f}), "
              f"Val Loss: {val_loss:.6f} (Endpoint: {val_endpoint:.6f}, "
              f"Smoothness: {val_smoothness:.6f}, Manifold: {val_manifold:.6f})")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': train_loss,
                'val_loss': val_loss,
                'manifold_dim': model.manifold_dim,
                'hidden_dim': model.hidden_dim,
                'sequence_length': model.sequence_length
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
                'train_endpoint_losses': train_endpoint_losses,
                'train_smoothness_losses': train_smoothness_losses,
                'train_manifold_losses': train_manifold_losses,
                'val_endpoint_losses': val_endpoint_losses,
                'val_smoothness_losses': val_smoothness_losses,
                'val_manifold_losses': val_manifold_losses,
                'manifold_dim': model.manifold_dim,
                'hidden_dim': model.hidden_dim,
                'sequence_length': model.sequence_length
            }, os.path.join(run_dir, f'checkpoint_epoch_{epoch+1}.pt'))
    
    # Save final model
    torch.save({
        'epoch': num_epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_endpoint_losses': train_endpoint_losses,
        'train_smoothness_losses': train_smoothness_losses,
        'train_manifold_losses': train_manifold_losses,
        'val_endpoint_losses': val_endpoint_losses,
        'val_smoothness_losses': val_smoothness_losses,
        'val_manifold_losses': val_manifold_losses,
        'manifold_dim': model.manifold_dim,
        'hidden_dim': model.hidden_dim,
        'sequence_length': model.sequence_length
    }, os.path.join(run_dir, 'final_model.pt'))
    
    # Plot training and validation losses
    plt.figure(figsize=(12, 10))
    
    # Total loss
    plt.subplot(3, 1, 1)
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Total Loss')
    plt.legend()
    plt.grid(True)
    
    # Component losses
    plt.subplot(3, 3, 4)
    plt.plot(train_endpoint_losses, label='Training')
    plt.plot(val_endpoint_losses, label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Endpoint Loss')
    plt.title('Endpoint Loss')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(3, 3, 5)
    plt.plot(train_smoothness_losses, label='Training')
    plt.plot(val_smoothness_losses, label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Smoothness Loss')
    plt.title('Smoothness Loss')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(3, 3, 6)
    plt.plot(train_manifold_losses, label='Training')
    plt.plot(val_manifold_losses, label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Manifold Loss')
    plt.title('Manifold Loss')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(run_dir, 'loss_curves.png'))
    
    print(f"Training complete. Models and plots saved to {run_dir}")
    return model, run_dir

def visualize_transitions(model, manifold_model, device, num_samples=5):
    """
    Visualize transitions between random pairs of points
    """
    # Create random start and end points in the manifold space
    # Use a smaller scale for the random points to keep them in a reasonable range
    start_points = torch.randn(num_samples, model.manifold_dim).to(device) * 0.5
    end_points = torch.randn(num_samples, model.manifold_dim).to(device) * 0.5
    
    # Generate transition paths
    model.eval()
    with torch.no_grad():
        paths = model(start_points, end_points)
    
    # Plot the paths
    plt.figure(figsize=(15, 10))
    
    for i in range(num_samples):
        plt.subplot(num_samples, 1, i + 1)
        
        # Get path for this sample
        path = paths[i].detach().cpu().numpy()
        
        # Plot each dimension with a different color
        for dim in range(min(model.manifold_dim, 8)):  # Limit to 8 dimensions for clarity
            plt.plot(path[:, dim], label=f'Dim {dim}')
        
        plt.title(f'Transition Path {i+1}')
        plt.xlabel('Step')
        plt.ylabel('Manifold Value')
        if i == 0:
            plt.legend()
    
    plt.tight_layout()
    
    return plt.gcf()

def main(args):
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    print(f"Using device: {device}")
    
    # Print arguments
    print("\nArguments:")
    for arg in vars(args):
        print(f"  {arg}: {getattr(args, arg)}")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load manifold model
    manifold_model = load_manifold_model(args.manifold_model)
    
    if manifold_model is None:
        print("Failed to load manifold model. Exiting.")
        return
    
    # Move manifold model to device
    manifold_model = manifold_model.to(device)
    
    # Load phase data
    phase_data = load_phase_data(args.phase_data)
    
    if phase_data is None:
        print("Failed to load phase data. Exiting.")
        return
    
    # Prepare transition dataset
    start_points, end_points, manifold_points = prepare_transition_dataset(
        manifold_model, phase_data, device, 
        num_samples=args.num_samples,
        min_frames=args.min_frames
    )
    
    # Prepare data loaders
    train_loader, val_loader = prepare_data_loaders(
        start_points, end_points,
        batch_size=args.batch_size,
        val_ratio=args.val_ratio
    )
    
    # Create sampler model
    sampler_model = TransitionSampler(
        manifold_dim=manifold_model.latent_dim,
        hidden_dim=args.hidden_dim,
        sequence_length=args.sequence_length
    )
    
    # Move model to device
    sampler_model = sampler_model.to(device)
    
    # Print model summary
    print("\nTransition sampler model summary:")
    print(f"  Manifold dimension: {manifold_model.latent_dim}")
    print(f"  Hidden dimension: {args.hidden_dim}")
    print(f"  Sequence length: {args.sequence_length}")
    print(f"  Total parameters: {sum(p.numel() for p in sampler_model.parameters())}")
    
    # Train model
    sampler_model, run_dir = train(
        model=sampler_model,
        manifold_model=manifold_model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        manifold_points=torch.tensor(manifold_points, device=device) if args.use_manifold_loss else None,
        num_epochs=args.epochs,
        lr=args.learning_rate,
        save_dir=args.output_dir
    )
    
    # Visualize transitions
    print("Visualizing random transitions...")
    fig = visualize_transitions(sampler_model, manifold_model, device)
    fig.savefig(os.path.join(run_dir, 'transition_examples.png'))
    
    print("Training complete!")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Train transition sampler for the manifold")
    
    parser.add_argument("--manifold-model", type=str, default="./output/manifold/run_20250509_143611/best_model.pt",
                        help="Path to the trained manifold model")
    parser.add_argument("--phase-data", type=str, default="./output/phases/train_phases.dat",
                        help="Path to the phase data")
    parser.add_argument("--output-dir", type=str, default="./output/sampler",
                        help="Directory to save trained models and visualizations")
    parser.add_argument("--batch-size", type=int, default=32,
                        help="Batch size for training")
    parser.add_argument("--epochs", type=int, default=50,
                        help="Number of training epochs")
    parser.add_argument("--learning-rate", type=float, default=0.001,
                        help="Learning rate")
    parser.add_argument("--hidden-dim", type=int, default=128,
                        help="Dimensionality of hidden layers")
    parser.add_argument("--sequence-length", type=int, default=16,
                        help="Number of steps in the transition sequence")
    parser.add_argument("--val-ratio", type=float, default=0.1,
                        help="Ratio of validation data")
    parser.add_argument("--num-samples", type=int, default=10000,
                        help="Number of transition samples to generate")
    parser.add_argument("--min-frames", type=int, default=10,
                        help="Minimum number of frames required for a style")
    parser.add_argument("--use-manifold-loss", action="store_true",
                        help="Use manifold consistency loss (slower but potentially better results)")
    parser.add_argument("--cpu", action="store_true",
                        help="Use CPU instead of GPU")
    
    args = parser.parse_args()
    
    main(args)
