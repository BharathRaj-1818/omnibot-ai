"""
Voice Service - Speech-to-Text (Whisper) and Text-to-Speech (gTTS)
This file was not provided — created from scratch to match main.py API.
"""

import io
import logging
import asyncio
import tempfile
import os
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceService:
    """
    Voice processing service.
    - Speech-to-Text: OpenAI Whisper (runs locally, free)
    - Text-to-Speech: gTTS (Google TTS, free)
    """

    def __init__(self, whisper_model: str = "base"):
        """
        Args:
            whisper_model: Whisper model size — tiny | base | small | medium | large
                           'base' is a good balance of speed and accuracy (~150MB)
        """
        self.whisper_model_name = os.getenv("VOICE_MODEL", whisper_model)
        self._whisper = None
        logger.info(f"VoiceService created — Whisper '{self.whisper_model_name}' loads on first use")

    def _load_whisper(self):
        """Load Whisper model synchronously (called from thread pool)."""
        if self._whisper is not None:
            return
        try:
            import whisper
            self._whisper = whisper.load_model(self.whisper_model_name)
            logger.info(f"✅ Whisper model '{self.whisper_model_name}' loaded")
        except Exception as e:
            logger.error(f"Whisper load failed: {e}")
            raise
    
    async def speech_to_text(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None
    ) -> str:
        """
        Convert audio bytes to text using Whisper.

        Args:
            audio_bytes: Raw audio file bytes (WAV, MP3, OGG, FLAC, etc.)
            language: Language code hint (e.g. 'en', 'es'). None = auto-detect.

        Returns:
            Transcribed text string.
        """
        loop = asyncio.get_event_loop()

        # Load model in thread pool (non-blocking)
        await loop.run_in_executor(None, self._load_whisper)

        # Write audio to a temp file (Whisper needs a file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            options = {}
            if language and language != "auto":
                options["language"] = language

            result = await loop.run_in_executor(
                None,
                lambda: self._whisper.transcribe(tmp_path, **options)
            )
            text = result.get("text", "").strip()
            logger.info(f"Transcribed {len(audio_bytes)} bytes → '{text[:60]}...'")
            return text

        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            raise

        finally:
            os.unlink(tmp_path)  # Always clean up temp file
    
    async def text_to_speech(
        self,
        text: str,
        language: str = "en",
        slow: bool = False
    ) -> io.BytesIO:
        """
        Convert text to MP3 audio using gTTS.

        Args:
            text: Text to synthesize.
            language: BCP-47 language code (e.g. 'en', 'hi', 'es').
            slow: Speak slowly (useful for language learning).

        Returns:
            BytesIO buffer containing MP3 audio data.
        """
        try:
            from gtts import gTTS

            # gTTS is synchronous — run in thread pool
            loop = asyncio.get_event_loop()

            def _synthesize():
                tts = gTTS(text=text, lang=language, slow=slow)
                buffer = io.BytesIO()
                tts.write_to_fp(buffer)
                buffer.seek(0)
                return buffer

            buffer = await loop.run_in_executor(None, _synthesize)
            logger.info(f"TTS generated {buffer.getbuffer().nbytes} bytes for '{text[:40]}...'")
            return buffer

        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            raise
