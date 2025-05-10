#!/usr/bin/env python3
"""
Fixed versions of forward and inverse kinematics functions that handle
dimension issues and provide better compatibility across different PyTorch versions.
"""

import torch
import numpy as np
from typing import List, Tuple, Union, Any

# First try to import from pytorch3d if available
try:
    from pytorch3d.transforms import quaternion_multiply, quaternion_apply
    print("Using installed PyTorch3D transforms")
except ImportError:
    # Fall back to our own implementations
    print("Using fallback quaternion implementations")
    def quaternion_apply(quaternion, point):
        """
        Apply the rotation given by a quaternion to a point.
        """
        # Ensure quaternion has the right shape
        if quaternion.shape[-1] != 4:
            raise ValueError(f"Expected quaternion to have shape [..., 4], got {quaternion.shape}")
        
        # Ensure point has the right shape
        if point.shape[-1] != 3:
            raise ValueError(f"Expected point to have shape [..., 3], got {point.shape}")
            
        # q_real is the scalar part (w), q_imag is the vector part (x, y, z)
        q = quaternion.unsqueeze(-2)  # Add dimension for points
        q_real = q[..., 0]
        q_imag = q[..., 1:]
        
        # Apply quaternion rotation: q * p * q^-1
        real_vec_cross = torch.cross(q_imag, point, dim=-1)
        real_vec = point * q_real.unsqueeze(-1)
        vector = 2.0 * real_vec_cross + point + 2.0 * torch.cross(q_imag, real_vec_cross, dim=-1)
        
        return vector

    def quaternion_multiply(q1, q2):
        """
        Multiply quaternions q1 and q2.
        """
        # Ensure quaternions have the right shape
        if q1.shape[-1] != 4 or q2.shape[-1] != 4:
            raise ValueError(f"Expected quaternions with shape [..., 4], got {q1.shape} and {q2.shape}")
            
        # Extract components
        w1, x1, y1, z1 = q1[..., 0], q1[..., 1], q1[..., 2], q1[..., 3]
        w2, x2, y2, z2 = q2[..., 0], q2[..., 1], q2[..., 2], q2[..., 3]
        
        # Compute the quaternion product
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
        z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
        
        # Stack the components to form the result
        quat = torch.stack([w, x, y, z], dim=-1)
        return quat

def normalize_dimensions(local_rotations, local_offsets, hip_positions):
    """
    Normalize the dimensions of the inputs to ensure they're compatible for forward kinematics.
    
    Args:
        local_rotations: Tensor of shape [..., J, 4] (quaternions)
        local_offsets: Tensor of shape [..., J, 3] (offsets)
        hip_positions: Tensor of shape [..., 3] or [..., 1, 3] (hip positions)
        
    Returns:
        local_rotations: Normalized tensor [B, T, J, 4]
        local_offsets: Normalized tensor [B, T, J, 3]
        hip_positions: Normalized tensor [B, T, 1, 3]
        batch_dims: List of batch dimensions
    """
    # Get the batch dimensions
    batch_dims = list(local_rotations.shape[:-2])
    
    # Ensure at least 2D batch dimensions (batch, time)
    if len(batch_dims) < 2:
        if len(local_rotations.shape) == 2:  # [J, 4]
            local_rotations = local_rotations.unsqueeze(0).unsqueeze(0)  # [1, 1, J, 4]
            batch_dims = [1, 1]
        elif len(local_rotations.shape) == 3:  # [B or T, J, 4]
            local_rotations = local_rotations.unsqueeze(1 if local_rotations.shape[0] > 1 else 0)
            batch_dims = [local_rotations.shape[0], local_rotations.shape[1]]
    
    # Handle local_offsets dimensions
    if len(local_offsets.shape) < 4:
        if len(local_offsets.shape) == 2:  # [J, 3]
            # Expand to match batch dims
            local_offsets = local_offsets.unsqueeze(0).unsqueeze(0).expand(batch_dims[0], batch_dims[1], -1, -1)
        elif len(local_offsets.shape) == 3:  # [B or T, J, 3]
            if local_offsets.shape[0] == batch_dims[0]:
                # Assume it's [B, J, 3], add time dimension
                local_offsets = local_offsets.unsqueeze(1).expand(-1, batch_dims[1], -1, -1)
            else:
                # Assume it's [1, J, 3] or [T, J, 3]
                local_offsets = local_offsets.unsqueeze(0).expand(batch_dims[0], -1, -1, -1)
    
    # Handle hip_positions dimensions
    if len(hip_positions.shape) < 4:
        if len(hip_positions.shape) == 1:  # [3]
            hip_positions = hip_positions.unsqueeze(0).unsqueeze(0).unsqueeze(0)  # [1, 1, 1, 3]
        elif len(hip_positions.shape) == 2:
            if hip_positions.shape[0] == 1:  # [1, 3]
                hip_positions = hip_positions.unsqueeze(0).unsqueeze(0)  # [1, 1, 1, 3]
            else:  # [B, 3] or [T, 3]
                hip_positions = hip_positions.unsqueeze(1).unsqueeze(1)  # [B, 1, 1, 3] or [T, 1, 1, 3]
        elif len(hip_positions.shape) == 3:  # [B, T, 3]
            hip_positions = hip_positions.unsqueeze(2)  # [B, T, 1, 3]
    
    return local_rotations, local_offsets, hip_positions, batch_dims

