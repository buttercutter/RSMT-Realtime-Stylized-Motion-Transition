#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import numpy as np
import torch

# Define a simple 2D array of phase vectors (dummy data)
phase_vectors = np.random.rand(30, 32)  # 30 frames, 32-dimensional phase vectors
phase_tensor = torch.tensor(phase_vectors, dtype=torch.float32)

print("Created phase vectors with shape:", phase_vectors.shape)

# Create a simple skeleton structure
skeleton_data = {
    "offsets": np.zeros((22, 3), dtype=np.float32),
    "parents": [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21][:22],
    "names": ["Hips", "LeftHip", "LeftKnee", "LeftAnkle", "LeftToe",
              "RightHip", "RightKnee", "RightAnkle", "RightToe",
              "Chest", "Chest2", "Chest3", "Chest4", "Neck", "Head",
              "LeftCollar", "LeftShoulder", "LeftElbow", "LeftWrist",
              "RightCollar", "RightShoulder", "RightElbow", "RightWrist"][:22]
}

print("Created skeleton structure")

# Try to import our modules
print("Importing motion_decoder...")
try:
    from src.utils.motion_decoder import decode_phase_to_motion
    print("Successfully imported decode_phase_to_motion")
    
    # Decode the phase vectors to motion
    print("Decoding phase vectors to motion...")
    motion_data = decode_phase_to_motion(phase_tensor, skeleton_data=skeleton_data)
    print("Motion data keys:", list(motion_data.keys()))
    print("Motion data shapes:")
    for key, value in motion_data.items():
        print(f"  {key}: {value.shape}")
    
    print("Importing bvh_writer...")
    from src.utils.bvh_writer import save_to_bvh
    print("Successfully imported save_to_bvh")
    
    # Save the motion to BVH
    output_path = "./output/inference/test_motion.bvh"
    print(f"Saving motion to BVH: {output_path}")
    success = save_to_bvh(motion_data, output_path, skeleton_data=skeleton_data)
    print("BVH save result:", "Success" if success else "Failed")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
