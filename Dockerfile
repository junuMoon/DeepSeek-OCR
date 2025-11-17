FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    wget \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set python3 as default python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Upgrade pip
RUN python3 -m pip install --upgrade pip setuptools wheel

# Set TRITON_PTXAS_PATH for CUDA 11.8 compatibility
ENV TRITON_PTXAS_PATH=/usr/local/cuda-11.8/bin/ptxas

# Install PyTorch 2.6.0 with CUDA 11.8
RUN pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \
    --index-url https://download.pytorch.org/whl/cu118

# Install vLLM from GitHub release
RUN pip install https://github.com/vllm-project/vllm/releases/download/v0.8.5/vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl

# Set vLLM environment
ENV VLLM_USE_V1=0

# Copy project requirements
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Install flash-attn (this can take a while)
RUN pip install flash-attn==2.7.3 --no-build-isolation

# Copy DeepSeek-OCR code
COPY DeepSeek-OCR-master /app/DeepSeek-OCR-master

# Copy FastAPI application
COPY api /app/api

# Set working directory
WORKDIR /app

# Add DeepSeek-OCR-vllm to Python path for imports
ENV PYTHONPATH=/app:/app/DeepSeek-OCR-master/DeepSeek-OCR-vllm:$PYTHONPATH

# Default command
CMD ["/bin/bash"]
