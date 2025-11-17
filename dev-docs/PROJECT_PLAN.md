---
project: DeepSeek-OCR vLLM Inference Server
started: 2025-11-17T19:42:07+09:00
updated: 2025-11-17T21:11:10+09:00
status: completed
current_phase: 2
---

# DeepSeek-OCR vLLM Inference Server

## Project Overview

vLLM OpenAI 프로토콜로는 DeepSeek-OCR 모델의 커스텀 로직(DeepseekOCRProcessor, NoRepeatNGramLogitsProcessor)이 적용되지 않는 문제를 해결하기 위해, Docker 환경에서 FastAPI + vLLM AsyncEngine 기반의 커스텀 인퍼런스 서버를 구축합니다.

## Architecture

```
Client
  ↓ (HTTP multipart/form-data)
FastAPI Server (Docker)
  ├─ POST /ocr (type 파라미터로 document/image 구분)
  ├─ DeepseekOCRProcessor (이미지 전처리)
  ├─ vLLM AsyncEngine (앱 시작시 로드)
  └─ Markdown 텍스트 반환
```

## Key Requirements

- Model Path: `/nfs/train/llm-lab/models/deepseek-ai/DeepSeek-OCR`
- Environment: Docker (CUDA 11.8 + PyTorch 2.6.0 + vLLM 0.8.5)
- Input: Multipart file upload
- Output: Markdown text only
- Prompts: Default (document/image) + custom support
- Config: .env file

## Timeline

### Phase 0: Docker Setup (completed - 2025-11-17T20:26:20+09:00)
- ✅ Dockerfile 작성 (Python 3.10, CUDA 11.8, PyTorch 2.6.0, vLLM 0.8.5)
- ✅ docker-compose.yml, .env 작성
- ✅ GPU 확인 (NVIDIA A100-SXM4-80GB)
- ✅ 커스텀 모델 등록 및 로드 성공 (6.23 GiB)
- Issues resolved: Python 3.12→3.10, vLLM wheel optimization, custom model registration

### Phase 1: Code Validation (completed - 2025-11-17T20:47:00+09:00)
- ✅ config.py 설정 (MODEL_PATH, INPUT_PATH, OUTPUT_PATH)
- ✅ GPU 설정 (GPU 7 사용, 메모리 50% = 40GB)
- ✅ 테스트 환경 준비 (출력 디렉토리)
- ✅ 단일 이미지 테스트 (en_paper.png) - 100% 정확도
- ✅ DeepseekOCRProcessor, NoRepeatNGramLogitsProcessor 동작 확인
- ✅ 품질 검증 (마크다운, 바운딩 박스)
- Issues resolved: GPU selection, container path mapping
- Performance: 27.3s initialization, ~3s inference, 40GB GPU memory

### Phase 2: FastAPI Server (completed - 2025-11-17T21:11:10+09:00)
- ✅ API 구조 설계 및 구현 (api/core, api/services, api/models, api/routers)
- ✅ EngineManager 싱글톤 (FastAPI lifespan에서 초기화)
- ✅ ImagePreprocessor (DeepseekOCRProcessor 통합, 파일 검증)
- ✅ OutputPostprocessor (마크다운 정리, 특수 토큰 제거)
- ✅ Pydantic 모델 (OCRRequest, OCRResponse, HealthResponse, ModelInfo)
- ✅ API 엔드포인트 (GET /, GET /health, GET /models, POST /api/v1/ocr)
- ✅ Docker 통합 (Dockerfile, docker-compose.yml 업데이트)
- ✅ 테스트 및 검증 (en_paper.png, Phase 1과 동일한 결과 확인)
- Issues resolved: Module import paths (PYTHONPATH), GPU device mapping (CUDA_VISIBLE_DEVICES)
- Performance: 27s server startup, ~3.7s per OCR request (Phase 1과 동일)
- API Docs: http://localhost:8000/docs (Swagger UI)
