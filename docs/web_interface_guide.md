# RSMT Web Interface Guide

This guide covers the new RSMT web interface and neural network server implementation that provides real-time motion transition capabilities through a modern web browser.

## Overview

The RSMT web interface consists of:
- **Neural Network Server**: FastAPI-based server with PyTorch model integration
- **Progressive Loading**: Models load on-demand for fast startup
- **RESTful API**: Complete API for motion processing and analysis
- **Web Visualization**: Browser-based motion transition viewer

## Quick Start

### 1. Start the Server

```bash
cd /home/barberb/RSMT-Realtime-Stylized-Motion-Transition
python output/web_viewer/rsmt_server_progressive.py
```

The server will start on `http://localhost:8001` with progressive model loading.

### 2. Access Web Interface

Open your browser and navigate to:
```
http://localhost:8001
```

The interface provides real-time motion transition visualization and controls.

## Server Architecture

### Neural Network Models

The server implements enhanced neural network models based on the original RSMT architecture:

#### DeepPhase Model
- **Architecture**: 132 → 256 → 128 → 32 → 2D phase coordinates
- **Function**: Encodes motion data into phase manifold coordinates
- **Checkpoint**: Loads weights from `/output/phase_model/minimal_phase_model.pth`

#### StyleVAE Model  
- **Architecture**: 132 → 256 → 128 → 256-dimensional style vector
- **Function**: Extracts motion style characteristics
- **Output**: 256-dimensional style encoding

#### TransitionNet Model
- **Architecture**: Neural network for motion transition generation
- **Input**: Start motion + Style code + Phase coordinates
- **Output**: Smooth motion transitions

### Progressive Loading System

The server implements intelligent model loading:

1. **Fast Startup**: Server starts immediately without waiting for model loading
2. **On-Demand Loading**: Models load when first API call is made
3. **Fallback Algorithms**: Enhanced interpolation when neural networks unavailable
4. **Error Recovery**: Graceful degradation with sophisticated fallback systems

## API Endpoints

### Server Status
```http
GET /api/status
```

Returns server status and model information:
```json
{
  "status": "online",
  "server": "RSMT Neural Network Server (Progressive Loading)",
  "models": {
    "deephase": true,
    "stylevae": true, 
    "transitionnet": true,
    "skeleton": true
  },
  "models_initialized": true,
  "gpu_available": true,
  "torch_version": "2.7.0+cu126"
}
```

### Phase Encoding
```http
POST /api/encode_phase
```

Encodes motion data into phase coordinates:

**Request:**
```json
{
  "motion_data": {
    "frames": [[0,1,2,3,4,5], [1,2,3,4,5,6]],
    "frame_time": 0.016667
  },
  "sequence_length": 60
}
```

**Response:**
```json
{
  "phase_coordinates": [[0.1, 0.2], [0.3, 0.4]],
  "processing_time": 0.001,
  "status": "success"
}
```

### Style Encoding
```http
POST /api/encode_style
```

Extracts style vector from motion data:

**Request:**
```json
{
  "motion_data": {
    "frames": [[0,1,2,3,4,5], [1,2,3,4,5,6]]
  }
}
```

**Response:**
```json
{
  "style_code": [0.1, 0.2, ...], // 256-dimensional vector
  "processing_time": 3.2,
  "status": "success"
}
```

### Motion Transition Generation
```http
POST /api/generate_transition
```

Generates smooth motion transitions:

**Request:**
```json
{
  "start_motion": {
    "frames": [[0,1,2], [0.1,1.1,2.1]]
  },
  "target_motion": {
    "frames": [[5,6,7], [5.1,6.1,7.1]]
  },
  "style_code": [0.1, 0.2, 0.3],
  "transition_length": 30,
  "transition_type": "smooth"
}
```

**Response:**
```json
{
  "transition_frames": [[...], [...], ...],
  "quality_metrics": {
    "smoothness": 0.95,
    "naturalness": 0.87,
    "style_preservation": 0.92,
    "temporal_consistency": 0.89
  },
  "processing_time": 0.026,
  "status": "success"
}
```

### Motion Analysis
```http
POST /api/analyze_motion
```

Analyzes motion characteristics:

**Request:**
```json
{
  "motion_data": {
    "frames": [[0,1,2], [1,2,3], [2,3,4]]
  }
}
```

