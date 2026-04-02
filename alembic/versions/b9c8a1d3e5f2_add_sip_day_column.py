"""add_sip_day_column

Revision ID: b9c8a1d3e5f2
Revises: a8f1c9b7d2e3
Create Date: 2026-04-01 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9c8a1d3e5f2'
down_revision: Union[str, None] = 'a8f1c9b7d2e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add sip_day column to sip_schedules table
    op.add_column('sip_schedules', sa.Column('sip_day', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    # Remove sip_day column
    op.drop_column('sip_schedules', 'sip_day')
