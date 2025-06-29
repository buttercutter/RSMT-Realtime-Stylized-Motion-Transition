#!/usr/bin/env python3
"""
Complete RSMT Pipeline Test

This script tests the end-to-end RSMT pipeline:
1. Generate synthetic phase vectors
2. Decode phase vectors to motion
3. Save motion to BVH format
"""

import os
import sys
import numpy as np
import torch
import matplotlib.pyplot as plt

# Add the repository root to the path
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create output directory
output_dir = "./output/inference"
os.makedirs(output_dir, exist_ok=True)

# Step 1: Generate synthetic phase vectors
def generate_synthetic_phase_vectors(num_frames=60, phase_dim=32, num_cycles=2):
    """Generate synthetic phase vectors that create a cyclical pattern"""
    phase_vectors = np.zeros((num_frames, phase_dim))
    
    # Create a base frequency for each dimension
    freqs = np.linspace(0.5, 2.0, phase_dim)
    
    # Generate sinusoidal patterns
    for i in range(phase_dim):
        # Create a sinusoidal pattern with varying frequency
        phase_vectors[:, i] = np.sin(freqs[i] * num_cycles * 2 * np.pi * np.linspace(0, 1, num_frames))
    
    # Add some noise
    phase_vectors += 0.05 * np.random.randn(num_frames, phase_dim)
    
    return phase_vectors

# Step 2: Create a skeleton
def create_test_skeleton(num_joints=22):
    """Create a test skeleton structure"""
    # Standard skeleton structure
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
    offsets[21] = [0, -0.3, 0]  # RightElbow
    
    return {
        "parents": parents,
        "names": names,
        "offsets": offsets
    }

# Step 3: Run the test
def run_test():
    print("RSMT Pipeline Test")
    print("=================")
    
    # Generate phase vectors
    print("\nStep 1: Generating synthetic phase vectors...")
    phase_vectors = generate_synthetic_phase_vectors()
    print(f"Generated phase vectors with shape: {phase_vectors.shape}")
    
    # Plot the first few dimensions of the phase vectors
    plt.figure(figsize=(10, 6))
    for i in range(min(4, phase_vectors.shape[1])):
        plt.plot(phase_vectors[:, i], label=f'Dim {i}')
    plt.title("Sample of Phase Vector Dimensions")
    plt.xlabel("Frame")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "test_phase_vectors.png"))
    print(f"Saved phase vector plot to {output_dir}/test_phase_vectors.png")
    
    # Create test skeleton
    print("\nStep 2: Creating test skeleton...")
    skeleton_data = create_test_skeleton()
    print(f"Created skeleton with {len(skeleton_data['parents'])} joints")
    
    # Import our motion decoder
    print("\nStep 3: Converting phase vectors to motion...")
    try:
        from src.utils.motion_decoder import decode_phase_to_motion
        motion_data = decode_phase_to_motion(phase_vectors, skeleton_data=skeleton_data)
        print("Successfully decoded phase vectors to motion")
        print("Motion data keys:", list(motion_data.keys()))
        print("Motion data shapes:")
        for key, value in motion_data.items():
            print(f"  {key}: {value.shape}")
    except Exception as e:
        print(f"Error in motion decoding: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Save to BVH
    print("\nStep 4: Saving motion to BVH format...")
    try:
        from src.utils.bvh_writer import save_to_bvh
        output_path = os.path.join(output_dir, "test_pipeline.bvh")
        success = save_to_bvh(motion_data, output_path, skeleton_data=skeleton_data)
        if success:
            print(f"Successfully saved BVH file to {output_path}")
        else:
            print("Failed to save BVH file")
    except Exception as e:
        print(f"Error in BVH writing: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\nPipeline test complete!")
    print("=====================")
    print("Summary:")
    print(f"1. Generated {phase_vectors.shape[0]} frames of synthetic phase data")
    print(f"2. Created a {len(skeleton_data['parents'])}-joint skeleton")
    print(f"3. Converted phase vectors to motion data")
    print(f"4. Saved motion to BVH file at {output_dir}/test_pipeline.bvh")

if __name__ == "__main__":
    run_test()
