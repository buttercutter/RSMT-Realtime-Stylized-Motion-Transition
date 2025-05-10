"""
BVH Writer - Saves motion data to BVH format

This module provides utilities to save motion data (quaternions and positions)
to BVH format files for use in animation software.
"""

import numpy as np
import os
import sys

# Try different import approaches for BVH_mod
try:
    from src.utils import BVH_mod
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    try:
        from src.utils import BVH_mod
        print("Imported BVH_mod using relative path")
    except ImportError:
        print("ERROR: Could not import BVH_mod")
        raise

# Import quaternion utilities
try:
    from src.utils.np_vector import quat_to_euler
    print("Imported quat_to_euler from np_vector")
except ImportError:
    # Provide a fallback implementation if needed
    def quat_to_euler(quat):
        """
        Convert quaternion to Euler angles (ZYX convention)
        Simple implementation for fallback
        """
        print("Using fallback quat_to_euler implementation")
        # Extract quaternion components
        w, x, y, z = quat[..., 0], quat[..., 1], quat[..., 2], quat[..., 3]
        
        # Convert to Euler angles (ZYX order)
        # Formulas from: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
        
        # Roll (X-axis rotation)
        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)
        
        # Pitch (Y-axis rotation)
        sinp = 2.0 * (w * y - z * x)
        pitch = np.where(
            np.abs(sinp) >= 1.0,
            np.sign(sinp) * np.pi / 2.0,  # Use 90 degrees if out of range
            np.arcsin(sinp)
        )
        
        # Yaw (Z-axis rotation)
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        
        # Combine into output array
        euler = np.stack([roll, pitch, yaw], axis=-1)
        return euler


def save_to_bvh(motion_data, output_path, skeleton_data=None, frametime=1.0/30.0):
    """
    Save motion data to a BVH file
    
    Args:
        motion_data: Dictionary with motion data (from decode_phase_to_motion)
        output_path: Path where to save the BVH file
        skeleton_data: Optional skeleton data (if None, will use default)
        frametime: Frame time in seconds (default: 1/30 = 30fps)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Extract data from the motion_data dictionary
        local_rotations = motion_data.get("local_rotations")
        hip_positions = motion_data.get("hip_positions", None)
        
        # Check if we have the necessary data
        if local_rotations is None:
            print("Error: No rotation data provided.")
            return False
        
        # If hip positions aren't provided, use zeros
        if hip_positions is None:
            hip_positions = np.zeros((local_rotations.shape[0], 1, 3))
        elif hip_positions.shape[1] > 1:
            # Extract just the hip position (first joint)
            hip_positions = hip_positions[:, 0:1, :]
        
        # Ensure hip_positions has the right shape
        if len(hip_positions.shape) == 2:
            hip_positions = hip_positions[:, np.newaxis, :]
        
        # Use default skeleton if none is provided
        if skeleton_data is None:
            # Default skeleton structure
            num_joints = local_rotations.shape[1]
            offsets = np.zeros((num_joints, 3))
            parents = [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21][:num_joints]
            names = ["Hips", "LeftHip", "LeftKnee", "LeftAnkle", "LeftToe",
                     "RightHip", "RightKnee", "RightAnkle", "RightToe",
                     "Chest", "Chest2", "Chest3", "Chest4", "Neck", "Head",
                     "LeftCollar", "LeftShoulder", "LeftElbow", "LeftWrist",
                     "RightCollar", "RightShoulder", "RightElbow", "RightWrist"][:num_joints]
        else:
            offsets = skeleton_data["offsets"]
            parents = skeleton_data["parents"]
            names = skeleton_data.get("names", [f"joint_{i}" for i in range(len(parents))])
        
        # Create an Anim object
        anim = BVH_mod.Anim(
            quats=local_rotations,
            pos=hip_positions.reshape(hip_positions.shape[0], 3),  # Reshape to (N, 3)
            offsets=offsets,
            parents=parents,
            names=names
        )
        
        # Save to BVH file
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        BVH_mod.save_bvh(output_path, anim, frametime=frametime)
        
        print(f"BVH file saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error saving BVH file: {e}")
        import traceback
        traceback.print_exc()
        return False
