# Run just the bvh_to_binary function
import sys
import os
sys.path.append(os.getcwd())
from src.Datasets.Style100Processor import bvh_to_binary, save_skeleton

print("Converting BVH files to binary...")
bvh_to_binary()
print("Saving skeleton...")
save_skeleton()
print("Done!")
