#!/usr/bin/env python3
"""
Detailed data inspector for the binary files
"""

import os
import pickle
import sys
import numpy as np
import torch
from pprint import pprint
import traceback

def inspect_binary_file(file_path, max_samples=2):
    """
    Detailed inspection of a binary file
    """
    print(f"\n{'='*50}")
    print(f"Inspecting {file_path}")
    print(f"{'='*50}\n")
    
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        if isinstance(data, dict):
            print(f"Data is a dictionary with {len(data)} keys")
            
            # Get a sample style
            sample_keys = list(data.keys())[:max_samples]
            
            for key in sample_keys:
                print(f"\n--- Sample for style: {key} ---")
                style_data = data[key]
                
                if isinstance(style_data, dict):
                    print(f"Style data is a dictionary with keys: {list(style_data.keys())}")
                    
                    # Check all motion types available
                    for motion_type in style_data.keys():
                        print(f"\n  Motion type: {motion_type}")
                        motion_data = style_data[motion_type]
                        
                        if isinstance(motion_data, dict):
                            print(f"  Motion data is a dictionary with keys: {list(motion_data.keys())}")
                            
                            # Examine each key in the motion data
                            for field_name, field_data in motion_data.items():
                                if field_data is not None:
                                    if hasattr(field_data, 'shape'):
                                        print(f"  - {field_name}: type={type(field_data)}, shape={field_data.shape}")
                                        
                                        # Show a small sample of the data
                                        if len(field_data.shape) > 0:
                                            sample_slice = field_data
                                            if len(field_data.shape) >= 3:
                                                sample_slice = field_data[0, 0]
                                            elif len(field_data.shape) >= 2:
                                                sample_slice = field_data[0]
                                            
                                            print(f"    Sample data: {sample_slice}")
                                    else:
                                        print(f"  - {field_name}: type={type(field_data)}, value={field_data}")
                                else:
                                    print(f"  - {field_name}: None")
                        else:
                            print(f"  Motion data is of type: {type(motion_data)}")
                            if hasattr(motion_data, 'shape'):
                                print(f"  Shape: {motion_data.shape}")
                else:
                    print(f"Style data is of type: {type(style_data)}")
        else:
            print(f"Data is not a dictionary, it's a {type(data)}")
        
        print(f"\n{'='*50}")
        print("Inspection complete")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"Error during inspection: {e}")

def main():
    """
    Main function to inspect binary data files
    """
    data_dir = "./MotionData/100STYLE"
    
    # Files to inspect
    files = [
        "train_binary.dat",
        "test_binary.dat"
    ]
    
    # Set up a log file
    log_path = "./binary_inspection_log.txt"
    
    with open(log_path, 'w') as log_file:
        log_file.write("Binary Data Inspection Log\n")
        log_file.write("=======================\n\n")
        
        # Redirect stdout to this file during inspection
        original_stdout = sys.stdout
        sys.stdout = log_file
        
        try:
            for file_name in files:
                file_path = os.path.join(data_dir, file_name)
                if os.path.exists(file_path):
                    print(f"File exists: {file_path}")
                    print(f"File size: {os.path.getsize(file_path)} bytes")
                    try:
                        inspect_binary_file(file_path)
                    except Exception as e:
                        print(f"Inspection error: {e}")
                        traceback.print_exc(file=log_file)
                else:
                    print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error in main function: {e}")
            traceback.print_exc(file=log_file)
        
        # Restore stdout
        sys.stdout = original_stdout
    
    # Print a message to the console
    print(f"Inspection complete. Log saved to: {log_path}")

if __name__ == "__main__":
    main()
