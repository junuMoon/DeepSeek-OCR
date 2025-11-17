---
phase: 1
title: Code Validation & Image Testing
started: 2025-11-17T20:32:34+09:00
status: in-progress
---

# Phase 1: Code Validation & Image Testing

## Objective

기존 DeepSeek-OCR 코드를 사용하여 실제 이미지로 OCR 인퍼런스를 수행하고, 전체 파이프라인이 정상 동작하는지 검증합니다.

## Tasks

1. 설정 파일 수정 (config.py)
   - MODEL_PATH를 컨테이너 경로로 설정
   - INPUT_PATH, OUTPUT_PATH 설정

2. 테스트 환경 준비
   - 출력 디렉토리 생성
   - 테스트 이미지 확인

3. 단일 이미지 테스트
   - en_paper.png로 첫 테스트
   - run_dpsk_ocr_image.py 실행
   - 출력 검증

4. 품질 검증
   - 마크다운 정확도
   - 바운딩 박스 시각화
   - NoRepeatNGramLogitsProcessor 동작 확인

5. 확장 테스트 (선택적)
   - 다양한 이미지 타입 테스트
   - 성능 메트릭 수집

## Success Criteria

- 모델 로드 및 초기화 성공
- 이미지 전처리 (DeepseekOCRProcessor) 정상 동작
- OCR 인퍼런스 완료
- 마크다운 출력 생성 및 품질 확인
- 반복 텍스트 없음

## Test Images Available

Located in `/home/fran/DeepSeek-OCR/test-data/`:
- English: en_paper.png, en_paper_full.jpg, en_text.png, en_resource.png
- Korean: ko_text.png, ko_handwriting.png, ko_resource.png
- Code: code_python.png, code_ts.png

## Plans

(none yet)

## Issues

(none yet)

## Notes

(none yet)
