#!/usr/bin/env python3
"""
Debug version of the Final RSMT Implementation Test 
with additional logging and error handling
"""

import os
import sys
import numpy as np
import torch
import matplotlib.pyplot as plt
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='./output/inference/debug_final_test.log',
    filemode='w'
)
logger = logging.getLogger('debug_final_test')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

# Add the repository root to the path
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logger.info(f"Python sys.path: {sys.path}")

# Create output directory
output_dir = "./output/inference/final_test"
os.makedirs(output_dir, exist_ok=True)
logger.info(f"Created output directory: {output_dir}")

def generate_manifold_points(manifold_dim=8):
    """Generate two points in the manifold space"""
    logger.info(f"Generating manifold points with dim={manifold_dim}")
    
    # Generate two distinct points in manifold space
    source_point = torch.randn(1, manifold_dim)
    target_point = torch.randn(1, manifold_dim)
    
    # Normalize to unit length
    source_point = source_point / torch.norm(source_point)
    target_point = target_point / torch.norm(target_point)
    
    logger.debug(f"Source point: {source_point}")
    logger.debug(f"Target point: {target_point}")
    
    return source_point, target_point

def generate_transition_path(start_point, end_point, num_steps=30):
    """
    Generate a smooth transition path between start and end points
    using spherical linear interpolation (slerp)
    """
    logger.info(f"Generating transition path with {num_steps} steps")
    
    # Simple implementation of slerp for manifold points
    def slerp(p0, p1, t):
        omega = torch.acos((p0 * p1).sum())
        so = torch.sin(omega)
        
        # If points are very close, just use linear interpolation
        if abs(so) < 1e-8:
            logger.debug(f"Points very close, using linear interpolation at t={t}")
            return p0 * (1.0 - t) + p1 * t
            
        return torch.sin((1.0 - t) * omega) / so * p0 + torch.sin(t * omega) / so * p1
    
    # Generate transition path
    path = torch.zeros((num_steps, start_point.shape[1]))
    for i in range(num_steps):
        t = i / (num_steps - 1)  # Normalize to 0-1
        path[i] = slerp(start_point[0], end_point[0], t)
    
    logger.debug(f"First point in path: {path[0]}")
    logger.debug(f"Last point in path: {path[-1]}")
    
    return path

def decode_manifold_to_phase(manifold_points, phase_dim=32):
    """
    Decode manifold points to phase vectors
    In a real implementation, this would use a trained decoder
    """
    num_points = manifold_points.shape[0]
    logger.info(f"Decoding {num_points} manifold points to phase vectors with dim={phase_dim}")
    
    phase_vectors = torch.zeros((num_points, phase_dim))
    
    # Simple mapping from manifold to phase space
    # In a real implementation, this would be a neural network
    for i in range(num_points):
        # Create a phase vector based on the manifold point
        # Using the manifold point to modulate sine waves at different frequencies
        for j in range(phase_dim):
            freq = 0.5 + j * 0.1
            phase = torch.sin(freq * torch.arange(manifold_points.shape[1])).dot(manifold_points[i])
            phase_vectors[i, j] = torch.sin(phase * np.pi)
    
    logger.debug(f"First phase vector: {phase_vectors[0]}")
    logger.debug(f"Last phase vector: {phase_vectors[-1]}")
    
    return phase_vectors

def create_test_skeleton(num_joints=22):
    """Create a test skeleton structure"""
    logger.info(f"Creating test skeleton with {num_joints} joints")
    
    # Standard skeleton structure
    parents = [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21][:num_joints]
    names = ["Hips", "LeftHip", "LeftKnee", "LeftAnkle", "LeftToe",
             "RightHip", "RightKnee", "RightAnkle", "RightToe",
             "Chest", "Chest2", "Chest3", "Chest4", "Neck", "Head",
             "LeftCollar", "LeftShoulder", "LeftElbow", "LeftWrist",
             "RightCollar", "RightShoulder", "RightElbow", "RightWrist"][:num_joints]
    
    # Create default offsets (T-pose)
    offsets = np.zeros((num_joints, 3), dtype=np.float32)
    # Basic T-pose skeleton offsets
    offsets[0] = [0, 1.0, 0]  # Hip
    offsets[1] = [-0.2, -0.1, 0]  # LeftHip
    offsets[2] = [0, -0.5, 0]  # LeftKnee
    offsets[3] = [0, -0.5, 0]  # LeftAnkle
    offsets[4] = [0, -0.1, 0.2]  # LeftToe
    offsets[5] = [0.2, -0.1, 0]  # RightHip
    offsets[6] = [0, -0.5, 0]  # RightKnee
    offsets[7] = [0, -0.5, 0]  # RightAnkle
    offsets[8] = [0, -0.1, 0.2]  # RightToe
    offsets[9] = [0, 0.2, 0]  # Chest
    offsets[10] = [0, 0.2, 0]  # Chest2
    offsets[11] = [0, 0.2, 0]  # Chest3
    offsets[12] = [0, 0.2, 0]  # Chest4
    offsets[13] = [0, 0.1, 0]  # Neck
    offsets[14] = [0, 0.1, 0]  # Head
    offsets[15] = [-0.2, 0, 0]  # LeftCollar
    offsets[16] = [-0.2, 0, 0]  # LeftShoulder
    offsets[17] = [0, -0.3, 0]  # LeftElbow
    offsets[18] = [0, -0.3, 0]  # LeftWrist
    offsets[19] = [0.2, 0, 0]  # RightCollar
    offsets[20] = [0.2, 0, 0]  # RightShoulder
    offsets[21] = [0, -0.3, 0]  # RightElbow
    
    logger.debug(f"Skeleton parent hierarchy: {parents}")
    
    return {
        "parents": parents,
        "names": names,
        "offsets": offsets
    }

