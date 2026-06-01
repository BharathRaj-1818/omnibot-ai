"""
Personality Manager - Manages chatbot personality modes
This file was not provided — created from scratch to match main.py API.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


PERSONALITIES: Dict[str, Dict] = {
    "friendly": {
        "name": "friendly",
        "description": "Warm, approachable, and encouraging. Uses casual language and emojis.",
        "system_prompt": "You are a friendly, warm, and helpful assistant. Be encouraging and positive.",
        "sample_response": "Hey there! I'd love to help you with that! 😊",
        "response_formatter": {
            "add_emojis": True,
            "formal": False,
            "creative": False
        }
    },
    "professional": {
        "name": "professional",
        "description": "Formal, precise, and business-oriented. No slang or emojis.",
        "system_prompt": "You are a professional business assistant. Be concise, accurate, and formal.",
        "sample_response": "Thank you for your inquiry. I will address your request promptly.",
        "response_formatter": {
            "add_emojis": False,
            "formal": True,
            "creative": False
        }
    },
    "creative": {
        "name": "creative",
        "description": "Imaginative, expressive, and artistic. Uses vivid language and metaphors.",
        "system_prompt": "You are a creative, imaginative assistant. Use vivid language, metaphors, and storytelling.",
        "sample_response": "What a fascinating canvas of a question! Let's paint this together! ✨",
        "response_formatter": {
            "add_emojis": True,
            "formal": False,
            "creative": True
        }
    }
}


class PersonalityManager:
    """Manages chatbot personality modes."""

    def get_personality(self, mode) -> Dict:
        """
        Get personality configuration for a given mode.

        Args:
            mode: PersonalityMode enum value or string key.

        Returns:
            Personality config dict.
        """
        # Handle both enum values and raw strings
        key = mode.value if hasattr(mode, "value") else str(mode)

        if key not in PERSONALITIES:
            logger.warning(f"Unknown personality '{key}' — defaulting to 'friendly'")
            key = "friendly"

        return PERSONALITIES[key]
    
    def list_personalities(self) -> Dict[str, str]:
        """Return dict of mode → description for all personalities."""
        return {k: v["description"] for k, v in PERSONALITIES.items()}
