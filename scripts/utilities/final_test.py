#!/usr/bin/env python3
"""
Final RSMT Implementation Test

This script tests the complete RSMT pipeline:
1. Generate synthetic manifold points
2. Generate transition path between manifold points
3. Decode manifold points to phase vectors
4. Convert phase vectors to motion data
5. Save motion to BVH format
"""

import os
import sys
import numpy as np
import torch
import matplotlib.pyplot as plt
from datetime import datetime

# Add the repository root to the path
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create output directory
output_dir = "./output/inference/final_test"
os.makedirs(output_dir, exist_ok=True)


def generate_manifold_points(manifold_dim=8):
    """Generate two points in the manifold space"""
    # Generate two distinct points in manifold space
    source_point = torch.randn(1, manifold_dim)
    target_point = torch.randn(1, manifold_dim)
    
    # Normalize to unit length
    source_point = source_point / torch.norm(source_point)
    target_point = target_point / torch.norm(target_point)
    
    return source_point, target_point


def generate_transition_path(start_point, end_point, num_steps=30):
    """
    Generate a smooth transition path between start and end points
    using spherical linear interpolation (slerp)
    """
    # Simple implementation of slerp for manifold points
    def slerp(p0, p1, t):
        omega = torch.acos((p0 * p1).sum())
        so = torch.sin(omega)
        
        # If points are very close, just use linear interpolation
        if abs(so) < 1e-8:
            return p0 * (1.0 - t) + p1 * t
            
        return torch.sin((1.0 - t) * omega) / so * p0 + torch.sin(t * omega) / so * p1
    
    # Generate transition path
    path = torch.zeros((num_steps, start_point.shape[1]))
    for i in range(num_steps):
        t = i / (num_steps - 1)  # Normalize to 0-1
        path[i] = slerp(start_point[0], end_point[0], t)
    
    return path


def decode_manifold_to_phase(manifold_points, phase_dim=32):
    """
    Decode manifold points to phase vectors
    In a real implementation, this would use a trained decoder
    """
    num_points = manifold_points.shape[0]
    phase_vectors = torch.zeros((num_points, phase_dim))
    
    # Simple mapping from manifold to phase space
    # In a real implementation, this would be a neural network
    for i in range(num_points):
        # Create a phase vector based on the manifold point
        # Using the manifold point to modulate sine waves at different frequencies
        for j in range(phase_dim):
            freq = 0.5 + j * 0.1
            phase = torch.sin(freq * torch.arange(manifold_points.shape[1])).dot(manifold_points[i])
            phase_vectors[i, j] = torch.sin(phase * np.pi)
    
    return phase_vectors


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


def plot_vectors(vectors, title, filename, dims_to_plot=4):
    """Plot the first few dimensions of vectors"""
    plt.figure(figsize=(10, 6))
    for i in range(min(dims_to_plot, vectors.shape[1])):
        plt.plot(vectors[:, i].cpu().numpy(), label=f'Dim {i}')
    plt.title(title)
    plt.xlabel("Frame")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()


def run_final_test():
    """Run a complete end-to-end test of the RSMT implementation"""
    print("\n===== RSMT FINAL IMPLEMENTATION TEST =====")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Generate manifold points
        print("\n1. Generating points in manifold space...")
        source_point, target_point = generate_manifold_points()
        print(f"  Source point shape: {source_point.shape}")
        print(f"  Target point shape: {target_point.shape}")
        
        # Step 2: Generate transition path
        print("\n2. Generating transition path in manifold space...")
        num_frames = 60
        manifold_path = generate_transition_path(source_point, target_point, num_frames)
        print(f"  Transition path shape: {manifold_path.shape}")
        plot_vectors(manifold_path, "Manifold Transition Path", "manifold_path.png", 8)
        print(f"  Manifold path plot saved to {output_dir}/manifold_path.png")
        
        # Step 3: Decode manifold to phase
        print("\n3. Decoding manifold points to phase vectors...")
        phase_vectors = decode_manifold_to_phase(manifold_path)
        print(f"  Phase vectors shape: {phase_vectors.shape}")
        plot_vectors(phase_vectors, "Phase Vectors", "phase_vectors.png")
        print(f"  Phase vectors plot saved to {output_dir}/phase_vectors.png")
        
        # Step 4: Create skeleton data
        print("\n4. Creating skeleton data...")
        skeleton_data = create_test_skeleton()
        print(f"  Created skeleton with {len(skeleton_data['parents'])} joints")
        
        # Step 5: Convert phase vectors to motion
        print("\n5. Converting phase vectors to motion data...")
        try:
            from src.utils.motion_decoder import decode_phase_to_motion
            motion_data = decode_phase_to_motion(phase_vectors, skeleton_data=skeleton_data)
            print("  Successfully converted phase vectors to motion data")
            print("  Motion data contains:")
            for key, value in motion_data.items():
                print(f"    {key}: shape {value.shape}")
        except Exception as e:
            print(f"  Error in motion decoding: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Step 6: Save motion to BVH
        print("\n6. Saving motion to BVH format...")
        try:
            from src.utils.bvh_writer import save_to_bvh
            output_path = os.path.join(output_dir, "final_test.bvh")
            success = save_to_bvh(motion_data, output_path, skeleton_data=skeleton_data)
            
            if success:
                print(f"  Successfully saved BVH file to {output_path}")
            else:
                print("  Failed to save BVH file")
                return
        except Exception as e:
            print(f"  Error in BVH writing: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Final success message
        print("\n===== TEST COMPLETED SUCCESSFULLY =====")
        print(f"Output files location: {output_dir}")
        print("Files generated:")
        print(f"  - {output_dir}/manifold_path.png - Visualization of the manifold transition")
        print(f"  - {output_dir}/phase_vectors.png - Visualization of the phase vectors")
        print(f"  - {output_dir}/final_test.bvh - Animation file ready for playback")
        
    except Exception as e:
        print(f"\nUnexpected error in test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_final_test()
