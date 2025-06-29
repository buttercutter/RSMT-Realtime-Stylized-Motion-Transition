#!/usr/bin/env python3
"""
Generate phase vectors using the trained DeepPhase model
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

def load_model(model_path, input_dim=None):
    """
    Load the trained DeepPhase model
    """
    print(f"Loading model from {model_path}")
    
    # Load model checkpoint
    checkpoint = torch.load(model_path)
    
    # If input_dim is not provided, try to extract it from saved parameters
    if input_dim is None:
        # Check if model architecture info is saved in the checkpoint
        if 'input_dim' in checkpoint:
            input_dim = checkpoint['input_dim']
        else:
            # Default to the value we used during training
            input_dim = 92
            print(f"Input dimension not found in checkpoint, using default: {input_dim}")
    
    # Import DeepPhaseModel from the training script
    from train_deephase_simplified import DeepPhaseModel
    
    # Create a new model instance with the same architecture
    model = DeepPhaseModel(input_dim=input_dim)
    
    # Load the model weights
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    
    # Set model to evaluation mode
    model.eval()
    
    return model

def load_data(data_path):
    """
    Load motion data from binary files
    """
    print(f"Loading data from {data_path}")
    
    train_path = os.path.join(data_path, 'train_binary.dat')
    test_path = os.path.join(data_path, 'test_binary.dat')
    
    # Check if files exist
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print(f"Data files not found at {train_path} or {test_path}")
        return None, None
    
    try:
        # Load data
        with open(train_path, 'rb') as f:
            train_data = pickle.load(f)
        
        with open(test_path, 'rb') as f:
            test_data = pickle.load(f)
        
        print("Data loaded successfully")
        return train_data, test_data
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def generate_phases(model, data, device='cuda'):
    """
    Generate phase vectors for all motion data
    """
    print("Generating phase vectors...")
    
    # Move model to the specified device
    model = model.to(device)
    
    # Dictionary to store results
    phase_data = {}
    
    # Process each style
    for style_name, style_data in data.items():
        print(f"Processing style: {style_name}")
        
        # Check for motion data under 'BR' key
        if 'BR' in style_data:
            motion_info = style_data['BR']
            
            # Check for quaternion data
            if 'quats' in motion_info and motion_info['quats'] is not None:
                # Get quaternion data
                quats = motion_info['quats']
                
                # Convert to tensor
                quats_tensor = torch.tensor(quats, dtype=torch.float32)
                
                # Reshape to [time_steps, joint_count * 4]
                batch_size, joint_count, quat_dim = quats_tensor.shape
                flattened = quats_tensor.reshape(batch_size, -1)
                
                # Move to device
                flattened = flattened.to(device)
                
                # Process in batches to prevent memory issues
                with torch.no_grad():
                    # Get phase vector (latent representation)
                    _, phase_vector = model(flattened)
                
                # Convert back to numpy array
                phase_vector = phase_vector.cpu().numpy()
                
                # Store in result dictionary
                phase_data[style_name] = {
                    'phase': phase_vector,
                    'offsets': motion_info.get('offsets', None),
                    'hips': motion_info.get('hips', None),
                }
    
    print(f"Phase vectors generated for {len(phase_data)} styles")
    return phase_data

def save_phases(phase_data, output_path):
    """
    Save generated phase vectors to a file
    """
    print(f"Saving phase data to {output_path}")
    
    # Make sure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the data
    with open(output_path, 'wb') as f:
        pickle.dump(phase_data, f)
    
    print("Phase data saved successfully")

def visualize_phase_space(phase_data, output_path=None):
    """
    Visualize the phase vectors in 2D
    """
    print("Visualizing phase space...")
    
    # Extract all phase vectors
    phases = []
    labels = []
    
    for style_name, data in phase_data.items():
        phase = data['phase']
        phases.append(phase)
        labels.extend([style_name] * len(phase))
    
    # Convert to numpy array
    phases = np.vstack(phases)
    
    # Use PCA for dimensionality reduction
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    phases_2d = pca.fit_transform(phases)
    
    # Plot the results
    plt.figure(figsize=(12, 10))
    
    # Get unique labels and assign colors
    unique_labels = sorted(set(labels))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_labels)))
    
    # Create a dictionary mapping labels to colors
    color_dict = dict(zip(unique_labels, colors))
    
    # Plot each style with a different color
    for label in unique_labels:
        mask = [l == label for l in labels]
        plt.scatter(
            phases_2d[mask, 0], 
            phases_2d[mask, 1], 
            c=[color_dict[label]], 
            label=label, 
            alpha=0.7,
            s=10
        )
    
    plt.title("Phase Space Visualization (PCA)")
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    
    # Save the plot
    if output_path:
        plt.savefig(output_path)
        print(f"Visualization saved to {output_path}")
    
    # Show the plot (comment out in headless environments)
    # plt.show()

def main(args):
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    print(f"Using device: {device}")
    
    # Load the model
    model = load_model(args.model_path)
    
    # Load data
    train_data, test_data = load_data(args.data_path)
    
    if train_data is None or test_data is None:
        print("Failed to load data. Exiting.")
        return
    
    # Generate phases for training data
    train_phases = generate_phases(model, train_data, device)
    
    # Generate phases for test data
    test_phases = generate_phases(model, test_data, device)
    
    # Save the generated phases
    save_phases(train_phases, os.path.join(args.output_dir, 'train_phases.dat'))
    save_phases(test_phases, os.path.join(args.output_dir, 'test_phases.dat'))
    
    # Visualize the phase space for training data
    visualize_phase_space(train_phases, os.path.join(args.output_dir, 'train_phase_space.png'))
    
    # Visualize the phase space for test data
    visualize_phase_space(test_phases, os.path.join(args.output_dir, 'test_phase_space.png'))
    
    print("Phase generation complete!")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate phase vectors from trained DeepPhase model")
    
    parser.add_argument("--model-path", type=str, default="./output/deephase/best_model.pt",
                        help="Path to the trained model file")
    parser.add_argument("--data-path", type=str, default="./MotionData/100STYLE",
                        help="Path to the data directory")
    parser.add_argument("--output-dir", type=str, default="./output/phases",
                        help="Directory to save generated phases")
    parser.add_argument("--cpu", action="store_true",
                        help="Use CPU instead of GPU")
    
    args = parser.parse_args()
    
    main(args)
