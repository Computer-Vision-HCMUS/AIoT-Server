"""Seed deterministic, presentation-ready emotion sessions for August 2026.

The seed is safe to re-run: it replaces only sessions whose client ID starts
with ``demo-stat-2026-08-``.  It requires the normal demo user and device
created by ``python -m app.seed``.

Usage:
    python -m scripts.seed_demo_emotion_statistics
"""

from collections import Counter
from datetime import datetime, timedelta, timezone
import uuid

from app.database import SessionLocal
from app.models.emoticare import Device, EmotionSession, User
from app.seed import DEMO_USER_ID


SEED_PREFIX = "demo-stat-2026-08-"

# A healthy-looking month: calm/neutral dominate, happy grows through the
# current week, and a small number of stressful check-ins make the trend useful.
DAILY_EMOTIONS: dict[int, list[str]] = {
    1: ["neutral", "calm", "happy"],
    2: ["neutral", "happy", "calm", "stressed"],
    3: ["calm", "neutral", "happy"],
    4: ["neutral", "tired", "calm", "happy"],
    5: ["happy", "neutral", "calm"],
    6: ["neutral", "stressed", "calm", "happy"],
    7: ["happy", "calm", "neutral"],
    8: ["neutral", "tired", "happy", "calm"],
    9: ["calm", "happy", "neutral"],
    # Current week: a gentle recovery pattern for a meaningful trend card.
    10: ["stressed", "neutral", "tired", "calm"],
    11: ["neutral", "stressed", "calm", "happy"],
    12: ["calm", "neutral", "happy", "happy"],
    13: ["happy", "calm", "neutral", "happy"],
    14: ["happy", "calm", "happy", "neutral", "surprised"],
}

HOURS = (8, 11, 14, 18, 21)


def _confidence(emotion: str, index: int) -> float:
    base = 0.93 if emotion in {"happy", "calm", "neutral"} else 0.88
    return round(base - (index % 3) * 0.015, 3)


def seed() -> None:
    db = SessionLocal()
    try:
        user = db.get(User, DEMO_USER_ID)
        if user is None:
            raise RuntimeError(
                f"Demo user {DEMO_USER_ID} does not exist. Run `python -m app.seed` first."
            )
        device = db.query(Device).filter(Device.user_id == DEMO_USER_ID).first()
        if device is None:
            raise RuntimeError("Demo device does not exist. Run `python -m app.seed` first.")

        replaced = (
            db.query(EmotionSession)
            .filter(
                EmotionSession.device_id == device.id,
                EmotionSession.client_session_id.like(f"{SEED_PREFIX}%"),
            )
            .delete(synchronize_session=False)
        )

        sessions: list[EmotionSession] = []
        for day, emotions in DAILY_EMOTIONS.items():
            for index, emotion in enumerate(emotions):
                created_at = datetime(2026, 8, day, HOURS[index], 0, tzinfo=timezone.utc)
                sessions.append(
                    EmotionSession(
                        id=str(uuid.uuid4()),
                        client_session_id=f"{SEED_PREFIX}{day:02d}-{index + 1}",
                        user_id=DEMO_USER_ID,
                        device_id=device.id,
                        emotion_label=emotion,
                        confidence_score=_confidence(emotion, index),
                        quality_flag="clean",
                        inference_latency_ms=360 + index * 35,
                        client_created_at=created_at - timedelta(seconds=2),
                        created_at=created_at,
                    )
                )

        db.add_all(sessions)
        db.commit()
        distribution = Counter(session.emotion_label for session in sessions)
        print(f"[demo-stat-seed] Replaced {replaced} old demo session(s).")
        print(f"[demo-stat-seed] Inserted {len(sessions)} session(s) for August 2026.")
        print("[demo-stat-seed] Distribution: " + ", ".join(
            f"{label}={count}" for label, count in sorted(distribution.items())
        ))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