def plot_vectors(vectors, title, filename, dims_to_plot=4):
    """Plot the first few dimensions of vectors"""
    logger.info(f"Plotting vectors with shape {vectors.shape} to {filename}")
    
    plt.figure(figsize=(10, 6))
    for i in range(min(dims_to_plot, vectors.shape[1])):
        plt.plot(vectors[:, i].cpu().numpy(), label=f'Dim {i}')
    plt.title(title)
    plt.xlabel("Frame")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath)
    plt.close()
    
    logger.debug(f"Plot saved to {filepath}")
    return filepath

def test_motion_decoder_import():
    """Test if we can import the motion decoder module"""
    logger.info("Testing motion_decoder import...")
    try:
        import importlib.util
        spec = importlib.util.find_spec("src.utils.motion_decoder")
        if spec is None:
            logger.error("src.utils.motion_decoder module not found")
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info("Successfully imported motion_decoder")
        return True
    except Exception as e:
        logger.error(f"Error importing motion_decoder: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_bvh_writer_import():
    """Test if we can import the BVH writer module"""
    logger.info("Testing bvh_writer import...")
    try:
        import importlib.util
        spec = importlib.util.find_spec("src.utils.bvh_writer")
        if spec is None:
            logger.error("src.utils.bvh_writer module not found")
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info("Successfully imported bvh_writer")
        return True
    except Exception as e:
        logger.error(f"Error importing bvh_writer: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_final_test():
    """Run a complete end-to-end test of the RSMT implementation"""
    logger.info("\n===== RSMT FINAL IMPLEMENTATION TEST =====")
    logger.info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # First check module imports
    logger.info("Testing required module imports...")
    if not test_motion_decoder_import() or not test_bvh_writer_import():
        logger.error("Required module imports failed, test cannot proceed")
        return
    
    try:
        # Step 1: Generate manifold points
        logger.info("\n1. Generating points in manifold space...")
        source_point, target_point = generate_manifold_points()
        logger.info(f"  Source point shape: {source_point.shape}")
        logger.info(f"  Target point shape: {target_point.shape}")
        
        # Step 2: Generate transition path
        logger.info("\n2. Generating transition path in manifold space...")
        num_frames = 60
        manifold_path = generate_transition_path(source_point, target_point, num_frames)
        logger.info(f"  Transition path shape: {manifold_path.shape}")
        manifold_plot = plot_vectors(manifold_path, "Manifold Transition Path", "manifold_path.png", 8)
        logger.info(f"  Manifold path plot saved to {manifold_plot}")
        
        # Step 3: Decode manifold to phase
        logger.info("\n3. Decoding manifold points to phase vectors...")
        phase_vectors = decode_manifold_to_phase(manifold_path)
        logger.info(f"  Phase vectors shape: {phase_vectors.shape}")
        phase_plot = plot_vectors(phase_vectors, "Phase Vectors", "phase_vectors.png")
        logger.info(f"  Phase vectors plot saved to {phase_plot}")
        
        # Step 4: Create skeleton data
        logger.info("\n4. Creating skeleton data...")
        skeleton_data = create_test_skeleton()
        logger.info(f"  Created skeleton with {len(skeleton_data['parents'])} joints")
        
        # Step 5: Convert phase vectors to motion
        logger.info("\n5. Converting phase vectors to motion data...")
        try:
            # Explicit imports with manual path handling
            sys.path.insert(0, os.path.abspath('.'))
            from src.utils.motion_decoder import decode_phase_to_motion
            
            logger.info("  Calling decode_phase_to_motion...")
            motion_data = decode_phase_to_motion(phase_vectors, skeleton_data=skeleton_data)
            logger.info("  Successfully converted phase vectors to motion data")
            logger.info("  Motion data contains:")
            for key, value in motion_data.items():
                logger.info(f"    {key}: shape {value.shape}")
        except Exception as e:
            logger.error(f"  Error in motion decoding: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return
        
        # Step 6: Save motion to BVH
        logger.info("\n6. Saving motion to BVH format...")
        try:
            from src.utils.bvh_writer import save_to_bvh
            output_path = os.path.join(output_dir, "final_test.bvh")
            logger.info(f"  Calling save_to_bvh with output path: {output_path}")
            
            # Check if motion_data contains required keys
            required_keys = ["local_rotations", "hip_positions"]
            missing_keys = [key for key in required_keys if key not in motion_data]
            if missing_keys:
                logger.error(f"  Motion data is missing required keys: {missing_keys}")
            
            # Print shapes of data being passed
            for key, value in motion_data.items():
                logger.info(f"  Motion data {key}: shape {value.shape}, dtype {value.dtype}")
            
            success = save_to_bvh(motion_data, output_path, skeleton_data=skeleton_data)
            
            if success:
                logger.info(f"  Successfully saved BVH file to {output_path}")
            else:
                logger.error("  Failed to save BVH file")
                return
        except Exception as e:
            logger.error(f"  Error in BVH writing: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return
        
        # Final success message
        logger.info("\n===== TEST COMPLETED SUCCESSFULLY =====")
        logger.info(f"Output files location: {output_dir}")
        logger.info("Files generated:")
        logger.info(f"  - {manifold_plot} - Visualization of the manifold transition")
        logger.info(f"  - {phase_plot} - Visualization of the phase vectors")
        logger.info(f"  - {output_path} - Animation file ready for playback")
        
    except Exception as e:
        logger.error(f"\nUnexpected error in test: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    run_final_test()
