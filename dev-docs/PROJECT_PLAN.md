---
project: DeepSeek-OCR vLLM Inference Server
started: 2025-11-17T19:42:07+09:00
updated: 2025-11-17T20:32:34+09:00
status: in-progress
current_phase: 1
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

### Phase 1: Code Validation (in-progress - started 2025-11-17T20:32:34+09:00)
- config.py 설정 (MODEL_PATH, INPUT_PATH, OUTPUT_PATH)
- 테스트 환경 준비 (출력 디렉토리)
- 단일 이미지 테스트 (en_paper.png)
- DeepseekOCRProcessor, NoRepeatNGramLogitsProcessor 동작 확인
- 품질 검증 (마크다운, 바운딩 박스)
- 확장 테스트 (다양한 이미지 타입)

### Phase 2: FastAPI Server (planned)
- FastAPI 서버 구현 (POST /ocr 엔드포인트)
- vLLM AsyncEngine 싱글톤 관리
- 이미지 전처리 파이프라인 통합
- API 테스트 및 에러 핸들링
