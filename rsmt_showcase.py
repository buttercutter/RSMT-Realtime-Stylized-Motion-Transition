#!/usr/bin/env python3
"""
RSMT Showcase Demo

Generate a special showcase animation demonstrating different motion styles.
"""

import torch
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

# Add source to path
sys.path.append('src')
sys.path.append('.')

def create_showcase_animation():
    """Create a showcase animation with multiple style transitions"""
    print("🎭 Creating RSMT Showcase Animation...")
    
    os.makedirs("output/showcase", exist_ok=True)
    
    try:
        # Import required modules
        from src.geometry.quaternions import euler_to_quaternion, quaternion_to_matrix
        from src.utils.motion_decoder import create_motion_data
        from src.utils.bvh_writer import write_bvh
        
        # Generate a longer, more varied animation
        num_frames = 120  # 4 seconds at 30fps
        num_joints = 22
        
        print(f"  📝 Generating {num_frames} frames for {num_joints} joints...")
        
        # Create more sophisticated phase vectors with style transitions
        phase_vectors = np.zeros((num_frames, 32))
        
        for frame in range(num_frames):
            t = frame / num_frames
            
            # Create multiple motion phases with transitions
            if t < 0.25:  # Walking phase
                phase_base = create_walking_phase(frame, 0.25)
            elif t < 0.5:  # Transition to running
                mix_factor = (t - 0.25) * 4  # 0 to 1
                walk_phase = create_walking_phase(frame, 0.25)
                run_phase = create_running_phase(frame, 0.25)
                phase_base = walk_phase * (1 - mix_factor) + run_phase * mix_factor
            elif t < 0.75:  # Running phase
                phase_base = create_running_phase(frame, 0.5)
            else:  # Transition to dancing
                mix_factor = (t - 0.75) * 4  # 0 to 1
                run_phase = create_running_phase(frame, 0.75)
                dance_phase = create_dancing_phase(frame, 0.75)
                phase_base = run_phase * (1 - mix_factor) + dance_phase * mix_factor
            
            # Add some style variations
            style_vector = create_style_variations(frame, num_frames)
            
            # Combine base motion with style
            phase_vectors[frame] = np.concatenate([phase_base, style_vector])
        
        print("  🎯 Converting phase vectors to motion data...")
        
        # Create skeleton data
        skeleton_data = create_enhanced_skeleton()
        
        # Convert to motion using the motion decoder
        motion_data = create_motion_data(
            torch.tensor(phase_vectors, dtype=torch.float32),
            skeleton_data
        )
        
        print("  💾 Saving showcase animation to BVH...")
        
        # Save to BVH
        output_path = "./output/showcase/rsmt_showcase.bvh"
        success = write_bvh(motion_data, output_path, skeleton_data, fps=30)
        
        if success:
            print(f"  ✅ Showcase animation saved: {output_path}")
            
            # Create visualization of the phase vectors
            create_phase_visualization(phase_vectors, "output/showcase/showcase_phases.png")
            
            return output_path
        else:
            print("  ❌ Failed to save showcase animation")
            return None
            
    except Exception as e:
        print(f"  ❌ Error creating showcase: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_walking_phase(frame, offset):
    """Create a walking motion phase"""
    t = (frame + offset * 30) * 0.2  # Walking frequency
    
    phase = np.zeros(16)
    phase[0] = 0.5 + 0.3 * np.sin(t)  # Hip sway
    phase[1] = np.sin(t * 2)  # Leg alternation
    phase[2] = np.cos(t * 2)  # Opposite leg
    phase[3] = 0.2 * np.sin(t * 4)  # Minor vertical motion
    phase[4] = 0.1 * np.sin(t + np.pi)  # Arm swing left
    phase[5] = 0.1 * np.sin(t)  # Arm swing right
    phase[6] = 0.05 * np.sin(t * 3)  # Torso rotation
    
    # Add some randomness for variation
    phase[7:] = 0.05 * np.random.randn(9)
    
    return phase

def create_running_phase(frame, offset):
    """Create a running motion phase"""
    t = (frame + offset * 30) * 0.4  # Faster frequency
    
    phase = np.zeros(16)
    phase[0] = 0.7 + 0.4 * np.sin(t)  # More pronounced hip movement
    phase[1] = 1.2 * np.sin(t * 2)  # Stronger leg alternation
    phase[2] = 1.2 * np.cos(t * 2)  # Stronger opposite leg
    phase[3] = 0.4 * np.sin(t * 4)  # More vertical motion
    phase[4] = 0.2 * np.sin(t + np.pi)  # Stronger arm swing
    phase[5] = 0.2 * np.sin(t)  # Stronger arm swing
    phase[6] = 0.1 * np.sin(t * 3)  # More torso rotation
    
    # Running-specific movements
    phase[7] = 0.3 * np.sin(t * 2)  # Knee lift
    phase[8] = 0.2 * np.cos(t * 2 + np.pi)  # Opposite knee
    
    return phase

def create_dancing_phase(frame, offset):
    """Create a dancing motion phase"""
    t = (frame + offset * 30) * 0.6  # Different rhythm
    
    phase = np.zeros(16)
    phase[0] = 0.3 + 0.2 * np.sin(t * 1.5)  # Rhythmic hip movement
    phase[1] = 0.5 * np.sin(t * 0.75)  # Slower, more graceful leg movement
    phase[2] = 0.5 * np.cos(t * 0.75)  # Coordinated leg movement
    phase[3] = 0.3 * np.sin(t * 2.5)  # Bouncing motion
    phase[4] = 0.4 * np.sin(t * 1.25 + np.pi/4)  # Expressive arm movement
    phase[5] = 0.4 * np.sin(t * 1.25 - np.pi/4)  # Coordinated arms
    phase[6] = 0.2 * np.sin(t * 0.5)  # Smooth torso movement
    
    # Dance-specific movements
    phase[7] = 0.3 * np.sin(t * 1.5 + np.pi/3)  # Head movement
    phase[8] = 0.2 * np.cos(t * 2)  # Shoulder movement
    phase[9] = 0.15 * np.sin(t * 3)  # Hand gestures
    
    return phase

def create_style_variations(frame, total_frames):
    """Create style variation vectors"""
    t = frame / total_frames
    
    style = np.zeros(16)
    
    # Overall energy level (builds up over time)
    style[0] = min(1.0, t * 2)
    
    # Smoothness vs sharpness
    style[1] = 0.5 + 0.3 * np.sin(t * np.pi * 2)
    
    # Amplitude scaling
    style[2] = 0.8 + 0.2 * np.cos(t * np.pi * 3)
    
    # Timing variations
    style[3] = 0.1 * np.sin(t * np.pi * 5)
    
    # Character personality traits
    style[4] = 0.3  # Confidence
    style[5] = 0.7  # Fluidity
    style[6] = 0.5  # Expressiveness
    
    return style

def create_enhanced_skeleton():
    """Create enhanced skeleton data with proper hierarchy"""
    joint_names = [
        "Hips",           # 0
        "Spine",          # 1
        "Spine1",         # 2
        "Spine2",         # 3
        "Neck",           # 4
        "Head",           # 5
        "LeftShoulder",   # 6
        "LeftArm",        # 7
        "LeftForeArm",    # 8
        "LeftHand",       # 9
        "RightShoulder",  # 10
        "RightArm",       # 11
        "RightForeArm",   # 12
        "RightHand",      # 13
        "LeftUpLeg",      # 14
        "LeftLeg",        # 15
        "LeftFoot",       # 16
        "LeftToeBase",    # 17
        "RightUpLeg",     # 18
        "RightLeg",       # 19
        "RightFoot",      # 20
        "RightToeBase"    # 21
    ]
    
    # Parent indices (-1 for root)
    parents = [-1, 0, 1, 2, 3, 4, 3, 6, 7, 8, 3, 10, 11, 12, 0, 14, 15, 16, 0, 18, 19, 20]
    
    # Joint offsets (approximate human proportions)
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

def create_phase_visualization(phase_vectors, output_path):
    """Create visualization of phase vectors over time"""
    print("  📊 Creating phase vector visualization...")
    
    plt.figure(figsize=(15, 10))
    
    # Plot the first 16 phase components (motion components)
    plt.subplot(2, 1, 1)
    time_steps = np.arange(len(phase_vectors))
    
    for i in range(min(8, phase_vectors.shape[1])):
        plt.plot(time_steps, phase_vectors[:, i], label=f'Phase {i+1}', alpha=0.8)
    
    plt.title('RSMT Showcase - Motion Phase Components', fontsize=14, fontweight='bold')
    plt.xlabel('Frame')
    plt.ylabel('Phase Value')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Plot the style components
    plt.subplot(2, 1, 2)
    
    for i in range(16, min(24, phase_vectors.shape[1])):
        plt.plot(time_steps, phase_vectors[:, i], label=f'Style {i-15}', alpha=0.8)
    
    plt.title('RSMT Showcase - Style Components', fontsize=14, fontweight='bold')
    plt.xlabel('Frame')
    plt.ylabel('Style Value')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✅ Phase visualization saved: {output_path}")

def main():
    """Main function"""
    print("🎬 RSMT Showcase Demo Generator")
    print("=" * 50)
    
    # Create the showcase animation
    showcase_path = create_showcase_animation()
    
    if showcase_path:
        print("\n🎉 Showcase Animation Complete!")
        print("=" * 50)
        print(f"📁 Animation file: {showcase_path}")
        print("📊 Phase visualization: output/showcase/showcase_phases.png")
        
        print("\n🎭 Animation Features:")
        print("• 4 seconds of motion (120 frames)")
        print("• Walking → Running → Dancing transitions")
        print("• Dynamic style variations")
        print("• 22-joint humanoid skeleton")
        print("• Smooth motion transitions")
        
        print("\n🎯 How to View:")
        print("1. 🎨 Blender: Import the BVH file for best visualization")
        print("2. 🌐 Web viewer: http://localhost:8000/output/web_viewer/")
        print("3. 📈 Phase plots: Check the visualization PNG")
        
        # Analyze the file
        print("\n📊 File Analysis:")
        file_size = os.path.getsize(showcase_path)
        print(f"• File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"• Duration: 4.0 seconds")
        print(f"• Frame rate: 30 FPS")
        print(f"• Joint count: 22 joints")
    
    else:
        print("\n❌ Failed to create showcase animation")

if __name__ == "__main__":
    main()
