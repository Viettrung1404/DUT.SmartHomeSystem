"""add suggestion_decision_logs table

Revision ID: f1a2b3c4d5e6
Revises: c4f8d2a7e1b4
Create Date: 2026-05-09 10:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = ('c4f8d2a7e1b4', '8f3e9d0c2a1b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add audit logs for every suggestion decision candidate."""
    op.create_table(
        'suggestion_decision_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pattern_id', sa.Integer(), nullable=False),
        sa.Column('home_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('decision_score', sa.Float(), nullable=False),
        sa.Column('should_suggest', sa.Boolean(), nullable=False),
        sa.Column('blocked_by', sa.String(length=50), nullable=True),
        sa.Column('cooldown_signature', sa.String(length=255), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['home_id'], ['homes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pattern_id'], ['user_patterns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suggestion_decision_logs_id'), 'suggestion_decision_logs', ['id'], unique=False)
    op.create_index(op.f('ix_suggestion_decision_logs_home_id'), 'suggestion_decision_logs', ['home_id'], unique=False)
    op.create_index(op.f('ix_suggestion_decision_logs_user_id'), 'suggestion_decision_logs', ['user_id'], unique=False)


def downgrade() -> None:
    """Remove decision audit logs."""
    op.drop_index(op.f('ix_suggestion_decision_logs_user_id'), table_name='suggestion_decision_logs')
    op.drop_index(op.f('ix_suggestion_decision_logs_home_id'), table_name='suggestion_decision_logs')
    op.drop_index(op.f('ix_suggestion_decision_logs_id'), table_name='suggestion_decision_logs')
    op.drop_table('suggestion_decision_logs')
