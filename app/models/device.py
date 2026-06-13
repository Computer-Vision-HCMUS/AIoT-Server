"""
Device-level models: Device, TimerConfig, SleepConfig.

A Device represents one physical ESP32 board registered with the server.
Each device has at most one TimerConfig and one SleepConfig (1-to-1).
"""

import secrets
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _generate_token() -> str:
    return secrets.token_hex(32)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    device_type: Mapped[str] = mapped_column(
        Enum("smartclock", "visiondrive", name="device_type_enum"),
        nullable=False,
    )
    device_token: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, default=_generate_token
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # ── Relationships ──────────────────────────────────────────────────────
    timer_config: Mapped["TimerConfig"] = relationship(
        "TimerConfig", back_populates="device", uselist=False, cascade="all, delete-orphan"
    )
    sleep_config: Mapped["SleepConfig"] = relationship(
        "SleepConfig", back_populates="device", uselist=False, cascade="all, delete-orphan"
    )
    pomodoro_sessions: Mapped[list["PomodoroSession"]] = relationship(  # noqa: F821
        "PomodoroSession", back_populates="device", cascade="all, delete-orphan"
    )
    sleep_sessions: Mapped[list["SleepSession"]] = relationship(  # noqa: F821
        "SleepSession", back_populates="device", cascade="all, delete-orphan"
    )
    seminar_recordings: Mapped[list["SeminarRecording"]] = relationship(  # noqa: F821
        "SeminarRecording", back_populates="device", cascade="all, delete-orphan"
    )
    game_scores: Mapped[list["GameScore"]] = relationship(  # noqa: F821
        "GameScore", back_populates="device", cascade="all, delete-orphan"
    )
    study_sessions: Mapped[list["StudySession"]] = relationship(  # noqa: F821
        "StudySession", back_populates="device", cascade="all, delete-orphan"
    )
    presentation_sessions: Mapped[list["PresentationSession"]] = relationship(  # noqa: F821
        "PresentationSession", back_populates="device", cascade="all, delete-orphan"
    )
    trips: Mapped[list["Trip"]] = relationship(  # noqa: F821
        "Trip", back_populates="device", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Device id={self.id} device_id={self.device_id!r} type={self.device_type}>"


class TimerConfig(Base):
    """Pomodoro timer configuration — one per SmartClock device."""

    __tablename__ = "timer_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    # Duration in minutes; defaults match spec (25 / 5)
    study_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=25)
    break_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    device: Mapped["Device"] = relationship("Device", back_populates="timer_config")

    def __repr__(self) -> str:
        return (
            f"<TimerConfig device_id={self.device_id} "
            f"study={self.study_duration}m break={self.break_duration}m>"
        )


class SleepConfig(Base):
    """Sleep / alarm configuration — one per SmartClock device."""

    __tablename__ = "sleep_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    alarm_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Stored as "HH:MM" string; nullable when alarm is disabled
    alarm_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    # Duration in minutes; default 480 = 8 hours
    sleep_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=480)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    device: Mapped["Device"] = relationship("Device", back_populates="sleep_config")

    def __repr__(self) -> str:
        return (
            f"<SleepConfig device_id={self.device_id} "
            f"alarm={self.alarm_enabled} time={self.alarm_time}>"
        )


# ── Deferred imports to avoid circular references ─────────────────────────────
from app.models.smartclock import PomodoroSession, SleepSession, SeminarRecording, GameScore, StudySession, PresentationSession  # noqa: E402, F401
from app.models.visiondrive import Trip  # noqa: E402, F401
