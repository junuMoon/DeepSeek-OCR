"""
Test script for loading DeepSeek-OCR model with custom components
"""
import os
import sys

# Add DeepSeek-OCR-vllm to path
sys.path.insert(0, '/app/DeepSeek-OCR-master/DeepSeek-OCR-vllm')

# Set environment variables
os.environ['VLLM_USE_V1'] = '0'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

import torch
from vllm import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.model_executor.models.registry import ModelRegistry

# Import custom model
from deepseek_ocr import DeepseekOCRForCausalLM

# Register custom model
print("Registering custom DeepseekOCRForCausalLM model...")
ModelRegistry.register_model("DeepseekOCRForCausalLM", DeepseekOCRForCausalLM)

# Model path
MODEL_PATH = os.environ.get('MODEL_PATH', '/models/deepseek-ai/DeepSeek-OCR')

print(f"Model path: {MODEL_PATH}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")

# Create AsyncEngine with minimal config
print("\nCreating AsyncLLMEngine...")
engine_args = AsyncEngineArgs(
    model=MODEL_PATH,
    hf_overrides={"architectures": ["DeepseekOCRForCausalLM"]},
    max_model_len=256,  # Very small for testing with limited GPU memory
    gpu_memory_utilization=0.2,  # Conservative due to other processes
    trust_remote_code=True,
    tensor_parallel_size=1,
    enforce_eager=True,  # Disable cuda graphs to save memory
)

print("Initializing engine...")
engine = AsyncLLMEngine.from_engine_args(engine_args)

print("\n✅ Model loaded successfully!")
print(f"Model config: {engine.engine.model_config.model}")
print(f"Max model length: {engine.engine.model_config.max_model_len}")
