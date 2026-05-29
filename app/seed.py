from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.device import Device, SleepConfig, TimerConfig
from app.models.smartclock import (
    GameScore,
    PomodoroSession,
    SleepQualityReport,
    SleepSensorBatch,
    SleepSession,
)
from app.models.visiondrive import DistractionEvent, Trip


SMARTCLOCK_ID = "smartclock-demo-001"
SMARTCLOCK_TOKEN = "dev-smartclock-token"
VISIONDRIVE_ID = "visiondrive-demo-001"
VISIONDRIVE_TOKEN = "dev-visiondrive-token"


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _get_or_create_device(
    db: Session,
    device_id: str,
    device_type: str,
    device_token: str,
) -> Device:
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if device is None:
        device = Device(
            device_id=device_id,
            device_type=device_type,
            device_token=device_token,
        )
        db.add(device)
        db.flush()
        return device

    device.device_type = device_type
    device.device_token = device_token
    device.last_seen_at = datetime.now(timezone.utc)
    db.flush()
    return device


def _replace_device_children(db: Session, device: Device) -> None:
    for model in (PomodoroSession, SleepSession, GameScore, Trip):
        db.query(model).filter(model.device_id == device.id).delete(
            synchronize_session=False
        )
    db.query(TimerConfig).filter(TimerConfig.device_id == device.id).delete(
        synchronize_session=False
    )
    db.query(SleepConfig).filter(SleepConfig.device_id == device.id).delete(
        synchronize_session=False
    )
    db.flush()


def seed_database() -> None:
    db = SessionLocal()
    try:
        smartclock = _get_or_create_device(
            db,
            SMARTCLOCK_ID,
            "smartclock",
            SMARTCLOCK_TOKEN,
        )
        visiondrive = _get_or_create_device(
            db,
            VISIONDRIVE_ID,
            "visiondrive",
            VISIONDRIVE_TOKEN,
        )

        _replace_device_children(db, smartclock)
        _replace_device_children(db, visiondrive)

        db.add(
            TimerConfig(
                device_id=smartclock.id,
                study_duration=25,
                break_duration=5,
            )
        )
        db.add(
            SleepConfig(
                device_id=smartclock.id,
                alarm_enabled=True,
                alarm_time="06:30",
                sleep_duration=480,
            )
        )

        db.add_all(
            [
                PomodoroSession(
                    device_id=smartclock.id,
                    timestamp=_dt("2026-05-28T08:30:00Z"),
                    duration=1500,
                    session_type="study",
                ),
                PomodoroSession(
                    device_id=smartclock.id,
                    timestamp=_dt("2026-05-28T08:35:00Z"),
                    duration=300,
                    session_type="break",
                ),
                GameScore(
                    device_id=smartclock.id,
                    score=42,
                    timestamp=_dt("2026-05-28T10:00:00Z"),
                ),
            ]
        )

        sleep_session = SleepSession(
            device_id=smartclock.id,
            start_time=_dt("2026-05-28T23:00:00Z"),
            end_time=_dt("2026-05-29T06:10:00Z"),
            status="completed",
            sleep_score=86,
        )
        db.add(sleep_session)
        db.flush()

        db.add_all(
            [
                SleepSensorBatch(
                    sleep_session_id=sleep_session.id,
                    timestamp=_dt("2026-05-28T23:30:00Z"),
                    sound_level=18.5,
                    light_level=7.2,
                ),
                SleepSensorBatch(
                    sleep_session_id=sleep_session.id,
                    timestamp=_dt("2026-05-29T02:30:00Z"),
                    sound_level=22.0,
                    light_level=5.5,
                ),
                SleepSensorBatch(
                    sleep_session_id=sleep_session.id,
                    timestamp=_dt("2026-05-29T05:30:00Z"),
                    sound_level=31.0,
                    light_level=18.0,
                ),
                SleepQualityReport(
                    sleep_session_id=sleep_session.id,
                    duration_minutes=430,
                    quality_label="good",
                    duration_score=35,
                    sound_score=24,
                    light_score=27,
                    avg_sound_level=23.8,
                    avg_light_level=10.2,
                    duration_issue=True,
                    noise_issue=False,
                    light_issue=False,
                    recommendation=(
                        "Sleep quality is good. Try going to bed 30-60 minutes "
                        "earlier to reach the 8-hour target."
                    ),
                ),
            ]
        )

        trip = Trip(
            device_id=visiondrive.id,
            start_time=_dt("2026-05-29T01:00:00Z"),
            end_time=_dt("2026-05-29T01:25:00Z"),
            status="completed",
            safety_score=83,
        )
        db.add(trip)
        db.flush()

        db.add_all(
            [
                DistractionEvent(
                    trip_id=trip.id,
                    timestamp=_dt("2026-05-29T01:08:00Z"),
                    event_type="gaze_distraction",
                    severity="medium",
                ),
                DistractionEvent(
                    trip_id=trip.id,
                    timestamp=_dt("2026-05-29T01:18:00Z"),
                    event_type="phone_use",
                    severity="high",
                ),
            ]
        )

        db.commit()
        print("Seed data inserted.")
        print(f"SmartClock token: {SMARTCLOCK_TOKEN}")
        print(f"VisionDrive token: {VISIONDRIVE_TOKEN}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
