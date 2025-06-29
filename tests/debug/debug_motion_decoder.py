#!/usr/bin/env python3
"""
Debug Motion Decoder

Diagnose why the skeleton animations aren't showing movement.
"""

import torch
import numpy as np
import sys
import os

# Add source to path
sys.path.append('src')
sys.path.append('.')

def debug_motion_data():
    """Debug the motion decoder output"""
    print("🔍 Debugging Motion Decoder Output...")
    
    try:
        from src.utils.motion_decoder import create_motion_data
        
        # Create simple test phase vectors
        num_frames = 10
        phase_vectors = np.zeros((num_frames, 32))
        
        # Add some obvious patterns
        for frame in range(num_frames):
            t = frame / num_frames * 2 * np.pi
            phase_vectors[frame, 0] = 0.5 * np.sin(t)  # Hip motion
            phase_vectors[frame, 1] = np.sin(t * 2)    # Leg motion
            phase_vectors[frame, 2] = np.cos(t * 2)    # Opposite leg
            phase_vectors[frame, 4] = 0.3 * np.sin(t)  # Arm swing
        
        print(f"  📝 Input phase vectors shape: {phase_vectors.shape}")
        print(f"  📝 Sample phase values: {phase_vectors[0, :8]}")
        
        # Create skeleton
        skeleton_data = create_test_skeleton()
        
        # Convert to motion
        motion_data = create_motion_data(
            torch.tensor(phase_vectors, dtype=torch.float32),
            skeleton_data
        )
        
        print(f"\n  🎯 Motion data keys: {list(motion_data.keys())}")
        
        for key, data in motion_data.items():
            if isinstance(data, (torch.Tensor, np.ndarray)):
                print(f"  📊 {key}: shape {data.shape}")
                if len(data.shape) >= 2:
                    print(f"      Range: [{data.min():.4f}, {data.max():.4f}]")
                    print(f"      Mean: {data.mean():.4f}")
                    print(f"      Sample frame 0: {data[0].flatten()[:5]}")
                    print(f"      Sample frame 5: {data[5].flatten()[:5]}")
        
        # Check if data is changing over time
        print(f"\n  🔄 Motion variation analysis:")
        if 'local_rotations' in motion_data:
            rot_data = motion_data['local_rotations']
            frame_diff = torch.norm(rot_data[1] - rot_data[0]).item()
            total_diff = torch.norm(rot_data[-1] - rot_data[0]).item()
            print(f"      Frame-to-frame rotation change: {frame_diff:.6f}")
            print(f"      Total rotation change: {total_diff:.6f}")
        
        if 'global_positions' in motion_data:
            pos_data = motion_data['global_positions']
            frame_diff = torch.norm(pos_data[1] - pos_data[0]).item()
            total_diff = torch.norm(pos_data[-1] - pos_data[0]).item()
            print(f"      Frame-to-frame position change: {frame_diff:.6f}")
            print(f"      Total position change: {total_diff:.6f}")
        
        return motion_data
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_test_skeleton():
    """Create test skeleton data"""
    joint_names = [
        "Hips", "Spine", "Spine1", "Spine2", "Neck", "Head",
        "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
        "RightShoulder", "RightArm", "RightForeArm", "RightHand",
        "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
        "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"
    ]
    
    parents = [-1, 0, 1, 2, 3, 4, 3, 6, 7, 8, 3, 10, 11, 12, 0, 14, 15, 16, 0, 18, 19, 20]
    
    offsets = np.array([
        [0.0, 0.0, 0.0],      # Hips
        [0.0, 0.1, 0.0],      # Spine
        [0.0, 0.1, 0.0],      # Spine1
        [0.0, 0.1, 0.0],      # Spine2
        [0.0, 0.1, 0.0],      # Neck
        [0.0, 0.1, 0.0],      # Head
        [-0.15, 0.05, 0.0],   # LeftShoulder
        [-0.25, 0.0, 0.0],    # LeftArm
        [0.0, -0.25, 0.0],    # LeftForeArm
        [0.0, -0.2, 0.0],     # LeftHand
        [0.15, 0.05, 0.0],    # RightShoulder
        [0.25, 0.0, 0.0],     # RightArm
        [0.0, -0.25, 0.0],    # RightForeArm
        [0.0, -0.2, 0.0],     # RightHand
        [-0.1, -0.05, 0.0],   # LeftUpLeg
        [0.0, -0.4, 0.0],     # LeftLeg
        [0.0, -0.4, 0.0],     # LeftFoot
        [0.0, 0.0, 0.15],     # LeftToeBase
        [0.1, -0.05, 0.0],    # RightUpLeg
        [0.0, -0.4, 0.0],     # RightLeg
        [0.0, -0.4, 0.0],     # RightFoot
        [0.0, 0.0, 0.15]      # RightToeBase
    ])
    
    return {
        'joint_names': joint_names,
        'parents': parents,
        'offsets': offsets,
        'num_joints': len(joint_names)
    }

def debug_bvh_file(bvh_path):
    """Debug a BVH file to see if it contains animation data"""
    print(f"\n🔍 Debugging BVH file: {bvh_path}")
    
    if not os.path.exists(bvh_path):
        print(f"  ❌ File not found: {bvh_path}")
        return
    
    try:
        with open(bvh_path, 'r') as f:
            lines = f.readlines()
        
        in_motion = False
        frame_count = 0
        frame_time = 0.0
        sample_frames = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if line.startswith("Frames:"):
                frame_count = int(line.split()[-1])
            elif line.startswith("Frame Time:"):
                frame_time = float(line.split()[-1])
            elif line == "MOTION":
                in_motion = True
                continue
            elif in_motion and line and not line.startswith("Frames") and not line.startswith("Frame Time"):
                # This is motion data
                values = [float(x) for x in line.split()]
                if len(sample_frames) < 3:  # Store first 3 frames
                    sample_frames.append(values)
        
        print(f"  📊 Frame count: {frame_count}")
        print(f"  📊 Frame time: {frame_time}")
        print(f"  📊 FPS: {1.0/frame_time if frame_time > 0 else 0}")
        
        if sample_frames:
            print(f"  📊 Channels per frame: {len(sample_frames[0])}")
            print(f"  📊 Sample frame 0: {sample_frames[0][:10]}...")
            if len(sample_frames) > 1:
                print(f"  📊 Sample frame 1: {sample_frames[1][:10]}...")
                
                # Check for differences
                diff = [abs(a - b) for a, b in zip(sample_frames[0], sample_frames[1])]
                max_diff = max(diff) if diff else 0
                print(f"  🔄 Max change between frames: {max_diff:.6f}")
                
                if max_diff < 0.001:
                    print("  ⚠️  WARNING: Very little change between frames - animation might be static!")
                else:
                    print("  ✅ Animation data shows variation")
        else:
            print("  ❌ No motion data found!")
            
    except Exception as e:
        print(f"  ❌ Error reading BVH: {e}")

def main():
    """Main debug function"""
    print("🔍 RSMT Motion Decoder Diagnostics")
    print("=" * 50)
    
    # Debug motion decoder
    motion_data = debug_motion_data()
    
    # Debug existing BVH files
    bvh_files = [
        "output/inference/test_pipeline.bvh",
        "output/inference/test_bvh_writer.bvh", 
        "output/inference/final_test/final_test.bvh"
    ]
    
    for bvh_file in bvh_files:
        debug_bvh_file(bvh_file)
    
    print("\n🔧 Diagnosis Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
