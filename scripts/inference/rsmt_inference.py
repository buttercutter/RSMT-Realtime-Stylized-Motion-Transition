#!/usr/bin/env python3
"""
RSMT (Real-time Stylized Motion Transition) Inference Pipeline

This script provides end-to-end inference for the RSMT system, combining:
1. DeepPhase model for phase encoding
2. Manifold model for style encoding
3. Transition sampler for generating smooth transitions

Usage:
    python rsmt_inference.py --source_style [SOURCE_STYLE] --target_style [TARGET_STYLE] --transition_length [LENGTH]
"""

import os
import sys
import torch
import numpy as np
import pickle
import argparse
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import torch.nn.functional as F

# Add the repository root to the path
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Function to load the DeepPhase model
def load_deephase_model(model_path):
    """
    Load the trained DeepPhase model
    """
    print(f"Loading DeepPhase model from {model_path}")
    
    try:
        # Load checkpoint
        checkpoint = torch.load(model_path)
        
        # Import the DeepPhase model class
        from train_deephase_simplified import DeepPhaseModel
        
        # Create model - use default parameters from our training
        model = DeepPhaseModel(
            input_dim=32,
            hidden_dim=128,
            output_dim=32
        )
        
        # Load state dict
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
        
        # Set to eval mode
        model.eval()
        
        print(f"DeepPhase model loaded successfully")
        return model
    
    except Exception as e:
        print(f"Error loading DeepPhase model: {e}")
        import traceback
        traceback.print_exc()
        return None

# Function to load the Manifold model
def load_manifold_model(model_path):
    """
    Load the trained manifold model
    """
    print(f"Loading Manifold model from {model_path}")
    
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
            input_dim = 32  # Default from our training
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
        print(f"Error loading Manifold model: {e}")
        import traceback
        traceback.print_exc()
        return None

# Function to load the Transition Sampler model
def load_transition_model(model_path):
    """
    Load the trained transition sampler model
    """
    print(f"Loading Transition Sampler model from {model_path}")
    
    try:
        # Load checkpoint
        checkpoint = torch.load(model_path)
        
        # Import the transition sampler model class
        from train_transition_sampler import TransitionSampler
        
        # Get model parameters
        if 'manifold_dim' in checkpoint:
            manifold_dim = checkpoint['manifold_dim']
        else:
            manifold_dim = 8  # Default from our training
            print(f"Manifold dimension not found in checkpoint, using default: {manifold_dim}")
        
        if 'hidden_dim' in checkpoint:
            hidden_dim = checkpoint['hidden_dim']
        else:
            hidden_dim = 128
            print(f"Hidden dimension not found in checkpoint, using default: {hidden_dim}")
        
        if 'sequence_length' in checkpoint:
            sequence_length = checkpoint['sequence_length']
        else:
            sequence_length = 16
            print(f"Sequence length not found in checkpoint, using default: {sequence_length}")
        
        # Create model
        model = TransitionSampler(
            manifold_dim=manifold_dim,
            hidden_dim=hidden_dim,
            sequence_length=sequence_length
        )
        
        # Load state dict
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
        
        # Set to eval mode
        model.eval()
        
        print(f"Transition Sampler model loaded successfully")
        print(f"  Manifold dim: {manifold_dim}")
        print(f"  Hidden dim: {hidden_dim}")
        print(f"  Sequence length: {sequence_length}")
        
        return model
    
    except Exception as e:
        print(f"Error loading Transition Sampler model: {e}")
        import traceback
        traceback.print_exc()
        return None

# Function to load phase data
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

def encode_style_to_manifold(manifold_model, style_phase_vectors, device):
    """
    Encode style phase vectors to manifold space
    
    Args:
        manifold_model: The trained manifold model
        style_phase_vectors: Phase vectors for the style
        device: Device to use for computation
    
    Returns:
        Manifold space representation of the style
    """
    # Convert to tensor
    phase_tensor = torch.tensor(style_phase_vectors, dtype=torch.float32).to(device)
    
    # Encode to manifold space
    with torch.no_grad():
        mu, _ = manifold_model.encode(phase_tensor)
        manifold_point = mu.detach()
    
    return manifold_point

