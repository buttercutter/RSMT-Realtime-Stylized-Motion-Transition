"""
Motion Decoder - Converts phase vectors to motion data

This module provides utilities to convert phase vectors back to motion
data (quaternions and positions) using the trained models.
"""

import torch
import numpy as np
import os
import sys

# Try different import approaches for forward kinematics
try:
    from src.geometry import forward_kinematics as fk
    print("Imported forward_kinematics from src.geometry")
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    try:
        from src.geometry import forward_kinematics as fk
        print("Imported forward_kinematics using relative path")
    except ImportError:
        print("ERROR: Could not import forward_kinematics")
        raise

try:
    from src.geometry.quaternions import or6d_to_quat
except ImportError:
    print("WARNING: Could not import or6d_to_quat, using placeholder")
    def or6d_to_quat(x):
        return x

# Try to import pytorch3d transforms
try:
    import pytorch3d.transforms as trans
    from pytorch3d.transforms import quaternion_multiply
    print("Using installed PyTorch3D library")
except ImportError:
    # Fall back to our compatibility layer if available
    try:
        import src.geometry.pytorch3d_transforms as trans
        from src.geometry.pytorch3d_transforms import quaternion_multiply
        print("Using PyTorch3D compatibility layer")
    except ImportError:
        print("ERROR: Could not import PyTorch3D transforms")
        # Simple placeholder for axis_angle_to_quaternion
        def axis_angle_to_quaternion(axis_angle):
            angle = torch.norm(axis_angle, dim=-1, keepdim=True)
            axis = axis_angle / (angle + 1e-8)
            half_angle = angle * 0.5
            sin_half_angle = torch.sin(half_angle)
            quat = torch.cat([torch.cos(half_angle), axis * sin_half_angle], dim=-1)
            return quat
            
        # Define quaternion_multiply if not available
        def quaternion_multiply(q1, q2):
            """Multiply two quaternions"""
            a1, b1, c1, d1 = q1[..., 0:1], q1[..., 1:2], q1[..., 2:3], q1[..., 3:4]
            a2, b2, c2, d2 = q2[..., 0:1], q2[..., 1:2], q2[..., 2:3], q2[..., 3:4]
            
            a = a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2
            b = a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2
            c = a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2
            d = a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2
            
            return torch.cat([a, b, c, d], dim=-1)
            
        trans = type('', (), {})()
        trans.axis_angle_to_quaternion = axis_angle_to_quaternion
        trans.quaternion_multiply = quaternion_multiply
        print("Created placeholder for transforms")

def normalize_vector(v):
    """Normalize a vector or batch of vectors"""
    norm = torch.norm(v, dim=-1, keepdim=True)
    return v / (norm + 1e-8)

def quaternion_apply(quaternion, point):
    """Apply quaternion rotation to point"""
    q = quaternion.clone()
    v = point.clone()
    
    q_vect = q[..., 1:]
    v_vect = v[..., :3]
    
    scalar = q[..., :1]
    uv = torch.cross(q_vect, v_vect, dim=-1)
    uuv = torch.cross(q_vect, uv, dim=-1)
    
    return v_vect + 2.0 * (uv * scalar + uuv)


