#!/usr/bin/env python3
"""
Extreme Motion Test - Create maximum visibility animations

This test creates animations with extremely dramatic motion for maximum visibility.
"""

import torch
import numpy as np
import sys
import os

# Add project to path
sys.path.append('.')

def run_extreme_motion_test():
    """Run the extreme motion test with maximum visibility"""
    print("🎬 RSMT Extreme Motion Test")
    print("=" * 50)
    
    try:
        os.makedirs("output/extreme_motion", exist_ok=True)
        
        from src.utils.motion_decoder import create_enhanced_motion_data
        from src.utils.bvh_writer import save_to_bvh
        
        # Create test phase vectors with extreme values for maximum visibility
        num_frames = 60  # 2 seconds
        phase_vectors = create_extreme_test_vectors(num_frames)
        
        print(f"  📝 Created {num_frames} extreme test phase vectors")
        print(f"  📊 Phase vector range: [{phase_vectors.min():.2f}, {phase_vectors.max():.2f}]")
        
        # Create skeleton
        skeleton_data = create_test_skeleton()
        
        print("  🎯 Converting with enhanced motion decoder...")
        
        # Generate motion with enhanced decoder
        motion_data = create_enhanced_motion_data(phase_vectors, skeleton_data)
        
        print("  📊 Motion data analysis:")
        for key, data in motion_data.items():
            if isinstance(data, np.ndarray) and len(data.shape) >= 2:
                frame_diff = np.linalg.norm(data[1] - data[0]) if len(data) > 1 else 0
                total_diff = np.linalg.norm(data[-1] - data[0]) if len(data) > 1 else 0
                print(f"      {key}: frame-to-frame change = {frame_diff:.4f}, total change = {total_diff:.4f}")
        
        print("  💾 Saving extreme motion BVH...")
        
        # Save as BVH
        output_path = "./output/extreme_motion/extreme_motion.bvh"
        success = save_to_bvh(motion_data, output_path, skeleton_data, frametime=1.0/30.0)
        
        if success:
            file_size = os.path.getsize(output_path)
            print(f"  ✅ Extreme motion animation saved: {output_path}")
            print(f"  📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Verify the BVH file has dramatic changes
            verify_bvh_motion(output_path)
            
            return output_path
        else:
            print("  ❌ Failed to save extreme motion animation")
            return None
            
    except Exception as e:
        print(f"  ❌ Error in extreme motion test: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_extreme_test_vectors(num_frames):
    """Create phase vectors with extreme values for maximum visibility"""
    phase_vectors = np.zeros((num_frames, 32))
    
    for frame in range(num_frames):
        t = frame / num_frames
        
        # Extreme motion components - very large values
        base_freq = 1.0  # 1 complete cycle over the animation
        
        # Primary motion - use full range of values
        phase_vectors[frame, 0] = 5.0 * np.sin(2 * np.pi * t * base_freq * 2)  # Extreme hip sway
        phase_vectors[frame, 1] = 8.0 * np.sin(2 * np.pi * t * base_freq * 4)  # Extreme left leg
        phase_vectors[frame, 2] = 8.0 * np.cos(2 * np.pi * t * base_freq * 4)  # Extreme right leg
        phase_vectors[frame, 3] = 3.0 * np.sin(2 * np.pi * t * base_freq * 8)  # Extreme vertical
        
        # Extreme arm motion
        phase_vectors[frame, 4] = 6.0 * np.sin(2 * np.pi * t * base_freq * 4 + np.pi)  # Left arm
        phase_vectors[frame, 5] = 6.0 * np.sin(2 * np.pi * t * base_freq * 4)  # Right arm
        
        # Extreme spine motion
        phase_vectors[frame, 6] = 2.0 * np.sin(2 * np.pi * t * base_freq * 3)  # Spine rotation
        phase_vectors[frame, 7] = 1.5 * np.cos(2 * np.pi * t * base_freq * 6)  # Spine twist
        
        # Fill remaining with large variations
        for i in range(8, 32):
            freq_mult = 0.5 + i * 0.25
            amplitude = 2.0 + i * 0.1  # Increasing amplitude
            phase_vectors[frame, i] = amplitude * np.sin(2 * np.pi * t * base_freq * freq_mult + i)
    
    return phase_vectors

def create_test_skeleton():
    """Create test skeleton with standard structure"""
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
        [0.0, 0.15, 0.0],     # Spine
        [0.0, 0.15, 0.0],     # Spine1
        [0.0, 0.15, 0.0],     # Spine2
        [0.0, 0.12, 0.0],     # Neck
        [0.0, 0.12, 0.0],     # Head
        [-0.2, 0.05, 0.0],    # LeftShoulder
        [-0.3, 0.0, 0.0],     # LeftArm
        [0.0, -0.3, 0.0],     # LeftForeArm
        [0.0, -0.25, 0.0],    # LeftHand
        [0.2, 0.05, 0.0],     # RightShoulder
        [0.3, 0.0, 0.0],      # RightArm
        [0.0, -0.3, 0.0],     # RightForeArm
        [0.0, -0.25, 0.0],    # RightHand
        [-0.12, -0.05, 0.0],  # LeftUpLeg
        [0.0, -0.45, 0.0],    # LeftLeg
        [0.0, -0.45, 0.0],    # LeftFoot
        [0.0, 0.0, 0.18],     # LeftToeBase
        [0.12, -0.05, 0.0],   # RightUpLeg
        [0.0, -0.45, 0.0],    # RightLeg
        [0.0, -0.45, 0.0],    # RightFoot
        [0.0, 0.0, 0.18]      # RightToeBase
    ])
    
    return {
        'joint_names': joint_names,
        'parents': parents,
        'offsets': offsets,
        'num_joints': len(joint_names)
    }

