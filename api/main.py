"""
FastAPI application for DeepSeek-OCR inference server.

This module provides a REST API for performing OCR on images using
the DeepSeek-OCR model with vLLM AsyncEngine.
"""

import os
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.routers import health, ocr
from api.services.engine_manager import EngineManager

# Setup logging before anything else
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events:
    - Startup: Initialize vLLM AsyncEngine (singleton)
    - Shutdown: Cleanup resources
    """
    # Startup: Initialize the engine
    logger.info("=" * 80)
    logger.info("DeepSeek-OCR API Server Starting...")
    logger.info("=" * 80)

    try:
        # Set TRITON_PTXAS_PATH for CUDA 11.8
        if torch.version.cuda == "11.8":
            os.environ["TRITON_PTXAS_PATH"] = "/usr/local/cuda-11.8/bin/ptxas"
            logger.info("Set TRITON_PTXAS_PATH for CUDA 11.8")

        # Set vLLM version flag
        os.environ["VLLM_USE_V1"] = "0"

        # Log configuration
        logger.info(f"Model path: {settings.model_path}")
        logger.info(f"GPU memory utilization: {settings.gpu_memory_utilization}")
        logger.info(f"Max model length: {settings.max_model_len}")
        logger.info(f"Tensor parallel size: {settings.tensor_parallel_size}")
        logger.info(f"Workers: {settings.workers}")
        logger.info(f"CUDA devices: {os.environ.get('CUDA_VISIBLE_DEVICES', 'not set')}")

        # Initialize the engine (this takes ~27s)
        await EngineManager.initialize()

        logger.info("=" * 80)
        logger.info("DeepSeek-OCR API Server Ready")
        logger.info(f"Listening on {settings.api_host}:{settings.api_port}")
        logger.info("=" * 80)

        yield

    finally:
        # Shutdown: Cleanup
        logger.info("=" * 80)
        logger.info("DeepSeek-OCR API Server Shutting Down...")
        logger.info("=" * 80)

        await EngineManager.shutdown()

        logger.info("Shutdown complete")
        logger.info("=" * 80)


# Create FastAPI application
app = FastAPI(
    title="DeepSeek-OCR API",
    description=(
        "REST API for performing OCR on images using DeepSeek-OCR model with vLLM.\n\n"
        "Features:\n"
        "- Document and image OCR\n"
        "- Custom prompts\n"
        "- Markdown output\n"
        "- Bounding box detection\n"
        "- Anti-repetition processing"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(ocr.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "DeepSeek-OCR API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "model_info": "/models",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
    )
