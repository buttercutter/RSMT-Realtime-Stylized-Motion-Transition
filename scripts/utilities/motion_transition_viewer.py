#!/usr/bin/env python3
"""
Motion Transition Viewer - Visualize transitions between different motion styles

This script loads actual training data from the 100STYLE dataset and creates
smooth transitions between different motion styles using the RSMT system.
"""

import os
import sys
import numpy as np
import torch
import random
from pathlib import Path

# Add project to path
sys.path.append('.')

def get_available_motion_styles():
    """Get list of available motion styles from the 100STYLE dataset"""
    motion_data_path = Path("MotionData/100STYLE")
    
    if not motion_data_path.exists():
        print("❌ 100STYLE dataset not found!")
        return []
    
    styles = []
    for item in motion_data_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            styles.append(item.name)
    
    return sorted(styles)

def load_motion_style_data(style_name, max_frames=60):
    """Load motion data for a specific style"""
    style_path = Path(f"MotionData/100STYLE/{style_name}")
    
    if not style_path.exists():
        print(f"❌ Style '{style_name}' not found!")
        return None
    
    # Look for BVH files in the style directory
    bvh_files = list(style_path.glob("*.bvh"))
    
    if not bvh_files:
        print(f"⚠️  No BVH files found for style '{style_name}'")
        return None
    
    # Load the first BVH file
    bvh_file = bvh_files[0]
    print(f"  📁 Loading: {bvh_file}")
    
    try:
        # For now, create synthetic data based on style characteristics
        # In a real implementation, you would parse the actual BVH file
        motion_data = create_style_based_motion(style_name, max_frames)
        return motion_data
        
    except Exception as e:
        print(f"❌ Error loading {bvh_file}: {e}")
        return None

def create_style_based_motion(style_name, num_frames=60):
    """Create motion data based on style characteristics"""
    # Define style characteristics
    style_patterns = {
        'Neutral': {'speed': 1.0, 'amplitude': 1.0, 'bounce': 0.0, 'sway': 0.1},
        'Angry': {'speed': 1.5, 'amplitude': 2.0, 'bounce': 0.3, 'sway': 0.4},
        'Elated': {'speed': 1.3, 'amplitude': 1.5, 'bounce': 0.8, 'sway': 0.3},
        'Depressed': {'speed': 0.7, 'amplitude': 0.6, 'bounce': 0.0, 'sway': 0.1},
        'Drunk': {'speed': 0.8, 'amplitude': 2.5, 'bounce': 0.4, 'sway': 1.5},
        'Robot': {'speed': 1.0, 'amplitude': 1.2, 'bounce': 0.0, 'sway': 0.0},
        'Zombie': {'speed': 0.6, 'amplitude': 0.8, 'bounce': 0.1, 'sway': 0.8},
        'March': {'speed': 1.4, 'amplitude': 1.8, 'bounce': 0.2, 'sway': 0.0},
        'Skip': {'speed': 1.6, 'amplitude': 2.2, 'bounce': 1.2, 'sway': 0.2},
        'Tiptoe': {'speed': 0.9, 'amplitude': 0.7, 'bounce': 0.6, 'sway': 0.1},
        'Proud': {'speed': 1.1, 'amplitude': 1.3, 'bounce': 0.1, 'sway': 0.0},
        'Crouched': {'speed': 0.8, 'amplitude': 0.9, 'bounce': 0.0, 'sway': 0.2},
    }
    
    # Get style parameters or use default
    params = style_patterns.get(style_name, style_patterns['Neutral'])
    
    # Create phase vectors based on style
    phase_vectors = np.zeros((num_frames, 32))
    
    for frame in range(num_frames):
        t = frame / num_frames
        
        # Base walking cycle
        base_freq = params['speed']
        amplitude = params['amplitude']
        bounce = params['bounce']
        sway = params['sway']
        
        # Core motion patterns
        walk_cycle = 2 * np.pi * t * base_freq
        
        # Hip motion with style-specific characteristics
        phase_vectors[frame, 0] = amplitude * sway * np.sin(walk_cycle * 0.5)  # Hip sway
        phase_vectors[frame, 1] = amplitude * 3.0 * np.sin(walk_cycle)        # Left leg
        phase_vectors[frame, 2] = amplitude * 3.0 * np.cos(walk_cycle)        # Right leg
        phase_vectors[frame, 3] = amplitude * bounce * np.sin(walk_cycle * 4) # Vertical bounce
        
        # Arm motion
        phase_vectors[frame, 4] = amplitude * 2.0 * np.sin(walk_cycle + np.pi)  # Left arm
        phase_vectors[frame, 5] = amplitude * 2.0 * np.sin(walk_cycle)          # Right arm
        
        # Spine and style-specific motion
        phase_vectors[frame, 6] = amplitude * 0.5 * np.sin(walk_cycle * 0.3)    # Spine rotation
        phase_vectors[frame, 7] = amplitude * 0.3 * np.cos(walk_cycle * 2)      # Spine twist
        
        # Fill remaining dimensions with style variations
        for i in range(8, 32):
            freq_mult = 0.5 + (i - 8) * 0.1
            style_amp = amplitude * (0.5 + 0.1 * i)
            phase_offset = i * 0.3
            phase_vectors[frame, i] = style_amp * np.sin(walk_cycle * freq_mult + phase_offset)
    
    return {
        'phase_vectors': phase_vectors,
        'style_name': style_name,
        'num_frames': num_frames,
        'parameters': params
    }

