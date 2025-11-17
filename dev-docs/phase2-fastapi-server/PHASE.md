---
phase: 2
title: FastAPI Server Implementation
started: 2025-11-17T20:55:27+09:00
status: in-progress
---

# Phase 2: FastAPI Server Implementation

## Objective

Phase 1에서 검증된 DeepSeek-OCR 추론 파이프라인을 FastAPI 서버로 래핑하여 HTTP API로 제공합니다.

## Key Architecture Decisions

### 1. Singleton AsyncEngine Pattern

Problem: 엔진 초기화에 27.3초 + 6.23 GiB GPU 메모리 소요
Solution: 서버 시작 시 1회만 로드, 모든 요청이 동일한 엔진 인스턴스 공유

Implementation: FastAPI lifespan context manager 사용

### 2. Worker Configuration

Workers: 1 (필수)
Reason: AsyncEngine은 프로세스별 CUDA 컨텍스트 사용, 여러 워커는 GPU 메모리 고갈

Concurrency: 단일 워커 내에서 async 동시성으로 처리

### 3. API Design

Primary Endpoint: POST /api/v1/ocr
- Input: multipart/form-data (file, type, prompt, stream)
- Output: Streaming or full markdown text
- Validation: File type (jpg/png), size (10MB limit)

Health Endpoints: GET /health, GET /models

## Tasks

1. ⏳ Project structure setup
   - Create api/ directory structure
   - Create __init__.py files
   - Set up logging configuration

2. ⏳ Core configuration
   - Implement api/core/config.py with Pydantic settings
   - Implement api/core/errors.py with custom exceptions
   - Implement api/core/logging.py with structured logging

3. ⏳ Engine Manager
   - Implement api/services/engine.py with singleton pattern
   - Add async initialization
   - Add health check methods

4. ⏳ Preprocessing Service
   - Implement api/services/preprocessor.py
   - Port image loading logic from run_dpsk_ocr_image.py
   - Add prompt template handling

5. ⏳ Postprocessing Service
   - Implement api/services/postprocessor.py
   - Add markdown cleaning logic
   - Add special token removal

6. ⏳ Request/Response Models
   - Define Pydantic models in api/models/request.py
   - Define Pydantic models in api/models/response.py
   - Add validation rules

7. ⏳ Validators
   - Implement api/utils/validators.py
   - Add file type validation
   - Add file size validation

8. ⏳ Health Endpoint
   - Implement api/routes/health.py
   - Add /health endpoint
   - Add /models endpoint

9. ⏳ OCR Endpoint
   - Implement api/routes/ocr.py
   - Add streaming response handler
   - Add non-streaming response handler

10. ⏳ Main Application
    - Implement api/main.py with lifespan
    - Configure CORS middleware
    - Add error handlers

11. ⏳ Docker Integration
    - Update requirements.txt
    - Update docker-compose.yml command
    - Test container startup

12. ⏳ Testing
    - Write unit tests
    - Write integration tests
    - Create manual test script

13. ⏳ Documentation
    - Update PROJECT_PLAN.md
    - Create API documentation
    - Add usage examples

## Success Criteria

- Server starts successfully with AsyncEngine initialized
- POST /ocr endpoint accepts images and returns markdown
- Streaming responses work correctly
- File validation prevents invalid inputs
- Error handling covers common failure cases
- Health check endpoint reports accurate status
- API documentation is complete
- Manual tests pass with sample images

## Expected Performance

- Cold start: 27.3s (server first start, one time)
- Warm inference: ~3s per image
- Throughput: ~15-20 requests/minute
- GPU memory: 40GB (within limit)

## New Dependencies

- fastapi==0.115.0
- uvicorn[standard]==0.32.0
- python-multipart==0.0.12
- pydantic==2.9.0
- pydantic-settings==2.5.2

## Plans

- plans/fastapi-architecture.md - Detailed architecture and implementation plan

## Issues

(none yet)

## Notes

(none yet)
