"""
Health check and model info endpoints.
"""

from fastapi import APIRouter, status

from api.core.config import settings
from api.models.responses import HealthResponse, ModelInfo
from api.services.engine_manager import EngineManager

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API service is healthy and the model is loaded",
)
async def health_check() -> HealthResponse:
    """
    Check service health status.

    Returns:
        HealthResponse with service status and model readiness
    """
    is_ready = EngineManager.is_ready()

    if is_ready:
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            message="Service is ready to process requests",
        )
    else:
        return HealthResponse(
            status="initializing",
            model_loaded=False,
            message="Model is still loading, please wait",
        )


@router.get(
    "/models",
    response_model=ModelInfo,
    status_code=status.HTTP_200_OK,
    summary="Get model information",
    description="Retrieve information about the loaded DeepSeek-OCR model",
)
async def get_model_info() -> ModelInfo:
    """
    Get information about the current model.

    Returns:
        ModelInfo with model configuration details
    """
    return ModelInfo(
        model_path=settings.model_path,
        model_type="DeepseekOCRForCausalLM",
        max_tokens=settings.max_tokens,
        gpu_memory_utilization=settings.gpu_memory_utilization,
    )
