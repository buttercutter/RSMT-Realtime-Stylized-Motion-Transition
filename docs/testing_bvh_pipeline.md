# Testing the BVH Generation Pipeline

This document provides instructions for testing the RSMT system's BVH generation pipeline to ensure it's working correctly.

## Overview

The BVH generation pipeline converts phase vectors to motion data and then to BVH files. The key components are:

1. **Phase Vector Generation**: Either from the manifold model or synthetically created
2. **Motion Decoding**: Converting phase vectors to joint rotations and positions
3. **BVH File Creation**: Creating properly formatted BVH animation files

## Test Files

The repository includes several test scripts to verify each part of the pipeline:

1. `test_bvh_writer.py`: Tests only the BVH writer component with synthetic motion data
2. `test_pipeline.py`: Tests the entire pipeline from phase vectors to BVH files
3. `final_test.py`: Runs a complete test of the full RSMT implementation

## Running the Basic BVH Writer Test

To test just the BVH writer functionality:

```bash
python test_bvh_writer.py
```

This script will:
1. Generate synthetic motion data (quaternions and positions)
2. Create a sample skeleton structure
3. Use the BVH writer to save this to `./output/inference/test_bvh_writer.bvh`
4. Report success or failure

## Testing the Full Pipeline

To test the complete pipeline including phase vector decoding:

```bash
python test_pipeline.py
```

This script will:
1. Generate synthetic phase vectors
2. Create a test skeleton
3. Decode phase vectors to motion using `motion_decoder.py`
4. Save the motion to BVH using `bvh_writer.py`
5. Generate a visualization of the phase vectors

## Testing the Complete RSMT System

For a complete test of the entire RSMT system:

```bash
python final_test.py
```

This will:
1. Generate points in manifold space
2. Create a transition path in the manifold
3. Decode the manifold points to phase vectors
4. Convert phase vectors to motion data
5. Save the motion to BVH format

## Common Issues and Solutions

### TypeError with torch.sin()

If you encounter errors like `sin(): argument 'input' (position 1) must be Tensor, not float`, make sure all inputs to PyTorch functions are tensor objects. The fix involves converting float values to tensors:

```python
# Before
angle = 0.1 * torch.sin(2.0 * phase_value)  # Error if phase_value is a float

# After (fixed)
phase_tensor = torch.tensor(2.0 * phase_value, device=device)
angle = 0.1 * torch.sin(phase_tensor)
```

### BVH File Issues

If the generated BVH files have issues:

1. Check that joint hierarchies match expectations
2. Verify quaternion to Euler angle conversions are correct
3. Ensure the skeleton and motion data have compatible dimensions

## Verifying Output

To verify the generated BVH files are correct:

1. Open the BVH file in a viewer like Blender or BVHacker
2. Check for smooth motion without jitter or discontinuities
3. Verify joint orientations are anatomically correct
4. Check that the animation length matches the expected number of frames

## Next Steps

After confirming the tests work correctly, you can proceed to:
1. Train your own models using the training pipeline
2. Generate custom transitions using your trained models
3. Integrate the pipeline into your animation workflow
