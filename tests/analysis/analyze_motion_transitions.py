#!/usr/bin/env python3
"""
Analyze Motion Transitions - Verify transition patterns in generated BVH files

This script analyzes the motion transition BVH files to verify they contain
the expected style transitions and motion patterns.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_bvh_motion_data(bvh_path):
    """Extract and analyze motion data from BVH file"""
    print(f"📊 Analyzing: {bvh_path}")
    
    try:
        with open(bvh_path, 'r') as f:
            lines = f.readlines()
        
        motion_data = []
        in_motion = False
        frame_time = 0.033333  # Default frame time
        
        for line in lines:
            line = line.strip()
            if line.startswith("Frame Time:"):
                frame_time = float(line.split(":")[1])
            elif line == "MOTION":
                in_motion = True
                continue
            elif in_motion and line and not line.startswith("Frame"):
                values = [float(x) for x in line.split()]
                motion_data.append(values)
        
        if not motion_data:
            print("  ❌ No motion data found!")
            return None
            
        motion_array = np.array(motion_data)
        print(f"  📏 Motion data shape: {motion_array.shape}")
        print(f"  ⏱️  Frame time: {frame_time:.6f} seconds")
        print(f"  🎬 Total duration: {len(motion_data) * frame_time:.2f} seconds")
        
        return {
            'data': motion_array,
            'frame_time': frame_time,
            'num_frames': len(motion_data),
            'num_channels': len(motion_data[0]) if motion_data else 0
        }
        
    except Exception as e:
        print(f"  ❌ Error analyzing {bvh_path}: {e}")
        return None

def analyze_motion_transitions(motion_data, sequence_name):
    """Analyze motion patterns to identify transitions"""
    print(f"\n🔍 Analyzing motion patterns for: {sequence_name}")
    
    data = motion_data['data']
    num_frames = motion_data['num_frames']
    
    # Calculate frame-to-frame differences
    frame_diffs = []
    for i in range(1, len(data)):
        diff = np.linalg.norm(data[i] - data[i-1])
        frame_diffs.append(diff)
    
    frame_diffs = np.array(frame_diffs)
    
    # Find significant motion changes (potential transitions)
    mean_diff = np.mean(frame_diffs)
    std_diff = np.std(frame_diffs)
    threshold = mean_diff + 1.5 * std_diff
    
    transition_frames = np.where(frame_diffs > threshold)[0]
    
    print(f"  📊 Motion Analysis:")
    print(f"      Average frame change: {mean_diff:.4f}")
    print(f"      Max frame change: {np.max(frame_diffs):.4f}")
    print(f"      Min frame change: {np.min(frame_diffs):.4f}")
    print(f"      Standard deviation: {std_diff:.4f}")
    print(f"      Transition threshold: {threshold:.4f}")
    print(f"      Detected transition points: {len(transition_frames)}")
    
    if len(transition_frames) > 0:
        print(f"      Transition frames: {transition_frames[:10]}{'...' if len(transition_frames) > 10 else ''}")
    
    # Analyze motion segments
    segments = analyze_motion_segments(data, frame_diffs)
    
    return {
        'frame_diffs': frame_diffs,
        'mean_diff': mean_diff,
        'max_diff': np.max(frame_diffs),
        'transition_frames': transition_frames,
        'segments': segments
    }

def analyze_motion_segments(data, frame_diffs, segment_size=50):
    """Analyze motion in segments to identify style periods"""
    print(f"  🎭 Analyzing motion segments...")
    
    num_segments = len(data) // segment_size
    segments = []
    
    for i in range(num_segments):
        start_idx = i * segment_size
        end_idx = min((i + 1) * segment_size, len(data))
        
        segment_data = data[start_idx:end_idx]
        segment_diffs = frame_diffs[start_idx:end_idx-1] if end_idx-1 < len(frame_diffs) else frame_diffs[start_idx:]
        
        # Calculate segment characteristics
        avg_motion = np.mean(segment_diffs) if len(segment_diffs) > 0 else 0
        motion_variance = np.var(segment_diffs) if len(segment_diffs) > 0 else 0
        
        # Analyze position spread
        position_data = segment_data[:, :3]  # Assume first 3 channels are position
        position_spread = np.std(position_data, axis=0)
        
        segments.append({
            'segment': i,
            'start_frame': start_idx,
            'end_frame': end_idx,
            'avg_motion': avg_motion,
            'motion_variance': motion_variance,
            'position_spread': position_spread,
            'characteristics': classify_motion_style(avg_motion, motion_variance)
        })
        
        print(f"      Segment {i:2d} (frames {start_idx:3d}-{end_idx:3d}): "
              f"motion={avg_motion:.3f}, variance={motion_variance:.3f}, "
              f"style={segments[-1]['characteristics']}")
    
    return segments

def classify_motion_style(avg_motion, motion_variance):
    """Classify motion style based on motion characteristics"""
    if avg_motion > 20.0 and motion_variance > 50.0:
        return "High Energy (Skip/Angry)"
    elif avg_motion > 15.0:
        return "Energetic (March/Elated)"
    elif avg_motion > 10.0:
        return "Moderate (Neutral/Robot)"
    elif avg_motion > 5.0:
        return "Subdued (Depressed/Crouched)"
    else:
        return "Minimal (Tiptoe)"

def create_motion_visualization(analysis_results, sequence_name, output_path):
    """Create visualization of motion patterns"""
    print(f"  📈 Creating motion visualization...")
    
    try:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Motion Analysis: {sequence_name}', fontsize=16, fontweight='bold')
        
        # Plot 1: Frame-to-frame differences
        axes[0, 0].plot(analysis_results['frame_diffs'], linewidth=1.5, color='#f093fb')
        axes[0, 0].axhline(y=analysis_results['mean_diff'], color='#4facfe', linestyle='--', 
                          label=f'Mean: {analysis_results["mean_diff"]:.2f}')
        axes[0, 0].set_title('Frame-to-Frame Motion Changes')
        axes[0, 0].set_xlabel('Frame')
        axes[0, 0].set_ylabel('Motion Magnitude')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Motion segments
        segments = analysis_results['segments']
        segment_motions = [s['avg_motion'] for s in segments]
        segment_numbers = [s['segment'] for s in segments]
        
        bars = axes[0, 1].bar(segment_numbers, segment_motions, color='#4facfe', alpha=0.7)
        axes[0, 1].set_title('Motion by Segment (50-frame windows)')
        axes[0, 1].set_xlabel('Segment')
        axes[0, 1].set_ylabel('Average Motion')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Color code bars based on motion level
        for i, bar in enumerate(bars):
            motion = segment_motions[i]
            if motion > 15:
                bar.set_color('#f093fb')  # High energy
            elif motion > 10:
                bar.set_color('#4facfe')  # Moderate
            else:
                bar.set_color('#00f2fe')  # Low energy
        
        # Plot 3: Motion variance
        segment_variances = [s['motion_variance'] for s in segments]
        axes[1, 0].plot(segment_numbers, segment_variances, marker='o', linewidth=2, 
                       markersize=6, color='#f5576c')
        axes[1, 0].set_title('Motion Variance by Segment')
        axes[1, 0].set_xlabel('Segment')
        axes[1, 0].set_ylabel('Motion Variance')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Histogram of frame differences
        axes[1, 1].hist(analysis_results['frame_diffs'], bins=50, color='#4facfe', alpha=0.7, edgecolor='black')
        axes[1, 1].axvline(x=analysis_results['mean_diff'], color='#f093fb', linestyle='--', linewidth=2,
                          label=f'Mean: {analysis_results["mean_diff"]:.2f}')
        axes[1, 1].set_title('Distribution of Frame Changes')
        axes[1, 1].set_xlabel('Motion Magnitude')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"      ✅ Visualization saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"      ❌ Error creating visualization: {e}")
        return False

def run_motion_transition_analysis():
    """Main function to analyze all motion transition files"""
    print("📊 RSMT Motion Transition Analysis")
    print("=" * 60)
    
    transition_dir = Path("output/motion_transitions")
    
    if not transition_dir.exists():
        print("❌ Motion transitions directory not found!")
        return
    
    # Create analysis output directory
    analysis_dir = Path("output/motion_analysis")
    analysis_dir.mkdir(exist_ok=True)
    
    # Find all BVH files
    bvh_files = list(transition_dir.glob("*.bvh"))
    
    if not bvh_files:
        print("❌ No BVH files found in motion_transitions directory!")
        return
    
    print(f"📁 Found {len(bvh_files)} transition files to analyze\n")
    
    all_results = {}
    
    for bvh_file in sorted(bvh_files):
        sequence_name = bvh_file.stem.replace('_transitions', '').replace('_', ' ').title()
        
        # Analyze motion data
        motion_data = analyze_bvh_motion_data(bvh_file)
        if not motion_data:
            continue
            
        # Analyze transitions
        analysis_results = analyze_motion_transitions(motion_data, sequence_name)
        
        # Create visualization
        viz_path = analysis_dir / f"{bvh_file.stem}_analysis.png"
        create_motion_visualization(analysis_results, sequence_name, viz_path)
        
        all_results[sequence_name] = analysis_results
        print()  # Add spacing
    
    # Create summary
    print("📋 ANALYSIS SUMMARY")
    print("=" * 60)
    
    for name, results in all_results.items():
        print(f"\n🎭 {name}:")
        print(f"   Average motion: {results['mean_diff']:.3f}")
        print(f"   Max motion: {results['max_diff']:.3f}")
        print(f"   Transitions detected: {len(results['transition_frames'])}")
        
        # Show segment characteristics
        segments = results['segments']
        styles = [s['characteristics'] for s in segments]
        unique_styles = list(set(styles))
        print(f"   Motion styles detected: {len(unique_styles)}")
        for style in unique_styles:
            count = styles.count(style)
            print(f"      {style}: {count} segments")
    
    print(f"\n🎉 Analysis complete! Results saved to: {analysis_dir}")
    print("📊 View the analysis visualizations:")
    for png_file in analysis_dir.glob("*.png"):
        print(f"   • {png_file}")

def main():
    """Main function"""
    run_motion_transition_analysis()

if __name__ == "__main__":
    main()
