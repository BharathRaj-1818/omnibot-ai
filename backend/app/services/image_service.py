"""
Image Generation Service - Using Stable Diffusion via Hugging Face
"""

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import io
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)


class ImageService:
    """
    Image generation service using Stable Diffusion
    Uses free Hugging Face models
    """
    
    def __init__(self, model_id: str = model_id = "segmind/tiny-sd"):
        """
        Initialize image generation service
        
        Args:
            model_id: Hugging Face model identifier for Stable Diffusion
        """
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        self.enabled = True
        
        logger.info(f"Initializing Image Service with model: {model_id}")
        logger.info(f"Using device: {self.device}")
        
        # Load model (lazy loading to save memory)
        if self.device == "cuda":
            self._load_model()
        else:
            logger.warning("GPU not available. Image generation will be slow on CPU.")
            logger.warning("Consider using a smaller model or enabling GPU acceleration.")
    
    def _load_model(self):
        """Load Stable Diffusion pipeline"""
        try:
            logger.info("Loading Stable Diffusion model...")
            
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,  # Disable for faster inference
                requires_safety_checker=False
            )
            
            # Use DPM++ scheduler for better quality/speed
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            self.pipe.to(self.device)
            
            # Enable memory optimizations
            if self.device == "cuda":
                self.pipe.enable_attention_slicing()
                try:
                    self.pipe.enable_xformers_memory_efficient_attention()
                except:
                    logger.info("xformers not available, using standard attention")
            
            logger.info("✅ Image generation model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading image model: {str(e)}")
            logger.warning("Image generation will be disabled")
            self.enabled = False
    
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> io.BytesIO:
        """
        Generate image from text prompt
        
        Args:
            prompt: Text description of desired image
            negative_prompt: Things to avoid in the image
            width: Image width
            height: Image height
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            seed: Random seed for reproducibility
            
        Returns:
            BytesIO object containing PNG image data
        """
        if not self.enabled:
            raise Exception("Image generation is not available. GPU required.")
        
        if self.pipe is None:
            self._load_model()
        
        try:
            logger.info(f"Generating image: {prompt[:50]}...")
            
            # Set random seed if provided
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            
            # Generate image
            with torch.autocast(self.device):
                result = self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator
                )
            
            image = result.images[0]
            
            # Convert to BytesIO
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            logger.info("✅ Image generated successfully!")
            return img_byte_arr
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise
    
    async def generate_simple_placeholder(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512
    ) -> io.BytesIO:
        """
        Generate a simple placeholder image when GPU is not available
        Useful for testing without heavy compute
        """
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a gradient background
        img = Image.new('RGB', (width, height), color='#667eea')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = f"Image: {prompt[:30]}..."
        
        # Draw centered text
        text_bbox = draw.textbbox((0, 0), text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, fill='white')
        
        # Convert to BytesIO
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
    
    def is_available(self) -> bool:
        """Check if image generation is available"""
        return self.enabled and self.pipe is not None


# Lightweight alternative using pre-generated images or simpler models
class LightweightImageService:
    """
    Lightweight image service for resource-constrained environments
    Uses smaller models or placeholder generation
    """
    
    async def generate_image(self, prompt: str, **kwargs) -> io.BytesIO:
        """Generate placeholder or use lightweight model"""
        from PIL import Image, ImageDraw, ImageFont
        import random
        
        width = kwargs.get('width', 512)
        height = kwargs.get('height', 512)
        
        # Generate colorful placeholder
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
        color = random.choice(colors)
        
        img = Image.new('RGB', (width, height), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add prompt text
        text = f"🎨 {prompt[:40]}"
        text_bbox = draw.textbbox((0, 0), text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, fill='white')
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