def verify_bvh_motion(bvh_path):
    """Verify the BVH file contains dramatic motion changes"""
    print(f"\n  🔍 Verifying BVH motion: {bvh_path}")
    
    try:
        with open(bvh_path, 'r') as f:
            lines = f.readlines()
        
        motion_data = []
        in_motion = False
        
        for line in lines:
            line = line.strip()
            if line == "MOTION":
                in_motion = True
                continue
            elif in_motion and line and not line.startswith("Frame"):
                values = [float(x) for x in line.split()]
                motion_data.append(values)
        
        if len(motion_data) >= 2:
            frame1 = np.array(motion_data[0])
            frame2 = np.array(motion_data[1])
            frame_last = np.array(motion_data[-1])
            
            frame_diff = np.linalg.norm(frame2 - frame1)
            total_diff = np.linalg.norm(frame_last - frame1)
            max_value = max(max(abs(x) for x in frame) for frame in motion_data)
            
            print(f"      Frame-to-frame change: {frame_diff:.4f}")
            print(f"      Total animation change: {total_diff:.4f}")
            print(f"      Maximum value: {max_value:.4f}")
            
            if frame_diff > 5.0:
                print("      ✅ EXCELLENT: Very dramatic frame-to-frame changes!")
            elif frame_diff > 1.0:
                print("      ✅ GOOD: Substantial frame-to-frame changes")
            elif frame_diff > 0.1:
                print("      ⚠️  MODERATE: Some motion visible")
            else:
                print("      ❌ POOR: Motion changes too small to see clearly")
        
    except Exception as e:
        print(f"      ❌ Error verifying BVH: {e}")

def main():
    """Main function"""
    run_extreme_motion_test()
    
    print("\n🎉 Extreme Motion Test Complete!")
    print("=" * 50)
    print("\n🎯 If this test succeeded, you should now have:")
    print("• Extremely dramatic skeleton motion")
    print("• Frame-to-frame changes > 5.0 units")
    print("• Very visible arm swinging and leg movement")
    print("• Clear walking motion through space")
    
    print(f"\n🌐 View options:")
    print("• Web viewer: http://localhost:8000/output/web_viewer/")
    print("• Test viewer: http://localhost:8000/output/web_viewer/test.html")
    print("• Simple test: http://localhost:8000/output/web_viewer/simple_test.html")
    print("• Import to Blender for best results")

if __name__ == "__main__":
    main()
