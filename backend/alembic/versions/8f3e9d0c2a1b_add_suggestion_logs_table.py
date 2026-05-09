"""add suggestion_logs table

Revision ID: 8f3e9d0c2a1b
Revises: b30149459cec
Create Date: 2026-03-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '8f3e9d0c2a1b'
down_revision: Union[str, Sequence[str], None] = 'b30149459cec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create suggestion_logs table."""
    bind = op.get_bind()
    if inspect(bind).has_table('suggestion_logs'):
        return

    # Tạo ENUM cho ActionType nếu chưa có
    action_type_enum = postgresql.ENUM('SCHEDULE', 'ALERT', 'AUTOMATION', name='actiontype', create_type=True)
    action_type_enum.create(bind, checkfirst=True)
    action_type_column = postgresql.ENUM('SCHEDULE', 'ALERT', 'AUTOMATION', name='actiontype', create_type=False)

    op.create_table('suggestion_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('pattern_id', sa.Integer(), nullable=True),
        sa.Column('action_type', action_type_column, nullable=False),
        sa.Column('suggestion_text', sa.Text(), nullable=False),
        sa.Column('suggestion_json', postgresql.JSONB(), nullable=True),
        sa.Column('was_accepted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['pattern_id'], ['user_patterns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suggestion_logs_id'), 'suggestion_logs', ['id'], unique=False)


def downgrade() -> None:
    """Drop suggestion_logs table."""
    op.drop_index(op.f('ix_suggestion_logs_id'), table_name='suggestion_logs')
    op.drop_table('suggestion_logs')
    # Drop ENUM nếu không còn dùng
    enum = postgresql.ENUM('SCHEDULE', 'ALERT', 'AUTOMATION', name='actiontype')
    enum.drop(op.get_bind(), checkfirst=True)
