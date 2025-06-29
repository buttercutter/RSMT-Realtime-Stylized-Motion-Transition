# Motion Conversion in RSMT

This document explains how the RSMT system converts latent phase vectors to actual animation files.

## Overview

The RSMT pipeline includes components for converting phase vectors to motion data and saving that data to BVH format:

1. **Phase Vector Encoding**: Phase vectors are learned representations that encode motion in a compact way.
2. **Motion Decoding**: The `motion_decoder.py` module converts phase vectors back to actual joint rotations and positions.
3. **BVH Creation**: The `bvh_writer.py` module takes the motion data and saves it to BVH format.

## Implementation Details

### Motion Decoder

The motion decoder (`src/utils/motion_decoder.py`) takes phase vectors and produces:
- Local joint rotations (as quaternions)
- Global joint positions
- Hip positions

It implements forward kinematics to convert from local joint rotations to global positions, ensuring proper hierarchical transformations through the skeleton.

#### Important Implementation Notes

1. **PyTorch Tensor Handling**: The motion decoder uses PyTorch tensor operations for calculations. When using PyTorch math functions like `torch.sin()` or `torch.cos()`, inputs must be tensors, not Python scalar values:
   ```python
   # Correct:
   phase_tensor = torch.tensor(phase_value, device=device)
   result = torch.sin(phase_tensor)
   
   # Incorrect - will cause TypeError:
   result = torch.sin(phase_value)  # if phase_value is a float
   ```

2. **Forward Kinematics**: The decoder applies a hierarchical transformation from joint-local rotations to global positions, respecting the skeleton's hierarchy.

3. **Device Management**: All tensor operations maintain consistent device placement (CPU/CUDA) to avoid unnecessary transfers.

### BVH Writer

The BVH writer (`src/utils/bvh_writer.py`) handles:
- Converting quaternion rotations to Euler angles (required by BVH)
- Organizing joint hierarchies
- Writing proper BVH format files with correct frame timing

## Usage

To generate BVH animations from phase data:

```python
# Load or generate phase vectors
phase_vectors = ...  # Shape: [num_frames, phase_dim]

# Convert to motion data
from src.utils.motion_decoder import decode_phase_to_motion
motion_data = decode_phase_to_motion(phase_vectors, skeleton_data=skeleton_data)

# Save to BVH
from src.utils.bvh_writer import save_to_bvh
save_to_bvh(motion_data, "output.bvh", skeleton_data=skeleton_data)
```

## Extending the System

To improve motion quality:

1. Train a dedicated decoder model that maps from phase space to pose space
2. Implement footplant constraints for better ground interaction
3. Add joint limits to prevent unrealistic poses

The current implementation provides a robust foundation that can be extended with more sophisticated models as needed.
