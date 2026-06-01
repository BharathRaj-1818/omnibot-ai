"""
Image Service - Text-to-Image generation using Stable Diffusion via Hugging Face
This file was not provided — created from scratch to match main.py API.

NOTE: image_service is set to None in main.py by default to save RAM.
      To enable: change `image_service = None` to `image_service = ImageService()`
      Requires ~4GB RAM (CPU) or ~2GB VRAM (GPU).
"""

import io
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class ImageService:
    """
    Image generation using Stable Diffusion (diffusers library).
    Uses 'runwayml/stable-diffusion-v1-5' by default — free, open-source.
    Model loads lazily on first request.
    """

    def __init__(self, model_id: str = "runwayml/stable-diffusion-v1-5"):
        self.model_id = model_id
        self._pipe = None
        logger.info(f"ImageService created — model '{model_id}' loads on first request")

    def _load_pipeline_sync(self):
        """Load Stable Diffusion pipeline — runs in thread pool."""
        if self._pipe is not None:
            return
        try:
            import torch
            from diffusers import StableDiffusionPipeline

            logger.info(f"Loading Stable Diffusion: {self.model_id}")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32

            self._pipe = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=dtype,
                safety_checker=None  # Disable safety checker to save memory
            )
            self._pipe = self._pipe.to(device)

            # Memory optimization for CPU
            if device == "cpu":
                self._pipe.enable_attention_slicing()

            logger.info(f"✅ Stable Diffusion loaded on {device}")

        except Exception as e:
            logger.error(f"Pipeline load failed: {e}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = "",
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20
    ) -> io.BytesIO:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of the image.
            negative_prompt: Things to avoid in the image.
            width: Image width in pixels (256–1024).
            height: Image height in pixels (256–1024).
            num_inference_steps: More steps = better quality but slower (10–50).

        Returns:
            BytesIO buffer containing PNG image data.
        """
        loop = asyncio.get_event_loop()

        # Load model non-blocking
        await loop.run_in_executor(None, self._load_pipeline_sync)

        def _generate():
            result = self._pipe(
                prompt=prompt,
                negative_prompt=negative_prompt or "",
                width=width,
                height=height,
                num_inference_steps=num_inference_steps
            )
            image = result.images[0]
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            return buffer

        logger.info(f"Generating image: '{prompt[:60]}...' ({width}x{height})")
        buffer = await loop.run_in_executor(None, _generate)
        logger.info(f"Image generated: {buffer.getbuffer().nbytes} bytes")
        return buffer