def generate_transition(transition_model, start_point, end_point, num_steps, device):
    """
    Generate a transition between two points in the manifold space
    
    Args:
        transition_model: The trained transition sampler model
        start_point: Starting point in the manifold space
        end_point: Ending point in the manifold space
        num_steps: Number of steps in the transition
        device: Device to use for computation
    
    Returns:
        Tensor of shape [num_steps, manifold_dim] representing the transition path
    """
    # Ensure inputs are proper tensors
    if not isinstance(start_point, torch.Tensor):
        start_point = torch.tensor(start_point, dtype=torch.float32)
    if not isinstance(end_point, torch.Tensor):
        end_point = torch.tensor(end_point, dtype=torch.float32)
    
    # Add batch dimension if needed
    if start_point.dim() == 1:
        start_point = start_point.unsqueeze(0)
    if end_point.dim() == 1:
        end_point = end_point.unsqueeze(0)
    
    # Move to device
    start_point = start_point.to(device)
    end_point = end_point.to(device)
    
    # Generate transition path
    transition_model.eval()
    with torch.no_grad():
        path = transition_model(start_point, end_point, num_steps=num_steps)
    
    # Return the first batch item (we only have one transition)
    return path[0]

def decode_from_manifold(manifold_model, manifold_points, device):
    """
    Decode from manifold space back to phase space
    
    Args:
        manifold_model: The trained manifold model
        manifold_points: Points in the manifold space
        device: Device to use for computation
    
    Returns:
        Phase vectors corresponding to the manifold points
    """
    # Ensure input is a proper tensor
    if not isinstance(manifold_points, torch.Tensor):
        manifold_points = torch.tensor(manifold_points, dtype=torch.float32)
    
    # Move to device
    manifold_points = manifold_points.to(device)
    
    # Decode from manifold space
    with torch.no_grad():
        phase_vectors = manifold_model.decode(manifold_points)
    
    return phase_vectors

def plot_transition(transition_path, title="Transition Path", save_path=None):
    """
    Plot a transition path in the manifold space
    
    Args:
        transition_path: Tensor of shape [num_steps, manifold_dim]
        title: Title of the plot
        save_path: Path to save the plot
    """
    # Convert to numpy if needed
    if torch.is_tensor(transition_path):
        transition_path = transition_path.cpu().numpy()
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Plot each dimension
    for i in range(transition_path.shape[1]):
        plt.plot(transition_path[:, i], label=f'Dim {i}')
    
    plt.title(title)
    plt.xlabel('Step')
    plt.ylabel('Manifold Value')
    plt.legend()
    plt.grid(True)
    
    # Save if requested
    if save_path:
        plt.savefig(save_path)
    
    return plt.gcf()

def visualize_phase_space(phase_vectors, title="Phase Space", save_path=None):
    """
    Visualize phase vectors using dimensionality reduction
    
    Args:
        phase_vectors: Phase vectors to visualize
        title: Title of the plot
        save_path: Path to save the plot
    """
    # Convert to numpy if needed
    if torch.is_tensor(phase_vectors):
        phase_vectors = phase_vectors.cpu().numpy()
    
    # Flatten if needed
    if phase_vectors.ndim > 2:
        phase_vectors = phase_vectors.reshape(phase_vectors.shape[0], -1)
    
    # Reduce dimensionality with PCA
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    phase_2d = pca.fit_transform(phase_vectors)
    
    # Create figure
    plt.figure(figsize=(10, 8))
    
    # Plot points
    plt.scatter(phase_2d[:, 0], phase_2d[:, 1], alpha=0.7)
    
    # Add labels and title
    plt.title(title)
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.grid(True)
    
    # Save if requested
    if save_path:
        plt.savefig(save_path)
    
    return plt.gcf()

