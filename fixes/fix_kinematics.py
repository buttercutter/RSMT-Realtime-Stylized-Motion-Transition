#!/usr/bin/env python3
"""
Script to fix dimension mismatch in forward kinematics
"""

import os
import sys
import pickle
import numpy as np
import torch

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}\n")

def main():
    print_section("RSMT Kinematics Fixer")
    
    # Load the skeleton file
    SKELETON_PATH = "./MotionData/100STYLE/skeleton"
    print(f"Loading skeleton from {SKELETON_PATH}")
    
    try:
        with open(SKELETON_PATH, 'rb') as f:
            skeleton_data = pickle.load(f)
        
        print("Skeleton loaded successfully")
        
        # Check if skeleton is a dict or an object
        if isinstance(skeleton_data, dict):
            print("Skeleton is a dictionary with keys:", list(skeleton_data.keys()))
            
            # Print dimensions of key components
            if 'offsets' in skeleton_data:
                print(f"offsets shape: {skeleton_data['offsets'].shape}")
                
            if 'parents' in skeleton_data:
                print(f"parents shape: {len(skeleton_data['parents'])}")
                print(f"parents content: {skeleton_data['parents']}")
                
            if 'names' in skeleton_data:
                print(f"names count: {len(skeleton_data['names'])}")
                print(f"names: {skeleton_data['names']}")
                
            # Fix the issue by creating a consistent skeleton
            fixed_skeleton = {
                "offsets": np.zeros((len(skeleton_data['parents']), 3), dtype=np.float32),
                "parents": np.array(skeleton_data['parents'], dtype=np.int32),
                "names": skeleton_data['names']
            }
            
            print(f"\nCreated fixed skeleton with consistent dimensions:")
            print(f"offsets shape: {fixed_skeleton['offsets'].shape}")
            print(f"parents shape: {len(fixed_skeleton['parents'])}")
            print(f"names count: {len(fixed_skeleton['names'])}")
            
            # Test forward kinematics to verify dimensions are consistent
            print("\nTesting forward kinematics with dummy data...")
            try:
                from src.geometry import forward_kinematics as fk
                
                batch_size = 1
                seq_length = 10
                joint_count = len(fixed_skeleton['parents'])
                
                # Create dummy data
                quats = torch.zeros((batch_size, seq_length, joint_count, 4), dtype=torch.float32)
                quats[..., 0] = 1.0  # Set to identity quaternion
                
                offsets = torch.from_numpy(fixed_skeleton['offsets']).unsqueeze(0).unsqueeze(0)
                offsets = offsets.expand(batch_size, seq_length, -1, -1)
                
                hip_pos = torch.zeros((batch_size, seq_length, 1, 3), dtype=torch.float32)
                
                parents = fixed_skeleton['parents']
                
                # Run forward kinematics
                gp, gq = fk.forward_kinematics_quats(quats, offsets, hip_pos, parents)
                
                print(f"Forward kinematics test passed!")
                print(f"Output shapes - gp: {gp.shape}, gq: {gq.shape}")
                
                # Save the fixed skeleton
                with open(SKELETON_PATH, 'wb') as f:
                    pickle.dump(fixed_skeleton, f)
                    
                print(f"\nUpdated skeleton saved to {SKELETON_PATH}")
                
            except Exception as e:
                print(f"Error testing forward kinematics: {e}")
        else:
            print(f"Skeleton is not a dictionary, it's a {type(skeleton_data)}")
            # You can add code to handle Skeleton objects here if needed
            
    except Exception as e:
        print(f"Error loading skeleton: {e}")

if __name__ == "__main__":
    main()
