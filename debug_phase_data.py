#!/usr/bin/env python3
"""
Debug script to inspect phase data files
"""

import os
import sys
import pickle
import traceback

def inspect_file(file_path):
    """
    Load and print basic info about a pickle file
    """
    print(f"\nInspecting file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} bytes")
    
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        print(f"Data loaded successfully")
        print(f"Data type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Dictionary with {len(data)} keys")
            print(f"Keys: {list(data.keys())[:5]} {'...' if len(data) > 5 else ''}")
            
            # Check first item
            first_key = list(data.keys())[0]
            first_item = data[first_key]
            print(f"\nFirst item (key: {first_key}):")
            print(f"  Type: {type(first_item)}")
            
            if isinstance(first_item, dict):
                print(f"  Sub-keys: {list(first_item.keys())}")
                
                # Check each value
                for subkey, subvalue in first_item.items():
                    if hasattr(subvalue, 'shape'):
                        print(f"  - {subkey}: shape={subvalue.shape}, type={type(subvalue)}")
                    else:
                        print(f"  - {subkey}: {subvalue}")
        else:
            print(f"Not a dictionary: {type(data)}")
    
    except Exception as e:
        print(f"Error loading data: {e}")
        traceback.print_exc()

def main():
    # Files to inspect
    train_path = "./output/phases/train_phases.dat"
    test_path = "./output/phases/test_phases.dat"
    
    # Inspect files
    inspect_file(train_path)
    inspect_file(test_path)

if __name__ == "__main__":
    main()
