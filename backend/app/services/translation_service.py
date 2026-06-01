"""
Translation Service - Multi-language support using MarianMT (Hugging Face)
Language detection using langdetect (lightweight, no API needed).
This file was not provided — created from scratch to match main.py API.
"""

import logging
import asyncio
from typing import Optional, List, Dict
from functools import lru_cache

logger = logging.getLogger(__name__)

# Common language pairs supported by Helsinki-NLP MarianMT
# Full list: https://huggingface.co/Helsinki-NLP
SUPPORTED_LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "pl": "Polish",
    "ru": "Russian", "zh": "Chinese", "ja": "Japanese", "ko": "Korean",
    "ar": "Arabic", "hi": "Hindi", "tr": "Turkish", "sv": "Swedish",
    "da": "Danish", "fi": "Finnish", "nb": "Norwegian", "cs": "Czech",
    "ro": "Romanian", "hu": "Hungarian", "uk": "Ukrainian", "vi": "Vietnamese",
}


class TranslationService:
    """
    Translation service using Helsinki-NLP MarianMT models.
    Models are loaded on-demand per language pair (lazy loading).
    Language detection uses langdetect (fast, offline).
    """

    def __init__(self):
        self._model_cache: Dict[str, any] = {}  # key: "src-tgt"
        logger.info("TranslationService initialized (models load on first use)")

    def get_supported_languages(self) -> Dict[str, str]:
        """Return dict of supported language codes and names."""
        return SUPPORTED_LANGUAGES
    
    async def detect_language(self, text: str) -> str:
        """
        Detect language of input text.

        Returns:
            BCP-47 language code (e.g. 'en', 'es'). Falls back to 'en' on error.
        """
        try:
            loop = asyncio.get_event_loop()
            lang = await loop.run_in_executor(None, lambda: self._detect_sync(text))
            logger.info(f"Detected language: {lang}")
            return lang
        except Exception as e:
            logger.warning(f"Language detection failed: {e} — defaulting to 'en'")
            return "en"

    def _detect_sync(self, text: str) -> str:
        """Synchronous language detection using langdetect."""
        try:
            from langdetect import detect
            return detect(text)
        except Exception:
            return "en"
    

    
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Translate text between languages using MarianMT.

        Args:
            text: Text to translate.
            source_lang: Source language code (e.g. 'en').
            target_lang: Target language code (e.g. 'es').

        Returns:
            Translated text string.
        """
        if source_lang == target_lang:
            return text

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._translate_sync(text, source_lang, target_lang)
            )
            return result
        except Exception as e:
            logger.error(f"Translation failed ({source_lang}→{target_lang}): {e}")
            # Return original text on failure rather than crashing
            return text

    def _translate_sync(self, text: str, src: str, tgt: str) -> str:
        """Synchronous translation — called from thread pool."""
        from transformers import MarianMTModel, MarianTokenizer

        model_key = f"{src}-{tgt}"

        if model_key not in self._model_cache:
            model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
            logger.info(f"Loading translation model: {model_name}")
            try:
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
                self._model_cache[model_key] = (tokenizer, model)
                logger.info(f"✅ Translation model loaded: {model_name}")
            except Exception as e:
                # Try English as pivot language (src→en→tgt)
                logger.warning(f"Direct model {model_name} not found: {e}")
                raise ValueError(
                    f"No direct translation model for {src}→{tgt}. "
                    f"Try routing via English."
                )

        tokenizer, model = self._model_cache[model_key]
        inputs = tokenizer([text], return_tensors="pt", padding=True, truncation=True)

        import torch
        with torch.no_grad():
            translated = model.generate(**inputs)

        return tokenizer.decode(translated[0], skip_special_tokens=True)

    async def batch_translate(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[str]:
        """Translate multiple strings efficiently."""
        results = []
        for text in texts:
            translated = await self.translate(text, source_lang, target_lang)
            results.append(translated)
        return results
