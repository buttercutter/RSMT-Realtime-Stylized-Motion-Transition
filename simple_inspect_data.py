#!/usr/bin/env python3
"""
Simple script to inspect data files
"""
import os
import sys
import pickle
import numpy as np

DATA_DIR = "./MotionData/100STYLE"

def print_section(title):
    print(f"\n{'=' * 40}")
    print(f"  {title}")
    print(f"{'=' * 40}\n")

def inspect_file(filepath):
    print(f"Inspecting: {filepath}")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        if isinstance(data, dict):
            print(f"Dictionary with {len(data)} keys")
            for key, val in data.items():
                if isinstance(val, np.ndarray):
                    print(f"  - {key}: {type(val)} shape={val.shape} dtype={val.dtype}")
                    # Print a few sample values
                    if val.size > 0:
                        flat_val = val.flatten()
                        sample = flat_val[:5]
                        print(f"    Sample values: {sample}")
                else:
                    print(f"  - {key}: {type(val)}")
        else:
            print(f"Not a dictionary: {type(data)}")
            # Try to print some basic info
            if hasattr(data, 'shape'):
                print(f"Shape: {data.shape}")
    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    print_section("Data Inspection")
    
    # Check if the directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Data directory not found: {DATA_DIR}")
        return
    
    # List all files in the directory
    print(f"Files in {DATA_DIR}:")
    files = os.listdir(DATA_DIR)
    for file in files:
        print(f"  - {file}")
    
    # Inspect skeleton
    skeleton_path = os.path.join(DATA_DIR, 'skeleton')
    print_section("Skeleton")
    inspect_file(skeleton_path)
    
    # Inspect train data
    train_path = os.path.join(DATA_DIR, 'train_binary.dat')
    print_section("Training Data")
    inspect_file(train_path)
    
    # Inspect test data
    test_path = os.path.join(DATA_DIR, 'test_binary.dat')
    print_section("Test Data")
    inspect_file(test_path)

if __name__ == "__main__":
    main()
