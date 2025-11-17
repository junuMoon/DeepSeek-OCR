---
phase: 0
date: 2025-11-17T20:26:20+09:00
status: completed
related: ["plans/docker-environment.md"]
---

# Issue: Inefficient vLLM Wheel Handling

## Problem

Initial approach downloaded vLLM wheel (204MB) locally, then COPY into Docker image:

```dockerfile
COPY vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl /tmp/
RUN pip install /tmp/vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl
```

This added:
- 204MB to local directory
- 204MB to Docker build context
- Extra build step (COPY)

## Solution

Changed to direct URL installation:

```dockerfile
RUN pip install https://github.com/vllm-project/vllm/releases/download/v0.8.5/vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl
```

## Benefits

- No local file needed
- Cleaner Dockerfile
- Smaller build context
- One less layer in image

## Files Changed

- Dockerfile:31-32
- Deleted: vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl (204MB)

## Outcome

✅ Resolved - Simplified build process
