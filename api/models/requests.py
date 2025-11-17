"""
Request models for the DeepSeek-OCR API.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class OCRType(str, Enum):
    """Type of OCR to perform."""

    DOCUMENT = "document"
    IMAGE = "image"


class OCRRequest(BaseModel):
    """Request model for OCR endpoint (form fields only, file uploaded separately)."""

    type: OCRType = Field(
        default=OCRType.DOCUMENT,
        description="Type of OCR: 'document' for text-heavy documents, 'image' for general images",
    )
    custom_prompt: Optional[str] = Field(
        default=None,
        description="Custom prompt to override default. Use '<image>' as placeholder for image.",
        max_length=1000,
    )
    crop_mode: bool = Field(
        default=True,
        description="Whether to enable image cropping during preprocessing",
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0 = deterministic)",
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=8192,
        description="Maximum number of tokens to generate",
    )
    include_raw: bool = Field(
        default=False,
        description="Include raw model output (with special tokens) in response",
    )
    save_image_refs: bool = Field(
        default=False,
        description="Preserve image reference placeholders in markdown output",
    )

    @field_validator("custom_prompt")
    @classmethod
    def validate_custom_prompt(cls, v: Optional[str]) -> Optional[str]:
        """Ensure custom prompt contains <image> placeholder if provided."""
        if v is not None and "<image>" not in v:
            raise ValueError("Custom prompt must contain '<image>' placeholder")
        return v

    def get_prompt(self) -> str:
        """
        Get the final prompt to use for inference.

        Returns:
            Prompt string with <image> placeholder
        """
        if self.custom_prompt:
            return self.custom_prompt

        # Default prompts based on OCR type
        if self.type == OCRType.DOCUMENT:
            return "Recognize the text in <image>."
        elif self.type == OCRType.IMAGE:
            return "Describe <image> in detail."
        else:
            return "Recognize the text in <image>."
