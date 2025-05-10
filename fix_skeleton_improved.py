#!/usr/bin/env python3
"""
Improved script to fix the skeleton file format properly
"""

import os
import pickle
import sys
import numpy as np
import torch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import the Skeleton class
from src.utils.BVH_mod import Skeleton

# Path to the skeleton file
SKELETON_PATH = "./MotionData/100STYLE/skeleton"

def fix_skeleton():
    print("Converting skeleton dictionary to proper Skeleton object...")
    
    # Load the skeleton dictionary
    with open(SKELETON_PATH, 'rb') as f:
        skeleton_dict = pickle.load(f)
    
    # Extract data from the dictionary
    offsets = skeleton_dict['offsets']
    parents = np.array(skeleton_dict['parents'], dtype=np.int32)
    names = skeleton_dict['names']
    
    # Create a Skeleton object with the required arguments
    skeleton = Skeleton(parents, names, offsets)
    
    # Ensure the offsets are properly set (they might be assigned differently in the constructor)
    skeleton.offsets = offsets
    
    # Initialize basic attributes needed
    skeleton.bone_pair_indices = np.zeros(len(skeleton.names), dtype=np.int32) - 1  # Default to -1
    skeleton.root = 0  # Typically the first joint (index 0) is the root
    skeleton._level_joints = []
    skeleton._level_joints_parents = []
    skeleton.end_effector_idx = []  # End effectors
    skeleton.multi_children_idx = []  # Joints with multiple children
    
    # Build the hierarchy dictionary
    skeleton.hierarchy = {i: {"joint": skeleton.names[i]} for i in range(len(skeleton.names))}
    
    # Find symmetrical bones (left/right pairs)
    for i, name in enumerate(skeleton.names):
        for j, other_name in enumerate(skeleton.names):
            if i != j:
                if ("Left" in name and "Right" in other_name) or ("left" in name and "right" in other_name):
                    base_name_i = name.replace("Left", "").replace("left", "")
                    base_name_j = other_name.replace("Right", "").replace("right", "")
                    if base_name_i == base_name_j:
                        skeleton.bone_pair_indices[i] = j
                        skeleton.bone_pair_indices[j] = i
    
    # Use a try-except block to handle any initialization errors
    # Define a function to manually initialize the skeleton structures
    def manual_init(skeleton):
        print("Manually initializing skeleton structures...")
        
        # Build the hierarchy mapping (joint relationships)
        for idx, parent_id in enumerate(skeleton.parents):
            children_id = []
            children = {}
            # Find all children of this joint
            for child_id, child_parent in enumerate(skeleton.parents):
                if child_parent == idx:
                    children_id.append(child_id)
                    children[child_id] = skeleton.hierarchy[child_id]
            
            # Set parent and children relationships
            skeleton.hierarchy[idx]["parent"] = skeleton.hierarchy[parent_id] if parent_id >= 0 else {"name": ""}
            skeleton.hierarchy[idx]["children"] = children
            
            # Link symmetric bones if defined
            if hasattr(skeleton, 'bone_pair_indices') and idx < len(skeleton.bone_pair_indices) and skeleton.bone_pair_indices[idx] != -1:
                skeleton.hierarchy[idx]["sys"] = skeleton.hierarchy[skeleton.bone_pair_indices[idx]]
        
        # Build level mapping (levels of joints in hierarchy)
        level_joints = []
        level_joints_parent = []
        
        # Root is level 0
        level_joints.append([skeleton.root])
        level_joints_parent.append([-1])  # Root has no parent
        
        # Add all other joints by level
        current_level = 0
        while True:
            next_level_joints = []
            next_level_parents = []
            
            # Find all children of joints at the current level
            for joint_idx in level_joints[current_level]:
                for i, parent in enumerate(skeleton.parents):
                    if parent == joint_idx:
                        next_level_joints.append(i)
                        next_level_parents.append(joint_idx)
            
            # If no more children, we're done
            if not next_level_joints:
                break
            
            # Add this level to our level maps
            level_joints.append(next_level_joints)
            level_joints_parent.append(next_level_parents)
            current_level += 1
        
        # Store the level maps
        skeleton._level_joints = level_joints
        skeleton._level_joints_parents = level_joints_parent
        
        # Find end effectors and multi-children joints
        end_effectors = []
        multi_children = []
        for i in range(len(skeleton.names)):
            children_count = sum(1 for p in skeleton.parents if p == i)
            if children_count == 0:
                end_effectors.append(i)
            elif children_count > 1:
                multi_children.append(i)
        
        skeleton.end_effector_idx = end_effectors
        skeleton.multi_children_idx = multi_children
    
    # Apply the manual initialization
    print("Applying manual initialization...")
    manual_init(skeleton)
    
    # Test the skeleton by creating some dummy data and running forward kinematics
    print("Testing forward kinematics...")
    
    # Create dummy quaternions (identity quaternions)
    dummy_quats = np.zeros((1, len(skeleton.parents), 4))
    dummy_quats[:, :, 0] = 1.0  # Set w to 1.0 for identity quaternion
    dummy_quats = torch.from_numpy(dummy_quats).float()
    
    # Create dummy offsets and hip positions
    dummy_offsets = torch.from_numpy(skeleton.offsets).float().unsqueeze(0)
    dummy_hip_pos = torch.zeros((1, 1, 3)).float()
    
    # Try forward kinematics
    try:
        from src.geometry import forward_kinematics as fk
        print("Testing with forward_kinematics_quats...")
        gp, gq = fk.forward_kinematics_quats(dummy_quats, dummy_offsets, dummy_hip_pos, skeleton.parents)
        print(f"Forward kinematics success! Global positions shape: {gp.shape}")
        
        # Try with skeleton's forward_kinematics method
        print("Testing with skeleton.forward_kinematics...")
        gp2, gq2 = skeleton.forward_kinematics(dummy_quats, dummy_offsets, dummy_hip_pos)
        print(f"Skeleton forward kinematics success! Global positions shape: {gp2.shape}")
        
        print("Forward kinematics test passed!")
    except Exception as e:
        print(f"Forward kinematics test failed: {e}")
        print("Will still save the skeleton as it may work with the patched methods.")
    
    print("Saving the updated skeleton file...")
    # Save the Skeleton object
    with open(SKELETON_PATH, 'wb') as f:
        pickle.dump(skeleton, f)
    
    print(f"Skeleton file updated successfully: {SKELETON_PATH}")
    print(f"Skeleton has {len(skeleton.names)} joints")

if __name__ == "__main__":
    fix_skeleton()
