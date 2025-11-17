"""
OCR endpoint for processing images.
"""

import time
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from api.core.errors import DeepSeekOCRError
from api.core.logging import get_logger
from api.models.requests import OCRRequest, OCRType
from api.models.responses import ErrorResponse, OCRResponse
from api.services.engine_manager import EngineManager
from api.services.postprocessor import OutputPostprocessor
from api.services.preprocessor import ImagePreprocessor

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["ocr"])


@router.post(
    "/ocr",
    response_model=OCRResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform OCR on an image",
    description="Upload an image and get markdown text extracted via DeepSeek-OCR",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request or file"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Server error"},
        503: {"model": ErrorResponse, "description": "Model not ready"},
    },
)
async def perform_ocr(
    file: Annotated[UploadFile, File(description="Image file to process")],
    type: Annotated[OCRType, Form()] = OCRType.DOCUMENT,
    custom_prompt: Annotated[str | None, Form()] = None,
    crop_mode: Annotated[bool, Form()] = True,
    temperature: Annotated[float | None, Form(ge=0.0, le=2.0)] = None,
    max_tokens: Annotated[int | None, Form(ge=1, le=8192)] = None,
    include_raw: Annotated[bool, Form()] = False,
    save_image_refs: Annotated[bool, Form()] = False,
) -> OCRResponse:
    """
    Process an image and extract text using DeepSeek-OCR.

    Args:
        file: Image file to process
        type: Type of OCR (document or image)
        custom_prompt: Custom prompt (must contain '<image>')
        crop_mode: Enable image cropping
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        include_raw: Include raw output with special tokens
        save_image_refs: Preserve image reference placeholders

    Returns:
        OCRResponse with extracted markdown text

    Raises:
        HTTPException: If processing fails
    """
    start_time = time.time()

    try:
        # Build request model from form data
        request = OCRRequest(
            type=type,
            custom_prompt=custom_prompt,
            crop_mode=crop_mode,
            temperature=temperature,
            max_tokens=max_tokens,
            include_raw=include_raw,
            save_image_refs=save_image_refs,
        )

        logger.info(f"Processing OCR request: type={request.type}, file={file.filename}")

        # Read file data
        file_data = await file.read()

        # Preprocess image
        preprocessor = ImagePreprocessor()
        original_image, image_features = await preprocessor.preprocess(
            file_data=file_data,
            filename=file.filename or "unknown",
            crop_mode=request.crop_mode,
        )

        # Get prompt
        prompt = request.get_prompt()

        # Generate text using engine
        raw_output = await EngineManager.generate(
            prompt=prompt,
            image_features=image_features,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # Post-process output
        postprocessor = OutputPostprocessor()
        processed = postprocessor.postprocess(
            raw_output=raw_output,
            save_image_refs=request.save_image_refs,
            include_raw=request.include_raw,
        )

        # Calculate processing time
        processing_time = time.time() - start_time

        logger.info(
            f"OCR request completed successfully in {processing_time:.2f}s "
            f"(output: {len(processed['text'])} chars)"
        )

        return OCRResponse(
            text=processed["text"],
            raw=processed.get("raw"),
            processing_time=processing_time,
            prompt_used=prompt,
        )

    except DeepSeekOCRError as e:
        # Handle known application errors
        logger.error(f"OCR processing failed: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": e.message,
                "details": e.details,
                "status_code": e.status_code,
            },
        )

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error during OCR processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "An unexpected error occurred",
                "details": {"error": str(e)},
                "status_code": 500,
            },
        )
