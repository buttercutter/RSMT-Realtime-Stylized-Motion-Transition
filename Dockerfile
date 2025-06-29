# Multi-stage build for RSMT (Real-time Stylized Motion Transition)
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r rsmt && useradd -r -g rsmt rsmt

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Copy source code
COPY . .

# Install package in development mode
RUN pip install -e .

# Change ownership
RUN chown -R rsmt:rsmt /app

USER rsmt

# Expose ports
EXPOSE 8001 8888

CMD ["python", "rsmt/web/server.py"]

# Production stage
FROM base as production

# Copy only necessary files
COPY rsmt/ ./rsmt/
COPY scripts/ ./scripts/
COPY pyproject.toml setup.py README.md ./

# Install package
RUN pip install .

# Create directories for data and models
RUN mkdir -p /app/data/{datasets,models,outputs} && \
    chown -R rsmt:rsmt /app

USER rsmt

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/status || exit 1

# Expose port
EXPOSE 8001

# Default command
CMD ["python", "-m", "rsmt.web.server"]

# GPU-enabled stage
FROM nvidia/cuda:11.8-runtime-ubuntu20.04 as gpu

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    build-essential \
    git \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Create app user
RUN groupadd -r rsmt && useradd -r -g rsmt rsmt

# Set work directory
WORKDIR /app

# Copy requirements
COPY requirements.txt ./

# Install Python dependencies with CUDA support
RUN pip install --upgrade pip && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
    pip install -r requirements.txt

# Copy and install package
COPY rsmt/ ./rsmt/
COPY scripts/ ./scripts/
COPY pyproject.toml setup.py README.md ./

RUN pip install .

# Create directories
RUN mkdir -p /app/data/{datasets,models,outputs} && \
    chown -R rsmt:rsmt /app

USER rsmt

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/status || exit 1

# Expose port
EXPOSE 8001

# Default command
CMD ["python", "-m", "rsmt.web.server"]
