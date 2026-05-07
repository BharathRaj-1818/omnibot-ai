"""
Voice Service - Speech-to-Text and Text-to-Speech
Uses Whisper for STT and gTTS for TTS
"""

import whisper
from gtts import gTTS
import io
import tempfile
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)


class VoiceService:
    """
    Voice processing service for speech recognition and synthesis
    """
    
    def __init__(self, whisper_model: str = "base"):
        """
        Initialize voice service
        
        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large)
        """
        self.whisper_model_name = whisper_model
        self.whisper_model = None
        self.enabled = True
        
        logger.info(f"Initializing Voice Service with Whisper model: {whisper_model}")
        
        # Load Whisper model
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Load Whisper model for speech recognition"""
        try:
            logger.info("Loading Whisper model...")
            self.whisper_model = whisper.load_model(self.whisper_model_name)
            logger.info("✅ Whisper model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            logger.warning("Speech-to-text will be disabled")
            self.enabled = False
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        language: Optional[str] = None
    ) -> str:
        """
        Convert speech to text using Whisper
        
        Args:
            audio_data: Audio file data (bytes)
            language: Optional language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Transcribed text
        """
        if not self.enabled or self.whisper_model is None:
            raise Exception("Speech-to-text service is not available")
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            # Transcribe using Whisper
            logger.info("Transcribing audio...")
            
            result = await asyncio.to_thread(
                self.whisper_model.transcribe,
                temp_audio_path,
                language=language
            )
            
            text = result["text"].strip()
            detected_language = result.get("language", language or "unknown")
            
            logger.info(f"✅ Transcription complete: {text[:50]}... (Language: {detected_language})")
            
            # Clean up temp file
            import os
            os.unlink(temp_audio_path)
            
            return text
            
        except Exception as e:
            logger.error(f"Error in speech-to-text: {str(e)}")
            raise
    
    async def text_to_speech(
        self,
        text: str,
        language: str = "en",
        slow: bool = False
    ) -> io.BytesIO:
        """
        Convert text to speech using gTTS
        
        Args:
            text: Text to convert to speech
            language: Language code (e.g., 'en', 'es', 'fr', 'de')
            slow: Whether to speak slowly
            
        Returns:
            BytesIO object containing MP3 audio data
        """
        try:
            logger.info(f"Converting text to speech: {text[:50]}...")
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to BytesIO
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            logger.info("✅ Text-to-speech conversion complete!")
            
            return audio_buffer
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """Check if voice services are available"""
        return self.enabled and self.whisper_model is not None
    
    def get_supported_languages(self) -> dict:
        """Get list of supported languages for TTS"""
        return {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh-CN": "Chinese (Simplified)",
            "hi": "Hindi",
            "ar": "Arabic",
            "nl": "Dutch",
            "tr": "Turkish",
            "pl": "Polish",
            "uk": "Ukrainian",
            "vi": "Vietnamese",
            "th": "Thai",
            "id": "Indonesian",
            "sv": "Swedish",
            "no": "Norwegian",
            "da": "Danish",
            "fi": "Finnish",
            "cs": "Czech",
            "el": "Greek",
            "he": "Hebrew",
            "ro": "Romanian"
        }


# Lightweight alternative
class LightweightVoiceService:
    """
    Lightweight voice service using browser-based APIs
    Returns instructions for client-side processing
    """
    
    async def text_to_speech(
        self,
        text: str,
        language: str = "en",
        slow: bool = False
    ) -> io.BytesIO:
        """Generate TTS using gTTS (lightweight)"""
        try:
            tts = gTTS(text=text, lang=language, slow=slow)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            raise
    
    async def speech_to_text(self, audio_data: bytes, **kwargs) -> str:
        """Placeholder - recommend client-side browser API"""
        return "Please use browser's native speech recognition API for better performance"
