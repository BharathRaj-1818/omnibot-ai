"""
NLP Service - Conversational AI using Hugging Face Transformers
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from typing import List, Dict, Optional
import logging
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)


class NLPService:
    """
    Natural Language Processing service using free Hugging Face models
    Uses DialoGPT for conversational AI
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        """
        Initialize NLP service with conversational model
        
        Args:
            model_name: Hugging Face model identifier
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.conversation_history = {}  # Store conversation context per user
        
        logger.info(f"Initializing NLP Service with model: {model_name}")
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self._load_model()
    
    def _load_model(self):
        """Load the conversational model"""
        try:
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            logger.info("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.model.to(self.device)
            self.model.eval()
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("✅ Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    async def generate_response(
        self,
        message: str,
        context: Optional[List[Dict[str, str]]] = None,
        personality: Optional[Dict] = None,
        user_id: str = "anonymous",
        max_length: int = 150
    ) -> str:
        """
        Generate conversational response
        
        Args:
            message: User input message
            context: Previous conversation context
            personality: Personality configuration
            user_id: User identifier for context tracking
            max_length: Maximum response length
            
        Returns:
            Generated response text
        """
        try:
            # Get or initialize conversation history for user
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Prepare input with personality prefix if provided
            input_text = message
            if personality and "system_prompt" in personality:
                input_text = f"{personality['system_prompt']} {message}"
            
            # Add current message to history
            self.conversation_history[user_id].append(input_text)
            
            # Keep only last 5 messages for context window
            if len(self.conversation_history[user_id]) > 5:
                self.conversation_history[user_id] = self.conversation_history[user_id][-5:]
            
            # Encode conversation history
            conversation_text = " ".join(self.conversation_history[user_id])
            input_ids = self.tokenizer.encode(
                conversation_text + self.tokenizer.eos_token,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                output_ids = self.model.generate(
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
            
            # Decode response
            response = self.tokenizer.decode(
                output_ids[:, input_ids.shape[-1]:][0],
                skip_special_tokens=True
            )
            
            # Apply personality formatting if provided
            if personality and "response_formatter" in personality:
                response = self._format_with_personality(response, personality)
            
            # Clean up response
            response = response.strip()
            if not response:
                response = self._get_fallback_response(personality)
            
            # Add response to history
            self.conversation_history[user_id].append(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_fallback_response(personality)
    
    def _format_with_personality(self, response: str, personality: Dict) -> str:
        """Format response based on personality settings"""
        formatter = personality.get("response_formatter", {})
        
        # Add emojis for friendly mode
        if formatter.get("add_emojis", False):
            emojis = ["😊", "👍", "✨", "🌟", "💡"]
            import random
            response = f"{response} {random.choice(emojis)}"
        
        # Make more formal for professional mode
        if formatter.get("formal", False):
            response = response.replace("!", ".")
            response = response.replace("...", ".")
        
        # Add creative flair
        if formatter.get("creative", False):
            if not any(response.endswith(p) for p in [".", "!", "?"]):
                response += "!"
        
        return response
    
    def _get_fallback_response(self, personality: Optional[Dict] = None) -> str:
        """Get fallback response when generation fails"""
        fallbacks = {
            "friendly": "I'm here to help! Could you rephrase that? 😊",
            "professional": "I apologize, but I need more context. Could you please elaborate?",
            "creative": "Hmm, that's intriguing! Tell me more so I can paint you a vivid response! ✨"
        }
        
        if personality and "name" in personality:
            return fallbacks.get(personality["name"], "Could you please rephrase that?")
        
        return "Could you please rephrase that?"
    
    def clear_history(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []
            logger.info(f"Cleared conversation history for user: {user_id}")
    
    def get_context_summary(self, user_id: str) -> List[str]:
        """Get conversation history summary for a user"""
        return self.conversation_history.get(user_id, [])


# Alternative lightweight service for resource-constrained environments
class LightweightNLPService:
    """
    Lightweight NLP service using simpler models or rule-based responses
    Fallback when resources are limited
    """
    
    def __init__(self):
        logger.info("Initializing Lightweight NLP Service")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    
    async def generate_response(
        self,
        message: str,
        personality: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """Generate simple rule-based response"""
        
        # Analyze sentiment
        sentiment = self.sentiment_analyzer(message)[0]
        
        # Simple response generation based on sentiment and keywords
        message_lower = message.lower()
        
        greetings = ["hello", "hi", "hey", "greetings"]
        questions = ["what", "how", "when", "where", "why", "who"]
        
        if any(word in message_lower for word in greetings):
            return "Hello! How can I assist you today? 😊"
        
        elif any(word in message_lower for word in questions):
            return "That's a great question! I'd be happy to help you explore that topic."
        
        elif sentiment["label"] == "POSITIVE":
            return "I'm glad to hear that! Is there anything specific I can help you with?"
        
        elif sentiment["label"] == "NEGATIVE":
            return "I understand. I'm here to help. What can I do to assist you?"
        
        else:
            return "I see. Tell me more about that, I'm listening!"
