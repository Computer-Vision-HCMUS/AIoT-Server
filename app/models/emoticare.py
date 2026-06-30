"""
EmotiCare AIoT — Cloud database models.

Tables:
  users                 — người dùng, có pairing_code để ghép thiết bị
  devices               — thiết bị phần cứng, liên kết với user
  emotion_sessions      — emotion session đã sync từ Edge
  recommendation_requests — yêu cầu gợi ý hoạt động / media
  activity_feedback     — feedback hoạt động người dùng chọn
  conversation_requests — yêu cầu hội thoại và phản hồi cloud
  tft_reports           — báo cáo rút gọn trả về TFT
  media_items           — danh mục bài hát / podcast
  media_selection_logs  — log người dùng chọn media
"""

from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


JsonDocument = JSON().with_variant(JSONB, "postgresql")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ─── Users ────────────────────────────────────────────────────────────────────

class User(Base):
    """Người dùng — tạo qua web portal hoặc seed, ghép thiết bị bằng pairing_code."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    pairing_code: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    consent_audio_storage: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    devices: Mapped[list["Device"]] = relationship(
        "Device", back_populates="user", cascade="all, delete-orphan"
    )
    emotion_sessions: Mapped[list["EmotionSession"]] = relationship(
        "EmotionSession", back_populates="user", cascade="all, delete-orphan"
    )
    tft_reports: Mapped[list["TftReport"]] = relationship(
        "TftReport", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r}>"


# ─── Devices ──────────────────────────────────────────────────────────────────

class Device(Base):
    """Thiết bị phần cứng EmotiCare — liên kết với một User."""

    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    device_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    firmware_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        Enum("online", "offline", "disabled", name="device_status_enum"),
        nullable=False,
        default="offline",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="devices")
    emotion_sessions: Mapped[list["EmotionSession"]] = relationship(
        "EmotionSession", back_populates="device", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Device id={self.id} name={self.name!r} status={self.status}>"


# ─── Emotion Sessions ─────────────────────────────────────────────────────────

class EmotionSession(Base):
    """
    Emotion session đồng bộ từ Edge Device lên Cloud.
    client_session_id dùng để chống tạo trùng khi retry (idempotent).
    """

    __tablename__ = "emotion_sessions"
    __table_args__ = (
        UniqueConstraint(
            "device_id",
            "client_session_id",
            name="uq_emotion_device_client_session",
        ),
        Index("ix_emotion_user_created", "user_id", "created_at"),
        Index("ix_emotion_device_created", "device_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_session_id: Mapped[str] = mapped_column(
        String(80), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Emotion label taxonomy: happy | neutral | stressed | sad | angry | tired | uncertain
    emotion_label: Mapped[str] = mapped_column(String(50), nullable=False)
    # Confidence 0.000 – 1.000
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    # Quality of the audio/inference
    quality_flag: Mapped[str] = mapped_column(
        Enum("clean", "noisy", "too_short", "low_confidence", name="quality_flag_enum"),
        nullable=False,
    )
    inference_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Timestamp from the Edge device
    client_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="emotion_sessions")
    device: Mapped["Device"] = relationship("Device", back_populates="emotion_sessions")
    recommendation_requests: Mapped[list["RecommendationRequest"]] = relationship(
        "RecommendationRequest",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    conversation_requests: Mapped[list["ConversationRequest"]] = relationship(
        "ConversationRequest",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    media_selection_logs: Mapped[list["MediaSelectionLog"]] = relationship(
        "MediaSelectionLog",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<EmotionSession id={self.id} emotion={self.emotion_label} "
            f"confidence={self.confidence_score}>"
        )


# ─── Recommendation Requests ──────────────────────────────────────────────────

class RecommendationRequest(Base):
    """Yêu cầu gợi ý hoạt động/media từ Edge Device."""

    __tablename__ = "recommendation_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("emotion_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    request_payload: Mapped[dict] = mapped_column(JsonDocument, nullable=False)
    response_payload: Mapped[dict] = mapped_column(JsonDocument, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("success", "failed", "limited", name="reco_status_enum"),
        nullable=False,
        default="success",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # Relationships
    session: Mapped["EmotionSession"] = relationship(
        "EmotionSession", back_populates="recommendation_requests"
    )
    activity_feedbacks: Mapped[list["ActivityFeedback"]] = relationship(
        "ActivityFeedback",
        back_populates="recommendation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<RecommendationRequest id={self.id} status={self.status}>"


# ─── Activity Feedback ────────────────────────────────────────────────────────

class ActivityFeedback(Base):
    """Feedback người dùng chọn / đánh giá hoạt động được gợi ý."""

    __tablename__ = "activity_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    recommendation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recommendation_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_type: Mapped[str] = mapped_column(
        Enum(
            "breathing",
            "rest",
            "movement",
            "journaling",
            name="activity_type_enum",
        ),
        nullable=False,
    )
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    feedback_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    recommendation: Mapped["RecommendationRequest"] = relationship(
        "RecommendationRequest", back_populates="activity_feedbacks"
    )

    def __repr__(self) -> str:
        return (
            f"<ActivityFeedback id={self.id} type={self.activity_type} "
            f"selected={self.selected}>"
        )


# ─── Conversation Requests ────────────────────────────────────────────────────

class ConversationRequest(Base):
    """Yêu cầu hội thoại hỗ trợ cảm xúc — Cloud tạo phản hồi qua safety filter."""

    __tablename__ = "conversation_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("emotion_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_message_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_text: Mapped[str] = mapped_column(String(500), nullable=False)
    safety_flag: Mapped[str] = mapped_column(
        Enum("none", "low", "medium", "high", name="safety_flag_enum"),
        nullable=False,
        default="none",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    session: Mapped["EmotionSession"] = relationship(
        "EmotionSession", back_populates="conversation_requests"
    )

    def __repr__(self) -> str:
        return (
            f"<ConversationRequest id={self.id} safety_flag={self.safety_flag}>"
        )


# ─── TFT Reports ──────────────────────────────────────────────────────────────

class TftReport(Base):
    """Báo cáo rút gọn theo period, được Cloud tổng hợp và trả về TFT screen."""

    __tablename__ = "tft_reports"
    __table_args__ = (
        Index("ix_tft_report_user_period", "user_id", "period_type", "period_start"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_type: Mapped[str] = mapped_column(
        Enum("daily", "weekly", "monthly", "yearly", name="period_type_enum"),
        nullable=False,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    # JSON array of TFT cards: [{title, body, severity, action_id}]
    tft_cards: Mapped[list] = mapped_column(JsonDocument, nullable=False, default=list)
    # JSON object: {happy: 0.3, neutral: 0.2, ...}
    emotion_distribution: Mapped[dict] = mapped_column(JsonDocument, nullable=False, default=dict)
    trend_summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    data_quality: Mapped[str] = mapped_column(
        Enum("enough_data", "limited_data", name="data_quality_enum"),
        nullable=False,
        default="limited_data",
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="tft_reports")

    def __repr__(self) -> str:
        return (
            f"<TftReport id={self.id} period={self.period_type} "
            f"quality={self.data_quality}>"
        )


# ─── Media Items ──────────────────────────────────────────────────────────────

class MediaItem(Base):
    """Bài hát hoặc podcast trong database media — dùng cho Media Recommendation."""

    __tablename__ = "media_items"
    __table_args__ = (
        Index("ix_media_type_category", "media_type", "category"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    media_type: Mapped[str] = mapped_column(
        Enum("song", "podcast", name="media_type_enum"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    creator: Mapped[str | None] = mapped_column(String(160), nullable=True)
    category: Mapped[str] = mapped_column(
        Enum(
            "relax",
            "focus",
            "sleep",
            "happy",
            "sad_support",
            "anger_release",
            "energy_recover",
            name="media_category_enum",
        ),
        nullable=False,
    )
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    selection_logs: Mapped[list["MediaSelectionLog"]] = relationship(
        "MediaSelectionLog",
        back_populates="media_item",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<MediaItem id={self.id} type={self.media_type} "
            f"category={self.category} title={self.title!r}>"
        )


# ─── Media Selection Logs ─────────────────────────────────────────────────────

class MediaSelectionLog(Base):
    """Log mỗi lần người dùng chọn hoặc đánh giá một bài hát/podcast."""

    __tablename__ = "media_selection_logs"
    __table_args__ = (
        Index("ix_media_log_session", "session_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("emotion_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    media_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("media_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_intent: Mapped[str | None] = mapped_column(String(120), nullable=True)
    selected_category: Mapped[str] = mapped_column(String(50), nullable=False)
    feedback_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    session: Mapped["EmotionSession"] = relationship(
        "EmotionSession", back_populates="media_selection_logs"
    )
    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem", back_populates="selection_logs"
    )

    def __repr__(self) -> str:
        return (
            f"<MediaSelectionLog id={self.id} "
            f"media_item_id={self.media_item_id}>"
        )
