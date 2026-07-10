"""
EmotiCare AIoT — Pydantic schemas (request/response models).
"""

from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ─── Devices ──────────────────────────────────────────────────────────────────

class DevicePairRequest(BaseModel):
    pairing_code: str = Field(min_length=1, max_length=20)
    device_name: str = Field(min_length=1, max_length=120)
    firmware_version: Optional[str] = Field(default=None, max_length=50)


class DevicePairResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    user_id: str
    device_name: str
    device_token: str  # returned once only
    status: str
    paired_at: datetime


class DeviceHeartbeatRequest(BaseModel):
    firmware_version: Optional[str] = Field(default=None, max_length=50)


class DeviceHeartbeatResponse(BaseModel):
    device_id: str
    server_time: datetime
    status: str
    config_version: str


# ─── Emotion Sessions ─────────────────────────────────────────────────────────

EmotionLabel = Literal[
    "happy", "neutral", "stressed", "sad", "angry", "tired", "uncertain"
]
QualityFlag = Literal["clean", "noisy", "too_short", "low_confidence"]


class EmotionSessionItem(BaseModel):
    """One emotion session to be synced from the Edge Device."""

    client_session_id: str = Field(min_length=1, max_length=80)
    emotion_label: EmotionLabel
    confidence_score: float = Field(ge=0.0, le=1.0)
    quality_flag: QualityFlag
    inference_latency_ms: Optional[int] = Field(default=None, ge=0)
    client_created_at: datetime


class EmotionSessionSyncRequest(BaseModel):
    sessions: list[EmotionSessionItem] = Field(min_length=1, max_length=50)


class EmotionSessionSyncResponse(BaseModel):
    received_count: int
    total_submitted: int
    received_ids: list[str]


# ─── Recommendations ──────────────────────────────────────────────────────────

class RecommendationRequestPayload(BaseModel):
    session_id: str = Field(min_length=36, max_length=36)


class RecommendationResponse(BaseModel):
    recommendation_id: str
    emotion_label: str
    cards: list[dict[str, Any]]
    status: Literal["success", "failed", "limited"]


# ─── Media ────────────────────────────────────────────────────────────────────

MediaCategory = Literal[
    "relax", "focus", "sleep", "happy",
    "sad_support", "anger_release", "energy_recover"
]
MediaType = Literal["song", "podcast", "both"]


class MediaCategoriesResponse(BaseModel):
    categories: list[dict[str, str]]


class MediaRecommendationRequest(BaseModel):
    category: Optional[MediaCategory] = None
    media_type: Optional[MediaType] = None
    emotion_label: Optional[EmotionLabel] = None
    user_intent: Optional[str] = Field(default=None, max_length=120)


class MediaRecommendationResponse(BaseModel):
    category: Optional[str]
    media_type: str
    cards: list[dict[str, Any]]


# ─── Conversations ────────────────────────────────────────────────────────────

class ConversationRespondRequest(BaseModel):
    session_id: str = Field(min_length=36, max_length=36)
    user_message: Optional[str] = Field(default=None, max_length=500)


class ConversationRespondResponse(BaseModel):
    conversation_id: str
    safety_flag: Literal["none", "low", "medium", "high"]
    card: dict[str, Any]


# ─── Feedback ─────────────────────────────────────────────────────────────────

ActivityType = Literal["breathing", "rest", "movement", "journaling"]


class ActivityFeedbackRequest(BaseModel):
    recommendation_id: str = Field(min_length=36, max_length=36)
    activity_type: ActivityType
    selected: bool = False
    feedback_score: Optional[int] = Field(default=None, ge=1, le=5)


class MediaFeedbackRequest(BaseModel):
    session_id: str = Field(min_length=36, max_length=36)
    media_item_id: str = Field(min_length=36, max_length=36)
    user_intent: Optional[str] = Field(default=None, max_length=120)
    feedback_score: Optional[int] = Field(default=None, ge=1, le=5)


class FeedbackSavedResponse(BaseModel):
    feedback_id: str
    saved: bool


# ─── Reports ──────────────────────────────────────────────────────────────────

PeriodType = Literal["daily", "weekly", "monthly", "yearly"]


class TftSummaryResponse(BaseModel):
    report_id: str
    period_type: PeriodType
    period_start: date
    period_end: date
    cards: list[dict[str, Any]]
    emotion_distribution: dict[str, Any]
    trend_summary: Optional[str]
    data_quality: Literal["enough_data", "limited_data"]
    generated_at: datetime


class ReportGenerateRequest(BaseModel):
    period_type: PeriodType


class ReportGenerateResponse(BaseModel):
    report_id: str
    period_type: PeriodType
    data_quality: Literal["enough_data", "limited_data"]
    cards: list[dict[str, Any]]
    generated_at: datetime


# ─── Device Config ────────────────────────────────────────────────────────────

class DeviceConfigResponse(BaseModel):
    emotion_labels: list[str]
    confidence_thresholds: dict[str, float]
    quality_flags: list[str]
    sync_interval_sec: int
    heartbeat_interval_sec: int
    tft_card_max: int
    text_templates: dict[str, str]
    media_categories: list[str]
