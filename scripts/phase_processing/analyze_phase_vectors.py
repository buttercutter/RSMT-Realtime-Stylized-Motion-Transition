#!/usr/bin/env python3
"""
Analyze and visualize phase vectors in more detail
"""

import os
import sys
import torch
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import argparse

def load_phases(phase_path):
    """
    Load generated phase data
    """
    print(f"Loading phase data from {phase_path}")
    
    try:
        # Check file existence
        if not os.path.exists(phase_path):
            print(f"File not found: {phase_path}")
            return None
        
        print(f"File exists, size: {os.path.getsize(phase_path)} bytes")
        
        # Open and load pickle data
        with open(phase_path, 'rb') as f:
            phase_data = pickle.load(f)
        
        # Log details about loaded data
        print(f"Loaded phase data for {len(phase_data)} styles")
        
        # Print details about first style
        if len(phase_data) > 0:
            first_style = list(phase_data.keys())[0]
            first_data = phase_data[first_style]
            print(f"First style: {first_style}")
            print(f"Keys in first style data: {list(first_data.keys())}")
            
            if 'phase' in first_data:
                phase = first_data['phase']
                print(f"Phase shape: {phase.shape if hasattr(phase, 'shape') else 'unknown'}")
        
        return phase_data
    
    except Exception as e:
        print(f"Error loading phase data: {e}")
        import traceback
        traceback.print_exc()
        return None

def visualize_with_pca(phase_data, output_path, top_n_styles=None):
    """
    Visualize phase space using PCA with more detailed visualization
    """
    print("Visualizing phase space with PCA...")
    
    # Extract styles and phases
    styles = []
    phases = []
    style_names = []
    
    if top_n_styles:
        # Sort styles by number of frames if we want to limit visualization
        style_counts = {style: len(data['phase']) for style, data in phase_data.items()}
        top_styles = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[:top_n_styles]
        top_style_names = [s[0] for s in top_styles]
    else:
        top_style_names = list(phase_data.keys())
    
    # Extract data for selected styles
    for style_name in top_style_names:
        if style_name in phase_data:
            data = phase_data[style_name]
            phase = data['phase']
            phases.append(phase)
            style_names.append(style_name)
            styles.extend([style_name] * len(phase))
    
    # Convert to numpy array
    phases = np.vstack(phases)
    
    # Use PCA for dimensionality reduction
    pca = PCA(n_components=2)
    phases_2d = pca.fit_transform(phases)
    
    # Calculate explained variance
    explained_variance = pca.explained_variance_ratio_
    print(f"Explained variance by component: {explained_variance}")
    print(f"Total explained variance: {sum(explained_variance):.4f}")
    
    # Plot the results
    plt.figure(figsize=(14, 10))
    
    # Get unique styles
    unique_styles = sorted(set(styles))
    
    # Create a colormap with distinct colors
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_styles)))
    color_dict = dict(zip(unique_styles, colors))
    
    # Plot each style with a different color
    for style in unique_styles:
        mask = [s == style for s in styles]
        plt.scatter(
            phases_2d[mask, 0], 
            phases_2d[mask, 1], 
            c=[color_dict[style]], 
            label=style if len(unique_styles) <= 20 else None,  # Only show legend if not too many styles
            alpha=0.7,
            s=20
        )
    
    plt.title(f"Phase Space (PCA) - Explained Variance: {sum(explained_variance):.2f}")
    plt.xlabel(f"Component 1 ({explained_variance[0]:.2f})")
    plt.ylabel(f"Component 2 ({explained_variance[1]:.2f})")
    
    # Add legend if not too many styles
    if len(unique_styles) <= 20:
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path)
    print(f"PCA visualization saved to {output_path}")

