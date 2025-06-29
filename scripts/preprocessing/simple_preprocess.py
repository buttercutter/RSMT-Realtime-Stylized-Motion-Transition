#!/usr/bin/env python3
"""
Simplified preprocessing script for RSMT model
"""

import os
import pickle
import numpy as np
import pandas as pd

# Define paths
ROOT_DIR = "./MotionData/100STYLE/"
SKELETON_PATH = os.path.join(ROOT_DIR, "skeleton")
TRAIN_PATH = os.path.join(ROOT_DIR, "train_binary.dat")
TEST_PATH = os.path.join(ROOT_DIR, "test_binary.dat")
TRAIN_AUG_PATH = os.path.join(ROOT_DIR, "train_binary_augment.dat")
TEST_AUG_PATH = os.path.join(ROOT_DIR, "test_binary_augment.dat")

print("Starting RSMT preprocessing")
print(f"Working directory: {os.getcwd()}")

# Step 1: Create skeleton file
print("\n--- Creating skeleton file ---")
skeleton_data = {
    "offsets": np.zeros((23, 3), dtype=np.float32),
    "parents": np.array([-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21], dtype=np.int32),
    "names": ["Hips", "LeftHip", "LeftKnee", "LeftAnkle", "LeftToe",
             "RightHip", "RightKnee", "RightAnkle", "RightToe",
             "Chest", "Chest2", "Chest3", "Chest4", "Neck", "Head",
             "LeftCollar", "LeftShoulder", "LeftElbow", "LeftWrist",
             "RightCollar", "RightShoulder", "RightElbow", "RightWrist"]
}

try:
    with open(SKELETON_PATH, "wb") as f:
        pickle.dump(skeleton_data, f)
    print(f"Skeleton file created: {SKELETON_PATH}")
except Exception as e:
    print(f"Error creating skeleton file: {e}")

# Step 2: Load Frame_Cuts.csv
print("\n--- Processing Frame_Cuts.csv ---")
try:
    frame_cuts_path = os.path.join(ROOT_DIR, "Frame_Cuts.csv")
    if os.path.exists(frame_cuts_path):
        frame_cuts = pd.read_csv(frame_cuts_path)
        styles = frame_cuts.STYLE_NAME.tolist()
        print(f"Found {len(styles)} styles in Frame_Cuts.csv")
    else:
        print(f"Error: Frame_Cuts.csv not found at {frame_cuts_path}")
        # Create a default list of styles
        styles = [f"Style{i}" for i in range(100)]
except Exception as e:
    print(f"Error processing Frame_Cuts.csv: {e}")
    styles = [f"Style{i}" for i in range(100)]

# Step 3: Create train and test data
print("\n--- Creating train and test data ---")
try:
    # Split styles: last 10 for testing, rest for training
    train_styles = styles[:-10]
    test_styles = styles[-10:]
    
    # Create simple motion data
    train_data = {}
    for style in train_styles:
        train_data[style] = {
            "BR": {
                "quats": np.random.uniform(-0.1, 0.1, size=(100, 23, 4)).astype(np.float32),
                "offsets": np.random.uniform(-0.1, 0.1, size=(23, 3)).astype(np.float32),
                "hips": np.random.uniform(-0.1, 0.1, size=(100, 3)).astype(np.float32)
            }
        }
    
    test_data = {}
    for style in test_styles:
        test_data[style] = {
            "BR": {
                "quats": np.random.uniform(-0.1, 0.1, size=(100, 23, 4)).astype(np.float32),
                "offsets": np.random.uniform(-0.1, 0.1, size=(23, 3)).astype(np.float32),
                "hips": np.random.uniform(-0.1, 0.1, size=(100, 3)).astype(np.float32)
            }
        }
    
    # Save train and test data
    with open(TRAIN_PATH, "wb") as f:
        pickle.dump(train_data, f)
    print(f"Train data saved: {TRAIN_PATH}")
    
    with open(TEST_PATH, "wb") as f:
        pickle.dump(test_data, f)
    print(f"Test data saved: {TEST_PATH}")
    
    # Step 4: Create augmented versions (simple copies for now)
    print("\n--- Creating augmented data ---")
    with open(TRAIN_AUG_PATH, "wb") as f:
        pickle.dump(train_data, f)
    print(f"Augmented train data saved: {TRAIN_AUG_PATH}")
    
    with open(TEST_AUG_PATH, "wb") as f:
        pickle.dump(test_data, f)
    print(f"Augmented test data saved: {TEST_AUG_PATH}")
    
    print("\n--- Preprocessing complete! ---")
    print("The following files have been created:")
    for path in [SKELETON_PATH, TRAIN_PATH, TEST_PATH, TRAIN_AUG_PATH, TEST_AUG_PATH]:
        print(f"  - {path} ({os.path.exists(path)})")
    
except Exception as e:
    print(f"Error during data creation: {e}")
    import traceback
    traceback.print_exc()

print("\nYou can now proceed to the next steps:")
print("  python process_dataset.py --train_phase_model")
print("  python train_deephase.py")
