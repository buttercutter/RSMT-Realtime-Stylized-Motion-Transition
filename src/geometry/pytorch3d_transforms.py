"""
PyTorch3D compatibility module for RSMT
This provides the minimal set of functions needed from PyTorch3D
"""

import torch

def quaternion_apply(quaternion, point):
    """
    Apply the rotation given by a quaternion to a point.
    
    Args:
        quaternion: Quaternions of shape (..., 4)
        point: Points of shape (..., 3)
        
    Returns:
        Rotated points of shape (..., 3)
    """
    q_real = quaternion[..., 0:1]  # real part: w
    q_imag = quaternion[..., 1:]   # imaginary part: x, y, z
    
    # Formula: q * p * q^-1 for quaternion q and point p (as pure quaternion)
    # For unit quaternions, q^-1 = q_conjugate = [q_real, -q_imag]
    
    # Apply formula: 
    # v' = v + 2r(r×v) + 2q×(q×v)
    # where r is the real part of q, and q is the imaginary part
    
    qvec_cross = torch.cross(q_imag, point, dim=-1)
    temp = torch.cross(q_imag, qvec_cross, dim=-1)
    point_rotated = (
        point
        + 2.0 * (q_real * qvec_cross)
        + 2.0 * temp
    )
    
    return point_rotated

def quaternion_multiply(q1, q2):
    """
    Multiply two quaternions.
    
    Args:
        q1: First quaternions of shape (..., 4)
        q2: Second quaternions of shape (..., 4)
        
    Returns:
        The product of q1 and q2, shape (..., 4)
    """
    # Extract components
    a1, b1, c1, d1 = q1[..., 0:1], q1[..., 1:2], q1[..., 2:3], q1[..., 3:4]
    a2, b2, c2, d2 = q2[..., 0:1], q2[..., 1:2], q2[..., 2:3], q2[..., 3:4]
    
    # Hamilton product formula:
    # (a1 + b1i + c1j + d1k)(a2 + b2i + c2j + d2k) = 
    #     (a1a2 - b1b2 - c1c2 - d1d2) + 
    #     (a1b2 + b1a2 + c1d2 - d1c2)i +
    #     (a1c2 - b1d2 + c1a2 + d1b2)j +
    #     (a1d2 + b1c2 - c1b2 + d1a2)k
    
    # Real part (w)
    w = a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2
    
    # Imaginary parts (x, y, z)
    x = a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2
    y = a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2
    z = a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2
    
    return torch.cat([w, x, y, z], dim=-1)
