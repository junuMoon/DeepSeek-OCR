---
phase: 0
date: 2025-11-17T19:42:07+09:00
completed: 2025-11-17T20:26:20+09:00
status: completed
related: ["../issues/python-version-compatibility.md", "../issues/vllm-wheel-download.md", "../issues/custom-model-registration.md", "../notes/memory-requirements.md"]
---

# Docker Environment Setup Plan

## Context

DeepSeek-OCR는 다음 커스텀 컴포넌트들을 사용합니다:
- `DeepseekOCRForCausalLM`: 커스텀 모델 아키텍처 (run_dpsk_ocr_image.py:16, 26)
- `DeepseekOCRProcessor`: 이미지 전처리 (크롭, 리사이즈) (run_dpsk_ocr_image.py:21, 214)
- `NoRepeatNGramLogitsProcessor`: N-gram 반복 방지 (run_dpsk_ocr_image.py:20, 162)

vLLM OpenAI 서버로는 이들이 적용되지 않아, AsyncEngine을 직접 사용하는 방식으로 구현합니다.

## Requirements

From README.md:65-86:
- CUDA 11.8
- PyTorch 2.6.0
- vLLM 0.8.5 (whl 파일)
- flash-attn 2.7.3
- requirements.txt 패키지들

Model: `/nfs/train/llm-lab/models/deepseek-ai/DeepSeek-OCR` (확인 완료)

## Implementation Steps

### 1. Dockerfile

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Dependencies
RUN apt-get update && apt-get install -y \
    python3.12 python3-pip wget git

# PyTorch
RUN pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \
    --index-url https://download.pytorch.org/whl/cu118

# vLLM whl (download required)
COPY vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl /tmp/
RUN pip install /tmp/vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl

# Project requirements
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

# Flash attention
RUN pip install flash-attn==2.7.3 --no-build-isolation

WORKDIR /app
```

### 2. docker-compose.yml

```yaml
version: '3.8'

services:
  deepseek-ocr:
    build: .
    runtime: nvidia
    environment:
      - CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
      - MODEL_PATH=${MODEL_PATH}
    volumes:
      - /nfs/train/llm-lab/models:/models:ro
      - ./DeepSeek-OCR-master:/app/DeepSeek-OCR-master
      - .:/app
    ports:
      - "${PORT:-8000}:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 3. .env

```
MODEL_PATH=/models/deepseek-ai/DeepSeek-OCR
PORT=8000
CUDA_VISIBLE_DEVICES=0
```

### 4. Build & Test

```bash
# vLLM whl 다운로드 필요
wget https://github.com/vllm-project/vllm/releases/download/v0.8.5/vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl

# Build
docker-compose build

# Run
docker-compose up -d

# Test inside container
docker-compose exec deepseek-ocr python3
>>> import torch
>>> torch.cuda.is_available()
>>> from vllm import LLM
>>> # Basic test
```

## Success Criteria

- Container builds without errors
- GPU is accessible (torch.cuda.is_available() == True)
- vLLM can be imported
- Model can be loaded (basic test)

## Next Steps

After Phase 0 completion:
- Phase 1: Integrate DeepSeek-OCR custom code
- Test with actual images
