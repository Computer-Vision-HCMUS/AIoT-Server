"""emoticare_initial_schema

Replaces the SmartDesk Buddy schema (SmartClock + VisionDrive) with the
EmotiCare AIoT Internet Service schema defined in
docs/Spectification/EmotiCareAIoT/05_Internet Service.md

Revision ID: e001_emoticare
Revises:
Create Date: 2026-06-26 00:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM, JSONB

revision: str = "e001_emoticare"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_enum(name: str, *values: str) -> None:
    """Create a PostgreSQL enum type if it does not already exist."""
    vals = ", ".join(f"'{v}'" for v in values)
    op.execute(
        f"DO $$ BEGIN "
        f"CREATE TYPE {name} AS ENUM ({vals}); "
        f"EXCEPTION WHEN duplicate_object THEN NULL; END $$"
    )


def upgrade() -> None:
    # ── Drop all legacy enums that may exist from previous migrations ──────────
    for legacy in [
        "device_type_enum", "pomodoro_type_enum", "sleep_status_enum",
        "sleep_quality_label_enum", "seminar_status_enum", "trip_status_enum",
        "distraction_type_enum", "distraction_severity_enum",
        "study_status_enum", "presentation_status_enum",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {legacy} CASCADE")

    # ── Create EmotiCare enums ─────────────────────────────────────────────────
    _create_enum("device_status_enum", "online", "offline", "disabled")
    _create_enum("quality_flag_enum", "clean", "noisy", "too_short", "low_confidence")
    _create_enum("reco_status_enum", "success", "failed", "limited")
    _create_enum("activity_type_enum", "breathing", "rest", "movement", "journaling")
    _create_enum("safety_flag_enum", "none", "low", "medium", "high")
    _create_enum("period_type_enum", "daily", "weekly", "monthly", "yearly")
    _create_enum("data_quality_enum", "enough_data", "limited_data")
    _create_enum("media_type_enum", "song", "podcast")
    _create_enum(
        "media_category_enum",
        "relax", "focus", "sleep", "happy",
        "sad_support", "anger_release", "energy_recover",
    )

    # ── Table: users ───────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("pairing_code", sa.String(20), nullable=True),
        sa.Column("consent_audio_storage", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("pairing_code", name="uq_users_pairing_code"),
    )

    # ── Table: devices ─────────────────────────────────────────────────────────
    op.create_table(
        "devices",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("device_token_hash", sa.String(255), nullable=False),
        sa.Column("firmware_version", sa.String(50), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            ENUM("online", "offline", "disabled",
                    name="device_status_enum", create_type=False),
            nullable=False,
            server_default="offline",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_devices_user_id", "devices", ["user_id"])

    # ── Table: media_items ─────────────────────────────────────────────────────
    op.create_table(
        "media_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "media_type",
            ENUM("song", "podcast", name="media_type_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("creator", sa.String(160), nullable=True),
        sa.Column(
            "category",
            ENUM(
                "relax", "focus", "sleep", "happy",
                "sad_support", "anger_release", "energy_recover",
                name="media_category_enum", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("duration_sec", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_index("ix_media_type_category", "media_items", ["media_type", "category"])

    # ── Table: emotion_sessions ────────────────────────────────────────────────
    op.create_table(
        "emotion_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("client_session_id", sa.String(80), nullable=False),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "device_id", sa.String(36),
            sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("emotion_label", sa.String(50), nullable=False),
        sa.Column("confidence_score", sa.Numeric(4, 3), nullable=False),
        sa.Column(
            "quality_flag",
            ENUM(
                "clean", "noisy", "too_short", "low_confidence",
                name="quality_flag_enum", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("inference_latency_ms", sa.Integer(), nullable=True),
        sa.Column("client_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "device_id",
            "client_session_id",
            name="uq_emotion_device_client_session",
        ),
    )
    op.create_index("ix_emotion_user_created", "emotion_sessions", ["user_id", "created_at"])
    op.create_index("ix_emotion_device_created", "emotion_sessions", ["device_id", "created_at"])

    # ── Table: recommendation_requests ────────────────────────────────────────
    op.create_table(
        "recommendation_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id", sa.String(36),
            sa.ForeignKey("emotion_sessions.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("request_payload", JSONB, nullable=False),
        sa.Column("response_payload", JSONB, nullable=False),
        sa.Column(
            "status",
            ENUM("success", "failed", "limited",
                    name="reco_status_enum", create_type=False),
            nullable=False,
            server_default="success",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reco_session_id", "recommendation_requests", ["session_id"])

    # ── Table: activity_feedback ───────────────────────────────────────────────
    op.create_table(
        "activity_feedback",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "recommendation_id", sa.String(36),
            sa.ForeignKey("recommendation_requests.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "activity_type",
            ENUM("breathing", "rest", "movement", "journaling",
                    name="activity_type_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("feedback_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_activity_feedback_reco_id", "activity_feedback", ["recommendation_id"])

    # ── Table: conversation_requests ───────────────────────────────────────────
    op.create_table(
        "conversation_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id", sa.String(36),
            sa.ForeignKey("emotion_sessions.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("user_message_summary", sa.Text(), nullable=True),
        sa.Column("response_text", sa.String(500), nullable=False),
        sa.Column(
            "safety_flag",
            ENUM("none", "low", "medium", "high",
                    name="safety_flag_enum", create_type=False),
            nullable=False,
            server_default="none",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_conversation_session_id", "conversation_requests", ["session_id"])

    # ── Table: tft_reports ─────────────────────────────────────────────────────
    op.create_table(
        "tft_reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "period_type",
            ENUM("daily", "weekly", "monthly", "yearly",
                    name="period_type_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("tft_cards", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("emotion_distribution", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("trend_summary", sa.String(500), nullable=True),
        sa.Column(
            "data_quality",
            ENUM("enough_data", "limited_data",
                    name="data_quality_enum", create_type=False),
            nullable=False,
            server_default="limited_data",
        ),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_tft_report_user_period", "tft_reports",
        ["user_id", "period_type", "period_start"],
    )

    # ── Table: media_selection_logs ────────────────────────────────────────────
    op.create_table(
        "media_selection_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id", sa.String(36),
            sa.ForeignKey("emotion_sessions.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "media_item_id", sa.String(36),
            sa.ForeignKey("media_items.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("user_intent", sa.String(120), nullable=True),
        sa.Column("selected_category", sa.String(50), nullable=False),
        sa.Column("feedback_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_media_log_session", "media_selection_logs", ["session_id", "created_at"])


def downgrade() -> None:
    op.drop_table("media_selection_logs")
    op.drop_table("tft_reports")
    op.drop_table("conversation_requests")
    op.drop_table("activity_feedback")
    op.drop_table("recommendation_requests")
    op.drop_table("emotion_sessions")
    op.drop_table("media_items")
    op.drop_table("devices")
    op.drop_table("users")
    for enum_name in [
        "media_category_enum", "media_type_enum", "data_quality_enum",
        "period_type_enum", "safety_flag_enum", "activity_type_enum",
        "reco_status_enum", "quality_flag_enum", "device_status_enum",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
