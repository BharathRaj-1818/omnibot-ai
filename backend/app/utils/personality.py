"""
Personality Manager - Handle different chatbot personalities
"""

import json
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PersonalityManager:
    """
    Manage different chatbot personalities and modes
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize personality manager
        
        Args:
            config_path: Path to personality configuration file
        """
        self.config_path = config_path or "config/personalities.json"
        self.personalities = self._load_personalities()
        self.current_mode = "friendly"
        
        logger.info(f"Personality Manager initialized with {len(self.personalities)} modes")
    
    def _load_personalities(self) -> Dict:
        """Load personality configurations"""
        
        # Default personalities
        default_personalities = {
            "friendly": {
                "name": "friendly",
                "description": "Warm, casual, and engaging. Uses emojis and friendly language.",
                "system_prompt": "You are a friendly and helpful AI assistant. Be warm, use emojis occasionally, and engage in a casual, conversational tone.",
                "response_formatter": {
                    "add_emojis": True,
                    "formal": False,
                    "creative": False,
                    "tone": "casual"
                },
                "sample_phrases": [
                    "That's awesome! 😊",
                    "I'd be happy to help with that!",
                    "Great question! Let me explain...",
                    "You're doing great! Keep it up! 🌟"
                ],
                "sample_response": "Hey there! I'm here to help and chat! What's on your mind today? 😊"
            },
            "professional": {
                "name": "professional",
                "description": "Formal, structured, and business-like communication style.",
                "system_prompt": "You are a professional AI assistant. Provide clear, concise, and formal responses. Use proper grammar and maintain a business-appropriate tone.",
                "response_formatter": {
                    "add_emojis": False,
                    "formal": True,
                    "creative": False,
                    "tone": "formal"
                },
                "sample_phrases": [
                    "I would be pleased to assist you with that.",
                    "To clarify your inquiry...",
                    "Please find the information below.",
                    "Thank you for your question."
                ],
                "sample_response": "Good day. I am here to provide professional assistance. How may I help you today?"
            },
            "creative": {
                "name": "creative",
                "description": "Imaginative, expressive, and storytelling-focused responses.",
                "system_prompt": "You are a creative and imaginative AI assistant. Use vivid language, metaphors, and storytelling. Be expressive and think outside the box.",
                "response_formatter": {
                    "add_emojis": True,
                    "formal": False,
                    "creative": True,
                    "tone": "expressive"
                },
                "sample_phrases": [
                    "Picture this...",
                    "Let me paint you a picture!",
                    "Here's an interesting way to think about it...",
                    "Imagine if..."
                ],
                "sample_response": "Welcome to a world of imagination! ✨ I'm here to explore ideas, tell stories, and help your creativity soar! What adventure shall we embark on?"
            }
        }
        
        # Try to load from file if it exists
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    logger.info(f"Loaded personalities from {self.config_path}")
                    return loaded
        except Exception as e:
            logger.warning(f"Could not load personalities from file: {str(e)}")
        
        return default_personalities
    
    def get_personality(self, mode: str = "friendly") -> Dict:
        """
        Get personality configuration for specified mode
        
        Args:
            mode: Personality mode name
            
        Returns:
            Personality configuration dictionary
        """
        mode = mode.lower()
        
        if mode not in self.personalities:
            logger.warning(f"Unknown personality mode: {mode}, using friendly")
            mode = "friendly"
        
        return self.personalities[mode]
    
    def list_personalities(self) -> Dict[str, str]:
        """
        List all available personalities
        
        Returns:
            Dictionary of personality names and descriptions
        """
        return {
            name: config.get("description", "")
            for name, config in self.personalities.items()
        }
    
    def add_custom_personality(
        self,
        name: str,
        description: str,
        system_prompt: str,
        response_formatter: Optional[Dict] = None
    ) -> bool:
        """
        Add a custom personality
        
        Args:
            name: Personality name
            description: Personality description
            system_prompt: System prompt for this personality
            response_formatter: Optional formatting configuration
            
        Returns:
            True if successful
        """
        try:
            if response_formatter is None:
                response_formatter = {
                    "add_emojis": False,
                    "formal": False,
                    "creative": False,
                    "tone": "neutral"
                }
            
            self.personalities[name.lower()] = {
                "name": name.lower(),
                "description": description,
                "system_prompt": system_prompt,
                "response_formatter": response_formatter,
                "custom": True
            }
            
            logger.info(f"Added custom personality: {name}")
            
            # Save to file
            self._save_personalities()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom personality: {str(e)}")
            return False
    
    def _save_personalities(self):
        """Save personalities to configuration file"""
        try:
            # Create config directory if it doesn't exist
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.personalities, f, indent=2)
            
            logger.info(f"Saved personalities to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving personalities: {str(e)}")
    
    def get_sample_response(self, mode: str) -> str:
        """Get a sample response for a personality mode"""
        personality = self.get_personality(mode)
        return personality.get("sample_response", "Hello! How can I help you?")
