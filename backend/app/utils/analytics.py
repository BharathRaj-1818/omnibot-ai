"""
Analytics Tracker - Monitor chatbot usage and performance
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, Counter
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """
    Track and analyze chatbot usage, conversations, and performance
    """
    
    def __init__(self, storage_path: str = "data/analytics.json"):
        """
        Initialize analytics tracker
        
        Args:
            storage_path: Path to store analytics data
        """
        self.storage_path = storage_path
        self.conversations = []
        self.image_generations = []
        self.voice_interactions = []
        
        # In-memory stats
        self.stats = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_images": 0,
            "total_voice": 0,
            "active_users": set(),
            "personality_usage": Counter(),
            "language_usage": Counter(),
            "daily_stats": defaultdict(lambda: {
                "conversations": 0,
                "messages": 0,
                "images": 0,
                "users": set()
            })
        }
        
        logger.info("Analytics Tracker initialized")
    
    async def log_conversation(
        self,
        user_id: str,
        message: str,
        response: str,
        personality_mode: str,
        language: str = "en"
    ):
        """
        Log a conversation interaction
        
        Args:
            user_id: User identifier
            message: User message
            response: Bot response
            personality_mode: Active personality mode
            language: Detected language
        """
        try:
            timestamp = datetime.utcnow()
            date_key = timestamp.strftime("%Y-%m-%d")
            
            # Update stats
            self.stats["total_conversations"] += 1
            self.stats["total_messages"] += 2  # User message + bot response
            self.stats["active_users"].add(user_id)
            self.stats["personality_usage"][personality_mode] += 1
            self.stats["language_usage"][language] += 1
            
            # Daily stats
            self.stats["daily_stats"][date_key]["conversations"] += 1
            self.stats["daily_stats"][date_key]["messages"] += 2
            self.stats["daily_stats"][date_key]["users"].add(user_id)
            
            # Store conversation
            conversation_data = {
                "user_id": user_id,
                "message": message[:200],  # Truncate for privacy
                "response": response[:200],
                "personality_mode": personality_mode,
                "language": language,
                "timestamp": timestamp.isoformat()
            }
            
            self.conversations.append(conversation_data)
            
            # Keep only last 1000 conversations in memory
            if len(self.conversations) > 1000:
                self.conversations = self.conversations[-1000:]
            
        except Exception as e:
            logger.error(f"Error logging conversation: {str(e)}")
    
    async def log_image_generation(self, user_id: str, prompt: str):
        """
        Log an image generation event
        
        Args:
            user_id: User identifier
            prompt: Image generation prompt
        """
        try:
            timestamp = datetime.utcnow()
            date_key = timestamp.strftime("%Y-%m-%d")
            
            self.stats["total_images"] += 1
            self.stats["daily_stats"][date_key]["images"] += 1
            
            self.image_generations.append({
                "user_id": user_id,
                "prompt": prompt[:100],
                "timestamp": timestamp.isoformat()
            })
            
            # Keep only last 500 image generations
            if len(self.image_generations) > 500:
                self.image_generations = self.image_generations[-500:]
            
        except Exception as e:
            logger.error(f"Error logging image generation: {str(e)}")
    
    async def log_voice_interaction(self, user_id: str, interaction_type: str):
        """
        Log a voice interaction (STT or TTS)
        
        Args:
            user_id: User identifier
            interaction_type: 'stt' or 'tts'
        """
        try:
            self.stats["total_voice"] += 1
            
            self.voice_interactions.append({
                "user_id": user_id,
                "type": interaction_type,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error logging voice interaction: {str(e)}")
    
    async def get_analytics(
        self,
        user_id: Optional[str] = None,
        days: int = 7
    ) -> Dict:
        """
        Get analytics data
        
        Args:
            user_id: Optional user ID to filter by
            days: Number of days to include
            
        Returns:
            Analytics dictionary
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get daily stats for the period
            daily_stats_list = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                date_key = date.strftime("%Y-%m-%d")
                
                day_data = self.stats["daily_stats"].get(date_key, {
                    "conversations": 0,
                    "messages": 0,
                    "images": 0,
                    "users": set()
                })
                
                daily_stats_list.append({
                    "date": date_key,
                    "conversations": day_data["conversations"],
                    "messages": day_data["messages"],
                    "images": day_data["images"],
                    "active_users": len(day_data["users"])
                })
            
            # Get most popular personality
            popular_personality = "friendly"
            if self.stats["personality_usage"]:
                popular_personality = self.stats["personality_usage"].most_common(1)[0][0]
            
            # Language distribution
            language_dist = dict(self.stats["language_usage"])
            
            analytics = {
                "total_conversations": self.stats["total_conversations"],
                "total_messages": self.stats["total_messages"],
                "total_images_generated": self.stats["total_images"],
                "active_users": len(self.stats["active_users"]),
                "popular_personality": popular_personality,
                "language_distribution": language_dist,
                "daily_stats": daily_stats_list,
                "period_days": days
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "total_images_generated": 0,
                "active_users": 0,
                "popular_personality": "friendly",
                "language_distribution": {},
                "daily_stats": []
            }
    
    def save_analytics(self):
        """Save analytics to disk"""
        try:
            Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert sets to lists for JSON serialization
            save_data = {
                "conversations": self.conversations[-100:],  # Save last 100
                "image_generations": self.image_generations[-50:],
                "stats": {
                    "total_conversations": self.stats["total_conversations"],
                    "total_messages": self.stats["total_messages"],
                    "total_images": self.stats["total_images"],
                    "personality_usage": dict(self.stats["personality_usage"]),
                    "language_usage": dict(self.stats["language_usage"])
                }
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.info(f"Analytics saved to {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Error saving analytics: {str(e)}")
