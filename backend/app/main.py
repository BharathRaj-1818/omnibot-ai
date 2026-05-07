"""
OmniBot - Multi-Platform Conversational AI
Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional, List
import asyncio

from app.services.nlp_service import NLPService
from app.services.image_service import ImageService
from app.services.voice_service import VoiceService
from app.services.translation_service import TranslationService
from app.models.database import init_db, get_db
from app.models.schemas import (
    ChatRequest, ChatResponse, ImageGenerationRequest,
    PersonalityMode, AnalyticsResponse
)
from app.utils.personality import PersonalityManager
from app.utils.analytics import AnalyticsTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize services globally
nlp_service = None
image_service = None
voice_service = None
translation_service = None
personality_manager = None
analytics_tracker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    global nlp_service, image_service, voice_service, translation_service
    global personality_manager, analytics_tracker
    
    logger.info("🚀 Starting OmniBot services...")
    
    # Initialize database
    await init_db()
    
    # Initialize services
    nlp_service = NLPService()
    image_service = ImageService()
    voice_service = VoiceService()
    translation_service = TranslationService()
    personality_manager = PersonalityManager()
    analytics_tracker = AnalyticsTracker()
    
    logger.info("✅ All services initialized successfully!")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down services...")
    # Add cleanup code here if needed


# Create FastAPI app
app = FastAPI(
    title="OmniBot API",
    description="Multi-Platform Conversational AI with NLP, Image Generation, and Voice Support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to OmniBot API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "nlp": nlp_service is not None,
            "image": image_service is not None,
            "voice": voice_service is not None,
            "translation": translation_service is not None
        }
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user messages and returns AI responses
    """
    try:
        # Get current personality mode
        personality = personality_manager.get_personality(request.personality_mode)
        
        # Translate input if needed
        detected_language = "en"
        translated_message = request.message
        
        if request.auto_translate:
            detected_language = await translation_service.detect_language(request.message)
            if detected_language != "en":
                translated_message = await translation_service.translate(
                    request.message, 
                    source_lang=detected_language,
                    target_lang="en"
                )
        
        # Generate response using NLP service
        response = await nlp_service.generate_response(
            message=translated_message,
            context=request.context,
            personality=personality,
            user_id=request.user_id
        )
        
        # Translate response back if needed
        if request.auto_translate and detected_language != "en":
            response = await translation_service.translate(
                response,
                source_lang="en",
                target_lang=detected_language
            )
        
        # Track analytics
        await analytics_tracker.log_conversation(
            user_id=request.user_id,
            message=request.message,
            response=response,
            personality_mode=request.personality_mode,
            language=detected_language
        )
        
        return ChatResponse(
            response=response,
            personality_mode=request.personality_mode,
            detected_language=detected_language,
            confidence=0.95
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/api/generate-image")
async def generate_image(request: ImageGenerationRequest):
    """
    Generate images from text descriptions using Stable Diffusion
    """
    try:
        # Generate image
        image_data = await image_service.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_steps
        )
        
        # Track analytics
        await analytics_tracker.log_image_generation(
            user_id=request.user_id,
            prompt=request.prompt
        )
        
        return StreamingResponse(
            image_data,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=generated_image.png"}
        )
        
    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@app.post("/api/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...), language: Optional[str] = "en"):
    """
    Convert voice messages to text using Whisper
    """
    try:
        # Read audio file
        audio_data = await audio.read()
        
        # Convert speech to text
        text = await voice_service.speech_to_text(audio_data, language=language)
        
        return {"text": text, "language": language}
        
    except Exception as e:
        logger.error(f"Speech to text error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech recognition failed: {str(e)}")


@app.post("/api/text-to-speech")
async def text_to_speech(text: str, language: str = "en", slow: bool = False):
    """
    Convert text to speech using gTTS
    """
    try:
        # Generate speech
        audio_data = await voice_service.text_to_speech(text, language=language, slow=slow)
        
        return StreamingResponse(
            audio_data,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"}
        )
        
    except Exception as e:
        logger.error(f"Text to speech error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")


@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics(user_id: Optional[str] = None, days: int = 7):
    """
    Get conversation analytics and statistics
    """
    try:
        analytics = await analytics_tracker.get_analytics(user_id=user_id, days=days)
        return analytics
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")


@app.post("/api/personality")
async def switch_personality(mode: PersonalityMode):
    """
    Switch chatbot personality mode
    """
    try:
        personality = personality_manager.get_personality(mode)
        return {
            "mode": mode,
            "description": personality.get("description", ""),
            "sample_response": personality.get("sample_response", "")
        }
        
    except Exception as e:
        logger.error(f"Personality switch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Personality switch failed: {str(e)}")


@app.get("/api/languages")
async def get_supported_languages():
    """
    Get list of supported languages for translation
    """
    return {
        "languages": translation_service.get_supported_languages()
    }


@app.post("/api/translate")
async def translate_text(text: str, target_language: str, source_language: str = "auto"):
    """
    Translate text to target language
    """
    try:
        if source_language == "auto":
            source_language = await translation_service.detect_language(text)
        
        translated = await translation_service.translate(
            text,
            source_lang=source_language,
            target_lang=target_language
        )
        
        return {
            "original": text,
            "translated": translated,
            "source_language": source_language,
            "target_language": target_language
        }
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
