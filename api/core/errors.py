"""
Custom exception classes for the DeepSeek-OCR API.
"""

from typing import Any, Optional


class DeepSeekOCRError(Exception):
    """Base exception class for DeepSeek-OCR API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ModelNotLoadedError(DeepSeekOCRError):
    """Raised when attempting to use the model before it's loaded."""

    def __init__(self, message: str = "Model has not been loaded yet") -> None:
        super().__init__(message=message, status_code=503)


class ImageProcessingError(DeepSeekOCRError):
    """Raised when image preprocessing fails."""

    def __init__(
        self,
        message: str = "Failed to process image",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)


class InvalidFileError(DeepSeekOCRError):
    """Raised when uploaded file is invalid."""

    def __init__(
        self,
        message: str = "Invalid file",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)


class FileTooLargeError(DeepSeekOCRError):
    """Raised when uploaded file exceeds size limit."""

    def __init__(
        self,
        message: str = "File size exceeds maximum allowed size",
        max_size: Optional[int] = None,
    ) -> None:
        details = {"max_size_bytes": max_size} if max_size else {}
        super().__init__(message=message, status_code=413, details=details)


class InferenceError(DeepSeekOCRError):
    """Raised when model inference fails."""

    def __init__(
        self,
        message: str = "Model inference failed",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=500, details=details)


class UnsupportedFileTypeError(DeepSeekOCRError):
    """Raised when file type is not supported."""

    def __init__(
        self,
        message: str = "Unsupported file type",
        allowed_types: Optional[set[str]] = None,
    ) -> None:
        details = {"allowed_types": list(allowed_types)} if allowed_types else {}
        super().__init__(message=message, status_code=400, details=details)