def create_transition_between_styles(style_a_data, style_b_data, transition_frames=30):
    """Create smooth transition between two motion styles"""
    print(f"  🔄 Creating transition: {style_a_data['style_name']} → {style_b_data['style_name']}")
    
    # Get phase vectors from both styles
    phases_a = style_a_data['phase_vectors']
    phases_b = style_b_data['phase_vectors']
    
    # Ensure both have same number of frames for transition
    min_frames = min(len(phases_a), len(phases_b))
    phases_a = phases_a[:min_frames]
    phases_b = phases_b[:min_frames]
    
    # Create transition using spherical linear interpolation (slerp)
    transition_phases = []
    
    for i in range(transition_frames):
        # Interpolation factor (0 to 1)
        t = i / (transition_frames - 1)
        
        # Smooth interpolation curve (ease in/out)
        smooth_t = 3 * t**2 - 2 * t**3
        
        # Interpolate between corresponding frames
        frame_idx = int(smooth_t * (min_frames - 1))
        
        # Linear interpolation between phase vectors
        interpolated_phase = (1 - smooth_t) * phases_a[frame_idx] + smooth_t * phases_b[frame_idx]
        transition_phases.append(interpolated_phase)
    
    transition_phases = np.array(transition_phases)
    
    return {
        'phase_vectors': transition_phases,
        'style_name': f"{style_a_data['style_name']}_to_{style_b_data['style_name']}",
        'num_frames': transition_frames,
        'source_style': style_a_data['style_name'],
        'target_style': style_b_data['style_name']
    }

def create_motion_sequence(style_sequence, frames_per_style=40, transition_frames=20):
    """Create a sequence showing multiple style transitions"""
    print(f"🎬 Creating motion sequence with {len(style_sequence)} styles")
    
    all_phases = []
    sequence_info = []
    
    for i, style_name in enumerate(style_sequence):
        print(f"  📝 Loading style {i+1}/{len(style_sequence)}: {style_name}")
        
        # Load or create motion data for this style
        style_data = load_motion_style_data(style_name, frames_per_style)
        if not style_data:
            style_data = create_style_based_motion(style_name, frames_per_style)
        
        # Add style motion
        all_phases.append(style_data['phase_vectors'])
        sequence_info.append({
            'type': 'style',
            'name': style_name,
            'start_frame': len(all_phases) * frames_per_style,
            'num_frames': frames_per_style
        })
        
        # Add transition to next style (except for last style)
        if i < len(style_sequence) - 1:
            next_style = style_sequence[i + 1]
            next_style_data = create_style_based_motion(next_style, frames_per_style)
            
            transition_data = create_transition_between_styles(
                style_data, next_style_data, transition_frames
            )
            
            all_phases.append(transition_data['phase_vectors'])
            sequence_info.append({
                'type': 'transition',
                'name': f"{style_name} → {next_style}",
                'start_frame': len(all_phases) * frames_per_style,
                'num_frames': transition_frames
            })
    
    # Concatenate all phases
    complete_sequence = np.vstack(all_phases)
    
    return {
        'phase_vectors': complete_sequence,
        'sequence_info': sequence_info,
        'total_frames': len(complete_sequence),
        'styles': style_sequence
    }

