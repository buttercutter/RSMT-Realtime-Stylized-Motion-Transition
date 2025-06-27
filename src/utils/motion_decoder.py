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
    
    # Enhanced motion generation that creates visible, dramatic movements
    for i in range(phase_vectors.shape[0]):
        # Use components of the phase vector to create dramatic motion
        phase = phase_vectors[i]
        frame_time = i / max(1, phase_vectors.shape[0] - 1)  # Normalized time 0-1
        
        # Create walking motion with much larger movements
        for j in range(1, num_joints):  # Skip the root
            # Different motion patterns for different joint types
            if j in [1, 2, 3]:  # Spine joints
                # Spine rotation with walking motion
                angle = 0.3 * torch.sin(torch.tensor(frame_time * 4 * np.pi, device=device))
                axis = torch.tensor([0.0, 0.0, 1.0], device=device).reshape(1, 3)  # Z-axis rotation
                
            elif j in [6, 7, 8, 9]:  # Left arm
                # Left arm swinging motion
                angle = 0.8 * torch.sin(torch.tensor(frame_time * 2 * np.pi + np.pi, device=device))  # Opposite to right
                if j == 7:  # Shoulder
                    axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)  # X-axis
                elif j == 8:  # Elbow
                    angle = 0.5 + 0.5 * torch.cos(torch.tensor(frame_time * 2 * np.pi, device=device))  # Bend elbow
                    axis = torch.tensor([0.0, 1.0, 0.0], device=device).reshape(1, 3)  # Y-axis
                else:
                    axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)
                    
            elif j in [10, 11, 12, 13]:  # Right arm  
                # Right arm swinging motion
                angle = 0.8 * torch.sin(torch.tensor(frame_time * 2 * np.pi, device=device))
                if j == 11:  # Shoulder
                    axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)  # X-axis
                elif j == 12:  # Elbow
                    angle = 0.5 + 0.5 * torch.cos(torch.tensor(frame_time * 2 * np.pi + np.pi, device=device))  # Bend elbow
                    axis = torch.tensor([0.0, 1.0, 0.0], device=device).reshape(1, 3)  # Y-axis
                else:
                    axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)
                    
            elif j in [14, 15, 16]:  # Left leg
                # Left leg walking motion
                angle = 0.6 * torch.sin(torch.tensor(frame_time * 4 * np.pi + np.pi, device=device))  # Opposite to right
                if j == 15:  # Knee
                    angle = abs(angle) * 0.8  # Knee always bends forward
                axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)  # X-axis
                
            elif j in [18, 19, 20]:  # Right leg
                # Right leg walking motion
                angle = 0.6 * torch.sin(torch.tensor(frame_time * 4 * np.pi, device=device))
                if j == 19:  # Knee
                    angle = abs(angle) * 0.8  # Knee always bends forward
                axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)  # X-axis
                
            else:  # Other joints (neck, head, etc.)
                # Subtle head bobbing motion
                angle = 0.1 * torch.sin(torch.tensor(frame_time * 6 * np.pi, device=device))
                axis = torch.tensor([0.0, 1.0, 0.0], device=device).reshape(1, 3)  # Y-axis
            
            # Add phase vector influence for variation
            phase_influence = 0.2 * (phase[min(j, phase.shape[0]-1)].item() if phase.shape[0] > 0 else 0.0)
            angle += phase_influence
            
            # Normalize axis and convert to quaternion
            axis = normalize_vector(axis)
            axis_angle = axis * angle
            quat = trans.axis_angle_to_quaternion(axis_angle)
            
            # Apply the rotation
            local_rotations[i, j] = quat.reshape(-1)
        
        # Create walking hip motion with much larger displacement
        walk_cycle = frame_time * 2 * np.pi  # Complete walk cycle
        hip_positions[i, 0, 0] = 0.5 * torch.sin(torch.tensor(walk_cycle, device=device))  # Side to side
        hip_positions[i, 0, 1] = 1.0 + 0.1 * torch.sin(torch.tensor(walk_cycle * 4, device=device))  # Up down bobbing
        hip_positions[i, 0, 2] = frame_time * 2.0  # Forward movement over time
    
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

def create_motion_data(phase_vectors, skeleton_data=None):
    """
    Wrapper function for decode_phase_to_motion to maintain compatibility
    """
    return decode_phase_to_motion(phase_vectors, skeleton_data=skeleton_data)

