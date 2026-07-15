"""
EmotiCare AIoT — Seed script.

Creates demo data for local development and API testing:
  - 1 demo user  (pairing_code = DEMO-001)
  - 1 demo device (token printed to console after seeding)
  - 20 media items (10 songs + 10 podcasts, 20-second MP3 metadata)

Usage:
    python -m app.seed
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from app.config import settings
from app.database import SessionLocal
from app.models.emoticare import Device, MediaItem, User


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"
DEMO_PAIRING_CODE = "DEMO-001"


def _media_url(path: str) -> str:
    if settings.SUPABASE_URL:
        base_url = settings.SUPABASE_URL.rstrip("/")
        bucket = settings.SUPABASE_MEDIA_BUCKET
        return f"{base_url}/storage/v1/object/public/{bucket}/{path}"
    return f"supabase://{settings.SUPABASE_MEDIA_BUCKET}/{path}"


MEDIA_SEED: list[dict] = [
    {"media_type": "song", "category": "relax", "title": "Calm Morning Pad", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/01-calm-morning-pad.mp3")},
    {"media_type": "song", "category": "relax", "title": "Soft Rain Keys", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/02-soft-rain-keys.mp3")},
    {"media_type": "song", "category": "focus", "title": "Low Focus Pulse", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/03-low-focus-pulse.mp3")},
    {"media_type": "song", "category": "focus", "title": "Clean Study Loop", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/04-clean-study-loop.mp3")},
    {"media_type": "song", "category": "sleep", "title": "Night Breath Drone", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/05-night-breath-drone.mp3")},
    {"media_type": "song", "category": "happy", "title": "Light Steps", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/06-light-steps.mp3")},
    {"media_type": "song", "category": "happy", "title": "Warm Smile Beat", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/07-warm-smile-beat.mp3")},
    {"media_type": "song", "category": "sad_support", "title": "Gentle Hold", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/08-gentle-hold.mp3")},
    {"media_type": "song", "category": "anger_release", "title": "Grounding Low Tone", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/09-grounding-low-tone.mp3")},
    {"media_type": "song", "category": "energy_recover", "title": "Small Energy Rise", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("music/10-small-energy-rise.mp3")},
    {"media_type": "podcast", "category": "relax", "title": "Bai tho 4-7-8", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/01-breathing-478.mp3")},
    {"media_type": "podcast", "category": "relax", "title": "Dung lai mot phut", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/02-one-minute-pause.mp3")},
    {"media_type": "podcast", "category": "focus", "title": "Bat dau tap trung", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/03-start-focus.mp3")},
    {"media_type": "podcast", "category": "sleep", "title": "Chuan bi nghi ngoi", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/04-prepare-rest.mp3")},
    {"media_type": "podcast", "category": "happy", "title": "Giu nang luong tot", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/05-keep-good-energy.mp3")},
    {"media_type": "podcast", "category": "sad_support", "title": "O canh noi buon", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/06-with-sadness.mp3")},
    {"media_type": "podcast", "category": "sad_support", "title": "Tu noi loi tu te", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/07-kind-self-talk.mp3")},
    {"media_type": "podcast", "category": "anger_release", "title": "Ha nhiet con gian", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/08-cool-down-anger.mp3")},
    {"media_type": "podcast", "category": "energy_recover", "title": "Nap lai nang luong", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/09-energy-recover.mp3")},
    {"media_type": "podcast", "category": "relax", "title": "Goi ten cam xuc", "creator": "EmotiCare Demo", "duration_sec": 20, "source_url": _media_url("podcast/10-name-the-feeling.mp3")},
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
