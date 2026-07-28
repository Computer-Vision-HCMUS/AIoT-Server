"""expand activity types for diverse action recommendations

Revision ID: e004_expand_activity_types
Revises: e003_drop_global_client_unique
Create Date: 2026-07-29 00:00:00
"""

from typing import Sequence, Union

from alembic import op


revision: str = "e004_expand_activity_types"
down_revision: Union[str, None] = "e003_drop_global_client_unique"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for activity_type in (
        "rest_water",
        "grounding",
        "body_scan",
        "task_reset",
        "gratitude",
        "reach_out",
    ):
        op.execute(f"ALTER TYPE activity_type_enum ADD VALUE IF NOT EXISTS '{activity_type}'")


def downgrade() -> None:
    # PostgreSQL cannot remove enum values in place without replacing the type.
    # Keeping values is safe for existing feedback records.
    pass
