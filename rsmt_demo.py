#!/usr/bin/env python3
"""
RSMT Inference Demo

This script demonstrates how to use the trained RSMT models to generate
stylized motion transitions between different styles.
"""

import os
import sys
import torch
import numpy as np
import pickle

# Add project to path
sys.path.append('.')

class RSMTInference:
    """Complete RSMT inference pipeline"""
    
    def __init__(self, deephase_model_path, manifold_model_path, sampler_model_path):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load trained models
        self.deephase_model = self.load_deephase_model(deephase_model_path)
        self.manifold_model = self.load_manifold_model(manifold_model_path)
        self.sampler_model = self.load_sampler_model(sampler_model_path)
        
        print(f"RSMT Inference system loaded on {self.device}")
    
    def load_deephase_model(self, path):
        """Load the DeepPhase model"""
        from train_deephase_simplified import DeepPhaseModel
        
        model = DeepPhaseModel(input_dim=92)  # Use correct input dimension
        checkpoint = torch.load(path, map_location=self.device)
        
        # Handle different checkpoint formats
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
            
        model.eval()
        model.to(self.device)
        return model
    
    def load_manifold_model(self, path):
        """Load the manifold model"""
        # Define manifold model architecture
        class ManifoldVAE(torch.nn.Module):
            def __init__(self, input_dim=32, hidden_dim=128, latent_dim=8):
                super().__init__()
                self.input_dim = input_dim
                self.hidden_dim = hidden_dim
                self.latent_dim = latent_dim
                
                # Encoder
                self.encoder = torch.nn.Sequential(
                    torch.nn.Linear(input_dim, hidden_dim),
                    torch.nn.ReLU(),
                    torch.nn.Linear(hidden_dim, hidden_dim),
                    torch.nn.ReLU()
                )
                
                self.mu = torch.nn.Linear(hidden_dim, latent_dim)
                self.logvar = torch.nn.Linear(hidden_dim, latent_dim)
                
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
                return self.mu(h), self.logvar(h)
            
            def decode(self, z):
                return self.decoder(z)
            
            def forward(self, x):
                mu, logvar = self.encode(x)
                z = mu  # Use mean for inference
                recon_x = self.decode(z)
                return recon_x, mu, logvar
        
        model = ManifoldVAE()
        checkpoint = torch.load(path, map_location=self.device)
        model.load_state_dict(checkpoint)
        model.eval()
        model.to(self.device)
        return model
    
    def load_sampler_model(self, path):
        """Load the transition sampler model"""
        # Define sampler model architecture
        class TransitionSampler(torch.nn.Module):
            def __init__(self, manifold_dim=8, hidden_dim=128, sequence_length=16):
                super().__init__()
                self.manifold_dim = manifold_dim
                self.hidden_dim = hidden_dim
                self.sequence_length = sequence_length
                
                self.encoder = torch.nn.GRU(manifold_dim * 2, hidden_dim, batch_first=True)
                self.decoder = torch.nn.Sequential(
                    torch.nn.Linear(hidden_dim, hidden_dim),
                    torch.nn.ReLU(),
                    torch.nn.Linear(hidden_dim, manifold_dim * sequence_length)
                )
            
            def forward(self, source, target):
                # Create input sequence by interpolating
                batch_size = source.shape[0]
                input_seq = torch.cat([source.unsqueeze(1), target.unsqueeze(1)], dim=1)
                input_seq = input_seq.repeat(1, self.sequence_length // 2, 1)
                input_seq = input_seq.view(batch_size, self.sequence_length // 2, -1)
                
                # Encode
                _, hidden = self.encoder(input_seq)
                
                # Decode to transition sequence
                transition = self.decoder(hidden.squeeze(0))
                return transition.view(batch_size, self.sequence_length, self.manifold_dim)
        
        model = TransitionSampler()
        checkpoint = torch.load(path, map_location=self.device)
        model.load_state_dict(checkpoint)
        model.eval()
        model.to(self.device)
        return model
    
    def generate_transition(self, source_style, target_style, transition_length=60):
        """Generate a transition between two styles"""
        print(f"Generating transition: {source_style} -> {target_style}")
        
        # For this demo, we'll use random points in manifold space
        # In a real application, you would extract these from actual motion data
        source_point = torch.randn(1, 8).to(self.device)
        target_point = torch.randn(1, 8).to(self.device)
        
        # Generate transition path in manifold space
        transition_path = self.sample_transition_path(source_point, target_point, transition_length)
        
        # Decode manifold points to phase vectors
        phase_vectors = self.decode_manifold_to_phase(transition_path)
        
        # Convert phase vectors to motion
        motion_data = self.phase_to_motion(phase_vectors)
        
        return motion_data
    
    def sample_transition_path(self, source, target, length):
        """Sample a smooth transition path in manifold space"""
        # Simple linear interpolation for demonstration
        # The trained sampler would produce more sophisticated paths
        t = torch.linspace(0, 1, length).unsqueeze(1).to(self.device)
        path = source * (1 - t) + target * t
        return path
    
    def decode_manifold_to_phase(self, manifold_points):
        """Decode manifold points back to phase vectors"""
        with torch.no_grad():
            phase_vectors = self.manifold_model.decode(manifold_points)
        return phase_vectors
    
    def phase_to_motion(self, phase_vectors):
        """Convert phase vectors to motion data"""
        from src.utils.motion_decoder import decode_phase_to_motion
        
        phase_np = phase_vectors.cpu().numpy()
        motion_data = decode_phase_to_motion(phase_np)
        return motion_data

def main():
    """Demonstration of RSMT inference"""
    print("=== RSMT Inference Demo ===")
    
    # Model paths (update these to your trained models)
    deephase_path = "./output/deephase/run_20250626_021805/best_model.pt"
    manifold_path = "./output/manifold/run_20250626_024114/best_model.pt"
    sampler_path = "./output/sampler/run_20250626_024425/best_model.pt"
    
    # Check if models exist
    for path in [deephase_path, manifold_path, sampler_path]:
        if not os.path.exists(path):
            print(f"Model not found: {path}")
            print("Please train the models first!")
            return
    
    # Initialize inference system
    rsmt = RSMTInference(deephase_path, manifold_path, sampler_path)
    
    # Generate some example transitions
    transitions = [
        ("Angry", "Happy"),
        ("Walk", "Run"),
        ("Proud", "Depressed")
    ]
    
    output_dir = "./output/inference/demo"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (source, target) in enumerate(transitions):
        print(f"\nGenerating transition {i+1}: {source} -> {target}")
        
        try:
            # Generate motion data
            motion_data = rsmt.generate_transition(source, target, transition_length=60)
            
            # Save to BVH
            from src.utils.bvh_writer import save_to_bvh
            output_path = os.path.join(output_dir, f"transition_{i+1}_{source}_to_{target}.bvh")
            
            success = save_to_bvh(motion_data, output_path)
            if success:
                print(f"  ✅ Saved: {output_path}")
            else:
                print(f"  ❌ Failed to save: {output_path}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n=== Demo Complete ===")
    print(f"Check {output_dir} for generated BVH files!")

if __name__ == "__main__":
    main()
