#!/usr/bin/env python3
# Staged preprocessing script for RSMT model

import os
import sys
import subprocess
import argparse

def check_environment():
    """Check if the virtual environment exists"""
    print("Checking Python environment...")
    if not os.path.exists(".venv/bin/python"):
        print("Creating virtual environment...")
        subprocess.run(["python", "-m", "venv", ".venv"])
    
    print("Activating virtual environment and installing dependencies...")
    # Create a compatible requirements file
    with open("requirements_compat.txt", "w") as f:
        f.write("""numpy>=1.20.0
matplotlib>=3.5.0
pandas>=1.4.0
torch>=1.13.0
pytorch_lightning>=1.5.0
scipy>=1.9.0
""")
    
    # We can't directly activate venv in this script, so we return the activation command
    return "source .venv/bin/activate && pip install -r requirements_compat.txt"

def run_step(cmd, step_name):
    print(f"Running {step_name}...")
    print(f"Command: {cmd}")
    print("=" * 50)
    print("Please run this command in your terminal.")
    print("=" * 50)
    return

def step1_convert_bvh():
    """Convert BVH files to binary"""
    code = """
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from src.Datasets.Style100Processor import bvh_to_binary

print("Starting BVH to binary conversion...")
bvh_to_binary()
print("BVH to binary conversion complete!")
"""
    with open("step1_convert_bvh.py", "w") as f:
        f.write(code)
    
    return "python step1_convert_bvh.py"

def step2_save_skeleton():
    """Save the skeleton structure"""
    code = """
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from src.Datasets.Style100Processor import save_skeleton

print("Saving skeleton structure...")
save_skeleton()
print("Skeleton saved successfully!")
"""
    with open("step2_save_skeleton.py", "w") as f:
        f.write(code)
    
    return "python step2_save_skeleton.py"

def step3_split_dataset():
    """Split the dataset into train and test sets"""
    code = """
import os
import sys
import pickle
import pandas as pd
sys.path.insert(0, os.path.abspath('.'))
from src.Datasets.Style100Processor import StyleLoader, read_binary

print("Splitting dataset into train and test sets...")
style_loader = StyleLoader()
try:
    style_loader.split_from_binary()
    print("Dataset split complete!")
except Exception as e:
    print(f"Error splitting dataset: {e}")
    import traceback
    traceback.print_exc()
"""
    with open("step3_split_dataset.py", "w") as f:
        f.write(code)
    
    return "python step3_split_dataset.py"

def step4_augment_dataset():
    """Augment the dataset"""
    code = """
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from src.Datasets.Style100Processor import StyleLoader

print("Augmenting dataset...")
style_loader = StyleLoader()
try:
    style_loader.augment_dataset()
    print("Dataset augmentation complete!")
except Exception as e:
    print(f"Error augmenting dataset: {e}")
    import traceback
    traceback.print_exc()
"""
    with open("step4_augment_dataset.py", "w") as f:
        f.write(code)
    
    return "python step4_augment_dataset.py"

def main():
    parser = argparse.ArgumentParser(description="RSMT preprocessing steps")
    parser.add_argument("step", type=int, choices=[0, 1, 2, 3, 4, 5], 
                        help="Step to execute: 0=setup env, 1=convert bvh, 2=save skeleton, 3=split dataset, 4=augment dataset, 5=all steps")
    
    args = parser.parse_args()
    
    if args.step == 0 or args.step == 5:
        activate_cmd = check_environment()
        run_step(activate_cmd, "environment setup")
        
    if args.step == 1 or args.step == 5:
        cmd = step1_convert_bvh()
        run_step(cmd, "BVH conversion")
        
    if args.step == 2 or args.step == 5:
        cmd = step2_save_skeleton()
        run_step(cmd, "skeleton saving")
        
    if args.step == 3 or args.step == 5:
        cmd = step3_split_dataset()
        run_step(cmd, "dataset splitting")
        
    if args.step == 4 or args.step == 5:
        cmd = step4_augment_dataset()
        run_step(cmd, "dataset augmentation")

if __name__ == "__main__":
    main()
