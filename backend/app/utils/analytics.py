"""
Analytics Tracker - Conversation metrics and usage statistics
This file was not provided — created from scratch to match main.py API.
Uses async SQLAlchemy to match the fixed database.py.
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import AsyncSessionLocal, Conversation, ImageGeneration

logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """Tracks conversation metrics and aggregates usage statistics."""
    
    async def log_conversation(
        self,
        user_id: str,
        message: str,
        response: str,
        personality_mode: str = "friendly",
        language: str = "en"
    ):
        """Persist a conversation turn to the database."""
        try:
            async with AsyncSessionLocal() as db:
                entry = Conversation(
                    user_id=user_id,
                    message=message,
                    response=response,
                    personality_mode=str(personality_mode.value if hasattr(personality_mode, "value") else personality_mode),
                    language=language,
                    timestamp=datetime.utcnow()
                )
                db.add(entry)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to log conversation: {e}")
            # Don't re-raise — analytics failure shouldn't break chat
    
    async def log_image_generation(self, user_id: str, prompt: str):
        """Persist an image generation event to the database."""
        try:
            async with AsyncSessionLocal() as db:
                entry = ImageGeneration(
                    user_id=user_id,
                    prompt=prompt,
                    width=512,
                    height=512,
                    timestamp=datetime.utcnow()
                )
                db.add(entry)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to log image generation: {e}")
    
    async def get_analytics(
        self,
        user_id: Optional[str] = None,
        days: int = 7
    ) -> Dict:
        """
        Aggregate analytics stats.

        Args:
            user_id: Filter to a specific user (None = all users).
            days: Look-back window in days.

        Returns:
            Dict matching the AnalyticsResponse schema.
        """
        try:
            async with AsyncSessionLocal() as db:
                since = datetime.utcnow() - timedelta(days=days)

                # Base filter
                filters = [Conversation.timestamp >= since]
                if user_id:
                    filters.append(Conversation.user_id == user_id)

                # Total conversations (unique sessions approximate: distinct user_id)
                total_conv_result = await db.execute(
                    select(func.count(Conversation.id)).where(and_(*filters))
                )
                total_conversations = total_conv_result.scalar() or 0

                # Total messages = same as conversations (each row = 1 user message)
                total_messages = total_conversations * 2  # user + bot turn

                # Active unique users
                active_users_result = await db.execute(
                    select(func.count(func.distinct(Conversation.user_id))).where(and_(*filters))
                )
                active_users = active_users_result.scalar() or 0

                # Most popular personality
                popular_result = await db.execute(
                    select(
                        Conversation.personality_mode,
                        func.count(Conversation.personality_mode).label("cnt")
                    )
                    .where(and_(*filters))
                    .group_by(Conversation.personality_mode)
                    .order_by(func.count(Conversation.personality_mode).desc())
                    .limit(1)
                )
                popular_row = popular_result.first()
                popular_personality = popular_row[0] if popular_row else "friendly"

                # Language distribution
                lang_result = await db.execute(
                    select(
                        Conversation.language,
                        func.count(Conversation.language).label("cnt")
                    )
                    .where(and_(*filters))
                    .group_by(Conversation.language)
                )
                language_distribution = {row[0]: row[1] for row in lang_result.all()}

                # Total images generated
                img_filters = [ImageGeneration.timestamp >= since]
                if user_id:
                    img_filters.append(ImageGeneration.user_id == user_id)

                total_img_result = await db.execute(
                    select(func.count(ImageGeneration.id)).where(and_(*img_filters))
                )
                total_images = total_img_result.scalar() or 0

                return {
                    "total_conversations": total_conversations,
                    "total_messages": total_messages,
                    "total_images_generated": total_images,
                    "active_users": active_users,
                    "popular_personality": popular_personality,
                    "language_distribution": language_distribution,
                    "daily_stats": []  # Can be extended later
                }

        except Exception as e:
            logger.error(f"Analytics query failed: {e}")
            # Return safe defaults on failure
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "total_images_generated": 0,
                "active_users": 0,
                "popular_personality": "friendly",
                "language_distribution": {},
                "daily_stats": []
            }