def visualize_with_tsne(phase_data, output_path, top_n_styles=None):
    """
    Visualize phase space using t-SNE
    """
    print("Visualizing phase space with t-SNE...")
    
    # Extract styles and phases
    styles = []
    phases = []
    style_names = []
    
    if top_n_styles:
        # Sort styles by number of frames if we want to limit visualization
        style_counts = {style: len(data['phase']) for style, data in phase_data.items()}
        top_styles = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[:top_n_styles]
        top_style_names = [s[0] for s in top_styles]
    else:
        top_style_names = list(phase_data.keys())
    
    # Extract data for selected styles
    for style_name in top_style_names:
        if style_name in phase_data:
            data = phase_data[style_name]
            phase = data['phase']
            phases.append(phase)
            style_names.append(style_name)
            styles.extend([style_name] * len(phase))
    
    # Convert to numpy array
    phases = np.vstack(phases)
    
    # Use t-SNE for dimensionality reduction
    tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
    phases_2d = tsne.fit_transform(phases)
    
    # Plot the results
    plt.figure(figsize=(14, 10))
    
    # Get unique styles
    unique_styles = sorted(set(styles))
    
    # Create a colormap with distinct colors
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_styles)))
    color_dict = dict(zip(unique_styles, colors))
    
    # Plot each style with a different color
    for style in unique_styles:
        mask = [s == style for s in styles]
        plt.scatter(
            phases_2d[mask, 0], 
            phases_2d[mask, 1], 
            c=[color_dict[style]], 
            label=style if len(unique_styles) <= 20 else None,  # Only show legend if not too many styles
            alpha=0.7,
            s=20
        )
    
    plt.title("Phase Space (t-SNE)")
    plt.xlabel("t-SNE Component 1")
    plt.ylabel("t-SNE Component 2")
    
    # Add legend if not too many styles
    if len(unique_styles) <= 20:
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path)
    print(f"t-SNE visualization saved to {output_path}")

def analyze_phase_components(phase_data, output_path):
    """
    Analyze phase vector components
    """
    print("Analyzing phase components...")
    
    # Extract all phase vectors
    all_phases = []
    
    for style_name, data in phase_data.items():
        phase = data['phase']
        all_phases.append(phase)
    
    # Convert to numpy array
    all_phases = np.vstack(all_phases)
    
    # Calculate statistics
    mean_phase = np.mean(all_phases, axis=0)
    std_phase = np.std(all_phases, axis=0)
    min_phase = np.min(all_phases, axis=0)
    max_phase = np.max(all_phases, axis=0)
    
    # Plot component statistics
    plt.figure(figsize=(16, 12))
    
    # Component means
    plt.subplot(2, 2, 1)
    plt.bar(range(len(mean_phase)), mean_phase)
    plt.title("Component Mean Values")
    plt.xlabel("Component Index")
    plt.ylabel("Mean Value")
    
    # Component standard deviations
    plt.subplot(2, 2, 2)
    plt.bar(range(len(std_phase)), std_phase)
    plt.title("Component Standard Deviations")
    plt.xlabel("Component Index")
    plt.ylabel("Standard Deviation")
    
    # Component ranges
    plt.subplot(2, 2, 3)
    plt.bar(range(len(max_phase)), max_phase - min_phase)
    plt.title("Component Ranges (Max - Min)")
    plt.xlabel("Component Index")
    plt.ylabel("Range")
    
    # Component distributions
    plt.subplot(2, 2, 4)
    
    # Plot distribution for a few selected components
    for i in range(min(5, all_phases.shape[1])):
        plt.hist(all_phases[:, i], bins=30, alpha=0.5, label=f"Component {i}")
    
    plt.title("Component Value Distributions")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path)
    print(f"Component analysis saved to {output_path}")

