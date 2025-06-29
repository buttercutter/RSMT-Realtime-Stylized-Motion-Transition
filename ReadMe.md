# RSMT Model README

Welcome to the official repository for the paper "RSMT: Real-time Stylized Motion Transition for Characters". This repository's code framework is similar to the paper "Real-time Controllable Motion Transition for Characters," which is a state-of-the-art method in the field of real-time and offline transition motion generation. If you wish to reproduce the paper, you can start from this repository.

## 🚀 Quick Start - Web Interface

**NEW**: Experience RSMT through our interactive web interface!

```bash
# Start the neural network server
cd /home/barberb/RSMT-Realtime-Stylized-Motion-Transition
python output/web_viewer/rsmt_server_progressive.py

# Open browser to http://localhost:8001
```

The web interface provides:
- **Real-time motion transition generation**
- **Neural network-powered inference**
- **Interactive motion visualization**
- **Complete API access**

## Documentation

For detailed documentation, please refer to the [`docs/`](docs/) directory:

- [Installation Guide](docs/installation.md): How to set up the RSMT environment
- [**Web Interface Guide**](docs/web_interface_guide.md): **NEW** - Complete guide to the RSMT web interface
- [**API Documentation**](docs/api_documentation.md): **NEW** - RESTful API reference for neural network server
- [**Deployment Guide**](docs/deployment_guide.md): **NEW** - Production deployment instructions
- [Dataset Preparation](docs/dataset_preparation.md): How to prepare the 100STYLE dataset for training
- [Training Pipeline](docs/training_pipeline.md): Complete pipeline for training the RSMT model
- [Inference Guide](docs/inference_guide.md): How to use the trained model for generating transitions
- [Model Architecture](docs/model_architecture.md): Technical details of the RSMT model architecture
- [Troubleshooting](docs/troubleshooting.md): Common issues and their solutions

## 🆕 New Features

### Web Interface & Neural Network Server
- **Interactive Web Interface**: Browser-based motion transition visualization
- **Progressive Loading**: Fast server startup with on-demand model loading
- **Real PyTorch Inference**: Actual neural network models with trained weights
- **RESTful API**: Complete API for motion processing and analysis
- **Enhanced Algorithms**: Sophisticated fallback systems with advanced interpolation

### Neural Network Models
- **DeepPhase Model**: 132→256→128→32→2D architecture with checkpoint weights
- **StyleVAE Model**: 256-dimensional style vector generation
- **TransitionNet Model**: Neural network-based motion transition generation
- **Quality Metrics**: Real-time motion quality analysis with FFT-based rhythm detection

### API Endpoints
- `/api/status` - Server and model status
- `/api/encode_phase` - Phase coordinate encoding
- `/api/encode_style` - Style vector extraction  
- `/api/generate_transition` - Motion transition generation
- `/api/analyze_motion` - Advanced motion analysis

See the [Web Interface Guide](docs/web_interface_guide.md) for complete details.

## Project Structure

The project has been reorganized for better maintainability and navigation:

```
├── src/                    # Core source code (unchanged)
├── scripts/               # Organized scripts by functionality
│   ├── preprocessing/     # Data preprocessing scripts
│   ├── training/         # Model training scripts
│   ├── inference/        # Inference and demo scripts
│   ├── benchmarking/     # Benchmark and evaluation scripts
│   ├── utilities/        # Utility and helper scripts
│   └── phase_processing/ # Phase-related processing
├── tests/                # Testing and debugging
│   ├── unit/            # Unit tests
│   ├── debug/           # Debug scripts
│   ├── analysis/        # Analysis scripts
│   └── integration/     # Integration tests
├── config/              # Configuration files
├── logs/                # Log files and data
├── fixes/               # Fix and maintenance scripts
├── docs/                # Documentation
│   └── project_docs/    # Project-specific documentation
├── tools/               # Development tools
└── output/              # Generated outputs
```

## Overview