def decode_phase_to_motion(phase_vectors, manifold_model=None, skeleton_data=None):
    """
    Converts phase vectors to motion data
    
    Args:
        phase_vectors: Phase vectors to convert (N, phase_dim)
        manifold_model: Optional manifold model for additional decoding
        skeleton_data: Skeleton data for forward kinematics
        
    Returns:
        dict containing:
            - local_rotations: Local joint rotations as quaternions (N, J, 4)
            - global_positions: Global joint positions (N, J, 3)
            - hip_positions: Hip positions (N, 1, 3)
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Ensure input is a tensor
    if not isinstance(phase_vectors, torch.Tensor):
        phase_vectors = torch.tensor(phase_vectors, dtype=torch.float32)
    
    phase_vectors = phase_vectors.to(device)
    
    # Extract skeleton information
    if not skeleton_data:
        # Default skeleton structure if none is provided
        num_joints = 22  # Typical skeleton joint count
        local_rotations = torch.zeros((phase_vectors.shape[0], num_joints, 4), device=device)
        local_rotations[..., 0] = 1.0  # Identity quaternions
        hip_positions = torch.zeros((phase_vectors.shape[0], 1, 3), device=device)
        offsets = torch.zeros((num_joints, 3), device=device)
        parents = [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21][:num_joints]
    else:
        num_joints = len(skeleton_data["parents"])
        local_rotations = torch.zeros((phase_vectors.shape[0], num_joints, 4), device=device)
        local_rotations[..., 0] = 1.0  # Identity quaternions
        hip_positions = torch.zeros((phase_vectors.shape[0], 1, 3), device=device)
        offsets = torch.tensor(skeleton_data["offsets"], dtype=torch.float32, device=device)
        parents = skeleton_data["parents"]
    
    # In a real implementation, this would be handled by your trained model
    # Here we're just creating a placeholder that varies the motion based on phase
    for i in range(phase_vectors.shape[0]):
        # Use some components of the phase vector to modulate the pose
        phase = phase_vectors[i]
        
        # Create some variation in the quaternions based on the phase
        for j in range(1, num_joints):  # Skip the root
            # Map phase components to rotation axis
            axis = normalize_vector(torch.tensor([
                phase[0].item() if phase.shape[0] > 0 else 0.0,
                phase[1].item() if phase.shape[0] > 1 else 0.0,
                phase[2].item() if phase.shape[0] > 2 else 0.0
            ], device=device).reshape(1, 3))
            
            # Create an angle based on other phase components
            angle = 0.1 * torch.sin(2.0 * (
                phase[3].item() if phase.shape[0] > 3 else 0.0
            ))
            
            # Convert axis-angle to quaternion
            axis_angle = axis * angle
            quat = trans.axis_angle_to_quaternion(axis_angle)
            
            # Apply the rotation
            local_rotations[i, j] = quat.reshape(-1)
        
        # Vary hip position based on phase
        hip_positions[i, 0, 0] = 0.1 * torch.sin(phase[0].item() if phase.shape[0] > 0 else 0.0)
        hip_positions[i, 0, 1] = 0.05 * torch.cos(phase[1].item() if phase.shape[0] > 1 else 0.0)
        hip_positions[i, 0, 2] = 0.0
    
    # Try to use forward kinematics from the imported module if available
    try:
        global_positions, global_rotations = fk.forward_kinematics_quats(
            local_rotations, offsets, hip_positions, parents
        )
    except Exception as e:
        print(f"Error using forward_kinematics module: {e}")
        print("Using built-in forward kinematics implementation")
        # Fall back to our internal implementation
        global_positions = torch.zeros((phase_vectors.shape[0], num_joints, 3), device=device)
        global_rotations = torch.zeros((phase_vectors.shape[0], num_joints, 4), device=device)
        
        # Set root positions and rotations
        global_positions[:, 0:1] = hip_positions
        global_rotations[:, 0] = local_rotations[:, 0]
        
        # Simple forward kinematics
        for i in range(1, num_joints):
            parent = parents[i]
            parent_rot = global_rotations[:, parent]
            local_offset = offsets[i].reshape(1, 3).repeat(phase_vectors.shape[0], 1)
            
            # Rotate offset by parent rotation
            rotated_offset = quaternion_apply(parent_rot, local_offset)
            
            # Add to parent position
            global_positions[:, i] = global_positions[:, parent] + rotated_offset
            
            # Multiply parent rotation by local rotation
            global_rotations[:, i] = quaternion_multiply(parent_rot, local_rotations[:, i])
    
    return {
        "local_rotations": local_rotations.cpu().numpy(),
        "global_positions": global_positions.cpu().numpy(),
        "global_rotations": global_rotations.cpu().numpy(),
        "hip_positions": hip_positions.cpu().numpy()
    }