def fixed_forward_kinematics(local_rotations, local_offsets, hip_positions, parents):
    """
    Fixed version of forward_kinematics_quats that handles dimension issues properly.
    
    Args:
        local_rotations: Local rotations as quaternions [B, T, J, 4]
        local_offsets: Local offsets [B, T, J, 3] or [J, 3]
        hip_positions: Hip positions [B, T, 3] or [B, T, 1, 3]
        parents: List or array of parent indices
        
    Returns:
        global_positions: Global joint positions [B, T, J, 3]
        global_quats: Global joint rotations as quaternions [B, T, J, 4]
    """
    # Normalize dimensions
    local_rotations, local_offsets, hip_positions, batch_dims = normalize_dimensions(
        local_rotations, local_offsets, hip_positions)
    
    # Extract key dimensions
    batch_size, seq_len = batch_dims
    num_joints = local_rotations.shape[-2]
    
    # Initialize global rotations and positions
    global_quats = [local_rotations[..., :1, :]]  # Root rotation is the same as local
    global_positions = [hip_positions]  # Root position is the hip position
    
    # Process joints in hierarchy order
    for i in range(1, num_joints):
        parent = parents[i]
        
        # Get parent quaternion and position
        parent_quat = global_quats[parent]
        parent_pos = global_positions[parent]
        
        # Get local offset and quaternion for this joint
        local_offset = local_offsets[..., i:i+1, :]
        local_quat = local_rotations[..., i:i+1, :]
        
        # Apply parent rotation to the offset to get the offset in global space
        offset_global = quaternion_apply(parent_quat, local_offset)
        
        # Add parent position to get global position
        joint_pos = parent_pos + offset_global
        
        # Combine parent and local rotations to get global rotation
        joint_quat = quaternion_multiply(parent_quat, local_quat)
        
        # Store global position and rotation
        global_positions.append(joint_pos)
        global_quats.append(joint_quat)
    
    # Concatenate all joints
    global_positions = torch.cat(global_positions, dim=-2)
    global_quats = torch.cat(global_quats, dim=-2)
    
    return global_positions, global_quats

# Alias for compatibility
forward_kinematics_quats_fixed = fixed_forward_kinematics

if __name__ == "__main__":
    # Test the functions with dummy data
    print("Testing fixed kinematics functions...")
    
    # Create dummy data
    batch_size = 2
    seq_len = 10
    num_joints = 23
    
    # Create identity quaternions for all joints
    dummy_quats = torch.zeros((batch_size, seq_len, num_joints, 4))
    dummy_quats[..., 0] = 1.0  # Identity quaternion
    
    # Create some random offsets
    dummy_offsets = torch.randn((num_joints, 3))
    
    # Create a hip position
    dummy_hip = torch.zeros((batch_size, seq_len, 3))
    
    # Define a parent hierarchy
    dummy_parents = [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21]
    
    # Run forward kinematics
    print("Running fixed forward kinematics...")
    global_pos, global_rot = fixed_forward_kinematics(
        dummy_quats, dummy_offsets, dummy_hip, dummy_parents)
    
    # Print the results
    print(f"Input dimensions:")
    print(f"- Local quaternions: {dummy_quats.shape}")
    print(f"- Local offsets: {dummy_offsets.shape}")
    print(f"- Hip positions: {dummy_hip.shape}")
    print(f"Output dimensions:")
    print(f"- Global positions: {global_pos.shape}")
    print(f"- Global rotations: {global_rot.shape}")
    
    print("Test complete!")