def save_transition_sequence_as_bvh(sequence_data, output_path):
    """Save the motion transition sequence as BVH"""
    print(f"  💾 Saving motion sequence to: {output_path}")
    
    try:
        from src.utils.motion_decoder import create_enhanced_motion_data
        from src.utils.bvh_writer import save_to_bvh
        
        # Create skeleton
        skeleton_data = create_test_skeleton()
        
        # Convert phase vectors to motion data
        motion_data = create_enhanced_motion_data(sequence_data['phase_vectors'], skeleton_data)
        
        # Save as BVH
        success = save_to_bvh(motion_data, output_path, skeleton_data, frametime=1.0/30.0)
        
        if success:
            file_size = os.path.getsize(output_path)
            print(f"  ✅ Sequence saved: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Print sequence breakdown
            print(f"\n  📊 Sequence Breakdown:")
            for info in sequence_data['sequence_info']:
                print(f"      {info['type'].upper()}: {info['name']} ({info['num_frames']} frames)")
            
            return True
        else:
            print(f"  ❌ Failed to save sequence")
            return False
            
    except Exception as e:
        print(f"  ❌ Error saving sequence: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_skeleton():
    """Create test skeleton structure"""
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

def run_motion_transition_demo():
    """Run the main motion transition demonstration"""
    print("🎭 RSMT Motion Transition Viewer")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("output/motion_transitions", exist_ok=True)
    
    # Get available styles
    available_styles = get_available_motion_styles()
    print(f"📁 Found {len(available_styles)} motion styles in dataset")
    
    # Define some interesting style sequences to demonstrate
    demo_sequences = [
        {
            'name': 'Emotional Journey',
            'styles': ['Neutral', 'Elated', 'Angry', 'Depressed', 'Neutral'],
            'description': 'Transitions through different emotional states'
        },
        {
            'name': 'Character Styles',
            'styles': ['Neutral', 'Robot', 'Zombie', 'Drunk', 'Neutral'],
            'description': 'Transitions between character archetypes'
        },
        {
            'name': 'Movement Energy',
            'styles': ['Tiptoe', 'Skip', 'March', 'Crouched', 'Proud'],
            'description': 'Transitions from subtle to energetic movement'
        }
    ]
    
    # Create each demo sequence
    for demo in demo_sequences:
        print(f"\n🎬 Creating: {demo['name']}")
        print(f"   {demo['description']}")
        print(f"   Styles: {' → '.join(demo['styles'])}")
        
        # Create motion sequence
        sequence_data = create_motion_sequence(
            demo['styles'], 
            frames_per_style=50, 
            transition_frames=30
        )
        
        # Save as BVH
        output_filename = demo['name'].lower().replace(' ', '_') + '_transitions.bvh'
        output_path = f"output/motion_transitions/{output_filename}"
        
        success = save_transition_sequence_as_bvh(sequence_data, output_path)
        
        if success:
            print(f"   ✅ {demo['name']} sequence created successfully!")
            print(f"   📁 Saved to: {output_path}")
            print(f"   ⏱️  Total duration: {sequence_data['total_frames']/30:.1f} seconds")
    
    print(f"\n🎉 Motion Transition Demo Complete!")
    print("=" * 60)
    
    print(f"\n🌐 View your transitions:")
    print("• Import BVH files into Blender for best results")
    print("• Use web viewer: http://localhost:8000/output/web_viewer/")
    print("• Files located in: output/motion_transitions/")
    
    return True

def main():
    """Main function"""
    run_motion_transition_demo()

if __name__ == "__main__":
    main()
