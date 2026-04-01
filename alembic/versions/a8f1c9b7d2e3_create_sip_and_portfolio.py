"""create_sip_and_portfolio

Revision ID: a8f1c9b7d2e3
Revises: d5e8f3a2b1c9
Create Date: 2026-04-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8f1c9b7d2e3'
down_revision: Union[str, None] = 'd5e8f3a2b1c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SIP schedules table
    op.create_table(
        'sip_schedules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('selected_basket', sa.String(), nullable=False),
        sa.Column('monthly_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('next_due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sip_schedules_user_id'), 'sip_schedules', ['user_id'], unique=False)
    op.create_index(op.f('ix_sip_schedules_goal_id'), 'sip_schedules', ['goal_id'], unique=False)

    # Portfolio summary table
    op.create_table(
        'portfolio_summary',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('total_invested', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('current_value', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolio_summary_user_id'), 'portfolio_summary', ['user_id'], unique=False)
    op.create_index(op.f('ix_portfolio_summary_goal_id'), 'portfolio_summary', ['goal_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_portfolio_summary_goal_id'), table_name='portfolio_summary')
    op.drop_index(op.f('ix_portfolio_summary_user_id'), table_name='portfolio_summary')
    op.drop_table('portfolio_summary')

    op.drop_index(op.f('ix_sip_schedules_goal_id'), table_name='sip_schedules')
    op.drop_index(op.f('ix_sip_schedules_user_id'), table_name='sip_schedules')
    op.drop_table('sip_schedules')
