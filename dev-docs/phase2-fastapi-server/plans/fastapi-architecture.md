---
phase: 2
date: 2025-11-17T20:55:27+09:00
status: in-progress
related: [../PHASE.md, ../../phase1-code-validation/notes/inference-test-results.md]
---

# FastAPI Server Architecture Plan

## Overview

This plan details the FastAPI server implementation that wraps the validated DeepSeek-OCR vLLM AsyncEngine inference pipeline from Phase 1.

## Project Structure

```
/app
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── ocr.py          # POST /api/v1/ocr
│   │   └── health.py       # GET /health, GET /models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── engine.py       # EngineManager singleton
│   │   ├── preprocessor.py # Image preprocessing
│   │   └── postprocessor.py # Markdown cleaning
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py      # Pydantic request models
│   │   └── response.py     # Pydantic response models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration with pydantic-settings
│   │   ├── logging.py      # Structured logging setup
│   │   └── errors.py       # Custom exception classes
│   └── utils/
│       ├── __init__.py
│       └── validators.py   # File validation utilities
└── DeepSeek-OCR-master/    # Existing validated code (Phase 1)
```

## Component Design

### 1. Lifespan Management (api/main.py)

FastAPI lifespan context manager handles AsyncEngine lifecycle:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize singleton AsyncEngine once
    logger.info("Initializing AsyncEngine...")
    app.state.engine_manager = EngineManager()
    await app.state.engine_manager.initialize()
    logger.info("Server ready")

    yield  # Server runs here

    # Shutdown: Cleanup
    logger.info("Shutting down")

app = FastAPI(lifespan=lifespan)
```

Benefits:
- Engine loads once (27.3s startup delay, but only at server start)
- Engine persists across all requests (shared singleton)
- Proper async context management
- Clean shutdown handling

### 2. EngineManager Singleton (api/services/engine.py)

Manages AsyncEngine lifecycle with thread-safe singleton pattern:

```python
class EngineManager:
    def __init__(self):
        self.engine = None
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self):
        async with self._lock:
            if not self._initialized:
                # Register custom model
                ModelRegistry.register_model("DeepseekOCRForCausalLM", DeepseekOCRForCausalLM)

                # Create engine
                engine_args = AsyncEngineArgs(
                    model=settings.model_path,
                    hf_overrides={"architectures": ["DeepseekOCRForCausalLM"]},
                    block_size=256,
                    max_model_len=8192,
                    enforce_eager=False,
                    trust_remote_code=True,
                    tensor_parallel_size=1,
                    gpu_memory_utilization=0.5,
                )
                self.engine = AsyncLLMEngine.from_engine_args(engine_args)
                self._initialized = True

    async def get_engine(self):
        if not self._initialized:
            await self.initialize()
        return self.engine
```

Critical: Double-check locking ensures only one engine is created even with concurrent requests during startup.

### 3. Request Flow (api/routes/ocr.py)

```
Client Request
    ↓
Validate File (type, size)
    ↓
Load PIL Image
    ↓
Preprocess (DeepseekOCRProcessor)
    ↓
Generate (AsyncEngine with NoRepeatNGramLogitsProcessor)
    ↓
Stream/Return Markdown
    ↓
Response
```

Key points:
- File validation before loading (prevent memory bombs)
- Async streaming for real-time feedback
- Error handling at each step

### 4. Configuration Management (api/core/config.py)

Using pydantic-settings for environment variable management:

```python
class Settings(BaseSettings):
    # Model
    model_path: str = "/models/deepseek-ai/DeepSeek-OCR"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1  # MUST be 1

    # GPU
    cuda_device: str = "7"
    gpu_memory_utilization: float = 0.5

    # Limits
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list[str] = ["jpg", "jpeg", "png"]

    class Config:
        env_file = ".env"

settings = Settings()
```

### 5. Error Handling Strategy

Custom exception hierarchy:

```python
class OCRError(Exception): pass
class EngineNotReadyError(OCRError): pass
class PreprocessingError(OCRError): pass
class InferenceError(OCRError): pass
class FileValidationError(OCRError): pass
```

FastAPI exception handlers convert to proper HTTP responses:
- FileValidationError → 400 Bad Request
- EngineNotReadyError → 503 Service Unavailable
- Exception → 500 Internal Server Error

## API Specification

### POST /api/v1/ocr

Extract text from image/document.

**Request:**
```
Content-Type: multipart/form-data

file: (required) Image file (jpg, png, jpeg)
type: (optional) "document" or "image" (default: "document")
prompt: (optional) Custom prompt override
stream: (optional) Enable streaming (default: true)
```

**Response (streaming):**
```
Content-Type: text/event-stream

