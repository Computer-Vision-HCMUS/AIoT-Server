"""remove_global_client_session_unique

Remove the legacy global unique constraint on emotion_sessions.client_session_id.
Idempotency must be scoped by (device_id, client_session_id), because different
Edge devices may generate the same local client_session_id.

Revision ID: e003_drop_global_client_unique
Revises: e002_emoticare_internet
Create Date: 2026-06-30 00:00:00
"""

from typing import Sequence, Union

from alembic import op

revision: str = "e003_drop_global_client_unique"
down_revision: Union[str, None] = "e002_emoticare_internet"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE emotion_sessions "
        "DROP CONSTRAINT IF EXISTS emotion_sessions_client_session_id_key"
    )
    op.execute(
        "ALTER TABLE emotion_sessions "
        "DROP CONSTRAINT IF EXISTS uq_emotion_sessions_client_id"
    )


def downgrade() -> None:
    op.create_unique_constraint(
        "emotion_sessions_client_session_id_key",
        "emotion_sessions",
        ["client_session_id"],
    )
