"""Add nro_cliente column to cases

Revision ID: 20260112234500
Revises: 20260112233643
Create Date: 2026-01-12 23:45:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260112234500'
down_revision = '20260112233643'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add nro_cliente column to cases table
    op.add_column('cases', sa.Column('nro_cliente', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_cases_nro_cliente'), 'cases', ['nro_cliente'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_cases_nro_cliente'), table_name='cases')
    op.drop_column('cases', 'nro_cliente')

