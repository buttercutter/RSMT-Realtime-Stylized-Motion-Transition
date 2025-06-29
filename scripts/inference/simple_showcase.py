#!/usr/bin/env python3
"""
Simple RSMT Showcase Demo

Create a demonstration animation using the existing tested pipeline.
"""

import os
import sys
import numpy as np
import torch
import matplotlib.pyplot as plt

def create_simple_showcase():
    """Create a simple showcase using the existing pipeline"""
    print("🎭 Creating Simple RSMT Showcase...")
    
    os.makedirs("output/simple_showcase", exist_ok=True)
    
    try:
        # Use the existing working test pipeline
        print("  🔄 Running enhanced pipeline test...")
        
        # Create enhanced synthetic phase vectors
        num_frames = 90  # 3 seconds
        phase_vectors = create_enhanced_phase_vectors(num_frames)
        
        # Save phase vector visualization
        create_phase_plot(phase_vectors, "output/simple_showcase/enhanced_phases.png")
        
        # Use existing motion decoder pipeline (from test_pipeline.py)
        sys.path.append('.')
        
        # Import the working pipeline components
        from src.utils.motion_decoder import create_motion_data
        from src.utils.bvh_writer import write_bvh
        
        # Create skeleton data (using the existing working format)
        skeleton_data = create_showcase_skeleton()
        
        print("  🎯 Converting to motion data...")
        
        # Convert phase vectors to motion
        motion_data = create_motion_data(
            torch.tensor(phase_vectors, dtype=torch.float32),
            skeleton_data
        )
        
        print("  💾 Saving showcase BVH...")
        
        # Save as BVH
        output_path = "./output/simple_showcase/enhanced_showcase.bvh"
        success = write_bvh(motion_data, output_path, skeleton_data, fps=30)
        
        if success:
            print(f"  ✅ Enhanced showcase saved: {output_path}")
            return output_path
        else:
            print("  ❌ Failed to save showcase")
            return None
            
    except Exception as e:
        print(f"  ❌ Error creating showcase: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_enhanced_phase_vectors(num_frames):
    """Create more sophisticated phase vectors"""
    print(f"  📝 Generating {num_frames} enhanced phase vectors...")
    
    phase_vectors = np.zeros((num_frames, 32))
    
    for frame in range(num_frames):
        t = frame / num_frames
        
        # Base walking motion with variations
        base_freq = 0.3
        
        # Primary motion components (first 16 dimensions)
        phase_vectors[frame, 0] = 0.5 + 0.4 * np.sin(2 * np.pi * t * base_freq * 4)  # Hip motion
        phase_vectors[frame, 1] = np.sin(2 * np.pi * t * base_freq * 8)  # Left leg
        phase_vectors[frame, 2] = np.cos(2 * np.pi * t * base_freq * 8)  # Right leg
        phase_vectors[frame, 3] = 0.3 * np.sin(2 * np.pi * t * base_freq * 16)  # Vertical bounce
        
        # Arm swinging
        phase_vectors[frame, 4] = 0.2 * np.sin(2 * np.pi * t * base_freq * 8 + np.pi)  # Left arm
        phase_vectors[frame, 5] = 0.2 * np.sin(2 * np.pi * t * base_freq * 8)  # Right arm
        
        # Torso and spine
        phase_vectors[frame, 6] = 0.1 * np.sin(2 * np.pi * t * base_freq * 6)  # Spine rotation
        phase_vectors[frame, 7] = 0.05 * np.cos(2 * np.pi * t * base_freq * 12)  # Spine twist
        
        # Secondary motions
        for i in range(8, 16):
            freq_mult = 1 + i * 0.5
            phase_vectors[frame, i] = 0.1 * np.sin(2 * np.pi * t * base_freq * freq_mult + i)
        
        # Style components (last 16 dimensions)
        # Add progressive style changes
        style_progress = t
        
        # Energy/intensity that builds up
        phase_vectors[frame, 16] = min(1.0, style_progress * 1.5)
        
        # Smoothness/sharpness variation
        phase_vectors[frame, 17] = 0.5 + 0.3 * np.sin(2 * np.pi * t * 2)
        
        # Amplitude variations
        phase_vectors[frame, 18] = 0.8 + 0.2 * np.cos(2 * np.pi * t * 3)
        
        # Rhythmic variations
        phase_vectors[frame, 19] = 0.5 + 0.2 * np.sin(2 * np.pi * t * 5)
        
        # Character traits
        phase_vectors[frame, 20] = 0.6  # Confidence
        phase_vectors[frame, 21] = 0.8  # Fluidity
        phase_vectors[frame, 22] = 0.4 + 0.3 * np.sin(2 * np.pi * t)  # Expressiveness
        
        # Add some controlled randomness for natural variation
        for i in range(23, 32):
            phase_vectors[frame, i] = 0.05 * np.sin(2 * np.pi * t * (i - 20) + frame * 0.1)
    
    return phase_vectors

def create_showcase_skeleton():
    """Create skeleton data for the showcase"""
    # Use the same structure as the working pipeline
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

def create_phase_plot(phase_vectors, output_path):
    """Create visualization of the enhanced phase vectors"""
    print(f"  📊 Creating phase visualization: {output_path}")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Enhanced RSMT Showcase - Phase Vector Analysis', fontsize=16, fontweight='bold')
    
    time_steps = np.arange(len(phase_vectors))
    
    # Plot 1: Primary motion components
    ax1 = axes[0, 0]
    for i in range(8):
        ax1.plot(time_steps, phase_vectors[:, i], 
                label=f'Motion {i+1}', alpha=0.8, linewidth=2)
    ax1.set_title('Primary Motion Components', fontweight='bold')
    ax1.set_xlabel('Frame')
    ax1.set_ylabel('Phase Value')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Secondary motion components
    ax2 = axes[0, 1]
    for i in range(8, 16):
        ax2.plot(time_steps, phase_vectors[:, i], 
                label=f'Secondary {i-7}', alpha=0.7, linewidth=1.5)
    ax2.set_title('Secondary Motion Components', fontweight='bold')
    ax2.set_xlabel('Frame')
    ax2.set_ylabel('Phase Value')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Style components
    ax3 = axes[1, 0]
    style_names = ['Energy', 'Smoothness', 'Amplitude', 'Rhythm', 'Confidence', 'Fluidity', 'Expression']
    for i, name in enumerate(style_names):
        if 16 + i < phase_vectors.shape[1]:
            ax3.plot(time_steps, phase_vectors[:, 16 + i], 
                    label=name, alpha=0.8, linewidth=2)
    ax3.set_title('Style Components', fontweight='bold')
    ax3.set_xlabel('Frame')
    ax3.set_ylabel('Style Value')
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Phase space visualization (2D projection)
    ax4 = axes[1, 1]
    # Project to 2D using first two principal components
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    phase_2d = pca.fit_transform(phase_vectors)
    
    # Color by time
    scatter = ax4.scatter(phase_2d[:, 0], phase_2d[:, 1], 
                         c=time_steps, cmap='viridis', alpha=0.7, s=30)
    
    # Add arrow to show progression
    for i in range(0, len(phase_2d) - 5, 5):
        ax4.annotate('', xy=phase_2d[i + 5], xytext=phase_2d[i],
                    arrowprops=dict(arrowstyle='->', alpha=0.5, color='red'))
    
    ax4.set_title('Phase Space Trajectory (PCA Projection)', fontweight='bold')
    ax4.set_xlabel('Principal Component 1')
    ax4.set_ylabel('Principal Component 2')
    plt.colorbar(scatter, ax=ax4, label='Frame')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def main():
    """Main function"""
    print("🎬 Simple RSMT Showcase Generator")
    print("=" * 50)
    
    try:
        # Install sklearn if needed for PCA
        import sklearn
    except ImportError:
        print("  📦 Installing scikit-learn for analysis...")
        os.system("pip install scikit-learn")
    
    # Create the showcase
    showcase_path = create_simple_showcase()
    
    if showcase_path:
        print("\n🎉 Simple Showcase Complete!")
        print("=" * 50)
        print(f"📁 Animation: {showcase_path}")
        print("📊 Visualization: output/simple_showcase/enhanced_phases.png")
        
        print("\n🎭 Features:")
        print("• 3 seconds of enhanced motion (90 frames)")
        print("• Complex phase vector patterns")
        print("• Style variations over time")
        print("• 22-joint skeleton animation")
        
        print("\n🎯 View Options:")
        print("1. 🎨 Blender: Import the BVH file")
        print("2. 🌐 Web viewer: http://localhost:8000/output/web_viewer/")
        print("3. 📈 Analysis: Check the phase visualization PNG")
        
        # File info
        if os.path.exists(showcase_path):
            file_size = os.path.getsize(showcase_path)
            print(f"\n📊 File: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    else:
        print("\n❌ Showcase creation failed")

if __name__ == "__main__":
    main()
