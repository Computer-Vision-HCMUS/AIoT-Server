from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.device import Device, SleepConfig, TimerConfig
from app.models.smartclock import (
    GameScore,
    PomodoroSession,
    PresentationSession,
    SeminarRecording,
    SleepQualityReport,
    SleepSensorBatch,
    SleepSession,
    StudySession,
)
from app.models.visiondrive import DistractionEvent, Trip


SMARTCLOCK_ID = "smartclock-demo-001"
SMARTCLOCK_2_ID = "smartclock-demo-002"
SMARTCLOCK_TOKEN = "dev-smartclock-token"
SMARTCLOCK_2_TOKEN = "dev-smartclock-token-2"
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
    for model in (
        PomodoroSession,
        SleepSession,
        GameScore,
        StudySession,
        PresentationSession,
        SeminarRecording,
        Trip,
    ):
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
        smartclock_2 = _get_or_create_device(
            db,
            SMARTCLOCK_2_ID,
            "smartclock",
            SMARTCLOCK_2_TOKEN,
        )
        visiondrive = _get_or_create_device(
            db,
            VISIONDRIVE_ID,
            "visiondrive",
            VISIONDRIVE_TOKEN,
        )

        _replace_device_children(db, smartclock)
        _replace_device_children(db, smartclock_2)
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
        db.add(
            TimerConfig(
                device_id=smartclock_2.id,
                study_duration=50,
                break_duration=10,
            )
        )
        db.add(
            SleepConfig(
                device_id=smartclock_2.id,
                alarm_enabled=False,
                sleep_duration=420,
            )
        )

        # ── Pomodoro Sessions ─────────────────────────────────────────────────
        # Week 1: 2025-11-03 (Monday)
        pomo_2025_11_03_s1 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-11-03T08:30:00Z"),
            duration=25,
            session_type="study",
        )
        pomo_2025_11_03_b1 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-11-03T09:00:00Z"),
            duration=5,
            session_type="break",
        )
        pomo_2025_11_03_s2 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-11-03T09:30:00Z"),
            duration=25,
            session_type="study",
        )
        pomo_2025_11_03_b2 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-11-03T10:00:00Z"),
            duration=5,
            session_type="break",
        )

        # Week 2: 2025-11-17 (Monday)
        pomo_2025_11_17_s1 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-11-17T14:00:00Z"),
            duration=25,
            session_type="study",
        )
        pomo_2025_11_17_b1 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-11-17T14:30:00Z"),
            duration=5,
            session_type="break",
        )
        pomo_2025_11_17_s2 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-11-17T15:00:00Z"),
            duration=25,
            session_type="study",
        )

        # Week 3: 2025-12-08 (Monday)
        pomo_2025_12_08_s1 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-12-08T09:00:00Z"),
            duration=25,
            session_type="study",
        )
        pomo_2025_12_08_b1 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-12-08T09:30:00Z"),
            duration=10,
            session_type="break",
        )
        pomo_2025_12_08_s2 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-12-08T10:00:00Z"),
            duration=25,
            session_type="study",
        )
        pomo_2025_12_08_s3 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2025-12-08T10:30:00Z"),
            duration=25,
            session_type="study",
        )

        # Recent: 2026-05-28 (existing dates)
        pomo_2026_05_28_s1 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2026-05-28T08:30:00Z"),
            duration=25,
            session_type="study",
        )
        pomo_2026_05_28_b1 = PomodoroSession(
            device_id=smartclock.id,
            timestamp=_dt("2026-05-28T08:35:00Z"),
            duration=5,
            session_type="break",
        )
        pomo_2_s1 = PomodoroSession(
            device_id=smartclock_2.id,
            timestamp=_dt("2026-05-29T07:30:00Z"),
            duration=50,
            session_type="study",
        )
        pomo_2_b1 = PomodoroSession(
            device_id=smartclock_2.id,
            timestamp=_dt("2026-05-29T08:20:00Z"),
            duration=10,
            session_type="break",
        )

        db.add_all([
            pomo_2025_11_03_s1, pomo_2025_11_03_b1,
            pomo_2025_11_03_s2, pomo_2025_11_03_b2,
            pomo_2025_11_17_s1, pomo_2025_11_17_b1, pomo_2025_11_17_s2,
            pomo_2025_12_08_s1, pomo_2025_12_08_b1,
            pomo_2025_12_08_s2, pomo_2025_12_08_s3,
            pomo_2026_05_28_s1, pomo_2026_05_28_b1,
            pomo_2_s1, pomo_2_b1,
        ])
        db.flush()  # get IDs before building StudySessions

        # ── Study Sessions ────────────────────────────────────────────────────
        # StudySession 1 — 2025-11-03: 2 study (50 min) + 2 break (10 min), 2 pomodoros
        # focus_minutes = 25 + 25 = 50.0
        # break_minutes = 5 + 5 = 10.0
        db.add(StudySession(
            device_id=smartclock.id,
            start_time=_dt("2025-11-03T08:30:00Z"),
            end_time=_dt("2025-11-03T10:05:00Z"),
            status="completed",
            focus_minutes=50.0,
            break_minutes=10.0,
            pomodoro_count=2,
        ))

        # StudySession 2 — 2025-11-17: 2 study (50 min) + 1 break (5 min), 2 pomodoros
        # focus_minutes = 25 + 25 = 50.0
        # break_minutes = 5.0
        db.add(StudySession(
            device_id=smartclock.id,
            start_time=_dt("2025-11-17T14:00:00Z"),
            end_time=_dt("2025-11-17T15:35:00Z"),
            status="completed",
            focus_minutes=50.0,
            break_minutes=5.0,
            pomodoro_count=2,
        ))

        # StudySession 3 — 2025-12-08: 3 study (75 min) + 1 break (10 min), 3 pomodoros
        # focus_minutes = 25 + 25 + 25 = 75.0
        # break_minutes = 10.0
        db.add(StudySession(
            device_id=smartclock.id,
            start_time=_dt("2025-12-08T09:00:00Z"),
            end_time=_dt("2025-12-08T11:05:00Z"),
            status="completed",
            focus_minutes=75.0,
            break_minutes=10.0,
            pomodoro_count=3,
        ))

        # StudySession 4 — 2026-05-28: 1 study (25 min) + 1 break (5 min), 1 pomodoro
        # focus_minutes = 25.0
        # break_minutes = 5.0
        db.add(StudySession(
            device_id=smartclock.id,
            start_time=_dt("2026-05-28T08:30:00Z"),
            end_time=_dt("2026-05-28T09:05:00Z"),
            status="completed",
            focus_minutes=25.0,
            break_minutes=5.0,
            pomodoro_count=1,
        ))

        db.add(StudySession(
            device_id=smartclock_2.id,
            start_time=_dt("2026-05-29T07:30:00Z"),
            end_time=_dt("2026-05-29T08:30:00Z"),
            status="completed",
            focus_minutes=50.0,
            break_minutes=10.0,
            pomodoro_count=1,
        ))

        db.add_all([
            GameScore(
                device_id=smartclock.id,
                score=42,
                timestamp=_dt("2026-05-28T10:00:00Z"),
            ),
            GameScore(
                device_id=smartclock.id,
                score=77,
                timestamp=_dt("2026-05-29T10:00:00Z"),
            ),
            GameScore(
                device_id=smartclock.id,
                score=58,
                timestamp=_dt("2026-05-30T10:00:00Z"),
            ),
            GameScore(
                device_id=smartclock_2.id,
                score=91,
                timestamp=_dt("2026-05-29T09:00:00Z"),
            ),
            GameScore(
                device_id=smartclock_2.id,
                score=36,
                timestamp=_dt("2026-05-30T09:00:00Z"),
            ),
        ])

        # ── Legacy Seminar Recordings ─────────────────────────────────────────
        # Kept for backward-compatible demo data; Objective 3 uses PresentationSession.
        db.add_all([
            SeminarRecording(
                device_id=smartclock.id,
                file_path="/mock/seminar/demo-001.wav",
                duration=180.0,
                status="completed",
                clarity_score=80.0,
                speed_score=76.0,
                noise_score=88.0,
                confidence_score=74.0,
                evaluated_at=_dt("2025-11-10T10:20:00Z"),
            ),
            SeminarRecording(
                device_id=smartclock_2.id,
                file_path="/mock/seminar/demo-002.wav",
                duration=210.0,
                status="completed",
                clarity_score=86.0,
                speed_score=81.0,
                noise_score=90.0,
                confidence_score=84.0,
                evaluated_at=_dt("2026-05-29T08:45:00Z"),
            ),
        ])

        # ── Presentation Sessions ─────────────────────────────────────────────
        # Completed session 1 — 2025-11-10
        # presentation_score = (85 + 78 + 90 + 82) / 4 = 83.75
        db.add(PresentationSession(
            device_id=smartclock.id,
            start_time=_dt("2025-11-10T10:00:00Z"),
            end_time=_dt("2025-11-10T10:15:00Z"),
            status="completed",
            clarity_score=85.0,
            speed_score=78.0,
            noise_score=90.0,
            confidence_score=82.0,
            presentation_score=(85.0 + 78.0 + 90.0 + 82.0) / 4,  # 83.75
            speech_rate=145.0,
            feedback="Good pacing overall. Work on reducing filler words.",
        ))

        # Completed session 2 — 2025-12-05
        # presentation_score = (72 + 68 + 75 + 65) / 4 = 70.0
        db.add(PresentationSession(
            device_id=smartclock.id,
            start_time=_dt("2025-12-05T14:00:00Z"),
            end_time=_dt("2025-12-05T14:20:00Z"),
            status="completed",
            clarity_score=72.0,
            speed_score=68.0,
            noise_score=75.0,
            confidence_score=65.0,
            presentation_score=(72.0 + 68.0 + 75.0 + 65.0) / 4,  # 70.0
            speech_rate=162.0,
            feedback="Speaking too fast at times. Slow down and breathe.",
        ))

        # Completed session 3 — 2026-01-20
        # presentation_score = (91 + 88 + 94 + 92) / 4 = 91.25
        db.add(PresentationSession(
            device_id=smartclock.id,
            start_time=_dt("2026-01-20T09:30:00Z"),
            end_time=_dt("2026-01-20T09:50:00Z"),
            status="completed",
            clarity_score=91.0,
            speed_score=88.0,
            noise_score=94.0,
            confidence_score=92.0,
            presentation_score=(91.0 + 88.0 + 94.0 + 92.0) / 4,  # 91.25
            speech_rate=138.0,
            feedback="Excellent delivery! Very clear and confident.",
        ))

        # Pending session — 2026-05-28 (just started, no scores yet)
        db.add(PresentationSession(
            device_id=smartclock.id,
            start_time=_dt("2026-05-28T11:00:00Z"),
            status="pending",
        ))

        # ── Sleep Sessions ────────────────────────────────────────────────────
        # Sleep session 1 — 2025-11-15 (November)
        sleep_session_nov = SleepSession(
            device_id=smartclock.id,
            start_time=_dt("2025-11-15T22:30:00Z"),
            end_time=_dt("2025-11-16T06:00:00Z"),
            status="completed",
            sleep_score=72,
        )
        db.add(sleep_session_nov)
        db.flush()

        db.add_all([
            SleepSensorBatch(
                sleep_session_id=sleep_session_nov.id,
                timestamp=_dt("2025-11-15T23:00:00Z"),
                sound_level=24.0,
                light_level=3.5,
            ),
            SleepSensorBatch(
                sleep_session_id=sleep_session_nov.id,
                timestamp=_dt("2025-11-16T02:00:00Z"),
                sound_level=38.5,
                light_level=4.0,
            ),
            SleepSensorBatch(
                sleep_session_id=sleep_session_nov.id,
                timestamp=_dt("2025-11-16T05:00:00Z"),
                sound_level=29.0,
                light_level=12.0,
            ),
            SleepQualityReport(
                sleep_session_id=sleep_session_nov.id,
                duration_minutes=450,
                quality_label="fair",
                duration_score=30,
                sound_score=20,
                light_score=22,
                avg_sound_level=30.5,
                avg_light_level=6.5,
                duration_issue=False,
                noise_issue=True,
                light_issue=False,
                recommendation=(
                    "Sleep disrupted by noise. Consider using earplugs or "
                    "a white-noise machine to improve sleep continuity."
                ),
            ),
        ])

        # Sleep session 2 — 2025-12-20 (December)
        sleep_session_dec = SleepSession(
            device_id=smartclock.id,
            start_time=_dt("2025-12-20T23:00:00Z"),
            end_time=_dt("2025-12-21T07:30:00Z"),
            status="completed",
            sleep_score=91,
        )
        db.add(sleep_session_dec)
        db.flush()

        db.add_all([
            SleepSensorBatch(
                sleep_session_id=sleep_session_dec.id,
                timestamp=_dt("2025-12-20T23:30:00Z"),
                sound_level=14.0,
                light_level=2.0,
            ),
            SleepSensorBatch(
                sleep_session_id=sleep_session_dec.id,
                timestamp=_dt("2025-12-21T03:00:00Z"),
                sound_level=16.5,
                light_level=1.5,
            ),
            SleepSensorBatch(
                sleep_session_id=sleep_session_dec.id,
                timestamp=_dt("2025-12-21T06:30:00Z"),
                sound_level=19.0,
                light_level=8.0,
            ),
            SleepQualityReport(
                sleep_session_id=sleep_session_dec.id,
                duration_minutes=510,
                quality_label="excellent",
                duration_score=40,
                sound_score=30,
                light_score=21,
                avg_sound_level=16.5,
                avg_light_level=3.8,
                duration_issue=False,
                noise_issue=False,
                light_issue=False,
                recommendation=(
                    "Excellent sleep! Keep maintaining your current sleep schedule "
                    "and environment."
                ),
            ),
        ])

        # Sleep session 3 — 2026-05-28 (original, moved here to group all sleep sessions)
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

        trip_2 = Trip(
            device_id=visiondrive.id,
            start_time=_dt("2026-05-30T03:00:00Z"),
            end_time=_dt("2026-05-30T03:45:00Z"),
            status="completed",
            safety_score=94,
        )
        db.add(trip_2)
        db.flush()
        db.add(
            DistractionEvent(
                trip_id=trip_2.id,
                timestamp=_dt("2026-05-30T03:22:00Z"),
                event_type="drowsiness",
                severity="low",
            )
        )

        trip_3 = Trip(
            device_id=visiondrive.id,
            start_time=_dt("2026-05-31T04:00:00Z"),
            end_time=_dt("2026-05-31T04:35:00Z"),
            status="completed",
            safety_score=71,
        )
        db.add(trip_3)
        db.flush()
        db.add_all([
            DistractionEvent(
                trip_id=trip_3.id,
                timestamp=_dt("2026-05-31T04:12:00Z"),
                event_type="phone_use",
                severity="medium",
            ),
            DistractionEvent(
                trip_id=trip_3.id,
                timestamp=_dt("2026-05-31T04:28:00Z"),
                event_type="gaze_distraction",
                severity="high",
            ),
        ])

        db.commit()
        print("Seed data inserted.")
        print(f"SmartClock token: {SMARTCLOCK_TOKEN}")
        print(f"SmartClock 2 token: {SMARTCLOCK_2_TOKEN}")
        print(f"VisionDrive token: {VISIONDRIVE_TOKEN}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
