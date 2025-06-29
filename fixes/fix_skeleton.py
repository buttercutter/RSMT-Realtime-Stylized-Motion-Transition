#!/usr/bin/env python3
"""
Script to fix the skeleton file format
"""

import os
import pickle
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import the Skeleton class
from src.utils.BVH_mod import Skeleton

# Path to the skeleton file
SKELETON_PATH = "./MotionData/100STYLE/skeleton"

def fix_skeleton():
    print("Converting skeleton dictionary to Skeleton object...")
    
    # Load the skeleton dictionary
    with open(SKELETON_PATH, 'rb') as f:
        skeleton_dict = pickle.load(f)
    
    # Create a Skeleton object
    skeleton_obj = Skeleton()
    
    # Transfer data from dictionary to Skeleton object
    skeleton_obj.offsets = skeleton_dict['offsets']
    skeleton_obj.parents = skeleton_dict['parents']
    skeleton_obj.names = skeleton_dict['names']
    
    # Initialize the hierarchy
    skeleton_obj.init()
    
    # Save the Skeleton object
    with open(SKELETON_PATH, 'wb') as f:
        pickle.dump(skeleton_obj, f)
    
    print(f"Skeleton file updated successfully: {SKELETON_PATH}")

if __name__ == "__main__":
    fix_skeleton()
