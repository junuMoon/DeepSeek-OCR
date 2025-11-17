---
phase: 0
date: 2025-11-17T20:26:20+09:00
status: completed
related: ["plans/docker-environment.md"]
---

# Issue: Python 3.12 Not Available in Ubuntu 22.04

## Problem

Initial Dockerfile specified Python 3.12, but Ubuntu 22.04 repositories don't include it:

```
E: Unable to locate package python3.12
E: Unable to locate package python3.12-dev
```

Build failed at step 6 (apt-get install python3.12).

## Root Cause

Ubuntu 22.04 (Jammy) ships with Python 3.10 as default. Python 3.12 requires:
- Adding deadsnakes PPA, or
- Using Ubuntu 24.04, or
- Using default Python 3.10

## Solution

Changed Dockerfile to use Ubuntu 22.04's default Python 3.10:

```dockerfile
# Before
RUN apt-get install -y python3.12 python3.12-dev ...

# After
RUN apt-get install -y python3 python3-dev ...
```

## Impact

- Build succeeded with Python 3.10.12
- Compatible with vLLM 0.8.5 and PyTorch 2.6.0
- No functional issues observed

## Files Changed

- Dockerfile:9-19

## Outcome

✅ Resolved - Build successful with Python 3.10
