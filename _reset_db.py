"""
Reset database for EmotiCare AIoT — DEVELOPMENT USE ONLY.

Strategy: drop everything, then use Base.metadata.create_all() to create
tables directly from ORM models (bypassing Alembic enum conflicts), then
stamp alembic_version to current head so future migrations work correctly.
"""

from sqlalchemy import create_engine, text
from app.config import settings
from app.database import Base
import app.models  # noqa: registers all models

engine = create_engine(settings.DATABASE_URL)

OLD_TABLES = [
    "media_selection_logs", "tft_reports", "conversation_requests",
    "activity_feedback", "recommendation_requests", "emotion_sessions",
    "media_items", "sleep_quality_reports", "sleep_sensor_batches",
    "distraction_events", "presentation_sessions", "study_sessions",
    "pomodoro_sessions", "game_scores", "sleep_sessions", "seminar_recordings",
    "trips", "sleep_configs", "timer_configs", "devices", "users",
    "alembic_version",
]

OLD_ENUMS = [
    "device_type_enum", "pomodoro_type_enum", "sleep_status_enum",
    "sleep_quality_label_enum", "seminar_status_enum", "trip_status_enum",
    "distraction_type_enum", "distraction_severity_enum", "study_status_enum",
    "presentation_status_enum", "device_status_enum", "quality_flag_enum",
    "reco_status_enum", "activity_type_enum", "safety_flag_enum",
    "period_type_enum", "data_quality_enum", "media_type_enum", "media_category_enum",
]

print("=== Dropping all tables and enums ===")
with engine.begin() as conn:
    for table in OLD_TABLES:
        conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        print(f"  Dropped table: {table}")
    for enum in OLD_ENUMS:
        conn.execute(text(f"DROP TYPE IF EXISTS {enum} CASCADE"))
        print(f"  Dropped enum: {enum}")

print("\n=== Creating tables from ORM models (Base.metadata.create_all) ===")
Base.metadata.create_all(engine, checkfirst=True)
print("  Tables created successfully.")

print("\n=== Stamping alembic_version to current head ===")
with engine.begin() as conn:
    conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"))
    conn.execute(text("DELETE FROM alembic_version"))
    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('e001_emoticare')"))
print("  Stamped: e001_emoticare")

print("\n=== DB reset complete! ===")
print("Run: python -m app.seed  to populate demo data.")
