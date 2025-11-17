---
issue: Container Path Mapping
date: 2025-11-17T20:43:00+09:00
status: resolved
---

# Container Path Mapping Issue

## Problem

Initial config.py used host filesystem paths:
```python
INPUT_PATH = '/home/fran/DeepSeek-OCR/test-data/en_paper.png'
OUTPUT_PATH = '/home/fran/DeepSeek-OCR/test-output'
```

Error when running inside container:
```
error: [Errno 2] No such file or directory: '/home/fran/DeepSeek-OCR/test-data/en_paper.png'
```

## Root Cause

Code runs inside Docker container where host paths are not directly accessible. Must use container mount points defined in docker-compose.yml:

```yaml
volumes:
  - /nfs/train/llm-lab/models:/models:ro
  - ./DeepSeek-OCR-master:/app/DeepSeek-OCR-master
  - .:/workspace  # Current directory mounted here
```

## Solution

Updated config.py to use container paths:
```python
MODEL_PATH = '/models/deepseek-ai/DeepSeek-OCR'  # NFS mount
INPUT_PATH = '/workspace/test-data/en_paper.png'   # Project root mount
OUTPUT_PATH = '/workspace/test-output'             # Project root mount
```

## Path Mapping Reference

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| /nfs/train/llm-lab/models | /models | Model weights (read-only) |
| ./DeepSeek-OCR-master | /app/DeepSeek-OCR-master | Source code |
| . (project root) | /workspace | Data and outputs |

## Status

RESOLVED - All paths now use correct container mount points
