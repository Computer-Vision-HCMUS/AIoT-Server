"""remove yearly report period

Revision ID: e005_remove_yearly_period
Revises: e004_expand_activity_types
Create Date: 2026-07-29 00:00:00
"""

from typing import Sequence, Union

from alembic import op


revision: str = "e005_remove_yearly_period"
down_revision: Union[str, None] = "e004_expand_activity_types"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL does not support removing an enum value in place.  The column
    # is temporarily text so the enum can be recreated without ``yearly``.
    op.execute("ALTER TABLE tft_reports ALTER COLUMN period_type TYPE text USING period_type::text")
    op.execute("DROP TYPE period_type_enum")
    op.execute("CREATE TYPE period_type_enum AS ENUM ('daily', 'weekly', 'monthly')")
    op.execute(
        "ALTER TABLE tft_reports ALTER COLUMN period_type "
        "TYPE period_type_enum USING period_type::period_type_enum"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE tft_reports ALTER COLUMN period_type TYPE text USING period_type::text")
    op.execute("DROP TYPE period_type_enum")
    op.execute(
        "CREATE TYPE period_type_enum AS ENUM ('daily', 'weekly', 'monthly', 'yearly')"
    )
    op.execute(
        "ALTER TABLE tft_reports ALTER COLUMN period_type "
        "TYPE period_type_enum USING period_type::period_type_enum"
    )
