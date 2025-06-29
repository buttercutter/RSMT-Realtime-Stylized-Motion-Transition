#!/usr/bin/env python3
"""
Minimal RSMT Training Script

This script provides a simplified training pipeline that avoids dependency issues
and focuses on getting the core system working.
"""

import os
import sys
import torch
import numpy as np
import pickle
from datetime import datetime

# Add project root to path
sys.path.append('.')
sys.path.append('src')

def load_100style_data():
    """Load the preprocessed 100STYLE dataset"""
    print("Loading 100STYLE dataset...")
    
    # Check if binary data exists
    data_dir = "./MotionData/100STYLE"
    train_file = os.path.join(data_dir, "train_binary.dat")
    test_file = os.path.join(data_dir, "test_binary.dat")
    
    if not os.path.exists(train_file):
        print(f"Training data not found at {train_file}")
        return None, None
    
    try:
        # Load binary data (this is a simplified loader)
        with open(train_file, 'rb') as f:
            train_data = pickle.load(f)
        
        with open(test_file, 'rb') as f:
            test_data = pickle.load(f)
            
        print(f"Loaded train data: {len(train_data) if train_data else 0} sequences")
        print(f"Loaded test data: {len(test_data) if test_data else 0} sequences")
        
        return train_data, test_data
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def create_minimal_phase_model(input_dim=132, latent_dim=32):
    """Create a minimal phase autoencoder"""
    class PhaseAutoencoder(torch.nn.Module):
        def __init__(self, input_dim, latent_dim):
            super().__init__()
            self.encoder = torch.nn.Sequential(
                torch.nn.Linear(input_dim, 256),
                torch.nn.ReLU(),
                torch.nn.Linear(256, 128),
                torch.nn.ReLU(),
                torch.nn.Linear(128, latent_dim)
            )
            
            self.decoder = torch.nn.Sequential(
                torch.nn.Linear(latent_dim, 128),
                torch.nn.ReLU(),
                torch.nn.Linear(128, 256),
                torch.nn.ReLU(),
                torch.nn.Linear(256, input_dim)
            )
        
        def forward(self, x):
            latent = self.encoder(x)
            reconstructed = self.decoder(latent)
            return reconstructed, latent
    
    return PhaseAutoencoder(input_dim, latent_dim)

def train_minimal_phase_model():
    """Train a minimal phase model"""
    print("Creating minimal phase model...")
    
    # Create dummy data for now (we'll replace this with real data)
    batch_size = 32
    seq_length = 60
    input_dim = 132  # Typical motion data dimension
    
    # Create synthetic training data
    print("Creating synthetic training data...")
    train_data = torch.randn(1000, input_dim)
    
    # Create model
    model = create_minimal_phase_model(input_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.MSELoss()
    
    # Training loop
    print("Starting training...")
    num_epochs = 10
    
    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = len(train_data) // batch_size
        
        for i in range(0, len(train_data), batch_size):
            batch = train_data[i:i+batch_size]
            
            optimizer.zero_grad()
            reconstructed, latent = model(batch)
            loss = criterion(reconstructed, batch)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / num_batches
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")
    
    # Save model
    os.makedirs("./output/phase_model", exist_ok=True)
    model_path = "./output/phase_model/minimal_phase_model.pth"
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")
    
    return model

def test_phase_model():
    """Test the trained phase model"""
    print("Testing phase model...")
    
    # Load model
    model_path = "./output/phase_model/minimal_phase_model.pth"
    if not os.path.exists(model_path):
        print("No trained model found. Please train first.")
        return
    
    model = create_minimal_phase_model()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # Test with dummy data
    test_input = torch.randn(1, 132)
    with torch.no_grad():
        reconstructed, latent = model(test_input)
        
    print(f"Input shape: {test_input.shape}")
    print(f"Latent shape: {latent.shape}")
    print(f"Reconstructed shape: {reconstructed.shape}")
    print("Phase model test completed successfully!")

def main():
    """Main training function"""
    print("=== Minimal RSMT Training ===")
    print(f"Started at: {datetime.now()}")
    
    # Check CUDA availability
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Step 1: Load data
    train_data, test_data = load_100style_data()
    
    # Step 2: Train phase model
    model = train_minimal_phase_model()
    
    # Step 3: Test phase model
    test_phase_model()
    
    print("=== Training completed ===")

if __name__ == "__main__":
    main()
