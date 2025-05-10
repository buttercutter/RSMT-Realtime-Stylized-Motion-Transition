# Troubleshooting

This guide provides solutions to common issues that you might encounter when working with the RSMT model.

## Installation Issues

### PyTorch3D Installation Fails

**Issue**: Error installing PyTorch3D dependency.

**Solutions**:

1. Install from source:
   ```bash
   pip install 'git+https://github.com/facebookresearch/pytorch3d.git@stable'
   ```

2. Try using conda:
   ```bash
   conda install pytorch3d -c pytorch3d
   ```

3. Check CUDA compatibility:
   ```bash
   # Verify your CUDA version
   nvcc --version
   
   # Install compatible PyTorch version first
   pip install torch==1.13.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html
   
   # Then install PyTorch3D
   pip install pytorch3d==0.4.0
   ```

### CUDA Out of Memory Errors

**Issue**: CUDA out of memory during training or inference.

**Solutions**:
1. Reduce batch size in the respective training script
2. Use a smaller sequence length
3. Train on a GPU with more memory
4. Enable gradient checkpointing for memory-efficient backpropagation

## Dataset Preparation Issues

### BVH File Conversion Errors

**Issue**: Errors when converting BVH files to binary format.

**Solutions**:
1. Check if the 100STYLE dataset has the expected structure
2. Ensure `Frame_Cuts.csv` exists in the 100STYLE directory
3. Try running the simplified preprocessing script:
   ```bash
   python simple_preprocess.py
   ```
4. Check for specific errors in the BVH files:
   ```bash
   python inspect_dataset.py
   ```

### Missing Skeleton File

**Issue**: Training fails due to missing skeleton file.

**Solution**:
Manually create the skeleton file:
```bash
python -c "from src.Datasets.Style100Processor import save_skeleton; save_skeleton()"
```

## Training Issues

### Phase Manifold Training Issues

**Issue**: Phase manifold training produces poor results.

**Solutions**:
1. Ensure the dataset preprocessing is correct
2. Try different learning rates
3. Check for overfitting and adjust regularization
4. Inspect velocity calculations in the preprocessing steps

### Sampler Training Diverges

**Issue**: Loss explodes during sampler training.

**Solutions**:
1. Lower the learning rate
2. Add gradient clipping:
   ```python
   # Add to train_transitionNet.py
   torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
   ```
3. Check that the manifold model is properly trained and loaded
4. Ensure phase vectors are properly generated

## Inference Issues

### PyTorch Type Errors in Motion Decoder

**Issue**: Error `sin(): argument 'input' (position 1) must be Tensor, not float` when running the pipeline.

**Solutions**:
1. Make sure to convert float values to PyTorch tensors before using PyTorch math functions:
   ```python
   # Incorrect:
   value = torch.sin(2.0 * float_value)
   
   # Correct:
   value = torch.sin(torch.tensor(2.0 * float_value, device=device))
   ```
2. This error commonly occurs in the motion_decoder.py when calculating angles or positions.
3. Check that all inputs to PyTorch math functions (sin, cos, etc.) are tensor objects, not Python floats.

### Foot Skating in Generated Animations

**Issue**: Character feet slide on the ground during animations.

**Solutions**:
1. Enable the foot skating loss during training
2. Apply a post-processing foot contact cleanup:
   ```python
   from src.utils.foot_cleanup import fix_foot_contacts
   
   # Apply foot cleanup to the generated motion
   cleaned_motion = fix_foot_contacts(generated_motion)
   ```

### Discontinuities in Transitions

**Issue**: Motion transitions have visible discontinuities.

**Solutions**:
1. Increase the transition length
2. Ensure the source and target motions are compatible
3. Check that phase vectors are continuous
4. Try different blending strategies in the sampler

## File Format Issues

### BVH Output Errors

**Issue**: Generated BVH files cannot be opened in animation software.

**Solutions**:
1. Check the joint hierarchy in the generated file
2. Verify rotation formats are consistent
3. Try opening the file with different BVH viewers
4. Use the debug utility:
   ```bash
   python debug_bvh.py --file path/to/output.bvh
   ```

## Performance Issues

### Slow Inference

**Issue**: Model inference is too slow for real-time applications.

**Solutions**:
1. Use half precision (float16) for inference:
   ```python
   model = model.half()
   ```
2. Optimize the batch size for your hardware
3. Consider model quantization for deployment
4. Use TorchScript to compile the model:
   ```python
   scripted_model = torch.jit.script(model)
   ```

## Getting Additional Help

If you continue to experience issues not addressed in this guide:

1. Check the original paper and supplementary materials
2. Visit the project homepage: [https://yuyujunjun.github.io/publications/Siggraph2023_RSMT/](https://yuyujunjun.github.io/publications/Siggraph2023_RSMT/)
3. Search for similar issues in the computer animation research community
4. Consider reaching out to the paper authors directly