data: {"text": "chunk1"}
data: {"text": "chunk2"}
...
data: {"done": true}
```

**Response (non-streaming):**
```json
{
  "text": "Full markdown...",
  "metadata": {
    "image_width": 1024,
    "image_height": 768,
    "processing_time": 3.2
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "engine_ready": true,
  "gpu_memory_used": "40GB"
}
```

### GET /models

Model information.

**Response:**
```json
{
  "model": "deepseek-ai/DeepSeek-OCR",
  "capabilities": ["document", "image"],
  "max_image_size": "6400x6400",
  "supported_formats": ["jpg", "png", "jpeg"]
}
```

## Implementation Sequence

### Phase 2.1: Core Infrastructure (Tasks 1-3)
- Create project structure
- Implement core modules (config, logging, errors)
- Implement EngineManager

### Phase 2.2: Services (Tasks 4-5)
- Implement preprocessor (image loading, DeepseekOCRProcessor integration)
- Implement postprocessor (markdown cleaning)

### Phase 2.3: API Layer (Tasks 6-10)
- Define Pydantic models
- Implement validators
- Implement health endpoints
- Implement OCR endpoint
- Implement main app with lifespan

### Phase 2.4: Integration & Testing (Tasks 11-13)
- Update Docker configuration
- Write tests
- Update documentation

## Technical Decisions Rationale

### Why Lifespan over @app.on_event?

Lifespan is the modern FastAPI pattern:
- on_event("startup") is deprecated in FastAPI 0.109+
- Better async context management
- Cleaner shutdown handling
- Follows current best practices

### Why Workers=1?

Multiple workers are incompatible with singleton AsyncEngine:
- Each worker is a separate process
- CUDA context is per-process
- Multiple engines would each load 6.23 GiB (GPU memory exhaustion)
- AsyncEngine is designed for single persistent instance

Solution: Use workers=1 with async concurrency within the single worker.

### Why Streaming Default?

Streaming improves user experience:
- OCR takes 3+ seconds per image
- Users see immediate progress
- Better for long documents
- Matches original run_dpsk_ocr_image.py behavior

Non-streaming is available for batch/API clients that prefer complete responses.

### Why No Background Queue?

Background queuing (Celery, Redis, etc.) is unnecessary:
- Single GPU processes requests sequentially anyway
- FastAPI async handles concurrent connections efficiently
- vLLM has internal request batching
- Simpler architecture reduces operational complexity

Future optimization: Add queue if multi-GPU setup is needed.

## Performance Expectations

Based on Phase 1 results:

- Cold start: 27.3s (server startup, one-time)
- Model loading: 6.23 GiB GPU memory
- Inference: ~3s per image (en_paper.png baseline)
- GPU memory: 40GB total (50% utilization)
- Throughput: ~15-20 requests/minute

Bottleneck: Single GPU sequential processing
Optimization opportunities (Phase 3+):
- Request batching if multiple images arrive simultaneously
- Multi-GPU deployment with load balancing
- CUDA graph optimization (already enabled with enforce_eager=False)

## Security Considerations

### Input Validation
- File type whitelist (jpg, png, jpeg only)
- File size limit (10MB)
- Image dimension checks (prevent decompression bombs)
- Prompt length limits (prevent token exhaustion)

### Rate Limiting
Future consideration: Add slowapi for per-IP rate limiting

### CORS
Development: Allow all origins
Production: Restrict to trusted domains

## Testing Strategy

### Unit Tests
- Preprocessor: Test image loading, prompt handling
- Postprocessor: Test markdown cleaning
- Validators: Test file type/size validation
- EngineManager: Test singleton pattern (mock AsyncEngine)

### Integration Tests
- End-to-end OCR request (with test image)
- Health endpoint verification
- Error handling (invalid files, engine errors)

### Load Tests
- Concurrent requests handling
- Memory leak detection
- Performance degradation under load

### Manual Tests
```bash
# Health check
curl http://localhost:8000/health

# OCR request (non-streaming)
curl -X POST http://localhost:8000/api/v1/ocr \
  -F "file=@test-data/en_paper.png" \
  -F "type=document" \
  -F "stream=false"

# OCR request (streaming)
curl -X POST http://localhost:8000/api/v1/ocr \
  -F "file=@test-data/en_paper.png" \
  -F "type=document" \
  -F "stream=true" \
  --no-buffer
```

## Docker Integration

### requirements.txt Updates
```
# Add to existing dependencies:
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12
pydantic==2.9.0
pydantic-settings==2.5.2
```

### docker-compose.yml Updates
```yaml
services:
  deepseek-ocr:
    # ... existing config ...
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Change from: `command: /bin/bash` (development)
To: `command: uvicorn ...` (production)

## Success Criteria

- [ ] Server starts successfully in <30s
- [ ] AsyncEngine initializes once and persists
- [ ] POST /ocr accepts images and returns markdown
- [ ] Streaming responses work correctly
- [ ] File validation prevents invalid inputs (wrong type, too large)
- [ ] Health check reports accurate engine status
- [ ] Error handling covers common failure cases
- [ ] Manual tests pass with Phase 1 test images
- [ ] GPU memory stays within 40-50GB limit
- [ ] API documentation is complete

## Next Steps (Phase 3)

After Phase 2 completion, consider:
- Performance optimization (batching, caching)
- Multi-GPU support
- Advanced monitoring (Prometheus, Grafana)
- Rate limiting and authentication
- PDF support (multi-page documents)
- Batch processing endpoint
