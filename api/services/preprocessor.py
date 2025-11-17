"""
Image preprocessing service for DeepSeek-OCR.

Handles image loading, validation, and preprocessing using DeepseekOCRProcessor.
"""

import io
from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageOps

from api.core.config import settings
from api.core.errors import (
    FileTooLargeError,
    ImageProcessingError,
    InvalidFileError,
    UnsupportedFileTypeError,
)
from api.core.logging import get_logger
from process.image_process import DeepseekOCRProcessor

logger = get_logger(__name__)


class ImagePreprocessor:
    """
    Handles image validation and preprocessing for OCR.

    Uses DeepseekOCRProcessor to tokenize images and prepare them
    for vLLM engine inference.
    """

    def __init__(self) -> None:
        """Initialize the preprocessor with DeepseekOCRProcessor."""
        self.processor = DeepseekOCRProcessor()
        logger.info("ImagePreprocessor initialized")

    @staticmethod
    def load_image(image_data: Union[bytes, str, Path]) -> Image.Image:
        """
        Load and normalize an image from various sources.

        Handles EXIF orientation correction to ensure images are properly oriented.

        Args:
            image_data: Image data as bytes, file path string, or Path object

        Returns:
            PIL Image in RGB mode

        Raises:
            ImageProcessingError: If image loading fails
        """
        try:
            # Load image based on input type
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = Image.open(image_data)

            # Apply EXIF transpose to handle rotation metadata
            corrected_image = ImageOps.exif_transpose(image)

            # Convert to RGB if necessary
            if corrected_image.mode != "RGB":
                corrected_image = corrected_image.convert("RGB")

            return corrected_image

        except Exception as e:
            logger.error(f"Failed to load image: {e}", exc_info=True)
            raise ImageProcessingError(
                message="Failed to load and process image",
                details={"error": str(e)},
            )

    @staticmethod
    def validate_file(
        file_data: bytes,
        filename: str,
        max_size: Optional[int] = None,
    ) -> None:
        """
        Validate uploaded file meets requirements.

        Args:
            file_data: Raw file bytes
            filename: Original filename
            max_size: Maximum file size in bytes (defaults to settings.max_file_size)

        Raises:
            FileTooLargeError: If file exceeds size limit
            UnsupportedFileTypeError: If file extension not allowed
            InvalidFileError: If file is invalid
        """
        if max_size is None:
            max_size = settings.max_file_size

        # Check file size
        file_size = len(file_data)
        if file_size > max_size:
            raise FileTooLargeError(
                message=f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes)",
                max_size=max_size,
            )

        # Check file extension
        file_ext = Path(filename).suffix.lower().lstrip(".")
        if file_ext not in settings.allowed_extensions:
            raise UnsupportedFileTypeError(
                message=f"File type '.{file_ext}' is not supported",
                allowed_types=settings.allowed_extensions,
            )

        # Validate it's actually an image by trying to open it
        try:
            image = Image.open(io.BytesIO(file_data))
            image.verify()  # Verify it's a valid image
        except Exception as e:
            raise InvalidFileError(
                message="File is not a valid image",
                details={"error": str(e)},
            )

    def tokenize_image(
        self,
        image: Image.Image,
        crop_mode: bool = True,
    ) -> str:
        """
        Tokenize image using DeepseekOCRProcessor.

        Args:
            image: PIL Image to process
            crop_mode: Whether to enable cropping mode

        Returns:
            Tokenized image features as string

        Raises:
            ImageProcessingError: If tokenization fails
        """
        try:
            logger.info(f"Tokenizing image (size: {image.size}, crop_mode: {crop_mode})")

            # Process image with DeepseekOCRProcessor
            image_features = self.processor.tokenize_with_images(
                images=[image],
                bos=True,
                eos=True,
                cropping=crop_mode,
            )

            logger.info("Image tokenization successful")
            return image_features

        except Exception as e:
            logger.error(f"Image tokenization failed: {e}", exc_info=True)
            raise ImageProcessingError(
                message="Failed to tokenize image",
                details={"error": str(e)},
            )

    async def preprocess(
        self,
        file_data: bytes,
        filename: str,
        crop_mode: bool = True,
    ) -> tuple[Image.Image, str]:
        """
        Full preprocessing pipeline: validate, load, and tokenize image.

        Args:
            file_data: Raw image file bytes
            filename: Original filename
            crop_mode: Whether to enable cropping mode

        Returns:
            Tuple of (original_image, tokenized_features)

        Raises:
            FileTooLargeError: If file too large
            UnsupportedFileTypeError: If unsupported file type
            InvalidFileError: If invalid file
            ImageProcessingError: If preprocessing fails
        """
        # Validate file
        self.validate_file(file_data, filename)

        # Load image
        image = self.load_image(file_data)

        # Tokenize image
        image_features = self.tokenize_image(image, crop_mode=crop_mode)

        return image, image_features
