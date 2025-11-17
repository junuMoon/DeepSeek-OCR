---
phase: 0
date: 2025-11-17T20:26:20+09:00
status: completed
related: ["issues/custom-model-registration.md"]
---

# Memory Requirements Analysis

## Model Size

Model weights: **6.23 GiB**

## GPU Memory Usage by Configuration

### Minimal Test (Current Test)
```python
max_model_len=256
gpu_memory_utilization=0.2
enforce_eager=True
```
- GPU allocated: ~15.8 GiB (0.2 × 79 GiB)
- KV cache blocks: 9,597
- Concurrency: 599.81x
- **Works with 40GB free on GPU**

### Medium Configuration
```python
max_model_len=1024
gpu_memory_utilization=0.3-0.5
enforce_eager=False
```
- GPU needed: ~25-40 GiB
- Suitable for basic inference

### Full Configuration (from run_dpsk_ocr_image.py)
```python
max_model_len=8192
gpu_memory_utilization=0.75
enforce_eager=False
```
- GPU needed: **~60 GiB** (0.75 × 80 GiB)
- KV cache blocks: 35,529+
- **Requires dedicated GPU with no other processes**

## Current GPU Status (nvidia-smi)

GPU 0: 41,203 MiB / 81,920 MiB in use
- Process 207215: 41,192 MiB
- Only ~40 GB free

Other GPUs (1-7): Also ~41GB occupied each

## Recommendations

1. **For Testing**: Use minimal config (256 tokens, 0.2 util)
2. **For Production**:
   - Use dedicated GPU
   - Full config requires GPU with >60GB free
   - A100-80GB is appropriate

## Key Parameters Impact

| Parameter | Impact on Memory |
|-----------|------------------|
| `max_model_len` | Linear (KV cache size) |
| `gpu_memory_utilization` | Linear (total allocation) |
| `enforce_eager` | ~10-20% savings (no CUDA graphs) |
| `block_size` | Affects KV cache granularity |

## Memory Equation

```
Total = Model Weights + KV Cache + Activations + CUDA Graphs
      = 6.23 GiB + (max_model_len dependent) + 0.7 GiB + (0 if eager)
```

For max_model_len=8192:
```
KV Cache ≈ (gpu_memory_utilization × GPU_size) - 6.23 - 0.7
         ≈ (0.75 × 80) - 7 = ~53 GiB
```
