#!/usr/bin/env python3
"""
Enhanced Animation Test

Generate new animations with much more dramatic and visible motion.
"""

import torch
import numpy as np
import sys
import os

# Add project to path
sys.path.append('.')

def create_enhanced_test():
    """Create enhanced test animations with dramatic motion"""
    print("🎬 Creating Enhanced Animation Test...")
    
    os.makedirs("output/enhanced_test", exist_ok=True)
    
    try:
        from src.utils.motion_decoder import create_enhanced_motion_data
        from src.utils.bvh_writer import save_to_bvh
        
        # Create more varied phase vectors for better animation
        num_frames = 90  # 3 seconds at 30fps
        phase_vectors = create_dramatic_phase_vectors(num_frames)
        
        print(f"  📝 Generated {num_frames} dramatic phase vectors")
        
        # Create skeleton
        skeleton_data = create_test_skeleton()
        
        print("  🎯 Converting to enhanced motion data...")
        
        # Generate enhanced motion
        motion_data = create_enhanced_motion_data(phase_vectors, skeleton_data)
        
        print("  💾 Saving enhanced BVH animation...")
        
        # Save as BVH
        output_path = "./output/enhanced_test/dramatic_walking.bvh"
        success = save_to_bvh(motion_data, output_path, skeleton_data, frametime=1.0/30.0)
        
        if success:
            print(f"  ✅ Enhanced animation saved: {output_path}")
            
            # Create a second animation with different style
            print("  🎭 Creating style variation...")
            
            phase_vectors_2 = create_style_variation_phase_vectors(num_frames)
            motion_data_2 = create_enhanced_motion_data(phase_vectors_2, skeleton_data)
            
            output_path_2 = "./output/enhanced_test/style_variation.bvh"
            success_2 = save_to_bvh(motion_data_2, output_path_2, skeleton_data, frametime=1.0/30.0)
            
            if success_2:
                print(f"  ✅ Style variation saved: {output_path_2}")
            
            return [output_path, output_path_2] if success_2 else [output_path]
        else:
            print("  ❌ Failed to save enhanced animation")
            return None
            
    except Exception as e:
        print(f"  ❌ Error creating enhanced test: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_dramatic_phase_vectors(num_frames):
    """Create phase vectors that will result in dramatic motion"""
    phase_vectors = np.zeros((num_frames, 32))
    
    for frame in range(num_frames):
        t = frame / num_frames
        
        # Create strong periodic patterns for walking
        base_freq = 2.0  # 2 complete cycles
        
        # Primary motion components - much larger values
        phase_vectors[frame, 0] = 2.0 * np.sin(2 * np.pi * t * base_freq)  # Strong hip sway
        phase_vectors[frame, 1] = 3.0 * np.sin(2 * np.pi * t * base_freq * 2)  # Left leg
        phase_vectors[frame, 2] = 3.0 * np.cos(2 * np.pi * t * base_freq * 2)  # Right leg (opposite)
        phase_vectors[frame, 3] = 1.5 * np.sin(2 * np.pi * t * base_freq * 4)  # Vertical bounce
        
        # Arm swinging - strong and opposite to legs
        phase_vectors[frame, 4] = 2.5 * np.sin(2 * np.pi * t * base_freq * 2 + np.pi)  # Left arm (opposite to right leg)
        phase_vectors[frame, 5] = 2.5 * np.sin(2 * np.pi * t * base_freq * 2)  # Right arm (with left leg)
        
        # Torso and spine motion
        phase_vectors[frame, 6] = 1.0 * np.sin(2 * np.pi * t * base_freq * 1.5)  # Spine rotation
        phase_vectors[frame, 7] = 0.8 * np.cos(2 * np.pi * t * base_freq * 3)  # Spine twist
        
        # Secondary joint motions
        for i in range(8, 16):
            freq_mult = 1 + (i - 8) * 0.5
            phase_vectors[frame, i] = 0.8 * np.sin(2 * np.pi * t * base_freq * freq_mult + i)
        
        # Style components for variation
        phase_vectors[frame, 16] = 1.0  # High energy
        phase_vectors[frame, 17] = 0.8 + 0.2 * np.sin(2 * np.pi * t * 3)  # Variable smoothness
        phase_vectors[frame, 18] = 1.2  # High amplitude
        phase_vectors[frame, 19] = 0.7 + 0.3 * np.cos(2 * np.pi * t * 5)  # Rhythmic variation
        
        # Character expression
        phase_vectors[frame, 20] = 0.9  # Confident
        phase_vectors[frame, 21] = 0.8  # Fluid
        phase_vectors[frame, 22] = 0.6 + 0.4 * np.sin(2 * np.pi * t)  # Expressive
        
        # Additional variation
        for i in range(23, 32):
            phase_vectors[frame, i] = 0.3 * np.sin(2 * np.pi * t * (i - 20) + frame * 0.2)
    
    return phase_vectors

def create_style_variation_phase_vectors(num_frames):
    """Create phase vectors for a different motion style"""
    phase_vectors = np.zeros((num_frames, 32))
    
    for frame in range(num_frames):
        t = frame / num_frames
        
        # Different rhythm - more like dancing or martial arts
        base_freq = 1.5
        
        # Different motion pattern - more complex
        phase_vectors[frame, 0] = 1.5 * np.sin(2 * np.pi * t * base_freq) + 0.5 * np.sin(2 * np.pi * t * base_freq * 3)
        phase_vectors[frame, 1] = 2.0 * np.sin(2 * np.pi * t * base_freq * 1.5 + np.pi/4)  
        phase_vectors[frame, 2] = 2.0 * np.sin(2 * np.pi * t * base_freq * 1.5 - np.pi/4)  
        phase_vectors[frame, 3] = 2.0 * np.sin(2 * np.pi * t * base_freq * 2.5)  
        
        # More expressive arm movements
        phase_vectors[frame, 4] = 3.0 * np.sin(2 * np.pi * t * base_freq * 1.25 + np.pi/3)
        phase_vectors[frame, 5] = 3.0 * np.sin(2 * np.pi * t * base_freq * 1.25 - np.pi/3)
        
        # More dynamic spine
        phase_vectors[frame, 6] = 1.5 * np.sin(2 * np.pi * t * base_freq * 0.75)
        phase_vectors[frame, 7] = 1.2 * np.cos(2 * np.pi * t * base_freq * 2)
        
        # Complex secondary motions
        for i in range(8, 16):
            freq_mult = 0.5 + (i - 8) * 0.3
            phase_vectors[frame, i] = 1.0 * np.sin(2 * np.pi * t * base_freq * freq_mult + i * np.pi/4)
        
        # Different style parameters
        phase_vectors[frame, 16] = 0.8 + 0.2 * np.sin(2 * np.pi * t * 2)  # Variable energy
        phase_vectors[frame, 17] = 0.3  # Sharper movements
        phase_vectors[frame, 18] = 1.5  # Very high amplitude
        phase_vectors[frame, 19] = 0.9  # Strong rhythm
        
        # Different character
        phase_vectors[frame, 20] = 0.7  # Moderate confidence
        phase_vectors[frame, 21] = 0.5  # Less fluid, more angular
        phase_vectors[frame, 22] = 1.0  # Very expressive
        
    return phase_vectors

def create_test_skeleton():
    """Create test skeleton matching the motion decoder expectations"""
    joint_names = [
        "Hips", "Spine", "Spine1", "Spine2", "Neck", "Head",
        "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
        "RightShoulder", "RightArm", "RightForeArm", "RightHand",
        "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
        "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"
    ]
    
    parents = [-1, 0, 1, 2, 3, 4, 3, 6, 7, 8, 3, 10, 11, 12, 0, 14, 15, 16, 0, 18, 19, 20]
    
    # Larger offsets for more visible motion
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

def main():
    """Main function"""
    print("🎬 Enhanced RSMT Animation Generator")
    print("=" * 50)
    
    # Create enhanced animations
    animation_paths = create_enhanced_test()
    
    if animation_paths:
        print("\n🎉 Enhanced Animations Complete!")
        print("=" * 50)
        
        for path in animation_paths:
            file_size = os.path.getsize(path) if os.path.exists(path) else 0
            print(f"📁 {path}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        print(f"\n🎭 Features:")
        print("• 3 seconds of dramatic motion (90 frames)")
        print("• Strong arm swinging and leg movement")
        print("• Hip sway and forward walking motion")
        print("• Multiple style variations")
        print("• Enhanced joint rotations for visibility")
        
        print("\n🎯 These animations should show MUCH more visible movement!")
        print("• Arms swinging dramatically")
        print("• Legs stepping with clear motion")
        print("• Character walking forward through space")
        print("• Obvious joint rotations and body movement")
        
        print(f"\n🌐 View in web browser: http://localhost:8000/output/enhanced_test/")
        print(f"🎨 Or import to Blender for best visualization")
    
    else:
        print("\n❌ Enhanced animation creation failed")

if __name__ == "__main__":
    main()