Our RSMT model is based on the 100STYLE dataset with the phase, which can be obtained by the trained phase manifold. You can download the 100STYLE dataset from https://www.ianxmason.com/100style/. The downloaded file should be set in `MotionData/100STYLE`. Before training our RSMT model, we show how to preprocess the 100STYLE dataset, then train the phase manifold, generate the phase vectors for all motion sequences, and lastly train the RSMT model, which consists of two components: a manifold and a sampler.

  ## Dataset Preprocessing

  To use the pre-trained 100STYLE dataset, first, download the 100STYLE folder and save it in `./MotionData/100STYLE`. Next, preprocess the 100STYLE dataset by running the following command in your terminal:

  ```bash
  python scripts/preprocessing/process_dataset.py --preprocess
  ```

  This includes converting all `.bvh` files to binary and augmenting the dataset. Once preprocessing is complete, the 100STYLE folder should contain the following files:

  - `skeleton`
  - `test_binary.dat`, `test_binary_agument.dat`
  - `train_binary.dat`, `train_binary_agument.dat`

  ## Train Phase Model

  To train the phase manifold, construct the dataset by running the following command:

  ```bash
  python scripts/preprocessing/process_dataset.py --train_phase_model
  ```

  Then train `deepphase` by running this command:

  ```bash
  python scripts/training/train_deephase.py
  ```

  The main part of the phase model comes from https://github.com/sebastianstarke/AI4Animation. We accelerated it by parallelly calculating Eq. 4 ($(s_x,s_y) = FC(L_i)$) of the paper "DeepPhase: Periodic Autoencoders for Learning Motion Phase Manifolds".

  After training, run the following code to validate:

  ```bash
  python scripts/training/train_deephase.py --test --version YOUR_VERSION --epoch YOUR_EPOCH
  ```

  This will plot two figures: 

  ![phase](./ReadMe.assets/phase.png) 

  ![SAFB](./ReadMe.assets/SAFB.png)

  ## Generate Phase Vectors for the Dataset

  To generate the phase vectors for the dataset, run the following command in your terminal:

  ```bash
  python scripts/preprocessing/process_dataset.py --add_phase_to_dataset --model_path "YOUR_PHASE_MODEL_PATH"
  ```

  ## Train Manifold

  Before training the manifold, split the motion sequences into windows of 60 frames by running the following command:

  ```bash
  python scripts/preprocessing/process_dataset.py --train_manifold_model
  ```

  After processing the dataset, train the model with the following command:

  ```bash
  python scripts/training/train_styleVAE.py 
  ```

  Once training is complete, you can validate it by running:

  ```bash
  python scripts/training/train_styleVAE.py --test --version YOUR_VERSION --epoch YOUR_EPOCH
  ```

  It generates multiple `.bvh` files, among which `test_net.bvh` is generated by the trained model. This process removes part of the training information from the model and saves the model as `m_save_model_YOUR_EPOCH`.

  ## Train Sampler

  First, prepare the dataset for style sequences by running the following command (Note: style sequences contain 120 frames per sequence, unlike the manifold which contains 60 frames per sequence):

  ```bash
  python scripts/preprocessing/process_dataset.py --train_sampler_model
  ```

  Then train the sampler, YOUR_MANIFOLD_MODEL should be repalced by `m_save_model_YOUR_EPOCH`:

  ```bash
  python scripts/training/train_transitionNet.py --moe_model YOUR_MANIFOLD_MODEL
  ```

  After training, you can validate the model by running:

  ```bash
  python scripts/training/train_transitionNet.py --test --moe_model YOUR_MANIFOLD_MODEL --version YOUR_VERSION --epoch YOUR_EPOCH
  ```

  The output result is `test_net.bvh`.

  Note: The model only supports sequences that have the phase vector at the first key frame.

  ### Generate Longer Sequences between Multiple Key-frames

  For more information on generating longer sequences between multiple key-frames, refer to the `scripts/inference/Running_LongSeq.py` file.

  ### Benchmarks

  To prepare the test dataset for benchmarks, run:

  ```bash
  python scripts/preprocessing/process_dataset.py --benchmarks
  ```

  Then run benchmarks with:

  ```bash
  python scripts/benchmarking/benchmark.py --model_path 
  ```

  ### General Applications

  To use this method on key frames without a corresponding phase vector, a possible way is to predict the phase vector for the first frame, given by the past frames. 

  After training all other components, train the phase predictor with the following command:

  ```bash
  python scripts/training/train_transitionNet.py --moe_model YOUR_MANIFOLD_MODEL --predict_phase --pretrained --version YOUR_VERSION --epoch YOUR_EPOCH
  ```

  ### Citation

  If you use RSMT in any context, please cite the following paper:

  ```
  Xiangjun Tang, Linjun Wu, He Wang, Bo Hu, Xu Gong, Yuchen Liao, Songnan Li, Qilong Kou, and Xiaogang Jin. 2023. RSMT: Real-time Stylized Motion Transition for Characters. In Special Interest Group on Computer Graphics and Interactive Techniques Conference Conference Proceedings (SIGGRAPH ’23 Conference Proceedings), August 6–10, 2023, Los Angeles, CA, USA. ACM, New York, NY, USA, 10 pages. https://doi.org/10.1145/3588432.3591514.
  ```

  ## Alternative Preprocessing Scripts

  In addition to the standard preprocessing workflow using `scripts/preprocessing/process_dataset.py --preprocess`, we provide several alternative preprocessing scripts:

  1. **Complete Preprocessing Script**: For a more robust preprocessing with detailed progress information:
     ```bash
     python scripts/preprocessing/preprocess_complete.py
     ```
     Or use the shell script with logging:
     ```bash
     bash scripts/preprocessing/run_preprocessing.sh
     ```

  2. **Simplified Preprocessing**: For a more streamlined preprocessing with fewer dependencies:
     ```bash
     python scripts/preprocessing/simple_preprocess.py
     ```

  3. **Diagnostic Scripts**: For inspecting and troubleshooting datasets:
     ```bash
     python tests/analysis/inspect_dataset.py
     ```

  For more details on preprocessing options, refer to the [Dataset Preparation](docs/dataset_preparation.md) documentation.

  ## Home Page

  [https://yuyujunjun.github.io/publications/2023-08-06RSMT/](https://yuyujunjun.github.io/publications/Siggraph2023_RSMT/)
