"""add suggestion_feedback_logs table

Revision ID: c4f8d2a7e1b4
Revises: b30149459cec
Create Date: 2026-04-27 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c4f8d2a7e1b4'
down_revision: Union[str, Sequence[str], None] = 'b30149459cec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add normalized suggestion feedback tracking."""
    feedback_type_enum = postgresql.ENUM(
        'ACCEPT', 'REJECT', 'IGNORE',
        name='suggestionfeedbacktype',
        create_type=True,
    )
    feedback_type_enum.create(op.get_bind(), checkfirst=True)
    feedback_type_column = postgresql.ENUM(
        'ACCEPT', 'REJECT', 'IGNORE',
        name='suggestionfeedbacktype',
        create_type=False,
    )

    op.create_table(
        'suggestion_feedback_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('suggestion_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('feedback_type', feedback_type_column, nullable=False),
        sa.Column('feedback_reason', sa.Text(), nullable=True),
        sa.Column('feedback_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['suggestion_id'], ['suggestion_logs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('suggestion_id', name='uq_suggestion_feedback_suggestion_id'),
    )
    op.create_index(op.f('ix_suggestion_feedback_logs_id'), 'suggestion_feedback_logs', ['id'], unique=False)


def downgrade() -> None:
    """Remove normalized suggestion feedback tracking."""
    op.drop_index(op.f('ix_suggestion_feedback_logs_id'), table_name='suggestion_feedback_logs')
    op.drop_table('suggestion_feedback_logs')

    feedback_type_enum = postgresql.ENUM('ACCEPT', 'REJECT', 'IGNORE', name='suggestionfeedbacktype')
    feedback_type_enum.drop(op.get_bind(), checkfirst=True)
