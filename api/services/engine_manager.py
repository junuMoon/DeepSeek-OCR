"""
Singleton manager for vLLM AsyncEngine.

This module provides a singleton pattern to manage the DeepSeek-OCR model engine,
ensuring it's loaded only once at server startup to avoid the 27.3s initialization overhead.
"""

import asyncio
import os
import time
from typing import Optional

from vllm import AsyncLLMEngine, SamplingParams
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.model_executor.models.registry import ModelRegistry

from api.core.config import settings
from api.core.errors import InferenceError, ModelNotLoadedError
from api.core.logging import get_logger
from process.ngram_norepeat import NoRepeatNGramLogitsProcessor

# Import and register custom model
from deepseek_ocr import DeepseekOCRForCausalLM

logger = get_logger(__name__)


class EngineManager:
    """
    Singleton manager for vLLM AsyncEngine.

    Ensures only one instance of the AsyncEngine exists per process,
    preventing duplicate GPU memory usage and initialization overhead.
    """

    _instance: Optional["EngineManager"] = None
    _engine: Optional[AsyncLLMEngine] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _initialized: bool = False

    def __new__(cls) -> "EngineManager":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(cls) -> None:
        """
        Initialize the vLLM AsyncEngine.

        This should be called once at server startup via the FastAPI lifespan context.
        """
        async with cls._lock:
            if cls._initialized:
                logger.warning("Engine already initialized, skipping re-initialization")
                return

            logger.info("Initializing vLLM AsyncEngine...")
            start_time = time.time()

            try:
                # Register custom model
                ModelRegistry.register_model("DeepseekOCRForCausalLM", DeepseekOCRForCausalLM)
                logger.info("Registered DeepseekOCRForCausalLM model")

                # Apply CUDA configuration
                settings.apply_cuda_config()

                # Create engine args
                engine_args = AsyncEngineArgs(
                    model=settings.model_path,
                    hf_overrides={"architectures": ["DeepseekOCRForCausalLM"]},
                    block_size=256,
                    max_model_len=settings.max_model_len,
                    enforce_eager=False,
                    trust_remote_code=settings.trust_remote_code,
                    tensor_parallel_size=settings.tensor_parallel_size,
                    gpu_memory_utilization=settings.gpu_memory_utilization,
                )

                # Initialize engine
                cls._engine = AsyncLLMEngine.from_engine_args(engine_args)
                cls._initialized = True

                elapsed = time.time() - start_time
                logger.info(f"Engine initialized successfully in {elapsed:.2f}s")

            except Exception as e:
                logger.error(f"Failed to initialize engine: {e}", exc_info=True)
                cls._initialized = False
                raise InferenceError(
                    message="Failed to initialize model engine",
                    details={"error": str(e)},
                )

    @classmethod
    async def shutdown(cls) -> None:
        """Shutdown the engine and cleanup resources."""
        async with cls._lock:
            if cls._engine is not None:
                logger.info("Shutting down vLLM AsyncEngine...")
                # Note: vLLM AsyncEngine doesn't have explicit shutdown in current version
                # Resources will be cleaned up when the process exits
                cls._engine = None
                cls._initialized = False
                logger.info("Engine shutdown complete")

    @classmethod
    def get_engine(cls) -> AsyncLLMEngine:
        """
        Get the AsyncEngine instance.

        Returns:
            AsyncLLMEngine instance

        Raises:
            ModelNotLoadedError: If engine hasn't been initialized
        """
        if not cls._initialized or cls._engine is None:
            raise ModelNotLoadedError("Engine has not been initialized. Call initialize() first.")
        return cls._engine

    @classmethod
    async def generate(
        cls,
        prompt: str,
        image_features: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """
        Generate text using the AsyncEngine.

        Args:
            prompt: Text prompt for generation
            image_features: Pre-processed image features from DeepseekOCRProcessor
            temperature: Sampling temperature (defaults to settings.temperature)
            max_tokens: Maximum tokens to generate (defaults to settings.max_tokens)
            stream: Whether to stream the output (for future implementation)

        Returns:
            Generated text

        Raises:
            ModelNotLoadedError: If engine hasn't been initialized
            InferenceError: If generation fails
        """
        engine = cls.get_engine()

        try:
            # Setup logits processors for anti-repetition
            # Whitelist: <td>, </td> tokens
            logits_processors = [
                NoRepeatNGramLogitsProcessor(
                    ngram_size=settings.ngram_size,
                    window_size=settings.window_size,
                    whitelist_token_ids={128821, 128822},
                )
            ]

            # Create sampling params
            sampling_params = SamplingParams(
                temperature=temperature if temperature is not None else settings.temperature,
                max_tokens=max_tokens if max_tokens is not None else settings.max_tokens,
                logits_processors=logits_processors,
                skip_special_tokens=False,
            )

            # Generate unique request ID
            request_id = f"request-{int(time.time() * 1000)}"

            # Build request based on whether we have image features
            if image_features and "<image>" in prompt:
                request = {
                    "prompt": prompt,
                    "multi_modal_data": {"image": image_features},
                }
            elif prompt:
                request = {"prompt": prompt}
            else:
                raise InferenceError(
                    message="Prompt cannot be empty",
                    details={"prompt": prompt},
                )

            # Generate output
            logger.info(f"Starting generation for request {request_id}")
            start_time = time.time()

            full_text = ""
            async for request_output in engine.generate(request, sampling_params, request_id):
                if request_output.outputs:
                    full_text = request_output.outputs[0].text

            elapsed = time.time() - start_time
            logger.info(
                f"Generation complete for {request_id} in {elapsed:.2f}s "
                f"({len(full_text)} chars)"
            )

            return full_text

        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            raise InferenceError(
                message="Model inference failed",
                details={"error": str(e)},
            )

    @classmethod
    def is_ready(cls) -> bool:
        """Check if the engine is initialized and ready."""
        return cls._initialized and cls._engine is not None
