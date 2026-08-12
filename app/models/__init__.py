"""
EmotiCare AIoT — model registry.
Import all models here so Alembic auto-detects them via Base.metadata.
"""

from app.models.emoticare import (
    ActivityFeedback,
    ConversationRequest,
    Device,
    EmotionSession,
    MediaItem,
    MediaSelectionLog,
    RecommendationRequest,
    TftReport,
    User,
)

__all__ = [
    "User",
    "Device",
    "EmotionSession",
    "RecommendationRequest",
    "ActivityFeedback",
    "ConversationRequest",
    "TftReport",
    "MediaItem",
    "MediaSelectionLog",
]