def convert_phase_to_motion(phase_vectors, source_motion_data=None, skeleton_data=None):
    """
    Convert phase vectors back to motion data
    
    Args:
        phase_vectors: Phase vectors to convert
        source_motion_data: Source motion data to use as reference
        skeleton_data: Skeleton data for forward kinematics
    
    Returns:
        Motion data in the appropriate format
    """
    print("Converting phase vectors to motion data...")
    
    # Import our motion decoder
    from src.utils.motion_decoder import decode_phase_to_motion
    
    # Decode the phase vectors to motion data
    motion_data = decode_phase_to_motion(
        phase_vectors, 
        skeleton_data=skeleton_data
    )
    
    return motion_data

def save_motion_to_bvh(motion_data, output_path, skeleton_data=None):
    """
    Save motion data to BVH format
    
    Args:
        motion_data: Motion data to save
        output_path: Path to save the BVH file
        skeleton_data: Optional skeleton data for the BVH file
    
    Returns:
        True if successful, False otherwise
    """
    print(f"Saving motion data to BVH file: {output_path}")
    
    if motion_data is None:
        print("Error: No motion data provided.")
        return False
    
    # Import our BVH writer
    from src.utils.bvh_writer import save_to_bvh
    
    # Save the motion data to BVH
    success = save_to_bvh(
        motion_data, 
        output_path, 
        skeleton_data=skeleton_data, 
        frametime=1.0/30.0  # 30 FPS
    )
    
    return success

