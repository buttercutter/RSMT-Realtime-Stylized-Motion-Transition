# Inference Guide

This guide explains how to use the trained RSMT model to generate stylized motion transitions. After completing the training pipeline, you can use the model through different interfaces.

## 🌐 Web Interface (Recommended)

The easiest way to use RSMT is through the interactive web interface:

### Quick Start
```bash
# Start the neural network server
cd /home/barberb/RSMT-Realtime-Stylized-Motion-Transition
python output/web_viewer/rsmt_server_progressive.py

# Open browser to http://localhost:8001
```

### Features
- **Real-time motion transition generation**
- **Interactive visualization**
- **Neural network-powered inference**
- **Quality metrics and analysis**
- **RESTful API access**

See the [Web Interface Guide](web_interface_guide.md) for complete details.

### API Usage
```python
import requests

# Generate transition via API
response = requests.post('http://localhost:8001/api/generate_transition', json={
    "start_motion": {"frames": [[0,1,2,3,4,5]]},
    "target_motion": {"frames": [[10,11,12,13,14,15]]}, 
    "style_code": [0.1, 0.2, 0.3],
    "transition_length": 30
})

transition = response.json()
print("Generated", len(transition["transition_frames"]), "transition frames")
```

## 🖥️ Command Line Inference

### Basic Inference

To generate a basic motion transition using the trained model:

```bash
python train_transitionNet.py --test --moe_model YOUR_MANIFOLD_MODEL --version YOUR_VERSION --epoch YOUR_EPOCH
```

Replace the placeholders:
- `YOUR_MANIFOLD_MODEL`: Path to the trained manifold model (e.g., `m_save_model_198`)
- `YOUR_VERSION`: Version number of your trained model
- `YOUR_EPOCH`: Epoch number to use for inference

This will generate a `test_net.bvh` file containing the transition animation, which can be viewed in any BVH viewer software.

### Generating Longer Sequences between Multiple Key-frames

For more complex motion synthesis with multiple key-frames, use the `Running_LongSeq.py` script:

```bash
python Running_LongSeq.py --model_path YOUR_MODEL_PATH --source SOURCE_BVH --target TARGET_BVH --output OUTPUT_BVH
```

Where:
- `YOUR_MODEL_PATH`: Path to the trained model
- `SOURCE_BVH`: Path to the source motion BVH file
- `TARGET_BVH`: Path to the target motion BVH file
- `OUTPUT_BVH`: Path where the output BVH file will be saved

### Customizing Transition Parameters

You can customize the transition by modifying the parameters in `Running_LongSeq.py`:

```python
# Example modification in Running_LongSeq.py
tar_id = [50, 90, 130, 170, 210, 250, 290, 330]  # Target frame indices
time = [40, 40, 40, 40, 40, 80, 40, 40]  # Transition times
```

These parameters control the timing and placement of transitions between key-frames.

## Running Benchmarks

To evaluate the quality of transitions, you can run the benchmark script:

1. Prepare the test dataset for benchmarking:
   ```bash
   python process_dataset.py --benchmarks
   ```

2. Run the benchmark:
   ```bash
   python benchmark.py --model_path YOUR_MODEL_PATH --model_name "RSMT"
   ```

This will generate metrics for evaluating the quality of the transitions, including:
- Joint position error
- Joint rotation error
- NPSS (Normalized Power Spectrum Similarity)
- Foot skating metrics

## Inference with Phase Prediction

For cases where you don't have phase information for key-frames:

```bash
python train_transitionNet.py --test --moe_model YOUR_MANIFOLD_MODEL --predict_phase --version YOUR_VERSION --epoch YOUR_EPOCH
```

This uses the trained phase predictor to infer phase values from past frames.

## Batch Processing

To process multiple animations in batch:

```python
import torch
from src.Datasets.Style100Processor import StyleLoader
from src.utils import BVH_mod as BVH

# Load the model
model = torch.load('./results/Transitionv2_style100/myResults/VERSION/m_save_model_EPOCH')

# Load dataset
loader = StyleLoader()
loader.load_dataset("+phase_gv10")  # Load with phase information

# Process multiple motions
for style in loader.train_motions:
    for content in loader.train_motions[style]:
        # Process each motion...
```

## Visualizing Results

The generated BVH files can be visualized using:
- [Blender](https://www.blender.org/) with BVH import plugin
- [MotionBuilder](https://www.autodesk.com/products/motionbuilder/overview)
- [BVHacker](http://www.bvhacker.com/)
- Custom visualization using Python libraries like matplotlib

## Advanced Usage

For advanced usage, you can modify the transition parameters directly in the code:

```python
# Example modification to transition parameters
pred_pos, pred_rot, pred_phase, _ = model.shift_running(
    gp.cuda(), loc_rot.cuda(), phases.cuda(), None,
    None, target_style, noise, 
    start_id=10,              # Start frame index
    target_id=target_id,      # Target frame index
    length=length,            # Transition length
    phase_schedule=1.0        # Phase schedule factor
)
```

## Exporting to Other Formats

To export the generated animations to formats other than BVH:

1. Convert BVH to FBX using Blender or MotionBuilder
2. Export to game engines like Unity or Unreal Engine

## Performance Considerations

- The inference speed depends on the model size and hardware capabilities
- For real-time applications, consider running on a GPU
- Batch processing can improve throughput for multiple animations

## Next Steps

For details on the technical architecture of the model, refer to the [Model Architecture](model_architecture.md) document.