**Response:**
```json
{
  "velocity_stats": {
    "mean_velocity": 1.732,
    "max_velocity": 1.732,
    "velocity_variance": 0.0
  },
  "rhythm_analysis": {
    "periodicity": 0.75,
    "regularity": 0.85,
    "tempo": 120.0
  },
  "style_classification": {
    "neutral": 0.2,
    "aggressive": 0.6,
    "graceful": 0.1,
    "robotic": 0.1
  },
  "quality_score": 0.88,
  "processing_time": 0.002,
  "status": "success"
}
```

## Advanced Features

### Neural Network Inference

The server performs real PyTorch inference:

1. **Checkpoint Loading**: Loads trained model weights
2. **GPU Acceleration**: CUDA support when available
3. **Batch Processing**: Efficient tensor operations
4. **Memory Management**: Optimized for real-time performance

### Quality Metrics

Advanced motion quality analysis:

- **Smoothness**: Acceleration variance analysis
- **Naturalness**: Velocity pattern evaluation
- **Style Preservation**: Style code influence measurement
- **Temporal Consistency**: Frame-to-frame change analysis

### Enhanced Algorithms

When neural networks unavailable, sophisticated fallback algorithms:

- **Smooth Interpolation**: Cubic smoothstep functions
- **Style Integration**: Temporal variation with style influence
- **FFT Analysis**: Frequency-domain rhythm detection
- **Motion Classification**: Energy-based style categorization

## Performance Optimization

### Model Loading Strategy

```python
# Progressive loading approach
def try_load_models():
    if models_loaded:
        return True
    
    # Load PyTorch and models on-demand
    # Fallback to enhanced algorithms if needed
```

### Input Processing

- **Automatic Padding**: Handles variable input dimensions
- **Dimension Matching**: Ensures compatibility with model architecture
- **Batch Optimization**: Efficient tensor operations

### Memory Management

- **On-Demand Loading**: Models load only when needed
- **GPU Memory**: Efficient CUDA memory usage
- **Tensor Cleanup**: Proper memory deallocation

## Development Setup

### Dependencies

```bash
# Core dependencies
pip install fastapi uvicorn
pip install torch torchvision torchaudio
pip install pytorch-lightning==1.8.6
pip install numpy scipy

# Web dependencies
pip install jinja2 aiofiles
```

### Running Development Server

```bash
cd output/web_viewer
python rsmt_server_progressive.py
```

### Testing API Endpoints

```bash
# Test all endpoints
curl -s http://localhost:8001/api/status
curl -X POST -H "Content-Type: application/json" -d '{"motion_data":{"frames":[[0,1,2]]}}' http://localhost:8001/api/encode_style
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   pkill -f rsmt_server_progressive
   ```

2. **PyTorch Version Conflicts**
   ```bash
   pip install torch==2.0.1 torchvision==0.15.2 pytorch-lightning==1.8.6
   ```

3. **Model Loading Errors**
   - Check `/output/phase_model/minimal_phase_model.pth` exists
   - Verify PyTorch compatibility
   - Review server logs for detailed error information

### Performance Issues

1. **Slow Model Loading**
   - Models load on first API call (expected)
   - Subsequent calls are much faster

2. **High Memory Usage**
   - Normal for neural network inference
   - GPU memory usage is optimized

### Development Tips

1. **API Testing**: Use curl or Postman for endpoint testing
2. **Logging**: Check terminal output for detailed operation logs
3. **Model Updates**: Restart server after model checkpoint changes
4. **Web Interface**: Refresh browser after server restart

## Integration Examples

### Python Client

```python
import requests

# Test server status
response = requests.get('http://localhost:8001/api/status')
print(response.json())

# Generate transition
transition_data = {
    "start_motion": {"frames": [[0,1,2]]},
    "target_motion": {"frames": [[5,6,7]]},
    "style_code": [0.1, 0.2, 0.3],
    "transition_length": 10
}

response = requests.post(
    'http://localhost:8001/api/generate_transition',
    json=transition_data
)
print(response.json())
```

### JavaScript Client

```javascript
// Test API from web interface
async function generateTransition(startMotion, targetMotion, styleCode) {
    const response = await fetch('/api/generate_transition', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            start_motion: startMotion,
            target_motion: targetMotion,
            style_code: styleCode,
            transition_length: 30
        })
    });
    
    return await response.json();
}
```

This web interface provides a powerful, user-friendly way to interact with the RSMT neural network models in real-time through a modern web browser.
