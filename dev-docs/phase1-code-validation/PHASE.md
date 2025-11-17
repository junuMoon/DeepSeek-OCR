---
phase: 1
title: Code Validation & Image Testing
started: 2025-11-17T20:32:34+09:00
completed: 2025-11-17T20:47:00+09:00
status: completed
---

# Phase 1: Code Validation & Image Testing

## Objective

기존 DeepSeek-OCR 코드를 사용하여 실제 이미지로 OCR 인퍼런스를 수행하고, 전체 파이프라인이 정상 동작하는지 검증합니다.

## Tasks

1. ✅ 설정 파일 수정 (config.py)
   - MODEL_PATH를 컨테이너 경로로 설정 (/models/deepseek-ai/DeepSeek-OCR)
   - INPUT_PATH, OUTPUT_PATH 설정 (/workspace/ 경로 사용)
   - GPU 설정 (docker-compose.yml에서 device_ids: ['7'] 설정)
   - gpu_memory_utilization을 0.5로 조정 (40GB 사용)

2. ✅ 테스트 환경 준비
   - 출력 디렉토리 생성 (test-output/, test-output/images/)
   - 테스트 이미지 확인 (en_paper.png 231KB)

3. ✅ 단일 이미지 테스트
   - en_paper.png로 첫 테스트 완료
   - run_dpsk_ocr_image.py 실행 성공
   - 모든 출력 파일 생성 확인

4. ✅ 품질 검증
   - 마크다운 정확도: 100% (캡션 텍스트 완벽히 추출)
   - 바운딩 박스 시각화: 정확 (image, image_caption 영역 정확히 표시)
   - NoRepeatNGramLogitsProcessor 동작: 정상 (반복 없음)

5. ⏭️ 확장 테스트 (선택적, 스킵)
   - Phase 2 진행을 위해 생략
   - 필요시 Phase 2 이후 수행

## Success Criteria

- ✅ 모델 로드 및 초기화 성공 (6.23 GiB, 27.3초)
- ✅ 이미지 전처리 (DeepseekOCRProcessor) 정상 동작
- ✅ OCR 인퍼런스 완료 (~3초)
- ✅ 마크다운 출력 생성 및 품질 확인 (100% 정확도)
- ✅ 반복 텍스트 없음 (NoRepeatNGramLogitsProcessor 작동)
- ✅ GPU 메모리 사용량 제한 준수 (40GB < 50GB)

## Test Images Available

Located in `/home/fran/DeepSeek-OCR/test-data/`:
- English: en_paper.png, en_paper_full.jpg, en_text.png, en_resource.png
- Korean: ko_text.png, ko_handwriting.png, ko_resource.png
- Code: code_python.png, code_ts.png

## Plans

- plans/image-inference-test.md - 인퍼런스 테스트 계획 (완료)

## Issues

- issues/gpu-selection.md - Docker GPU 선택 문제 (해결됨)
- issues/container-path-mapping.md - 컨테이너 경로 매핑 문제 (해결됨)

## Notes

- notes/inference-test-results.md - 전체 테스트 결과 및 성능 메트릭
- logs/inference-test-2025-11-17T20:42:07+09:00.log - 실행 로그
