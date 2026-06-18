"""add_sleep_quality_reports

Revision ID: bc260fe3aabc
Revises: cdb4590661ad
Create Date: 2026-05-29 16:17:04.265015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc260fe3aabc'
down_revision: Union[str, None] = 'cdb4590661ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sleep_quality_reports',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sleep_session_id', sa.Integer(), nullable=False),
        sa.Column('duration_minutes', sa.Float(), nullable=False),
        sa.Column(
            'quality_label',
            sa.Enum('poor', 'fair', 'good', 'excellent', name='sleep_quality_label_enum'),
            nullable=False,
        ),
        sa.Column('duration_score', sa.Float(), nullable=True),
        sa.Column('sound_score', sa.Float(), nullable=True),
        sa.Column('light_score', sa.Float(), nullable=True),
        sa.Column('avg_sound_level', sa.Float(), nullable=True),
        sa.Column('avg_light_level', sa.Float(), nullable=True),
        sa.Column('duration_issue', sa.Boolean(), nullable=False),
        sa.Column('noise_issue', sa.Boolean(), nullable=False),
        sa.Column('light_issue', sa.Boolean(), nullable=False),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['sleep_session_id'], ['sleep_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sleep_session_id'),
    )
    op.create_index(
        op.f('ix_sleep_quality_reports_sleep_session_id'),
        'sleep_quality_reports',
        ['sleep_session_id'],
        unique=True,
    )
    op.create_index(
        'ix_sleep_quality_generated',
        'sleep_quality_reports',
        ['generated_at'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_sleep_quality_generated', table_name='sleep_quality_reports')
    op.drop_index(
        op.f('ix_sleep_quality_reports_sleep_session_id'),
        table_name='sleep_quality_reports',
    )
    op.drop_table('sleep_quality_reports')
