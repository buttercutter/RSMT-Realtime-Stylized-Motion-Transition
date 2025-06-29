#!/usr/bin/env python3
"""
Script to inspect the preprocessed data format from the 100STYLE dataset
"""

import os
import sys
import torch
import numpy as np
import pickle
import argparse

def inspect_binary_file(file_path):
    """Inspect the contents of a binary file"""
    print(f"Inspecting file: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        print(f"Data type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Dictionary with {len(data)} keys:")
            for key, value in data.items():
                if isinstance(value, np.ndarray) or isinstance(value, torch.Tensor):
                    print(f"  - {key}: shape {value.shape}, dtype {value.dtype}")
                else:
                    print(f"  - {key}: type {type(value)}")
                
                # Sample the first few elements if it's an array
                if isinstance(value, np.ndarray) and value.size > 0:
                    flat_value = value.flatten()
                    print(f"    Sample values: {flat_value[:5]}...")
                
                # For more complex structures, provide additional details
                if key == 'style_labels' and isinstance(value, np.ndarray):
                    unique_styles = np.unique(value)
                    print(f"    Unique style labels: {unique_styles}")
                    print(f"    Style label counts:")
                    for style in unique_styles:
                        count = np.sum(value == style)
                        print(f"      Style {style}: {count} samples")
        else:
            print("Data is not a dictionary.")
    
    except Exception as e:
        print(f"Error reading the file: {e}")

def inspect_skeleton(file_path):
    """Inspect the skeleton structure"""
    print(f"Inspecting skeleton file: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            skeleton = pickle.load(f)
        
        print(f"Skeleton type: {type(skeleton)}")
        
        if isinstance(skeleton, dict):
            print(f"Dictionary with {len(skeleton)} keys:")
            for key, value in skeleton.items():
                if isinstance(value, np.ndarray):
                    print(f"  - {key}: shape {value.shape}, dtype {value.dtype}")
                    if key == 'parents':
                        print(f"    Parent indices: {value}")
                    elif key == 'offsets':
                        print(f"    First few offsets: {value[:3]}")
                elif isinstance(value, list):
                    print(f"  - {key}: list with {len(value)} items")
                    if key == 'names':
                        print(f"    Joint names: {value}")
                else:
                    print(f"  - {key}: type {type(value)}")
        else:
            # Try to access common skeleton attributes
            if hasattr(skeleton, 'offsets'):
                print(f"Offsets shape: {skeleton.offsets.shape}")
            if hasattr(skeleton, 'parents'):
                print(f"Parents: {skeleton.parents}")
            if hasattr(skeleton, 'names'):
                print(f"Joint names: {skeleton.names}")
            if hasattr(skeleton, 'bone_pair_indices'):
                print(f"Bone pair indices: {skeleton.bone_pair_indices}")
    
    except Exception as e:
        print(f"Error reading the skeleton file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Inspect preprocessed data files")
    parser.add_argument("--data_dir", type=str, default="./MotionData/100STYLE", help="Data directory")
    args = parser.parse_args()
    
    # Inspect the skeleton file
    skeleton_path = os.path.join(args.data_dir, 'skeleton')
    if os.path.exists(skeleton_path):
        inspect_skeleton(skeleton_path)
    else:
        print(f"Skeleton file not found at {skeleton_path}")
    
    # Inspect training data
    train_path = os.path.join(args.data_dir, 'train_binary.dat')
    if os.path.exists(train_path):
        inspect_binary_file(train_path)
    else:
        print(f"Training data file not found at {train_path}")
    
    # Inspect test data
    test_path = os.path.join(args.data_dir, 'test_binary.dat')
    if os.path.exists(test_path):
        inspect_binary_file(test_path)
    else:
        print(f"Test data file not found at {test_path}")

if __name__ == "__main__":
    main()
