"""add_study_presentation_sessions

Revision ID: d1e2f3a4b5c6
Revises: bc260fe3aabc
Create Date: 2026-05-29 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, None] = 'bc260fe3aabc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tạo bảng study_sessions
    op.create_table(
        'study_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            'status',
            sa.Enum('completed', 'interrupted', name='study_status_enum'),
            nullable=False,
        ),
        sa.Column('focus_minutes', sa.Float(), nullable=False),
        sa.Column('break_minutes', sa.Float(), nullable=False),
        sa.Column('pomodoro_count', sa.Integer(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_study_device_start',
        'study_sessions',
        ['device_id', 'start_time'],
        unique=False,
    )

    # 2. Tạo bảng presentation_sessions
    op.create_table(
        'presentation_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'status',
            sa.Enum('pending', 'processing', 'completed', 'failed',
                    name='presentation_status_enum'),
            nullable=False,
            server_default='pending',
        ),
        sa.Column('presentation_score', sa.Float(), nullable=True),
        sa.Column('clarity_score', sa.Float(), nullable=True),
        sa.Column('speed_score', sa.Float(), nullable=True),
        sa.Column('noise_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('speech_rate', sa.Float(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_presentation_device_start',
        'presentation_sessions',
        ['device_id', 'start_time'],
        unique=False,
    )

    # Ghi chú: seminar_recordings KHÔNG bị xóa trong migration này
    # để tránh mất data production. Bảng cũ sẽ được deprecated.


def downgrade() -> None:
    op.drop_index('ix_presentation_device_start', table_name='presentation_sessions')
    op.drop_table('presentation_sessions')
    op.drop_index('ix_study_device_start', table_name='study_sessions')
    op.drop_table('study_sessions')
    # Xóa enum types trên PostgreSQL (SQLite không cần bước này)
    op.execute('DROP TYPE IF EXISTS presentation_status_enum')
    op.execute('DROP TYPE IF EXISTS study_status_enum')
