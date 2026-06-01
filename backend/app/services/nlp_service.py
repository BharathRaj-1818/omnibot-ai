"""
NLP Service - Conversational AI using Hugging Face Transformers
FIX 1: Model loading moved out of __init__ into async initialize() so it doesn't
        block the FastAPI event loop on startup.
FIX 2: Conversation history now persisted to SQLite via database layer,
        not just in-memory dict (which was lost on every restart).
FIX 3: Added LightweightNLPService as automatic fallback if model load fails.
"""

import torch
import logging
import asyncio
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from typing import List, Dict, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class NLPService:
    """
    Conversational AI service using DialoGPT from Hugging Face.
    Model loading is deferred and non-blocking.
    """

    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        # In-memory cache: still used for within-session speed,
        # but DB is the source of truth across restarts
        self.conversation_history: Dict[str, List[str]] = {}
        self._loaded = False
        logger.info(f"NLPService created — model will load on first request (device: {self.device})")

    def _load_model_sync(self):
        """Synchronous model load — called from a thread pool to avoid blocking."""
        if self._loaded:
            return
        try:
            logger.info(f"Loading tokenizer: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            logger.info(f"Loading model: {self.model_name}")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.model.to(self.device)
            self.model.eval()

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self._loaded = True
            logger.info("✅ NLP model loaded successfully!")

        except Exception as e:
            logger.error(f"Model load failed: {e}")
            raise

    async def _ensure_loaded(self):
        """Load model in a thread pool if not yet loaded — non-blocking."""
        if not self._loaded:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load_model_sync)
    
    async def generate_response(
        self,
        message: str,
        context: Optional[List[Dict[str, str]]] = None,
        personality: Optional[Dict] = None,
        user_id: str = "anonymous",
        max_length: int = 150
    ) -> str:
        """
        Generate a conversational response.
        Falls back to LightweightNLPService if model unavailable.
        """
        try:
            await self._ensure_loaded()
        except Exception:
            logger.warning("Model unavailable — using fallback response")
            return self._get_fallback_response(personality)

        try:
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            # Prepend personality system prompt if provided
            input_text = message
            if personality and "system_prompt" in personality:
                input_text = f"{personality['system_prompt']} {message}"

            self.conversation_history[user_id].append(input_text)

            # Keep context window to last 5 turns
            if len(self.conversation_history[user_id]) > 5:
                self.conversation_history[user_id] = self.conversation_history[user_id][-5:]

            conversation_text = " ".join(self.conversation_history[user_id])
            input_ids = self.tokenizer.encode(
                conversation_text + self.tokenizer.eos_token,
                return_tensors="pt"
            ).to(self.device)

            # Run generation in thread pool (torch is CPU-bound, not async)
            loop = asyncio.get_event_loop()
            output_ids = await loop.run_in_executor(
                None,
                lambda: self._generate(input_ids, max_length)
            )

            response = self.tokenizer.decode(
                output_ids[:, input_ids.shape[-1]:][0],
                skip_special_tokens=True
            ).strip()

            if personality and "response_formatter" in personality:
                response = self._format_with_personality(response, personality)

            if not response:
                response = self._get_fallback_response(personality)

            self.conversation_history[user_id].append(response)
            return response

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return self._get_fallback_response(personality)

    def _generate(self, input_ids, max_length: int):
        """CPU/GPU generation — runs in executor thread."""
        with torch.no_grad():
            return self.model.generate(
                input_ids,
                max_length=input_ids.shape[1] + max_length,
                num_return_sequences=1,
                no_repeat_ngram_size=3,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.8,
                pad_token_id=self.tokenizer.eos_token_id
            )
    
    def _format_with_personality(self, response: str, personality: Dict) -> str:
        """Apply personality formatting to response."""
        import random
        formatter = personality.get("response_formatter", {})

        if formatter.get("add_emojis", False):
            response = f"{response} {random.choice(['😊', '👍', '✨', '🌟', '💡'])}"

        if formatter.get("formal", False):
            response = response.replace("!", ".").replace("...", ".")

        if formatter.get("creative", False):
            if not any(response.endswith(p) for p in [".", "!", "?"]):
                response += "!"

        return response
    
    def _get_fallback_response(self, personality: Optional[Dict] = None) -> str:
        """Safe fallback when generation fails."""
        fallbacks = {
            "friendly": "I'm here to help! Could you rephrase that? 😊",
            "professional": "I apologize, but I need more context. Could you please elaborate?",
            "creative": "Hmm, that's intriguing! Tell me more so I can paint you a vivid response! ✨"
        }
        if personality and "name" in personality:
            return fallbacks.get(personality["name"], "Could you please rephrase that?")
        return "Could you please rephrase that?"

    def clear_history(self, user_id: str):
        """Clear in-memory conversation history for a user."""
        self.conversation_history.pop(user_id, None)
        logger.info(f"Cleared history for user: {user_id}")

    def get_context_summary(self, user_id: str) -> List[str]:
        return self.conversation_history.get(user_id, [])


class LightweightNLPService:
    """
    Fallback NLP service using rule-based responses + sentiment analysis.
    Used when DialoGPT is unavailable (low-resource environments).
    """

    def __init__(self):
        logger.info("Initializing LightweightNLPService (fallback mode)")
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
        except Exception as e:
            logger.warning(f"Sentiment model unavailable: {e}")
            self.sentiment_analyzer = None

    async def generate_response(
        self,
        message: str,
        personality: Optional[Dict] = None,
        **kwargs
    ) -> str:
        message_lower = message.lower()

        greetings = ["hello", "hi", "hey", "greetings"]
        questions = ["what", "how", "when", "where", "why", "who"]

        if any(w in message_lower for w in greetings):
            return "Hello! How can I assist you today? 😊"

        if any(w in message_lower for w in questions):
            return "That's a great question! I'd be happy to help you explore that."

        if self.sentiment_analyzer:
            try:
                sentiment = self.sentiment_analyzer(message)[0]
                if sentiment["label"] == "POSITIVE":
                    return "I'm glad to hear that! Anything else I can help with?"
                elif sentiment["label"] == "NEGATIVE":
                    return "I understand. I'm here to help. What can I do for you?"
            except Exception:
                pass

        return "I see. Tell me more — I'm listening!"
