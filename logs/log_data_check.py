#!/usr/bin/env python3
import os
import sys
import pickle

# Open a log file for writing
with open("data_check_log.txt", "w") as log:
    log.write("Python version: " + sys.version + "\n")
    log.write("Working directory: " + os.getcwd() + "\n")
    
    # Check if MotionData exists
    motion_data_dir = "./MotionData"
    log.write(f"Checking if {motion_data_dir} exists: {os.path.exists(motion_data_dir)}\n")
    
    if os.path.exists(motion_data_dir):
        log.write("Contents of MotionData:\n")
        for item in os.listdir(motion_data_dir):
            log.write(f"  - {item}\n")
        
        # Check 100STYLE
        style_dir = os.path.join(motion_data_dir, "100STYLE")
        log.write(f"Checking if {style_dir} exists: {os.path.exists(style_dir)}\n")
        
        if os.path.exists(style_dir):
            log.write("Contents of 100STYLE:\n")
            for item in os.listdir(style_dir):
                path = os.path.join(style_dir, item)
                size = os.path.getsize(path) if os.path.isfile(path) else "dir"
                log.write(f"  - {item}: {size} bytes\n")
            
            # Try to load skeleton
            skeleton_path = os.path.join(style_dir, "skeleton")
            log.write(f"Checking if skeleton exists: {os.path.exists(skeleton_path)}\n")
            
            if os.path.exists(skeleton_path):
                try:
                    with open(skeleton_path, 'rb') as f:
                        skeleton = pickle.load(f)
                    log.write("Successfully loaded skeleton\n")
                    log.write(f"Skeleton type: {type(skeleton)}\n")
                    
                    # Check skeleton attributes
                    if hasattr(skeleton, 'parents'):
                        log.write(f"Parents: {skeleton.parents}\n")
                    if hasattr(skeleton, 'offsets'):
                        log.write(f"Offsets shape: {skeleton.offsets.shape}\n")
                    if hasattr(skeleton, 'names'):
                        log.write(f"Names length: {len(skeleton.names)}\n")
                        log.write(f"First few names: {skeleton.names[:5]}\n")
                except Exception as e:
                    log.write(f"Error loading skeleton: {e}\n")
            
            # Try to load train data
            train_path = os.path.join(style_dir, "train_binary.dat")
            log.write(f"Checking if train_binary.dat exists: {os.path.exists(train_path)}\n")
            
            if os.path.exists(train_path):
                try:
                    with open(train_path, 'rb') as f:
                        train_data = pickle.load(f)
                    log.write("Successfully loaded training data\n")
                    log.write(f"Train data type: {type(train_data)}\n")
                    
                    if isinstance(train_data, dict):
                        log.write(f"Train data keys: {list(train_data.keys())}\n")
                        
                        # Examine each key
                        for key, value in train_data.items():
                            if isinstance(value, dict):
                                log.write(f"  {key} is a dictionary with keys: {list(value.keys())}\n")
                            elif hasattr(value, 'shape'):
                                log.write(f"  {key} has shape: {value.shape}\n")
                            else:
                                log.write(f"  {key} is a {type(value)}\n")
                except Exception as e:
                    log.write(f"Error loading train data: {e}\n")

print("Data check completed. See data_check_log.txt for results.")
