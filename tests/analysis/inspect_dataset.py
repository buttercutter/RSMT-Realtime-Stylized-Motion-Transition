import os
import sys
import traceback
import numpy as np
import pandas as pd

# Add the current directory to the path
sys.path.insert(0, os.path.abspath('.'))

def inspect_bvh_file():
    """Inspect a BVH file to understand its structure"""
    print("Inspecting BVH file structure...")
    
    bvh_path = "./MotionData/100STYLE/Aeroplane/Aeroplane_BR.bvh"
    if not os.path.exists(bvh_path):
        print(f"File not found: {bvh_path}")
        return
    
    print(f"File size: {os.path.getsize(bvh_path)} bytes")
    
    # Read and print the first few lines to understand the structure
    with open(bvh_path, 'r') as f:
        header_lines = []
        for i, line in enumerate(f):
            if i < 50:  # Read first 50 lines
                header_lines.append(line.strip())
            else:
                break
    
    # Print the header
    print("\nBVH File Header:")
    for line in header_lines[:20]:  # Print first 20 lines
        print(f"  {line}")
    
    # Try to analyze the joint structure
    joints = []
    current_depth = 0
    for line in header_lines:
        if "ROOT" in line or "JOINT" in line:
            joint_name = line.split()[-1]
            joints.append((joint_name, current_depth))
        elif "{" in line:
            current_depth += 1
        elif "}" in line:
            current_depth -= 1
    
    print("\nJoint Hierarchy:")
    for joint, depth in joints:
        print(f"  {'  ' * depth}{joint}")
    
    print(f"\nTotal joints found: {len(joints)}")
    
    # Try to import the BVH module and see what happens
    try:
        from src.utils import BVH_mod
        print("\nSuccessfully imported BVH_mod")
        print(f"Available functions in BVH_mod: {[f for f in dir(BVH_mod) if not f.startswith('_')]}")
    except Exception as e:
        print(f"\nError importing BVH_mod: {str(e)}")
        traceback.print_exc()

def inspect_dataset_structure():
    """Inspect the dataset structure"""
    print("\nInspecting dataset structure...")
    
    root_dir = "./MotionData/100STYLE/"
    frame_cuts_path = os.path.join(root_dir, "Frame_Cuts.csv")
    
    if not os.path.exists(frame_cuts_path):
        print(f"File not found: {frame_cuts_path}")
        return
    
    try:
        frame_cuts = pd.read_csv(frame_cuts_path)
        print(f"Frame_Cuts.csv contains {len(frame_cuts)} rows and {len(frame_cuts.columns)} columns")
        print(f"Columns: {', '.join(frame_cuts.columns)}")
        
        # Sample a few styles to check
        sample_styles = frame_cuts.STYLE_NAME[:5].tolist()
        print(f"\nSampling styles: {', '.join(sample_styles)}")
        
        for style in sample_styles:
            style_dir = os.path.join(root_dir, style)
            if os.path.exists(style_dir):
                bvh_files = [f for f in os.listdir(style_dir) if f.endswith('.bvh')]
                print(f"  {style} has {len(bvh_files)} BVH files: {', '.join(bvh_files)}")
            else:
                print(f"  Directory not found: {style_dir}")
    except Exception as e:
        print(f"Error analyzing dataset: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        inspect_bvh_file()
        inspect_dataset_structure()
    except Exception as e:
        print(f"Unhandled error: {str(e)}")
        traceback.print_exc()
