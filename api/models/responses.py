"""
Response models for the DeepSeek-OCR API.
"""

from typing import Optional

from pydantic import BaseModel, Field


class OCRResponse(BaseModel):
    """Response model for OCR endpoint."""

    text: str = Field(
        description="Cleaned markdown text extracted from the image",
    )
    raw: Optional[str] = Field(
        default=None,
        description="Raw model output with special tokens (only if include_raw=True)",
    )
    processing_time: float = Field(
        description="Total processing time in seconds",
        ge=0.0,
    )
    prompt_used: str = Field(
        description="The actual prompt that was used for inference",
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(
        description="Service health status",
        examples=["healthy", "unhealthy"],
    )
    model_loaded: bool = Field(
        description="Whether the model engine is loaded and ready",
    )
    message: Optional[str] = Field(
        default=None,
        description="Additional status information",
    )


class ModelInfo(BaseModel):
    """Information about the loaded model."""

    model_path: str = Field(
        description="Path to the model directory",
    )
    model_type: str = Field(
        description="Model architecture type",
        examples=["DeepseekOCRForCausalLM"],
    )
    max_tokens: int = Field(
        description="Maximum tokens supported",
        ge=0,
    )
    gpu_memory_utilization: float = Field(
        description="GPU memory utilization ratio",
        ge=0.0,
        le=1.0,
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(
        description="Error message",
    )
    details: Optional[dict] = Field(
        default=None,
        description="Additional error details",
    )
    status_code: int = Field(
        description="HTTP status code",
        ge=100,
        lt=600,
    )
