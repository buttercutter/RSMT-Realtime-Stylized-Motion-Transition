#!/usr/bin/env python3
"""
Simple script to inspect phase vectors
"""

import os
import sys
import pickle
import numpy as np

def load_phases(phase_path):
    """
    Load generated phase data
    """
    print(f"Loading phase data from {phase_path}")
    
    try:
        with open(phase_path, 'rb') as f:
            phase_data = pickle.load(f)
        
        print(f"Loaded phase data for {len(phase_data)} styles")
        return phase_data
    
    except Exception as e:
        print(f"Error loading phase data: {e}")
        return None

def analyze_phases(phase_data):
    """
    Simple analysis of phase vectors
    """
    print("\nPhase data analysis:")
    print("--------------------")
    
    # List available styles
    styles = list(phase_data.keys())
    print(f"Available styles: {styles}")
    
    # Check structure of the data
    first_style = styles[0]
    style_data = phase_data[first_style]
    
    print(f"\nStructure of data for style '{first_style}':")
    for key, value in style_data.items():
        if hasattr(value, 'shape'):
            print(f"- {key}: shape={value.shape}, dtype={value.dtype}")
        else:
            print(f"- {key}: {value}")
    
    # Print details about phase vectors
    if 'phase' in style_data:
        phase = style_data['phase']
        print(f"\nPhase vector statistics:")
        print(f"- Shape: {phase.shape}")
        print(f"- Min: {np.min(phase):.4f}")
        print(f"- Max: {np.max(phase):.4f}")
        print(f"- Mean: {np.mean(phase):.4f}")
        print(f"- Std: {np.std(phase):.4f}")
        
        # Sample values from first frame
        print(f"\nSample phase vector (first frame): {phase[0]}")

def main():
    """
    Main function
    """
    # Output paths
    train_phases_path = "./output/phases/train_phases.dat"
    test_phases_path = "./output/phases/test_phases.dat"
    
    # Load and analyze train phases
    print("\n=== TRAINING PHASE DATA ===\n")
    train_phases = load_phases(train_phases_path)
    if train_phases:
        analyze_phases(train_phases)
    
    # Load and analyze test phases
    print("\n=== TEST PHASE DATA ===\n")
    test_phases = load_phases(test_phases_path)
    if test_phases:
        analyze_phases(test_phases)

if __name__ == "__main__":
    main()
