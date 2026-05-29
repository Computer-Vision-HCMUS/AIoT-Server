"""
SmartClock-specific models:
  - PomodoroSession
  - SleepSession + SleepSensorBatch
  - SeminarRecording
  - GameScore
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ─── Pomodoro ─────────────────────────────────────────────────────────────────

class PomodoroSession(Base):
    """One completed Pomodoro study or break session."""

    __tablename__ = "pomodoro_sessions"
    __table_args__ = (
        Index("ix_pomodoro_device_timestamp", "device_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # ISO 8601 UTC timestamp of when the session completed
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Duration in seconds
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    session_type: Mapped[str] = mapped_column(
        Enum("study", "break", name="pomodoro_type_enum"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    device: Mapped["Device"] = relationship("Device", back_populates="pomodoro_sessions")  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<PomodoroSession id={self.id} type={self.session_type} "
            f"duration={self.duration}s>"
        )


# ─── Sleep ────────────────────────────────────────────────────────────────────

class SleepSession(Base):
    """One sleep monitoring session; contains multiple SleepSensorBatch rows."""

    __tablename__ = "sleep_sessions"
    __table_args__ = (
        Index("ix_sleep_device_start", "device_id", "start_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("active", "completed", name="sleep_status_enum"),
        nullable=False,
        default="active",
    )
    sleep_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    device: Mapped["Device"] = relationship("Device", back_populates="sleep_sessions")  # noqa: F821
    sensor_batches: Mapped[list["SleepSensorBatch"]] = relationship(
        "SleepSensorBatch", back_populates="sleep_session", cascade="all, delete-orphan"
    )
    quality_report: Mapped["SleepQualityReport"] = relationship(
        "SleepQualityReport",
        back_populates="sleep_session",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<SleepSession id={self.id} status={self.status} "
            f"score={self.sleep_score}>"
        )


class SleepSensorBatch(Base):
    """
    A batch of sensor readings uploaded every ~240 s during a SleepSession.
    sound_level and light_level are raw numeric values from the ESP32 sensors.
    """

    __tablename__ = "sleep_sensor_batches"
    __table_args__ = (
        Index("ix_sleep_batch_session_ts", "sleep_session_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sleep_session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sleep_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sound_level: Mapped[float] = mapped_column(Float, nullable=False)
    light_level: Mapped[float] = mapped_column(Float, nullable=False)

    sleep_session: Mapped["SleepSession"] = relationship(
        "SleepSession", back_populates="sensor_batches"
    )

    def __repr__(self) -> str:
        return (
            f"<SleepSensorBatch id={self.id} "
            f"sound={self.sound_level} light={self.light_level}>"
        )


class SleepQualityReport(Base):
    """
    One generated sleep quality report for a completed SleepSession.
    Stores the Sleep Monitoring use case result shown to the user.
    """

    __tablename__ = "sleep_quality_reports"
    __table_args__ = (
        Index("ix_sleep_quality_generated", "generated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sleep_session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sleep_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    duration_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    quality_label: Mapped[str] = mapped_column(
        Enum("poor", "fair", "good", "excellent", name="sleep_quality_label_enum"),
        nullable=False,
    )
    duration_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    sound_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    light_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_sound_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_light_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_issue: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    noise_issue: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    light_issue: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    sleep_session: Mapped["SleepSession"] = relationship(
        "SleepSession", back_populates="quality_report"
    )

    def __repr__(self) -> str:
        return (
            f"<SleepQualityReport session_id={self.sleep_session_id} "
            f"label={self.quality_label}>"
        )


# ─── Seminar ──────────────────────────────────────────────────────────────────

class SeminarRecording(Base):
    """An uploaded speech recording and its AI evaluation result."""

    __tablename__ = "seminar_recordings"
    __table_args__ = (
        Index("ix_seminar_device_created", "device_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    # Duration of the recording in seconds
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pending", "processing", "completed", "failed", name="seminar_status_enum"),
        nullable=False,
        default="pending",
    )
    # AI evaluation scores (0–100); null until evaluation completes
    clarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    speed_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    noise_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    device: Mapped["Device"] = relationship("Device", back_populates="seminar_recordings")  # noqa: F821

    def __repr__(self) -> str:
        return f"<SeminarRecording id={self.id} status={self.status}>"


# ─── Game ─────────────────────────────────────────────────────────────────────

class GameScore(Base):
    """A single Flappy Bird game result."""

    __tablename__ = "game_scores"
    __table_args__ = (
        Index("ix_game_device_score", "device_id", "score"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    device: Mapped["Device"] = relationship("Device", back_populates="game_scores")  # noqa: F821

    def __repr__(self) -> str:
        return f"<GameScore id={self.id} score={self.score}>"


# ── Deferred import to avoid circular reference ───────────────────────────────
from app.models.device import Device  # noqa: E402, F401