def main(args):
    # Set verbose mode for debugging
    print(f"Running RSMT Inference with arguments: {args}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    print(f"Using device: {device}")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Configure output file paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    transition_plot_path = os.path.join(args.output_dir, f"transition_plot_{timestamp}.png")
    phase_plot_path = os.path.join(args.output_dir, f"phase_space_{timestamp}.png")
    output_bvh_path = os.path.join(args.output_dir, f"transition_{timestamp}.bvh")
    
    # Load models
    deephase_model = load_deephase_model(args.deephase_model)
    if deephase_model is None:
        print("Failed to load DeepPhase model. Exiting.")
        return
    
    manifold_model = load_manifold_model(args.manifold_model)
    if manifold_model is None:
        print("Failed to load Manifold model. Exiting.")
        return
    
    transition_model = load_transition_model(args.transition_model)
    if transition_model is None:
        print("Failed to load Transition Sampler model. Exiting.")
        return
    
    # Move models to device
    deephase_model = deephase_model.to(device)
    manifold_model = manifold_model.to(device)
    transition_model = transition_model.to(device)
    
    # Load phase data
    phase_data = load_phase_data(args.phase_data)
    if phase_data is None:
        print("Failed to load phase data. Exiting.")
        return
    
    # Check if the styles exist in the data
    if args.source_style not in phase_data:
        print(f"Source style '{args.source_style}' not found in phase data. Available styles: {list(phase_data.keys())}")
        return
    
    if args.target_style not in phase_data:
        print(f"Target style '{args.target_style}' not found in phase data. Available styles: {list(phase_data.keys())}")
        return
    
    # Extract phase vectors for the source and target styles
    source_phase = phase_data[args.source_style]['phase']
    target_phase = phase_data[args.target_style]['phase']
    
    # Check if skeleton data is available
    skeleton_data = None
    if 'skeleton' in phase_data:
        skeleton_data = phase_data['skeleton']
    elif 'offsets' in phase_data[args.source_style]:
        # Try to construct skeleton from the source style data
        print("Constructing skeleton from source style data")
        skeleton_data = {
            "offsets": phase_data[args.source_style]['offsets'],
            "parents": [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21]
        }
    
    print(f"Source style: {args.source_style}, Phase shape: {source_phase.shape}")
    print(f"Target style: {args.target_style}, Phase shape: {target_phase.shape}")
    
    # Choose frame indices to use as endpoints
    source_idx = min(args.source_frame, source_phase.shape[0] - 1)
    target_idx = min(args.target_frame, target_phase.shape[0] - 1)
    
    # Extract specific frames
    source_frame_phase = source_phase[source_idx]
    target_frame_phase = target_phase[target_idx]
    
    # Encode to manifold space
    source_manifold = encode_style_to_manifold(manifold_model, source_frame_phase, device)
    target_manifold = encode_style_to_manifold(manifold_model, target_frame_phase, device)
    
    print(f"Encoded to manifold space:")
    print(f"  Source manifold shape: {source_manifold.shape}")
    print(f"  Target manifold shape: {target_manifold.shape}")
    
    # Generate transition in manifold space
    manifold_transition = generate_transition(
        transition_model, 
        source_manifold, 
        target_manifold, 
        args.transition_length, 
        device
    )
    
    print(f"Generated transition path in manifold space: {manifold_transition.shape}")
    
    # Decode back to phase space
    phase_transition = decode_from_manifold(manifold_model, manifold_transition, device)
    
    print(f"Decoded to phase space: {phase_transition.shape}")
    
    # Visualize the transition in manifold space
    plot_transition(
        manifold_transition,
        title=f"Transition from {args.source_style} to {args.target_style} in Manifold Space",
        save_path=transition_plot_path
    )
    
    # Visualize the phase space
    visualize_phase_space(
        phase_transition,
        title=f"Phase Space Transition from {args.source_style} to {args.target_style}",
        save_path=phase_plot_path
    )
    
    # Convert phase vectors to motion
    motion_data = convert_phase_to_motion(phase_transition, skeleton_data=skeleton_data)
    
    # Save motion to BVH
    save_motion_to_bvh(motion_data, output_bvh_path, skeleton_data=skeleton_data)
    
    print("\nInference complete!")
    print(f"Transition plot saved to: {transition_plot_path}")
    print(f"Phase space plot saved to: {phase_plot_path}")
    print(f"Motion BVH file saved to: {output_bvh_path}")
    print("\nNOTE: This is a simple implementation of motion decoding.")
    print("For production use, you may want to:")
    print("1. Train a dedicated decoder model for higher quality motion")
    print("2. Implement proper skeleton retargeting if needed")
    print("3. Add foot contact handling for better ground interaction")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="RSMT Inference Pipeline")
    
    parser.add_argument("--deephase-model", type=str, 
                        default="./output/deephase/run_20250509_140327/best_model.pt",
                        help="Path to the trained DeepPhase model")
    
    parser.add_argument("--manifold-model", type=str, 
                        default="./output/manifold/run_20250509_143611/best_model.pt",
                        help="Path to the trained Manifold model")
    
    parser.add_argument("--transition-model", type=str, 
                        default="./output/sampler/run_20250509_144132/best_model.pt",
                        help="Path to the trained Transition Sampler model")
    
    parser.add_argument("--phase-data", type=str, 
                        default="./output/phases/train_phases.dat",
                        help="Path to the phase data")
    
    parser.add_argument("--source-style", type=str, default="Aeroplane",
                        help="Source style name")
    
    parser.add_argument("--target-style", type=str, default="Gorilla",
                        help="Target style name")
    
    parser.add_argument("--source-frame", type=int, default=0,
                        help="Frame index to use from source style")
    
    parser.add_argument("--target-frame", type=int, default=0,
                        help="Frame index to use from target style")
    
    parser.add_argument("--transition-length", type=int, default=30,
                        help="Number of frames in the transition")
    
    parser.add_argument("--output-dir", type=str, default="./output/inference",
                        help="Directory to save outputs")
    
    parser.add_argument("--cpu", action="store_true",
                        help="Use CPU instead of GPU")
    
    args = parser.parse_args()
    
    main(args)
