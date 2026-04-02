"""add nav tracking columns to explore_holdings

Revision ID: 9230d7883b43
Revises: 0fcd64e828eb
Create Date: 2026-04-02 12:37:02.987838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9230d7883b43'
down_revision: Union[str, None] = '0fcd64e828eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add NAV tracking columns to explore_holdings
    op.add_column('explore_holdings', sa.Column('last_known_nav', sa.Float(), nullable=True))
    op.add_column('explore_holdings', sa.Column('nav_last_updated', postgresql.TIMESTAMP(), nullable=True))


def downgrade() -> None:
    # Remove NAV tracking columns
    op.drop_column('explore_holdings', 'nav_last_updated')
    op.drop_column('explore_holdings', 'last_known_nav')
