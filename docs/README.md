# RSMT Documentation

Welcome to the documentation for RSMT (Real-time Stylized Motion Transition for Characters). This documentation provides detailed instructions for using the RSMT model, including data preprocessing, training the model, and generating stylized motion transitions.

## Documentation Contents

1. [Installation Guide](installation.md) - How to set up the RSMT environment
2. [Dataset Preparation](dataset_preparation.md) - How to prepare the 100STYLE dataset for training
3. [Training Pipeline](training_pipeline.md) - Complete pipeline for training the RSMT model
4. [Inference Guide](inference_guide.md) - How to use the trained model for generating transitions
5. [Model Architecture](model_architecture.md) - Technical details of the RSMT model architecture
6. [Troubleshooting](troubleshooting.md) - Common issues and their solutions

## Overview

RSMT (Real-time Stylized Motion Transition for Characters) is a deep learning model for generating high-quality, stylized character motion transitions in real-time. It builds upon earlier work in real-time controllable motion transitions, with enhancements for style control.

The RSMT model consists of several key components:
- Phase Manifold for temporal encoding
- Manifold component for spatial encoding
- Sampler for generating the transitions

For more detailed information, please refer to the original paper and the specific documentation sections listed above.

## Citation

If you use RSMT in your research or project, please cite:

```
Xiangjun Tang, Linjun Wu, He Wang, Bo Hu, Xu Gong, Yuchen Liao, Songnan Li, Qilong Kou, and Xiaogang Jin. 2023. RSMT: Real-time Stylized Motion Transition for Characters. In Special Interest Group on Computer Graphics and Interactive Techniques Conference Conference Proceedings (SIGGRAPH '23 Conference Proceedings), August 6–10, 2023, Los Angeles, CA, USA. ACM, New York, NY, USA, 10 pages. https://doi.org/10.1145/3588432.3591514.
```

## Project Homepage

For more information, visit the project homepage:
[https://yuyujunjun.github.io/publications/Siggraph2023_RSMT/](https://yuyujunjun.github.io/publications/Siggraph2023_RSMT/)
