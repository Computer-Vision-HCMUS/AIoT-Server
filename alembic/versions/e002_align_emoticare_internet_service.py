"""align_emoticare_internet_service

Align the schema with docs/Spectification/EmotiCareAIoT/05_Internet Service.md:
device-scoped session idempotency, wider token hash storage, and DATE report
period boundaries.

Revision ID: e002_emoticare_internet
Revises: e001_emoticare
Create Date: 2026-06-29 00:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e002_emoticare_internet"
down_revision: Union[str, None] = "e001_emoticare"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "devices",
        "device_token_hash",
        existing_type=sa.String(length=64),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    op.execute(
        "ALTER TABLE emotion_sessions "
        "DROP CONSTRAINT IF EXISTS uq_emotion_sessions_client_id"
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'uq_emotion_device_client_session'
            ) THEN
                ALTER TABLE emotion_sessions
                ADD CONSTRAINT uq_emotion_device_client_session
                UNIQUE (device_id, client_session_id);
            END IF;
        END $$;
        """
    )

    op.alter_column(
        "tft_reports",
        "period_start",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Date(),
        existing_nullable=False,
        postgresql_using="period_start::date",
    )
    op.alter_column(
        "tft_reports",
        "period_end",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Date(),
        existing_nullable=False,
        postgresql_using="period_end::date",
    )


def downgrade() -> None:
    op.alter_column(
        "tft_reports",
        "period_end",
        existing_type=sa.Date(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="period_end::timestamp with time zone",
    )
    op.alter_column(
        "tft_reports",
        "period_start",
        existing_type=sa.Date(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="period_start::timestamp with time zone",
    )

    op.execute(
        "ALTER TABLE emotion_sessions "
        "DROP CONSTRAINT IF EXISTS uq_emotion_device_client_session"
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'uq_emotion_sessions_client_id'
            ) THEN
                ALTER TABLE emotion_sessions
                ADD CONSTRAINT uq_emotion_sessions_client_id
                UNIQUE (client_session_id);
            END IF;
        END $$;
        """
    )

    op.alter_column(
        "devices",
        "device_token_hash",
        existing_type=sa.String(length=255),
        type_=sa.String(length=64),
        existing_nullable=False,
    )
