---
phase: 1
date: 2025-11-17T20:32:34+09:00
status: in-progress
related: []
---

# Image Inference Test Plan

## Context

Phase 0에서 Docker 환경 구축과 커스텀 모델 등록이 완료되었습니다. 이제 실제 이미지로 OCR을 수행하여 전체 파이프라인을 검증합니다.

## Key Components

### 1. run_dpsk_ocr_image.py
Main inference script that:
- Loads and preprocesses images
- Registers custom model (DeepseekOCRForCausalLM)
- Creates AsyncLLMEngine
- Runs inference with streaming output
- Saves results (markdown + visualizations)

### 2. DeepseekOCRProcessor
Image preprocessing with dynamic cropping:
- BASE_SIZE: 1024 (reference resolution)
- IMAGE_SIZE: 640 (crop size)
- CROP_MODE: True (Gundam mode - multiple crops)
- MAX_CROPS: 6 (max number of crops)

### 3. NoRepeatNGramLogitsProcessor
Prevents repetitive text generation:
- ngram_size: 30
- window_size: 90
- whitelist_token_ids: {128821, 128822} (table tags)

### 4. config.py Settings
Current configuration:
```python
BASE_SIZE = 1024
IMAGE_SIZE = 640
CROP_MODE = True
MAX_CROPS = 6
MODEL_PATH = 'deepseek-ai/DeepSeek-OCR'  # Needs update
INPUT_PATH = ''  # Needs to be set
OUTPUT_PATH = ''  # Needs to be set
PROMPT = '<image>\n<|grounding|>Convert the document to markdown.'
```

## Implementation Steps

### Step 1: Update config.py

Change paths to match container environment:
```python
MODEL_PATH = '/models/deepseek-ai/DeepSeek-OCR'
INPUT_PATH = '/home/fran/DeepSeek-OCR/test-data/en_paper.png'
OUTPUT_PATH = '/home/fran/DeepSeek-OCR/test-output'
```

### Step 2: Prepare Environment

```bash
# Create output directories
mkdir -p /home/fran/DeepSeek-OCR/test-output
mkdir -p /home/fran/DeepSeek-OCR/test-output/images

# Verify test images exist
ls -lh /home/fran/DeepSeek-OCR/test-data/
```

### Step 3: Run First Test

```bash
# Enter container
docker compose exec deepseek-ocr bash

# Navigate to code directory
cd /app/DeepSeek-OCR-master/DeepSeek-OCR-vllm

# Run inference
python run_dpsk_ocr_image.py
```

### Step 4: Verify Outputs

Expected files in OUTPUT_PATH:
- `result_ori.mmd` - Raw markdown with grounding tags
- `result.mmd` - Cleaned markdown
- `result_with_boxes.jpg` - Image with bounding boxes
- `images/` - Extracted image regions

Check commands:
```bash
ls -lh /home/fran/DeepSeek-OCR/test-output/
cat /home/fran/DeepSeek-OCR/test-output/result.mmd
```

### Step 5: Extended Testing (Optional)

Test sequence:
1. `en_paper.png` - Baseline document
2. `en_text.png` - Dense text
3. `code_python.png` - Code OCR
4. `ko_text.png` - Korean text
5. `en_resource.png` - Complex layout

For each image:
- Update INPUT_PATH in config.py
- Run inference
- Verify output quality
- Document issues

## Expected Behavior

### Image Processing Flow:
1. Load image with PIL
2. DeepseekOCRProcessor.tokenize_with_images():
   - Crop image based on CROP_MODE
   - Resize to IMAGE_SIZE
   - Convert to tensor
3. Pass to AsyncLLMEngine
4. Generate with NoRepeatNGramLogitsProcessor
5. Post-process output (extract bounding boxes, clean markdown)

### Output Format:

**result_ori.mmd:**
```markdown
# Document Title

Some text with grounding tags:
<|ref|>title<|/ref|><|det|>[[100,200,300,400]]<|/det|>
```

**result.mmd:**
```markdown
# Document Title

Some cleaned text with image references:
![](images/0.jpg)
```

## Potential Issues

### Issue 1: GPU Memory Insufficient
**Symptom:** CUDA out of memory
**Solution:**
- Reduce MAX_CROPS from 6 to 4
- Reduce gpu_memory_utilization in run_dpsk_ocr_image.py

### Issue 2: Model Path Not Found
**Symptom:** FileNotFoundError
**Solution:** Verify model path in container:
```bash
docker compose exec deepseek-ocr ls -la /models/deepseek-ai/DeepSeek-OCR
```

### Issue 3: Import Errors
**Symptom:** ModuleNotFoundError for deepseek_ocr or process modules
**Solution:** Ensure working directory is correct:
```bash
cd /app/DeepSeek-OCR-master/DeepSeek-OCR-vllm
```

### Issue 4: Slow Inference
**Symptom:** Takes >60s per image
**Solution:**
- Check GPU utilization with nvidia-smi
- Reduce max_model_len (currently 8192)
- Disable CROP_MODE for faster processing

### Issue 5: Poor Quality Output
**Symptom:** Gibberish or empty output
**Solution:**
- Verify image loads correctly
- Check PROMPT format
- Inspect result_ori.mmd for raw output

## Success Criteria

### Minimal Success:
- ✅ Model loads without errors
- ✅ Single image processes successfully
- ✅ Markdown output generated
- ✅ Output is readable

### Full Success:
- ✅ Multiple images process successfully
- ✅ OCR accuracy >90% for English
- ✅ Bounding boxes accurate
- ✅ No text repetition
- ✅ Inference time <30s per image
- ✅ Korean text recognized

## Performance Metrics to Collect

1. **Timing:**
   - Image preprocessing time
   - Model inference time
   - Post-processing time
   - Total time per image

2. **Memory:**
   - GPU memory usage
   - CPU memory usage

3. **Quality:**
   - OCR accuracy (manual inspection)
   - Bounding box precision
   - Layout preservation

## Next Steps

After Phase 1 validation:
- Phase 2: Build API server wrapper
- Implement batch processing
- Add request queueing
- Create REST endpoints
