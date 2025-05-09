# Debug script
import sys
import os
import pickle
import numpy as np
import pandas as pd
import torch

try:
    print("Python version:", sys.version)
    print("Checking imports...")
    print("Checking for Frame_Cuts.csv...")
    
    root_dir = "./MotionData/100STYLE/"
    if os.path.exists(root_dir + "Frame_Cuts.csv"):
        print("Frame_Cuts.csv exists!")
        frame_cuts = pd.read_csv(root_dir + "Frame_Cuts.csv")
        print("First few rows of Frame_Cuts.csv:")
        print(frame_cuts.head())
    else:
        print("Frame_Cuts.csv DOES NOT exist!")
    
    print("Checking for BVH files...")
    bvh_path = root_dir + "Aeroplane/Aeroplane_BR.bvh"
    if os.path.exists(bvh_path):
        print(f"BVH file exists: {bvh_path}")
    else:
        print(f"BVH file DOES NOT exist: {bvh_path}")
    
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    
    print("All imports successful!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
