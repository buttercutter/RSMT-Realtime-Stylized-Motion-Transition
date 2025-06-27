# RSMT Deployment Guide

This guide covers deploying the RSMT neural network server for production use.

## Quick Local Deployment

### Prerequisites

```bash
# Python 3.8+
python --version

# Required packages
pip install fastapi uvicorn torch torchvision pytorch-lightning numpy scipy
```

### Start Server

```bash
cd /home/barberb/RSMT-Realtime-Stylized-Motion-Transition
python output/web_viewer/rsmt_server_progressive.py
```

Server will be available at `http://localhost:8001`

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn

# Start with multiple workers
cd output/web_viewer
gunicorn rsmt_server_progressive:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8001

# Start server
CMD ["python", "output/web_viewer/rsmt_server_progressive.py"]
```

Build and run:

```bash
docker build -t rsmt-server .
docker run -p 8001:8001 rsmt-server
```

### Environment Variables

```bash
# Server configuration
export RSMT_HOST=0.0.0.0
export RSMT_PORT=8001
export RSMT_WORKERS=4

# Model paths
export RSMT_MODEL_PATH=/path/to/models
export RSMT_CHECKPOINT_PATH=/path/to/checkpoint.pth

# GPU configuration
export CUDA_VISIBLE_DEVICES=0
```

## Nginx Configuration

For production with SSL:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Performance Tuning

### Model Loading Optimization

```python
# Pre-load models at startup
def preload_models():
    try_load_models()

# Add to server startup
@app.on_event("startup")
async def startup_event():
    preload_models()
```

### Memory Management

```python
# Clear GPU cache periodically
import torch

def clear_gpu_cache():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
```

### CPU Optimization

```bash
# Set optimal thread count
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
```

## Monitoring

### Health Checks

```bash
# Simple health check
curl http://localhost:8001/api/status

# Response time monitoring
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8001/api/status
```

### Logging Configuration

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rsmt_server.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Metrics

```python
import time
import psutil

# Monitor resource usage
def get_system_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "gpu_memory": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
    }
```

## Security Considerations

### CORS Configuration

```python
# Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### API Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/generate_transition")
@limiter.limit("10/minute")
async def generate_transition(request: Request, ...):
    # Endpoint implementation
```

### Input Validation

```python
from pydantic import validator

class TransitionRequest(BaseModel):
    # ... existing fields ...
    
    @validator('transition_length')
    def validate_length(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('transition_length must be between 1 and 1000')
        return v
```

## Scaling

### Horizontal Scaling

```bash
# Run multiple instances
python rsmt_server_progressive.py --port 8001 &
python rsmt_server_progressive.py --port 8002 &
python rsmt_server_progressive.py --port 8003 &
```

### Load Balancer Configuration

```nginx
upstream rsmt_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    location / {
        proxy_pass http://rsmt_backend;
    }
}
```

### GPU Scaling

```python
# Multi-GPU support
if torch.cuda.device_count() > 1:
    model = torch.nn.DataParallel(model)
```

## Backup and Recovery

### Model Checkpoints

```bash
# Backup model files
cp -r output/phase_model/ backup/phase_model_$(date +%Y%m%d)/
```

### Configuration Backup

```bash
# Backup server configuration
cp output/web_viewer/rsmt_server_progressive.py backup/
cp requirements.txt backup/
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   sudo lsof -i :8001
   kill -9 <PID>
   ```

2. **Out of Memory**
   ```bash
   # Reduce batch size or model complexity
   export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
   ```

3. **Model Loading Errors**
   ```bash
   # Check model file permissions
   ls -la output/phase_model/
   chmod 644 output/phase_model/minimal_phase_model.pth
   ```

### Debug Mode

```bash
# Start server with debug logging
PYTHONPATH=. python output/web_viewer/rsmt_server_progressive.py --log-level debug
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile API endpoints
def profile_endpoint():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # API call code here
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

This deployment guide provides comprehensive instructions for deploying the RSMT neural network server in various environments.
