#!/usr/bin/env python3

import os
import sys
import numpy as np

# Add the repository root to the path
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create a simple test motion
frames = 30
num_joints = 22
parents = [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21][:num_joints]
names = ["Hips", "LeftHip", "LeftKnee", "LeftAnkle", "LeftToe",
         "RightHip", "RightKnee", "RightAnkle", "RightToe",
         "Chest", "Chest2", "Chest3", "Chest4", "Neck", "Head",
         "LeftCollar", "LeftShoulder", "LeftElbow", "LeftWrist",
         "RightCollar", "RightShoulder", "RightElbow", "RightWrist"][:num_joints]

# Create default offsets (T-pose)
offsets = np.zeros((num_joints, 3), dtype=np.float32)
# Basic T-pose skeleton offsets
offsets[0] = [0, 1.0, 0]  # Hip
offsets[1] = [-0.2, -0.1, 0]  # LeftHip
offsets[2] = [0, -0.5, 0]  # LeftKnee
offsets[3] = [0, -0.5, 0]  # LeftAnkle
offsets[4] = [0, -0.1, 0.2]  # LeftToe
offsets[5] = [0.2, -0.1, 0]  # RightHip
offsets[6] = [0, -0.5, 0]  # RightKnee
offsets[7] = [0, -0.5, 0]  # RightAnkle
offsets[8] = [0, -0.1, 0.2]  # RightToe
offsets[9] = [0, 0.2, 0]  # Chest
offsets[10] = [0, 0.2, 0]  # Chest2
offsets[11] = [0, 0.2, 0]  # Chest3
offsets[12] = [0, 0.2, 0]  # Chest4
offsets[13] = [0, 0.1, 0]  # Neck
offsets[14] = [0, 0.1, 0]  # Head
offsets[15] = [-0.2, 0, 0]  # LeftCollar
offsets[16] = [-0.2, 0, 0]  # LeftShoulder
offsets[17] = [0, -0.3, 0]  # LeftElbow
offsets[18] = [0, -0.3, 0]  # LeftWrist
offsets[19] = [0.2, 0, 0]  # RightCollar
offsets[20] = [0.2, 0, 0]  # RightShoulder
offsets[21] = [0, -0.3, 0]  # RightElbow if applicable

# Create identity quaternions (no rotation)
local_rotations = np.zeros((frames, num_joints, 4))
local_rotations[:, :, 0] = 1.0  # w component = 1 for identity quaternions

# Create simple hip movement (swaying side to side)
hip_positions = np.zeros((frames, 1, 3))
for i in range(frames):
    # Simple swaying motion
    hip_positions[i, 0, 0] = 0.1 * np.sin(i * 0.2)  # X-axis sway
    hip_positions[i, 0, 1] = 1.0 + 0.05 * np.cos(i * 0.2)  # Y-axis bob
    
    # Add some joint rotations over time
    for j in range(1, num_joints):
        if j % 2 == 0:  # Alternate joints
            # Simple rotation around Y axis
            angle = 0.2 * np.sin(i * 0.1)
            local_rotations[i, j] = [np.cos(angle/2), 0, np.sin(angle/2), 0]  # Quaternion for Y rotation

# Calculate global positions with simple forward kinematics
global_positions = np.zeros((frames, num_joints, 3))
global_positions[:, 0] = hip_positions[:, 0]  # Root position

# For simplicity, just do a basic forward pass
for j in range(1, num_joints):
    parent = parents[j]
    global_positions[:, j] = global_positions[:, parent] + offsets[j]

# Create motion data dictionary
motion_data = {
    "local_rotations": local_rotations,
    "global_positions": global_positions,
    "global_rotations": local_rotations,  # Simplified - in a real implementation these would be calculated 
    "hip_positions": hip_positions
}

# Skeleton data
skeleton_data = {
    "offsets": offsets,
    "parents": parents,
    "names": names
}

# Now use our bvh_writer to save this to a BVH file
try:
    print("Importing BVH writer...")
    from src.utils.bvh_writer import save_to_bvh
    
    output_path = "./output/inference/test_bvh_writer.bvh"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Saving motion to BVH: {output_path}")
    success = save_to_bvh(motion_data, output_path, skeleton_data=skeleton_data)
    print("BVH save result:", "Success" if success else "Failed")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
