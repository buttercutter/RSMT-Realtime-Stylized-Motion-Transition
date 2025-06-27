# Viewing RSMT Results in Blender

## Quick Start Guide

### 1. Install Blender
- Download free from: https://www.blender.org/download/
- Install and launch Blender

### 2. Import BVH Animation
1. Delete the default cube (Select cube, press Delete)
2. Go to: File > Import > Motion Capture (.bvh)
3. Navigate to one of these BVH files:
   - `output/inference/test_pipeline.bvh`
   - `output/inference/final_test/final_test.bvh`
   - `output/inference/test_bvh_writer.bvh`

### 3. View Animation
1. Press SPACEBAR to play animation
2. Use mouse wheel to zoom
3. Middle mouse button to rotate view
4. Shift + middle mouse to pan

### 4. Enhance Visualization
1. In the 3D viewport, change shading to "Material Preview" or "Rendered"
2. Add a ground plane: Shift+A > Mesh > Plane, scale it up
3. Add lighting: Shift+A > Light > Sun

### 5. Export Animation
- File > Export > Alembic (.abc) for other software
- Or render as video: Rendering > Render Animation

## BVH Files Generated
- output/inference/test_bvh_writer.bvh
- output/inference/test_pipeline.bvh
- output/inference/final_test/final_test.bvh

## Tips
- BVH files contain skeleton animation data
- The character will appear as a stick figure initially
- You can add a mesh character and bind it to the skeleton for full character animation
- Blender's bone visualization shows the motion structure clearly
