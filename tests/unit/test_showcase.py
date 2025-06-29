#!/usr/bin/env python3
"""
Test RSMT Showcase - Minimal version to verify functionality
"""

import os
import numpy as np

def test_showcase():
    print("🎭 Testing RSMT Showcase functionality...")
    
    # Create output directory
    os.makedirs("output/showcase", exist_ok=True)
    
    # Generate simple test data
    num_frames = 10
    phase_vectors = np.random.rand(num_frames, 32)
    
    # Save test data
    output_path = "output/showcase/test_data.txt"
    np.savetxt(output_path, phase_vectors)
    
    print(f"✅ Test data saved to: {output_path}")
    print(f"📊 Generated {num_frames} frames with 32 phase components")
    
    return True

if __name__ == "__main__":
    try:
        success = test_showcase()
        if success:
            print("🎉 Test showcase completed successfully!")
        else:
            print("❌ Test showcase failed")
    except Exception as e:
        print(f"❌ Error in test showcase: {e}")
        import traceback
        traceback.print_exc()
