"""change_goal_target_amount_to_numeric

Revision ID: b1f6f07d2a4c
Revises: 78e393974153
Create Date: 2026-03-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1f6f07d2a4c"
down_revision: Union[str, None] = "78e393974153"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "goals",
        "target_amount",
        existing_type=sa.Float(),
        type_=sa.Numeric(14, 2),
        postgresql_using="target_amount::numeric(14,2)",
    )


def downgrade() -> None:
    op.alter_column(
        "goals",
        "target_amount",
        existing_type=sa.Numeric(14, 2),
        type_=sa.Float(),
        postgresql_using="target_amount::double precision",
    )
