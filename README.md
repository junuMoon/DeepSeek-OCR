# DeepSeek-OCR FastAPI Server

Production-ready FastAPI server for DeepSeek-OCR inference using vLLM AsyncEngine.

## Features

- REST API with OpenAPI documentation (Swagger UI)
- Asynchronous inference using vLLM AsyncEngine
- Docker-based deployment with CUDA support
- Document and image OCR endpoints
- Health monitoring

## Quick Start

### Prerequisites

- Docker with NVIDIA Container Toolkit
- NVIDIA GPU (tested on A100 80GB)
- Model files from [Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-OCR)

### Installation

1. Clone and configure:
```bash
git clone https://github.com/deepseek-ai/DeepSeek-OCR.git
cd DeepSeek-OCR

# Edit .env file
MODEL_PATH=/path/to/DeepSeek-OCR
PORT=8000
CUDA_VISIBLE_DEVICES=0
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

3. Access the API:
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Usage

### OCR Endpoint

```bash
# Document OCR
curl -X POST "http://localhost:8000/api/v1/ocr" \
  -F "file=@document.png" \
  -F "type=document"

# Image OCR with custom prompt
curl -X POST "http://localhost:8000/api/v1/ocr" \
  -F "file=@image.jpg" \
  -F "type=image" \
  -F "prompt=Describe this image in detail."
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Performance

- Server startup: ~27s (AsyncEngine initialization)
- Inference: ~3-4s per image
- GPU memory: ~40GB (A100)

## Development

See `dev-docs/` for detailed implementation notes:
- PROJECT_PLAN.md - Overall architecture
- phase2-fastapi-server/ - API implementation details

## Links

- [Model on Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-OCR)
- [Paper (arXiv)](https://arxiv.org/abs/2510.18234)
- [Original Repository](https://github.com/deepseek-ai/DeepSeek-OCR)