def compare_styles(phase_data, output_path, styles_to_compare=None):
    """
    Compare phase vectors between different styles
    """
    print("Comparing styles...")
    
    # If no styles specified, select a few interesting ones
    if styles_to_compare is None or len(styles_to_compare) < 2:
        all_styles = list(phase_data.keys())
        styles_to_compare = all_styles[:min(5, len(all_styles))]
    
    # Extract phase data for selected styles
    style_phases = {}
    available_styles = []
    
    # Check which of our requested styles are available
    for style_name in styles_to_compare:
        if style_name in phase_data:
            available_styles.append(style_name)
            data = phase_data[style_name]
            phase = data['phase']
            style_phases[style_name] = phase
    
    # Make sure we have at least 2 styles to compare
    if len(style_phases) < 2:
        print(f"Not enough styles found for comparison. Available styles: {list(phase_data.keys())[:5]}...")
        print(f"Requested: {styles_to_compare}")
        print(f"Available: {available_styles}")
        return
    
    # Use PCA to reduce dimensions
    all_phases = np.vstack([p for p in style_phases.values()])
    pca = PCA(n_components=2)
    all_phases_2d = pca.fit_transform(all_phases)
    
    # Split back into individual styles
    offset = 0
    style_phases_2d = {}
    
    for style_name, phase in style_phases.items():
        style_phases_2d[style_name] = all_phases_2d[offset:offset + len(phase)]
        offset += len(phase)
    
    # Plot comparison
    plt.figure(figsize=(14, 10))
    
    # Generate distinct colors
    colors = plt.cm.rainbow(np.linspace(0, 1, len(styles_to_compare)))
    
    # Plot each style
    for i, (style_name, phase_2d) in enumerate(style_phases_2d.items()):
        plt.scatter(
            phase_2d[:, 0],
            phase_2d[:, 1],
            c=[colors[i]],
            label=style_name,
            alpha=0.7,
            s=30
        )
        
        # Calculate and plot the mean point
        mean_x = np.mean(phase_2d[:, 0])
        mean_y = np.mean(phase_2d[:, 1])
        
        plt.scatter(
            [mean_x],
            [mean_y],
            c=[colors[i]],
            s=200,
            marker='*',
            edgecolors='black'
        )
        
        # Add a text label
        plt.annotate(
            style_name,
            xy=(mean_x, mean_y),
            xytext=(10, 10),
            textcoords='offset points',
            fontsize=12,
            fontweight='bold'
        )
    
    plt.title("Style Comparison in Phase Space")
    plt.xlabel(f"PCA Component 1 ({pca.explained_variance_ratio_[0]:.2f})")
    plt.ylabel(f"PCA Component 2 ({pca.explained_variance_ratio_[1]:.2f})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path)
    print(f"Style comparison saved to {output_path}")

def main(args):
    """
    Main function for phase analysis
    """
    try:
        print(f"Creating output directory: {args.output_dir}")
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        print(f"Loading phase data from {args.train_phases} and {args.test_phases}")
        # Load phase data
        train_phases = load_phases(args.train_phases)
        test_phases = load_phases(args.test_phases)
        
        print(f"Phase data loaded: train_phases={train_phases is not None}, test_phases={test_phases is not None}")
    except Exception as e:
        print(f"Error in main setup: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if train_phases:
        # PCA visualization
        visualize_with_pca(
            train_phases, 
            os.path.join(args.output_dir, 'train_phases_pca.png'),
            top_n_styles=args.top_n
        )
        
        # t-SNE visualization
        visualize_with_tsne(
            train_phases, 
            os.path.join(args.output_dir, 'train_phases_tsne.png'),
            top_n_styles=args.top_n
        )
        
        # Component analysis
        analyze_phase_components(
            train_phases,
            os.path.join(args.output_dir, 'train_phase_components.png')
        )
        
        # Style comparison
        if args.compare:
            compare_styles(
                train_phases,
                os.path.join(args.output_dir, 'train_style_comparison.png'),
                styles_to_compare=args.compare.split(',')
            )
    
    if test_phases:
        # PCA visualization
        visualize_with_pca(
            test_phases, 
            os.path.join(args.output_dir, 'test_phases_pca.png'),
            top_n_styles=args.top_n
        )
        
        # t-SNE visualization
        visualize_with_tsne(
            test_phases, 
            os.path.join(args.output_dir, 'test_phases_tsne.png'),
            top_n_styles=args.top_n
        )
        
        # Style comparison
        if args.compare:
            compare_styles(
                test_phases,
                os.path.join(args.output_dir, 'test_style_comparison.png'),
                styles_to_compare=args.compare.split(',')
            )
    
    print("Analysis complete!")

if __name__ == "__main__":
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Analyze phase vectors")
        
        parser.add_argument("--train-phases", type=str, default="./output/phases/train_phases.dat",
                            help="Path to the training phase data")
        parser.add_argument("--test-phases", type=str, default="./output/phases/test_phases.dat",
                            help="Path to the test phase data")
        parser.add_argument("--output-dir", type=str, default="./output/phase_analysis",
                            help="Directory to save analysis results")
        parser.add_argument("--top-n", type=int, default=None,
                            help="Limit visualization to top N styles by frame count")
        parser.add_argument("--compare", type=str, default=None,
                            help="Comma-separated list of styles to compare")
        
        args = parser.parse_args()
        
        # Add debug prints
        print("Starting analysis...")
        print(f"Train phases path: {args.train_phases}")
        print(f"Test phases path: {args.test_phases}")
        print(f"Output directory: {args.output_dir}")
        
        main(args)
        
    except Exception as e:
        import traceback
        print(f"Error in main script: {e}")
        traceback.print_exc()
