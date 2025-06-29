#!/usr/bin/env python3
import os
import pickle
import sys

print("Python version:", sys.version)
print("Working directory:", os.getcwd())

# Try to load the skeleton file
skeleton_path = "./MotionData/100STYLE/skeleton"
if os.path.exists(skeleton_path):
    print(f"Skeleton file exists at {skeleton_path}")
    try:
        with open(skeleton_path, 'rb') as f:
            skeleton = pickle.load(f)
        print("Successfully loaded skeleton")
        print(f"Skeleton type: {type(skeleton)}")
    except Exception as e:
        print(f"Error loading skeleton: {e}")
else:
    print(f"Skeleton file not found at {skeleton_path}")

# Try to load the training data
train_path = "./MotionData/100STYLE/train_binary.dat"
if os.path.exists(train_path):
    print(f"Train file exists at {train_path}")
    try:
        with open(train_path, 'rb') as f:
            train_data = pickle.load(f)
        print("Successfully loaded training data")
        print(f"Train data type: {type(train_data)}")
        if isinstance(train_data, dict):
            print(f"Train data keys: {train_data.keys()}")
    except Exception as e:
        print(f"Error loading train data: {e}")
else:
    print(f"Train file not found at {train_path}")
