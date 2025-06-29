
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

print("Starting BVH to binary conversion...")
try:
    from src.Datasets.Style100Processor import bvh_to_binary
    bvh_to_binary()
    print("BVH to binary conversion complete!")
except Exception as e:
    print(f"Error during BVH conversion: {e}")
    import traceback
    traceback.print_exc()
