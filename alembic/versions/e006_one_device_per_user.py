"""enforce one device per user

Revision ID: e006_one_device_per_user
Revises: e005_remove_yearly_period
Create Date: 2026-07-30 00:00:00
"""

from typing import Sequence, Union

from alembic import op


revision: str = "e006_one_device_per_user"
down_revision: Union[str, None] = "e005_remove_yearly_period"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_devices_user", "devices", ["user_id"])


def downgrade() -> None:
    op.drop_constraint("uq_devices_user", "devices", type_="unique")
