"""create funds_master table

Revision ID: 0fcd64e828eb
Revises: f05a19c2df60
Create Date: 2026-04-02 12:36:42.750091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0fcd64e828eb'
down_revision: Union[str, None] = 'f05a19c2df60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create funds_master table
    op.create_table(
        'funds_master',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scheme_code', sa.String(length=20), nullable=False),
        sa.Column('scheme_name', sa.String(length=255), nullable=False),
        sa.Column('fund_house', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_funds_master')),
        sa.UniqueConstraint('scheme_code', name=op.f('uq_funds_master_scheme_code'))
    )
    
    # Create indexes
    op.create_index(op.f('ix_funds_master_scheme_code'), 'funds_master', ['scheme_code'], unique=False)
    op.create_index(op.f('ix_funds_master_scheme_name'), 'funds_master', ['scheme_name'], unique=False)
    op.create_index(op.f('ix_funds_master_category'), 'funds_master', ['category'], unique=False)
    op.create_index(op.f('ix_funds_master_category_active'), 'funds_master', ['category', 'is_active'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_funds_master_category_active'), table_name='funds_master')
    op.drop_index(op.f('ix_funds_master_category'), table_name='funds_master')
    op.drop_index(op.f('ix_funds_master_scheme_name'), table_name='funds_master')
    op.drop_index(op.f('ix_funds_master_scheme_code'), table_name='funds_master')
    
    # Drop table
    op.drop_table('funds_master')
