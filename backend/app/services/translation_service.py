"""
Translation Service - Multi-language support using Hugging Face transformers
"""

from transformers import MarianMTModel, MarianTokenizer, pipeline
import logging
from typing import Optional, Dict
from functools import lru_cache
import asyncio

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Translation service using MarianMT models from Hugging Face
    Supports 100+ languages
    """
    
    def __init__(self):
        """Initialize translation service"""
        self.models = {}  # Cache for loaded models
        self.tokenizers = {}  # Cache for loaded tokenizers
        self.language_detector = None
        
        logger.info("Initializing Translation Service")
        
        # Initialize language detection
        self._load_language_detector()
    
    def _load_language_detector(self):
        """Load language detection pipeline"""
        try:
            logger.info("Loading language detection model...")
            self.language_detector = pipeline(
                "text-classification",
                model="papluca/xlm-roberta-base-language-detection"
            )
            logger.info("✅ Language detection model loaded!")
        except Exception as e:
            logger.error(f"Error loading language detector: {str(e)}")
            logger.warning("Language detection will use fallback method")
    
    def _get_model_name(self, source_lang: str, target_lang: str) -> str:
        """
        Get appropriate MarianMT model name for language pair
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Model name from Hugging Face
        """
        # Normalize language codes
        source_lang = source_lang.lower().split('-')[0]
        target_lang = target_lang.lower().split('-')[0]
        
        # Common language pair mappings
        # MarianMT uses special language codes
        lang_map = {
            "zh": "zh",
            "ja": "ja",
            "ko": "ko",
            "ar": "ar",
            "hi": "hi",
            "ru": "ru",
            "es": "es",
            "fr": "fr",
            "de": "de",
            "it": "it",
            "pt": "pt",
            "nl": "nl",
            "pl": "pl",
            "tr": "tr",
            "vi": "vi",
            "th": "th",
            "id": "id",
            "sv": "sv",
            "no": "no",
            "da": "da",
            "fi": "fi",
            "cs": "cs",
            "el": "el",
            "he": "he",
            "uk": "uk",
            "ro": "ro"
        }
        
        source = lang_map.get(source_lang, source_lang)
        target = lang_map.get(target_lang, target_lang)
        
        # MarianMT model naming convention
        if source == "en":
            return f"Helsinki-NLP/opus-mt-en-{target}"
        elif target == "en":
            return f"Helsinki-NLP/opus-mt-{source}-en"
        else:
            # For non-English pairs, translate via English
            return f"Helsinki-NLP/opus-mt-{source}-en"
    
    @lru_cache(maxsize=10)
    def _load_model(self, model_name: str):
        """
        Load and cache translation model
        
        Args:
            model_name: Hugging Face model identifier
            
        Returns:
            Tuple of (model, tokenizer)
        """
        try:
            if model_name not in self.models:
                logger.info(f"Loading translation model: {model_name}")
                
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
                
                self.tokenizers[model_name] = tokenizer
                self.models[model_name] = model
                
                logger.info(f"✅ Model loaded: {model_name}")
            
            return self.models[model_name], self.tokenizers[model_name]
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            raise
    
    async def detect_language(self, text: str) -> str:
        """
        Detect the language of input text
        
        Args:
            text: Input text
            
        Returns:
            Detected language code (e.g., 'en', 'es', 'fr')
        """
        try:
            if self.language_detector is None:
                return "en"  # Default fallback
            
            # Detect language
            result = self.language_detector(text[:512])[0]  # Use first 512 chars
            detected_lang = result['label'].lower()
            confidence = result['score']
            
            logger.info(f"Detected language: {detected_lang} (confidence: {confidence:.2f})")
            
            return detected_lang
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return "en"  # Default to English on error
    
    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "en",
        max_length: int = 512
    ) -> str:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code or 'auto' for detection
            target_lang: Target language code
            max_length: Maximum length of translation
            
        Returns:
            Translated text
        """
        try:
            # Auto-detect source language if needed
            if source_lang == "auto":
                source_lang = await self.detect_language(text)
            
            # No translation needed if languages match
            if source_lang == target_lang:
                return text
            
            logger.info(f"Translating from {source_lang} to {target_lang}")
            
            # Get model for language pair
            model_name = self._get_model_name(source_lang, target_lang)
            model, tokenizer = self._load_model(model_name)
            
            # Tokenize
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
            
            # Translate
            translated = model.generate(**inputs, max_length=max_length)
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            
            # If translating between two non-English languages, we need a second step
            if source_lang != "en" and target_lang != "en":
                logger.info(f"Two-step translation: {source_lang} -> en -> {target_lang}")
                # First translation gave us English, now translate to target
                model_name_2 = self._get_model_name("en", target_lang)
                model_2, tokenizer_2 = self._load_model(model_name_2)
                
                inputs_2 = tokenizer_2(translated_text, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
                translated_2 = model_2.generate(**inputs_2, max_length=max_length)
                translated_text = tokenizer_2.decode(translated_2[0], skip_special_tokens=True)
            
            logger.info(f"✅ Translation complete: {translated_text[:50]}...")
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            # Return original text if translation fails
            return text
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages
        
        Returns:
            Dictionary of language codes and names
        """
        return {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "nl": "Dutch",
            "pl": "Polish",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
            "hi": "Hindi",
            "tr": "Turkish",
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
            "uk": "Ukrainian",
            "ro": "Romanian"
        }


# Lightweight fallback service
class LightweightTranslationService:
    """
    Lightweight translation using simple dictionary or external free API
    """
    
    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
        """Simple translation or pass-through"""
        # In production, you could use a free API like LibreTranslate
        logger.info(f"Lightweight translation: {source_lang} -> {target_lang}")
        return text
    
    async def detect_language(self, text: str) -> str:
        """Simple language detection"""
        return "en"
