# Model Architecture

This document describes the technical architecture of the RSMT (Real-time Stylized Motion Transition for Characters) model.

## Overall Architecture

The RSMT model combines three main components:

1. **Phase Manifold**: Temporal encoding of motion
2. **Manifold**: Spatial encoding of motion
3. **Sampler**: Transition sequence generator

These components work together to generate high-quality, stylized motion transitions in real-time.

## Phase Manifold

The Phase Manifold is based on the DeepPhase model from the paper "DeepPhase: Periodic Autoencoders for Learning Motion Phase Manifolds".

### Structure
- Input: Motion sequence
- Encoder: Extracts velocity-based features from the motion
- Phase Predictor: Maps features to points on a 2D phase manifold
- Output: Phase coordinates (sx, sy) on unit circle

### Implementation
The phase manifold is implemented in `src/Net/DeepPhaseNet.py` as the `DeepPhaseNet` class, which employs:
- Motion feature extraction
- Self-adaptive frequency bands
- Cylinder mapping for phase continuity

## Manifold Component (StyleVAE)

The Manifold component learns to encode and decode motion content in a latent space.

### Structure
- Input: Motion sequence with phase information
- Encoder: Maps motion to latent space
- Latent Space: Disentangled representation of motion content
- Decoder: Reconstructs motion from latent space
- Output: Reconstructed motion sequence

### Implementation
The Manifold is implemented as a Variational Autoencoder (VAE) in `src/Net/StyleVAE.py` and includes:
- Bidirectional GRU for temporal encoding
- Film conditioning for style modulation
- Residual connections for stable training

## Sampler Component

The Sampler is responsible for generating the transition sequence between two motion styles.

### Structure
- Input: Source motion, target motion, transition length
- Phase Encoder: Encodes the phase trajectory
- Style Encoder: Extracts style code from target motion
- Transition Generator: Creates smooth transition
- Output: Generated transition sequence

### Implementation
The Sampler is implemented in `src/Net/TransitionNet.py` as the `TransitionNet` class and features:
- Scheduled phase blending
- Style interpolation
- Motion regulation to ensure physical plausibility

## Technical Details

### Motion Representation
- Positions: Global 3D joint positions
- Rotations: 6D rotation representation (continuous)
- Phase: 2D unit vector on phase manifold

### Input/Output Format
- Input BVH Motion Files: Joint hierarchy, positions, rotations
- Internal Format: Binary data structures with joint positions, rotations, offsets
- Output: BVH files with generated transitions

### Training Approach
- Two-stage training: First train phase manifold, then train transition model
- Loss Functions:
  - Reconstruction loss for joint positions and rotations
  - KL divergence loss for VAE regularization
  - Phase consistency loss
  - Foot skating loss for physical plausibility

### Optimization
- The model employs several optimization techniques:
  - Parallel calculation of phase coordinates
  - Batch processing of motion sequences
  - Efficient GPU utilization with PyTorch

## Network Dimensions

- Phase Manifold Input: Joint velocities (J×3 dimensions where J is number of joints)
- Manifold Latent Space: 512-dimensional vector
- Style Code: 256-dimensional vector
- GRU Hidden Units: 1024 dimensions

## Integration Flow

1. Source and target motions are encoded with phase information
2. Target style is extracted from the target motion
3. Transition length and timing are specified
4. The sampler generates the transition sequence
5. Post-processing ensures physical plausibility (e.g., foot contact)

## References

The RSMT model builds upon several previous works:
- "DeepPhase: Periodic Autoencoders for Learning Motion Phase Manifolds"
- "Real-time Controllable Motion Transition for Characters"
- "Mode-Adaptive Neural Networks for Quadruped Motion Control"

For a complete understanding of the model, please refer to the original paper:
"RSMT: Real-time Stylized Motion Transition for Characters" (SIGGRAPH '23)
