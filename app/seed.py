"""
EmotiCare AIoT — Seed script.

Creates demo data for local development and API testing:
  - 1 demo user  (pairing_code = DEMO-001)
  - 1 demo device (token printed to console after seeding)
  - 21 media items (3 per category × 7 categories, mix of song and podcast)

Usage:
    python -m app.seed
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.emoticare import Device, MediaItem, User


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"
DEMO_PAIRING_CODE = "DEMO-001"

MEDIA_SEED: list[dict] = [
    # relax
    {"media_type": "song",    "category": "relax",         "title": "Weightless",              "creator": "Marconi Union",          "duration_sec": 480},
    {"media_type": "song",    "category": "relax",         "title": "Clair de Lune",            "creator": "Claude Debussy",         "duration_sec": 320},
    {"media_type": "podcast", "category": "relax",         "title": "Bài thở 4-7-8",           "creator": "MindfulVN",              "duration_sec": 300},
    # focus
    {"media_type": "song",    "category": "focus",         "title": "Experience",               "creator": "Ludovico Einaudi",       "duration_sec": 360},
    {"media_type": "song",    "category": "focus",         "title": "Rain Sounds",              "creator": "Nature Sounds",          "duration_sec": 3600},
    {"media_type": "podcast", "category": "focus",         "title": "Deep Work Tips",           "creator": "Cal Newport Podcast",    "duration_sec": 900},
    # sleep
    {"media_type": "song",    "category": "sleep",         "title": "Gymnopédie No.1",         "creator": "Erik Satie",             "duration_sec": 195},
    {"media_type": "song",    "category": "sleep",         "title": "Sleep Drone",              "creator": "Ambient Works",          "duration_sec": 7200},
    {"media_type": "podcast", "category": "sleep",         "title": "Câu chuyện ngủ ngon",     "creator": "Ngủ Đi Em",              "duration_sec": 1200},
    # happy
    {"media_type": "song",    "category": "happy",         "title": "Happy",                   "creator": "Pharrell Williams",      "duration_sec": 233},
    {"media_type": "song",    "category": "happy",         "title": "Vui Lên Nào",             "creator": "AMEE",                   "duration_sec": 210},
    {"media_type": "podcast", "category": "happy",         "title": "Câu chuyện truyền cảm hứng", "creator": "Vietcetera",          "duration_sec": 1800},
    # sad_support
    {"media_type": "song",    "category": "sad_support",   "title": "The Night We Met",        "creator": "Lord Huron",             "duration_sec": 218},
    {"media_type": "song",    "category": "sad_support",   "title": "Tự Tình",                 "creator": "Hoàng Duyên",            "duration_sec": 240},
    {"media_type": "podcast", "category": "sad_support",   "title": "Khi Buồn Thì Sao",       "creator": "Tâm Tình VN",            "duration_sec": 1500},
    # anger_release
    {"media_type": "song",    "category": "anger_release", "title": "Breathe (2 AM)",          "creator": "Anna Nalick",            "duration_sec": 279},
    {"media_type": "song",    "category": "anger_release", "title": "Grounding Sounds",        "creator": "Healing Frequencies",    "duration_sec": 600},
    {"media_type": "podcast", "category": "anger_release", "title": "Kiểm soát cơn giận",     "creator": "PsychologyVN",           "duration_sec": 720},
    # energy_recover
    {"media_type": "song",    "category": "energy_recover","title": "Rise Up",                 "creator": "Andra Day",              "duration_sec": 275},
    {"media_type": "song",    "category": "energy_recover","title": "Sóng Gió",                "creator": "Jack & K-ICM",           "duration_sec": 220},
    {"media_type": "podcast", "category": "energy_recover","title": "Self-care Buổi Sáng",    "creator": "WellnessVN",             "duration_sec": 600},
]


def seed():
    db = SessionLocal()
    try:
        # ── User ──────────────────────────────────────────────────────────────
        existing_user = db.query(User).filter(User.id == DEMO_USER_ID).first()
        if existing_user:
            print(f"[seed] User already exists: id={DEMO_USER_ID}")
            user = existing_user
        else:
            user = User(
                id=DEMO_USER_ID,
                name="Demo User",
                pairing_code=DEMO_PAIRING_CODE,
                consent_audio_storage=False,
                created_at=_utcnow(),
                updated_at=_utcnow(),
            )
            db.add(user)
            db.commit()
            print(f"[seed] Created user: id={DEMO_USER_ID} pairing_code={DEMO_PAIRING_CODE}")

        # ── Device ────────────────────────────────────────────────────────────
        # Check if a device already exists for this user (seeded device)
        existing_device = (
            db.query(Device).filter(Device.user_id == DEMO_USER_ID).first()
        )
        if existing_device:
            print(f"[seed] Device already exists: id={existing_device.id}")
            print("[seed] Use /api/devices/pair with pairing_code=DEMO-001 to get a new token.")
        else:
            # Generate a fixed demo token for easy local testing
            demo_token = "demo-emoticare-device-token-local-dev"
            token_hash = hashlib.sha256(demo_token.encode()).hexdigest()
            device = Device(
                id=str(uuid.uuid4()),
                user_id=DEMO_USER_ID,
                name="Demo EmotiCare Device",
                device_token_hash=token_hash,
                firmware_version="1.0.0",
                status="offline",
                created_at=_utcnow(),
            )
            db.add(device)
            db.commit()
            print(f"[seed] Created device: id={device.id}")
            print(f"[seed] Demo device token (plain): {demo_token}")
            print("[seed] Use this in X-Device-Token header for testing.")

        # ── Media Items ───────────────────────────────────────────────────────
        created_count = 0
        for item_data in MEDIA_SEED:
            # Deduplicate by title + creator
            existing = (
                db.query(MediaItem)
                .filter(
                    MediaItem.title == item_data["title"],
                    MediaItem.creator == item_data["creator"],
                )
                .first()
            )
            if existing:
                continue
            media = MediaItem(
                id=str(uuid.uuid4()),
                **item_data,
                source_url=None,
                enabled=True,
            )
            db.add(media)
            created_count += 1

        db.commit()
        print(f"[seed] Created {created_count} media items ({len(MEDIA_SEED)} total in seed).")
        print("[seed] Done.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
