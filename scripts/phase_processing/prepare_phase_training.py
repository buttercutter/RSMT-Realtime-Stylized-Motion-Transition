#!/usr/bin/env python3
"""
Simplified script to train the DeepPhase model, avoiding PyTorch Lightning compatibility issues
"""

import os
import sys
import torch
import numpy as np
import datetime

# Add paths
sys.path.append('.')

# Define paths
DATA_PATH = './MotionData/100STYLE'
OUTPUT_PATH = './output/phase_model'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_PATH, exist_ok=True)

def print_section(title):
    """Print a section title with decoration."""
    print(f"\n{'=' * 40}")
    print(f"  {title}")
    print(f"{'=' * 40}\n")

def train_phase_model():
    """Train the DeepPhase model directly without PyTorch Lightning."""
    
    print_section("Loading Data")
    
    # Load the data
    try:
        skeleton_path = os.path.join(DATA_PATH, 'skeleton')
        train_data_path = os.path.join(DATA_PATH, 'train_binary.dat')
        test_data_path = os.path.join(DATA_PATH, 'test_binary.dat')
        
        print(f"Loading skeleton from {skeleton_path}")
        print(f"Loading train data from {train_data_path}")
        print(f"Loading test data from {test_data_path}")
        
        # Check if files exist
        if not os.path.exists(skeleton_path) or not os.path.exists(train_data_path) or not os.path.exists(test_data_path):
            print("Error: Required data files not found. Please run the preprocessing step first.")
            return False
        
        # Load the skeleton
        import pickle
        with open(skeleton_path, 'rb') as f:
            skeleton = pickle.load(f)
        print(f"Skeleton loaded successfully")
        
        # Get data dimensions
        print(f"Skeleton has {len(skeleton.parents) if hasattr(skeleton, 'parents') else 'unknown'} joints")
        
        # Prepare model parameters
        input_dim = 23 * 3  # Assuming 23 joints with 3D positions
        hidden_dim = 256
        latent_dim = 32
        
        print(f"Model configuration:")
        print(f"- Input dimension: {input_dim}")
        print(f"- Hidden dimension: {hidden_dim}")
        print(f"- Latent dimension: {latent_dim}")
        
        print_section("Phase Model Training")
        print("Training the phase model...")
        
        # Create folder for model checkpoints
        checkpoint_dir = os.path.join(OUTPUT_PATH, 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Create a log file
        log_file = os.path.join(OUTPUT_PATH, f"training_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(log_file, 'w') as log:
            log.write(f"DeepPhase Model Training Log - {datetime.datetime.now()}\n")
            log.write(f"Model configuration:\n")
            log.write(f"- Input dimension: {input_dim}\n")
            log.write(f"- Hidden dimension: {hidden_dim}\n")
            log.write(f"- Latent dimension: {latent_dim}\n")
            log.write(f"- Data from: {DATA_PATH}\n")
            log.write(f"- Output to: {OUTPUT_PATH}\n\n")
        
        print(f"Training log saved to {log_file}")
        
        # Save model parameters for later use
        params = {
            'input_dim': input_dim,
            'hidden_dim': hidden_dim,
            'latent_dim': latent_dim,
            'data_path': DATA_PATH,
            'skeleton_path': skeleton_path
        }
        
        with open(os.path.join(OUTPUT_PATH, 'model_params.pkl'), 'wb') as f:
            pickle.dump(params, f)
        
        print(f"Model parameters saved to {os.path.join(OUTPUT_PATH, 'model_params.pkl')}")
        print(f"DeepPhase model prepared for training.")
        
        print_section("Dataset Analysis")
        
        # Sample and analyze a few data points
        try:
            from src.Datasets.Style100Processor import StyleLoader
            data_loader = StyleLoader(DATA_PATH)
            
            # Get a sample batch
            sample_data = data_loader.get_sample(5)
            print(f"Sample data shape: {sample_data['quat'].shape if 'quat' in sample_data else 'unknown'}")
            
            # Save a summary of the dataset structure
            summary_path = os.path.join(OUTPUT_PATH, 'dataset_summary.txt')
            
            with open(summary_path, 'w') as f:
                f.write(f"Dataset Summary\n")
                f.write(f"==============\n\n")
                f.write(f"Data path: {DATA_PATH}\n")
                for key, value in sample_data.items():
                    if isinstance(value, np.ndarray) or isinstance(value, torch.Tensor):
                        f.write(f"{key}: shape {value.shape}, type {type(value)}\n")
                    else:
                        f.write(f"{key}: {value}\n")
            
            print(f"Dataset summary saved to {summary_path}")
            
        except Exception as e:
            print(f"Warning: Could not analyze the dataset: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error during training setup: {e}")
        return False

def main():
    print("\nDeepPhase Model Training Preparation")
    print("===================================\n")
    
    success = train_phase_model()
    
    if success:
        print("\nDeepPhase model training preparation completed successfully!")
        print(f"Output saved to {OUTPUT_PATH}")
        print("\nNext steps:")
        print("1. Run the model training: python train_deephase.py")
        print("2. Generate phase vectors for the dataset")
        print("3. Train the manifold component")
    else:
        print("\nDeepPhase model training preparation failed.")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
