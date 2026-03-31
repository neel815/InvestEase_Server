"""create_recommendations_and_selected_basket

Revision ID: c4d84bdac912
Revises: b1f6f07d2a4c
Create Date: 2026-03-31 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4d84bdac912"
down_revision: Union[str, None] = "b1f6f07d2a4c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("goals", sa.Column("selected_basket", sa.String(length=20), nullable=True))

    op.create_table(
        "recommendations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("goal_id", sa.UUID(), nullable=False),
        sa.Column("scheme_code", sa.String(length=40), nullable=False),
        sa.Column("scheme_name", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("basket_type", sa.String(length=20), nullable=False),
        sa.Column("returns_1y", sa.Float(), nullable=False),
        sa.Column("returns_3y", sa.Float(), nullable=False),
        sa.Column("returns_5y", sa.Float(), nullable=False),
        sa.Column("recommended_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recommendations_user_id"), "recommendations", ["user_id"], unique=False)
    op.create_index(op.f("ix_recommendations_goal_id"), "recommendations", ["goal_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_recommendations_goal_id"), table_name="recommendations")
    op.drop_index(op.f("ix_recommendations_user_id"), table_name="recommendations")
    op.drop_table("recommendations")
    op.drop_column("goals", "selected_basket")
