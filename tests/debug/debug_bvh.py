import os
import sys

# Current directory
print(f"Current directory: {os.getcwd()}")

# Check the 100STYLE folder
style_dir = "./MotionData/100STYLE/"
print(f"100STYLE directory exists: {os.path.exists(style_dir)}")

# Check for Frame_Cuts.csv
frame_cuts_path = os.path.join(style_dir, "Frame_Cuts.csv")
print(f"Frame_Cuts.csv exists: {os.path.exists(frame_cuts_path)}")

# Check a sample style folder
sample_style = "Aeroplane"
sample_style_path = os.path.join(style_dir, sample_style)
print(f"Sample style {sample_style} exists: {os.path.exists(sample_style_path)}")

# Check for BVH files
sample_bvh_path = os.path.join(sample_style_path, f"{sample_style}_BR.bvh")
print(f"Sample BVH file exists: {os.path.exists(sample_bvh_path)}")

# List files in the style folder
if os.path.exists(sample_style_path):
    print(f"Files in {sample_style}:")
    for file in os.listdir(sample_style_path):
        print(f"  - {file}")
else:
    print(f"Cannot list files in {sample_style} as it doesn't exist")

# Try to import the necessary modules
try:
    print("\nTrying to import modules:")
    import numpy as np
    print("✓ NumPy")
    import pandas as pd
    print("✓ Pandas")
    import torch
    print("✓ PyTorch")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    sys.path.insert(0, os.path.abspath('.'))
    try:
        from src.Datasets.Style100Processor import Swap100StyJoints
        print("✓ Swap100StyJoints")
    except Exception as e:
        print(f"✗ Error importing Swap100StyJoints: {e}")
    
    try:
        from src.utils.BVH_mod import read_bvh
        print("✓ read_bvh")
    except Exception as e:
        print(f"✗ Error importing read_bvh: {e}")
    
    try:
        from src.utils.motion_process import subsample
        print("✓ subsample")
    except Exception as e:
        print(f"✗ Error importing subsample: {e}")
        
except Exception as e:
    print(f"Error during imports: {e}")
    import traceback
    traceback.print_exc()
