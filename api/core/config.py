"""
Configuration settings for the DeepSeek-OCR API server.
Uses pydantic-settings for environment variable management.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Model configuration
    model_path: str = Field(
        default="/models/deepseek-ai/DeepSeek-OCR",
        description="Path to the DeepSeek-OCR model directory",
    )

    # vLLM Engine configuration
    tensor_parallel_size: int = Field(
        default=1,
        description="Number of GPUs to use for tensor parallelism",
    )
    gpu_memory_utilization: float = Field(
        default=0.5,
        description="GPU memory utilization (0.0 to 1.0)",
    )
    max_model_len: int = Field(
        default=4096,
        description="Maximum sequence length",
    )
    trust_remote_code: bool = Field(
        default=True,
        description="Trust remote code in model",
    )

    # Generation configuration
    temperature: float = Field(
        default=0.0,
        description="Sampling temperature",
    )
    max_tokens: int = Field(
        default=4096,
        description="Maximum number of tokens to generate",
    )
    ngram_size: int = Field(
        default=30,
        description="N-gram size for repetition penalty",
    )
    window_size: int = Field(
        default=90,
        description="Window size for repetition penalty",
    )

    # API configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host",
    )
    api_port: int = Field(
        default=8000,
        description="API server port",
    )
    workers: int = Field(
        default=1,
        description="Number of workers (must be 1 for GPU efficiency)",
    )

    # File upload limits
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        description="Maximum file size in bytes",
    )
    allowed_extensions: set[str] = Field(
        default={"png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"},
        description="Allowed image file extensions",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    # CUDA configuration
    cuda_visible_devices: Optional[str] = Field(
        default=None,
        description="CUDA visible devices (e.g., '0,1,2,3')",
    )

    @field_validator("workers")
    @classmethod
    def validate_workers(cls, v: int) -> int:
        """Ensure workers is set to 1 for GPU efficiency."""
        if v != 1:
            raise ValueError(
                "workers must be 1 to avoid duplicating GPU memory usage. "
                "Use async concurrency within a single worker instead."
            )
        return v

    @field_validator("gpu_memory_utilization")
    @classmethod
    def validate_gpu_memory(cls, v: float) -> float:
        """Ensure GPU memory utilization is between 0 and 1."""
        if not 0.0 < v <= 1.0:
            raise ValueError("gpu_memory_utilization must be between 0.0 and 1.0")
        return v

    @field_validator("model_path")
    @classmethod
    def validate_model_path(cls, v: str) -> str:
        """Ensure model path exists."""
        if not Path(v).exists():
            raise ValueError(f"Model path does not exist: {v}")
        return v

    def apply_cuda_config(self) -> None:
        """Apply CUDA configuration to environment."""
        if self.cuda_visible_devices is not None:
            os.environ["CUDA_VISIBLE_DEVICES"] = self.cuda_visible_devices


# Global settings instance
settings = Settings()
