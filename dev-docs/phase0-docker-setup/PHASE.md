---
phase: 0
title: Docker Setup
started: 2025-11-17T19:42:07+09:00
completed: 2025-11-17T20:26:20+09:00
status: completed
---

# Phase 0: Docker Setup

## Objective

vLLM 0.8.5 + PyTorch 2.6.0 + CUDA 11.8 환경을 Docker로 구축하고 기본 인퍼런스가 동작하는지 검증합니다.

## Tasks

1. Dockerfile 작성
   - Base image: nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
   - PyTorch 2.6.0 설치
   - vLLM 0.8.5 whl 설치
   - 기존 requirements.txt 반영

2. docker-compose.yml 작성
   - GPU 설정 (runtime: nvidia)
   - 볼륨 마운트 (모델 경로, 코드)
   - 환경변수 (.env 연동)

3. .env 파일 생성
   - MODEL_PATH
   - PORT
   - 기타 설정

4. Container 빌드 및 실행
   - Build 성공 확인
   - GPU 인식 확인

5. 기본 vLLM 인퍼런스 테스트
   - Python 셸에서 LLM 로드
   - 간단한 텍스트 프롬프트 테스트

## Plans

- [completed] docker-environment.md: Docker 환경 구축

## Issues

1. [completed] python-version-compatibility.md: Python 3.12 unavailable in Ubuntu 22.04
2. [completed] vllm-wheel-download.md: Inefficient wheel handling (local copy)
3. [completed] custom-model-registration.md: Model requires custom vLLM registration

## Notes

1. [completed] memory-requirements.md: GPU memory analysis for different configurations

## Summary

✅ Successfully built Docker environment with:
- CUDA 11.8 + PyTorch 2.6.0 + vLLM 0.8.5
- Python 3.10.12 (Ubuntu 22.04 default)
- Custom DeepSeek-OCR model registration working
- Model loads successfully (6.23 GiB)
- GPU: NVIDIA A100-SXM4-80GB verified

**Key Findings:**
- Custom model registration required via `ModelRegistry.register_model()`
- Memory requirements: 25-60GB depending on max_model_len
- Full config (8192 tokens) needs dedicated GPU with ~60GB free
