# RSMT API Documentation

This document provides comprehensive documentation for the RSMT Neural Network Server API endpoints.

## Base URL

```
http://localhost:8001
```

## Authentication

No authentication required for local development.

## Response Format

All API responses follow this structure:

```json
{
  "status": "success|error",
  "processing_time": 0.001,
  "...": "endpoint-specific data"
}
```

## Endpoints

### 1. Server Status

Get server status and model information.

#### Request
```http
GET /api/status
```

#### Response
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
  "timestamp": "2025-06-27T05:26:02Z",
  "gpu_available": true,
  "torch_version": "2.7.0+cu126",
  "models_initialized": true
}
```

#### Model Status Fields
- `deephase`: DeepPhase model loaded and ready
- `stylevae`: StyleVAE model loaded and ready
- `transitionnet`: TransitionNet model loaded and ready
- `skeleton`: Skeleton structure loaded and ready
- `models_initialized`: All models successfully initialized

---

### 2. Phase Encoding

Encode motion data into 2D phase manifold coordinates using the DeepPhase neural network.

#### Request
```http
POST /api/encode_phase
```

#### Request Body
```json
{
  "motion_data": {
    "frames": [
      [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
      [0.1, 1.1, 2.1, 3.1, 4.1, 5.1],
      [0.2, 1.2, 2.2, 3.2, 4.2, 5.2]
    ],
    "frame_time": 0.016667
  },
  "sequence_length": 60
}
```

#### Request Parameters
- `motion_data.frames`: Array of motion frames, each frame containing joint positions
- `motion_data.frame_time`: Time between frames in seconds (default: 0.016667 for 60 FPS)
- `sequence_length`: Maximum number of frames to process (optional, default: 60)

#### Response
```json
{
  "phase_coordinates": [
    [0.1, 0.2],
    [0.3, 0.4],
    [0.5, 0.6]
  ],
  "processing_time": 0.0024,
  "status": "success"
}
```

#### Response Fields
- `phase_coordinates`: Array of [sx, sy] coordinate pairs representing phase manifold positions
- `processing_time`: Time taken for neural network inference
- `status`: "success" or "error"

---

### 3. Style Encoding

Extract a 256-dimensional style vector from motion data using the StyleVAE neural network.

#### Request
```http
POST /api/encode_style
```

#### Request Body
```json
{
  "motion_data": {
    "frames": [
      [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
      [0.1, 1.1, 2.1, 3.1, 4.1, 5.1]
    ]
  },
  "phase_data": [
    [0.1, 0.2],
    [0.3, 0.4]
  ]
}
```

#### Request Parameters
- `motion_data.frames`: Array of motion frames
- `phase_data`: Optional phase coordinates (if available from previous encoding)

#### Response
```json
{
  "style_code": [
    -0.085, 0.037, 0.074, -0.029, 0.072, -0.085,
    "... 250 more values ..."
  ],
  "processing_time": 3.231,
  "status": "success"
}
```

#### Response Fields
- `style_code`: 256-dimensional style vector encoding motion characteristics
- `processing_time`: Time taken for neural network inference
- `status`: "success" or "error"

---

### 4. Motion Transition Generation

Generate smooth motion transitions between two motion sequences using neural networks.

#### Request
```http
POST /api/generate_transition
```

#### Request Body
```json
{
  "start_motion": {
    "frames": [
      [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
      [0.1, 0.1, 0.1, 1.1, 1.1, 1.1]
    ]
  },
  "target_motion": {
    "frames": [
      [5.0, 5.0, 5.0, 6.0, 6.0, 6.0],
      [5.1, 5.1, 5.1, 6.1, 6.1, 6.1]
    ]
  },
  "style_code": [0.1, 0.2, 0.3, 0.4, 0.5],
  "transition_length": 30,
  "transition_type": "smooth"
}
```

#### Request Parameters
- `start_motion.frames`: Starting motion sequence frames
- `target_motion.frames`: Target motion sequence frames  
- `style_code`: Style vector to influence the transition (from style encoding)
- `transition_length`: Number of transition frames to generate (default: 30)
- `transition_type`: Type of transition - "smooth", "linear", etc. (optional)

#### Response
```json
{
  "transition_frames": [
    [0.103, 0.099, 0.101, 1.099, 1.098, 1.100],
    [0.866, 0.867, 0.869, 1.868, 1.871, 1.865],
    "... more transition frames ..."
  ],
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

#### Response Fields
- `transition_frames`: Array of generated transition frames
- `quality_metrics`: Motion quality analysis
  - `smoothness`: Acceleration variance-based smoothness score (0-1)
  - `naturalness`: Velocity pattern naturalness score (0-1)
  - `style_preservation`: How well the style is preserved (0-1)
  - `temporal_consistency`: Frame-to-frame consistency score (0-1)
- `processing_time`: Time taken for transition generation
- `status`: "success" or "error"

---

### 5. Motion Analysis

Analyze motion data for velocity, rhythm, style characteristics, and overall quality.

#### Request
```http
POST /api/analyze_motion
```

#### Request Body
```json
{
  "motion_data": {
    "frames": [
      [0.0, 1.0, 2.0],
      [1.0, 2.0, 3.0],
      [2.0, 3.0, 4.0],
      [3.0, 4.0, 5.0]
    ],
    "frame_time": 0.016667
  }
}
```

#### Request Parameters
- `motion_data.frames`: Array of motion frames to analyze
- `motion_data.frame_time`: Time between frames (for tempo calculation)

#### Response
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

#### Response Fields
- `velocity_stats`: Motion velocity analysis
  - `mean_velocity`: Average motion velocity
  - `max_velocity`: Maximum velocity in sequence
  - `velocity_variance`: Velocity variation measure
- `rhythm_analysis`: FFT-based rhythm detection
  - `periodicity`: How periodic the motion is (0-1)
  - `regularity`: How regular the rhythm is (0-1)
  - `tempo`: Estimated tempo in BPM
- `style_classification`: Motion style probabilities
  - `neutral`: Neutral motion probability (0-1)
  - `aggressive`: Aggressive motion probability (0-1)
  - `graceful`: Graceful motion probability (0-1)
  - `robotic`: Robotic motion probability (0-1)
- `quality_score`: Overall motion quality (0-1)
- `processing_time`: Time taken for analysis
- `status`: "success" or "error"

## Data Formats

### Motion Frame Format

Each motion frame represents joint positions as a flat array:

```json
[
  x1, y1, z1,  // Joint 1 position
  x2, y2, z2,  // Joint 2 position
  ...
  xN, yN, zN   // Joint N position
]
```

### Skeleton Structure

The server uses a 21-joint skeleton:

```
Root, Hip, Spine, Spine1, Neck,
LeftShoulder, LeftArm, LeftForeArm, LeftHand,
RightShoulder, RightArm, RightForeArm, RightHand,
LeftUpLeg, LeftLeg, LeftFoot, LeftToe,
RightUpLeg, RightLeg, RightFoot, RightToe
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error description",
  "status": "error"
}
```

### Common Error Codes

#### 503 Service Unavailable
- Neural network models not loaded
- Server not ready

#### 422 Unprocessable Entity
- Invalid request format
- Missing required fields
- Invalid data types

#### 500 Internal Server Error
- Neural network inference error
- Unexpected server error

### Example Error Responses

#### Model Not Loaded
```json
{
  "detail": "Neural network models not available",
  "status": "error"
}
```

#### Invalid Input Format
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "motion_data"],
      "msg": "Field required"
    }
  ]
}
```

## Rate Limiting

No rate limiting currently implemented for local development.

## Performance Notes

### Model Loading
- Models load on first API call (2-5 second delay)
- Subsequent calls are much faster (< 100ms typical)
- Models remain loaded until server restart

### Processing Times
- **Phase Encoding**: ~1-10ms per request
- **Style Encoding**: ~1-5 seconds (neural network inference)
- **Transition Generation**: ~10-50ms depending on length
- **Motion Analysis**: ~1-5ms per request

### Input Size Limits
- **Motion Frames**: Recommended < 1000 frames per request
- **Transition Length**: Recommended < 100 frames
- **Frame Dimensions**: Automatically padded/truncated to 132 dimensions

## Code Examples

### Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8001"

def test_rsmt_api():
    # Test server status
    response = requests.get(f"{BASE_URL}/api/status")
    print("Status:", response.json())
    
    # Test motion encoding
    motion_data = {
        "motion_data": {
            "frames": [
                [0, 1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5, 6]
            ]
        }
    }
    
    # Get style code
    style_response = requests.post(
        f"{BASE_URL}/api/encode_style",
        json=motion_data
    )
    style_code = style_response.json()["style_code"]
    
    # Generate transition
    transition_data = {
        "start_motion": {"frames": [[0, 1, 2]]},
        "target_motion": {"frames": [[5, 6, 7]]},
        "style_code": style_code[:10],  # Use first 10 elements
        "transition_length": 5
    }
    
    transition_response = requests.post(
        f"{BASE_URL}/api/generate_transition",
        json=transition_data
    )
    
    print("Transition:", transition_response.json())

if __name__ == "__main__":
    test_rsmt_api()
```

### JavaScript/Browser Example

```javascript
class RSMTClient {
    constructor(baseUrl = 'http://localhost:8001') {
        this.baseUrl = baseUrl;
    }
    
    async getStatus() {
        const response = await fetch(`${this.baseUrl}/api/status`);
        return await response.json();
    }
    
    async encodeStyle(motionFrames) {
        const response = await fetch(`${this.baseUrl}/api/encode_style`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                motion_data: {frames: motionFrames}
            })
        });
        return await response.json();
    }
    
    async generateTransition(startFrames, targetFrames, styleCode, length = 30) {
        const response = await fetch(`${this.baseUrl}/api/generate_transition`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                start_motion: {frames: startFrames},
                target_motion: {frames: targetFrames},
                style_code: styleCode,
                transition_length: length
            })
        });
        return await response.json();
    }
}

// Usage
const client = new RSMTClient();

client.getStatus().then(status => {
    console.log('Server status:', status);
});
```

This API provides comprehensive access to the RSMT neural network capabilities for real-time motion transition generation and analysis.
