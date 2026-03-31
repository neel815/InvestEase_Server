"""concepts_baseline_compatibility

Revision ID: 9c2d4f1b7a11
Revises: 3f8b9d2c5e1a
Create Date: 2026-03-30 19:25:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '9c2d4f1b7a11'
down_revision: Union[str, None] = '3f8b9d2c5e1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Compatibility placeholder for existing databases already stamped at this revision.
    pass


def downgrade() -> None:
    pass
