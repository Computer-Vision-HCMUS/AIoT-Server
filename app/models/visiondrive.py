"""
VisionDriveAI-specific models:
  - Trip
  - DistractionEvent
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Trip(Base):
    """One driving trip recorded by a VisionDriveAI device."""

    __tablename__ = "trips"
    __table_args__ = (
        Index("ix_trip_device_start", "device_id", "start_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("active", "completed", name="trip_status_enum"),
        nullable=False,
        default="active",
    )
    # Safety score 0–100; null until trip is completed
    safety_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    device: Mapped["Device"] = relationship("Device", back_populates="trips")  # noqa: F821
    distraction_events: Mapped[list["DistractionEvent"]] = relationship(
        "DistractionEvent", back_populates="trip", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Trip id={self.id} status={self.status} "
            f"safety_score={self.safety_score}>"
        )


class DistractionEvent(Base):
    """
    A single distraction event detected during a Trip.

    event_type:
      - drowsiness      — eyes closed / head nodding
      - gaze_distraction — looking away from road
      - phone_use       — hand holding phone while moving

    severity: low | medium | high
    """

    __tablename__ = "distraction_events"
    __table_args__ = (
        Index("ix_distraction_trip_ts", "trip_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_type: Mapped[str] = mapped_column(
        Enum(
            "drowsiness",
            "gaze_distraction",
            "phone_use",
            name="distraction_type_enum",
        ),
        nullable=False,
    )
    severity: Mapped[str] = mapped_column(
        Enum("low", "medium", "high", name="distraction_severity_enum"),
        nullable=False,
    )

    trip: Mapped["Trip"] = relationship("Trip", back_populates="distraction_events")

    def __repr__(self) -> str:
        return (
            f"<DistractionEvent id={self.id} type={self.event_type} "
            f"severity={self.severity}>"
        )


# ── Deferred import to avoid circular reference ───────────────────────────────
from app.models.device import Device  # noqa: E402, F401
