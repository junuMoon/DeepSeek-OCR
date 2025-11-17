---
phase: 0
date: 2025-11-17T20:26:20+09:00
status: completed
related: ["plans/docker-environment.md"]
---

# Issue: vLLM Cannot Load DeepSeek-OCR Without Custom Registration

## Problem

Attempting to load model directly with vLLM LLM API failed:

```python
llm = LLM(model="/models/deepseek-ai/DeepSeek-OCR", trust_remote_code=True)
```

Error:
```
ValueError: Model architectures ['TransformersForCausalLM'] failed to be inspected
ImportError: cannot import name 'ALL_ATTENTION_FUNCTIONS' from 'transformers.modeling_utils'
```

## Root Cause

DeepSeek-OCR uses:
1. Custom model architecture: `TransformersForCausalLM` (not in vLLM registry)
2. Custom image processor: `DeepseekOCRProcessor`
3. Custom logits processor: `NoRepeatNGramLogitsProcessor`

vLLM cannot automatically load these custom components.

## Solution

Follow existing code pattern (run_dpsk_ocr_image.py):

```python
# Add custom modules to path
sys.path.insert(0, '/app/DeepSeek-OCR-master/DeepSeek-OCR-vllm')

# Import custom model
from deepseek_ocr import DeepseekOCRForCausalLM

# Register with vLLM
ModelRegistry.register_model("DeepseekOCRForCausalLM", DeepseekOCRForCausalLM)

# Create engine with override
engine_args = AsyncEngineArgs(
    model=MODEL_PATH,
    hf_overrides={"architectures": ["DeepseekOCRForCausalLM"]},
    ...
)
```

## Test Script

Created: `test_model_load.py`
- Registers custom model
- Loads with AsyncEngine
- Verifies GPU memory allocation

## Outcome

✅ Model loads successfully with custom registration