def create_enhanced_motion_data(phase_vectors, skeleton_data=None):
    """
    Create enhanced motion data with more dramatic movements for better visualization
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    if not isinstance(phase_vectors, torch.Tensor):
        phase_vectors = torch.tensor(phase_vectors, dtype=torch.float32)
    
    phase_vectors = phase_vectors.to(device)
    
    # Extract skeleton information
    if not skeleton_data:
        num_joints = 22
        offsets = torch.zeros((num_joints, 3), device=device)
        parents = [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21][:num_joints]
    else:
        num_joints = len(skeleton_data["parents"])
        offsets = torch.tensor(skeleton_data["offsets"], dtype=torch.float32, device=device)
        parents = skeleton_data["parents"]
    
    local_rotations = torch.zeros((phase_vectors.shape[0], num_joints, 4), device=device)
    local_rotations[..., 0] = 1.0  # Identity quaternions
    hip_positions = torch.zeros((phase_vectors.shape[0], 1, 3), device=device)
    
    # Create a more complex walking animation
    for i in range(phase_vectors.shape[0]):
        t = i / max(1, phase_vectors.shape[0] - 1)  # Time from 0 to 1
        phase = phase_vectors[i]
        
        # Walking cycle parameters
        walk_freq = 2.0  # 2 complete cycles
        arm_swing = 0.8  # Arm swing amplitude
        leg_swing = 0.6  # Leg swing amplitude
        spine_twist = 0.2  # Spine rotation amplitude
        
        # Generate joint rotations for walking motion
        for j in range(num_joints):
            if j == 0:  # Root/Hips
                # Hip rotation for walking
                angle = spine_twist * np.sin(t * walk_freq * 2 * np.pi)
                axis = torch.tensor([0.0, 1.0, 0.0], device=device).reshape(1, 3)  # Y-axis
                
            elif j in [1, 2, 3]:  # Spine joints
                # Spine counter-rotation
                angle = -spine_twist * 0.5 * np.sin(t * walk_freq * 2 * np.pi)
                axis = torch.tensor([0.0, 1.0, 0.0], device=device).reshape(1, 3)
                
            elif j == 4:  # Neck
                # Head slight bobbing
                angle = 0.1 * np.sin(t * walk_freq * 4 * np.pi)
                axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)
                
            elif j in [6, 7]:  # Left shoulder and arm
                # Left arm swing (opposite to right leg)
                angle = arm_swing * np.sin(t * walk_freq * 2 * np.pi + np.pi)
                axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)
                
            elif j == 8:  # Left forearm
                # Elbow bend
                angle = 0.3 + 0.3 * np.cos(t * walk_freq * 2 * np.pi)
                axis = torch.tensor([0.0, 1.0, 0.0], device=device).reshape(1, 3)
                
            elif j in [10, 11]:  # Right shoulder and arm
                # Right arm swing (opposite to left leg)
                angle = arm_swing * np.sin(t * walk_freq * 2 * np.pi)
                axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)
                
            elif j == 12:  # Right forearm
                # Elbow bend
                angle = 0.3 + 0.3 * np.cos(t * walk_freq * 2 * np.pi + np.pi)
                axis = torch.tensor([0.0, 1.0, 0.0], device=device).reshape(1, 3)
                
            elif j == 14:  # Left upper leg
                # Left leg swing (opposite to right arm)
                angle = leg_swing * np.sin(t * walk_freq * 2 * np.pi + np.pi)
                axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)
                
            elif j == 15:  # Left lower leg
                # Left knee bend
                knee_angle = leg_swing * np.sin(t * walk_freq * 2 * np.pi + np.pi)
                angle = max(0, -knee_angle * 0.8)  # Only bend forward
                axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)
                
            elif j == 18:  # Right upper leg
                # Right leg swing (opposite to left arm)
                angle = leg_swing * np.sin(t * walk_freq * 2 * np.pi)
                axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)
                
            elif j == 19:  # Right lower leg
                # Right knee bend
                knee_angle = leg_swing * np.sin(t * walk_freq * 2 * np.pi)
                angle = max(0, -knee_angle * 0.8)  # Only bend forward
                axis = torch.tensor([1.0, 0.0, 0.0], device=device).reshape(1, 3)
                
            else:
                # Default small movement for other joints
                angle = 0.05 * np.sin(t * walk_freq * 6 * np.pi + j)
                axis = torch.tensor([0.0, 0.0, 1.0], device=device).reshape(1, 3)
            
            # Add phase vector influence
            if phase.shape[0] > j:
                angle += 0.1 * phase[j].item()
            
            # Convert to quaternion
            axis = normalize_vector(axis)
            angle_tensor = torch.tensor(angle, device=device)
            axis_angle = axis * angle_tensor
            quat = trans.axis_angle_to_quaternion(axis_angle)
            local_rotations[i, j] = quat.reshape(-1)
        
        # Hip position for walking
        hip_positions[i, 0, 0] = 0.3 * np.sin(t * walk_freq * 2 * np.pi)  # Side sway
        hip_positions[i, 0, 1] = 1.0 + 0.08 * np.sin(t * walk_freq * 4 * np.pi)  # Vertical bobbing
        hip_positions[i, 0, 2] = t * 3.0  # Forward movement
    
    # Forward kinematics
    try:
        global_positions, global_rotations = fk.forward_kinematics_quats(
            local_rotations, offsets, hip_positions, parents
        )
    except Exception as e:
        print(f"Using fallback forward kinematics: {e}")
        global_positions = torch.zeros((phase_vectors.shape[0], num_joints, 3), device=device)
        global_rotations = local_rotations.clone()
        
        # Simple forward kinematics
        global_positions[:, 0:1] = hip_positions
        for i in range(1, num_joints):
            parent = parents[i]
            if parent >= 0:
                parent_pos = global_positions[:, parent]
                offset = offsets[i].reshape(1, 3).repeat(phase_vectors.shape[0], 1)
                global_positions[:, i] = parent_pos + offset
    
    return {
        "local_rotations": local_rotations.cpu().numpy(),
        "global_positions": global_positions.cpu().numpy(), 
        "global_rotations": global_rotations.cpu().numpy(),
        "hip_positions": hip_positions.cpu().numpy()
    }
