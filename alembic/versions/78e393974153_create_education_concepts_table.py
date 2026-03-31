"""create_education_concepts_table

Revision ID: 78e393974153
Revises: 3f8b9d2c5e1a
Create Date: 2026-03-30 18:59:33.372524

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '78e393974153'
down_revision: Union[str, None] = '9c2d4f1b7a11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = inspector.get_table_names()

    if 'concepts' not in table_names:
        op.create_table(
            'concepts',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('title', sa.String(length=120), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('category', sa.String(length=80), nullable=True),
            sa.Column('read_time_minutes', sa.Integer(), nullable=True),
            sa.Column('order_index', sa.Integer(), nullable=True),
            sa.Column('explanation', sa.Text(), nullable=True),
            sa.Column('number_example', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_concepts_id'), 'concepts', ['id'], unique=False)

        concepts_table = sa.table(
            'concepts',
            sa.column('id', postgresql.UUID(as_uuid=True)),
            sa.column('title', sa.String(length=120)),
            sa.column('description', sa.Text()),
            sa.column('category', sa.String(length=80)),
            sa.column('read_time_minutes', sa.Integer()),
            sa.column('order_index', sa.Integer()),
            sa.column('explanation', sa.Text()),
            sa.column('number_example', sa.Text()),
        )

        seed_rows = [
            {
                'id': uuid.uuid4(),
                'title': 'Systematic Investment Plan (SIP)',
                'description': 'A fixed amount invested every month to build wealth over time.',
                'category': 'Basics',
                'read_time_minutes': 4,
                'order_index': 1,
                'explanation': 'SIP automates disciplined investing and averages your purchase price across market cycles.',
                'number_example': '₹10,000 monthly for 10 years at 12% can grow to roughly ₹23 lakh.',
            },
            {
                'id': uuid.uuid4(),
                'title': 'Compounding',
                'description': 'Returns generating additional returns over long periods.',
                'category': 'Basics',
                'read_time_minutes': 5,
                'order_index': 2,
                'explanation': 'Compounding accelerates growth because each period builds on principal plus prior gains.',
                'number_example': '₹1,00,000 at 12% for 15 years can become about ₹5,47,000.',
            },
            {
                'id': uuid.uuid4(),
                'title': 'Mutual Funds',
                'description': 'Professionally managed pooled investment vehicles.',
                'category': 'Products',
                'read_time_minutes': 5,
                'order_index': 3,
                'explanation': 'Investors pool money into a fund that buys diversified securities managed by professionals.',
                'number_example': '₹5,000 SIP into an equity fund for 12 years at 11% can reach roughly ₹13 lakh.',
            },
            {
                'id': uuid.uuid4(),
                'title': 'NAV (Net Asset Value)',
                'description': 'Per-unit value of a mutual fund at day end.',
                'category': 'Products',
                'read_time_minutes': 3,
                'order_index': 4,
                'explanation': 'NAV is fund value per unit; your gains depend on NAV growth and units held.',
                'number_example': 'If NAV rises from ₹50 to ₹60, 1,000 units grow from ₹50,000 to ₹60,000.',
            },
            {
                'id': uuid.uuid4(),
                'title': 'Expense Ratio',
                'description': 'Annual fee charged by funds for management and operations.',
                'category': 'Products',
                'read_time_minutes': 3,
                'order_index': 5,
                'explanation': 'Lower costs leave more return for investors, especially over long horizons.',
                'number_example': 'On ₹10,00,000, 2% fee is ₹20,000/year vs 0.5% fee of ₹5,000/year.',
            },
            {
                'id': uuid.uuid4(),
                'title': 'Risk and Return',
                'description': 'Higher expected return usually comes with higher volatility.',
                'category': 'Planning',
                'read_time_minutes': 4,
                'order_index': 6,
                'explanation': 'Equity can deliver stronger growth but with larger short-term swings than debt assets.',
                'number_example': 'Debt target 7% vs equity target 12%, but equity may see 20% drawdowns in bad years.',
            },
            {
                'id': uuid.uuid4(),
                'title': 'Inflation',
                'description': 'The rate at which the cost of living rises over time.',
                'category': 'Planning',
                'read_time_minutes': 4,
                'order_index': 7,
                'explanation': 'Future goals must account for inflation so your corpus has real purchasing power.',
                'number_example': '₹10,00,000 today at 6% inflation needs about ₹17,90,000 in 10 years.',
            },
            {
                'id': uuid.uuid4(),
                'title': 'Diversification',
                'description': 'Spreading investments to avoid dependence on one asset.',
                'category': 'Planning',
                'read_time_minutes': 4,
                'order_index': 8,
                'explanation': 'Holding multiple assets can reduce concentrated downside risk from one segment.',
                'number_example': 'A 60/30/10 mix (equity/debt/gold) often falls less than 100% equity in corrections.',
            },
            {
                'id': uuid.uuid4(),
                'title': 'Asset Allocation',
                'description': 'Choosing how much to allocate across asset classes.',
                'category': 'Planning',
                'read_time_minutes': 5,
                'order_index': 9,
                'explanation': 'Allocation should match timeline, risk profile, and return requirement for each goal.',
                'number_example': 'Long-term growth investor may choose 75% equity and 25% debt.',
            },
            {
                'id': uuid.uuid4(),
                'title': 'Rebalancing',
                'description': 'Restoring target allocation periodically after market movement.',
                'category': 'Planning',
                'read_time_minutes': 4,
                'order_index': 10,
                'explanation': 'Rebalancing keeps risk in control by trimming overweight assets and adding underweight ones.',
                'number_example': 'If target is 70/30 and it drifts to 78/22, shift funds to return to 70/30.',
            },
        ]

        op.bulk_insert(concepts_table, seed_rows)
    else:
        existing_columns = {col['name'] for col in inspector.get_columns('concepts')}
        if 'explanation' not in existing_columns:
            op.add_column('concepts', sa.Column('explanation', sa.Text(), nullable=True))
        if 'number_example' not in existing_columns:
            op.add_column('concepts', sa.Column('number_example', sa.Text(), nullable=True))
        if 'created_at' not in existing_columns:
            op.add_column('concepts', sa.Column('created_at', sa.DateTime(), nullable=True))

        op.execute("UPDATE concepts SET explanation = description WHERE explanation IS NULL")

        example_updates = {
            'Systematic Investment Plan (SIP)': '₹10,000 monthly for 10 years at 12% can grow to roughly ₹23 lakh.',
            'Compounding': '₹1,00,000 at 12% for 15 years can become about ₹5,47,000.',
            'Mutual Funds': '₹5,000 SIP into an equity fund for 12 years at 11% can reach roughly ₹13 lakh.',
            'NAV (Net Asset Value)': 'If NAV rises from ₹50 to ₹60, 1,000 units grow from ₹50,000 to ₹60,000.',
            'Expense Ratio': 'On ₹10,00,000, 2% fee is ₹20,000/year vs 0.5% fee of ₹5,000/year.',
            'Risk and Return': 'Debt target 7% vs equity target 12%, but equity may see 20% drawdowns in bad years.',
            'Inflation': '₹10,00,000 today at 6% inflation needs about ₹17,90,000 in 10 years.',
            'Diversification': 'A 60/30/10 mix (equity/debt/gold) often falls less than 100% equity in corrections.',
            'Asset Allocation': 'Long-term growth investor may choose 75% equity and 25% debt.',
            'Rebalancing': 'If target is 70/30 and it drifts to 78/22, shift funds to return to 70/30.',
        }

        for title, number_example in example_updates.items():
            op.execute(
                sa.text(
                    """
                    UPDATE concepts
                    SET number_example = :number_example
                    WHERE title = :title
                      AND (number_example IS NULL OR number_example = '')
                    """
                ).bindparams(title=title, number_example=number_example)
            )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if 'concepts' in inspector.get_table_names():
        existing_columns = {col['name'] for col in inspector.get_columns('concepts')}
        if 'number_example' in existing_columns:
            op.drop_column('concepts', 'number_example')
        if 'explanation' in existing_columns:
            op.drop_column('concepts', 'explanation')
        if 'created_at' in existing_columns:
            op.drop_column('concepts', 'created_at')
