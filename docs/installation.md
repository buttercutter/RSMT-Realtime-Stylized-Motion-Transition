# Installation Guide

This guide outlines the steps required to set up your environment for the RSMT (Real-time Stylized Motion Transition for Characters) model.

## System Requirements

- CUDA-compatible GPU (recommended: NVIDIA GPU with at least 8GB VRAM)
- CUDA Toolkit 11.7
- Python 3.8 or higher

## Setting up the Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/RSMT-Realtime-Stylized-Motion-Transition.git
   cd RSMT-Realtime-Stylized-Motion-Transition
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Dependencies

The main dependencies for RSMT are:
- matplotlib==3.5.2
- numpy==1.22.3
- pandas==1.4.3
- pytorch3d==0.4.0
- pytorch_lightning==1.5.10
- scipy==1.9.0
- torch==1.13.0+cu117

> **Note**: Installing PyTorch3D can sometimes be challenging. If you encounter issues with PyTorch3D installation, see the [Troubleshooting](troubleshooting.md) section.

## Directory Structure

After installation, ensure your project has the following directory structure:

```
RSMT-Realtime-Stylized-Motion-Transition/
├── MotionData/
│   └── 100STYLE/  # Place the dataset here
├── src/
│   ├── Datasets/
│   ├── geometry/
│   ├── Module/
│   ├── Net/
│   └── utils/
├── docs/
├── process_dataset.py
├── train_deephase.py
├── train_styleVAE.py
├── train_transitionNet.py
├── Running_LongSeq.py
├── benchmark.py
└── requirements.txt
```

## Dataset Setup

The 100STYLE dataset should be downloaded and placed in the `MotionData/100STYLE/` directory. For detailed instructions on dataset preparation, refer to the [Dataset Preparation](dataset_preparation.md) guide.

## Next Steps

After successful installation, follow the [Dataset Preparation](dataset_preparation.md) guide to prepare the 100STYLE dataset for training.
