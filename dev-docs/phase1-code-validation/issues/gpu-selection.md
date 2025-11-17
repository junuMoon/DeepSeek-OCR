---
issue: GPU Selection in Docker Compose
date: 2025-11-17T20:44:00+09:00
status: resolved
---

# GPU Selection Issue

## Problem

Docker container was using GPU 0 instead of requested GPU 7.

Initial docker-compose.yml configuration:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

With `CUDA_VISIBLE_DEVICES=7` in .env, the container still accessed GPU 0 (Bus ID: 07:00.0).

## Root Cause

The `count: 1` parameter selects the first available GPU, ignoring `CUDA_VISIBLE_DEVICES` environment variable at the Docker runtime level.

## Solution

Changed docker-compose.yml to explicitly specify GPU by device ID:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['7']
          capabilities: [gpu]
```

## Verification

After fix:
```bash
$ docker compose exec deepseek-ocr nvidia-smi --query-gpu=index,pci.bus_id --format=csv
index, pci.bus_id
0, 00000000:BD:00.0  # GPU 7 mapped to container index 0
```

## Status

RESOLVED - Container now correctly uses GPU 7 (Bus ID: BD:00.0)
