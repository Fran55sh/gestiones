"""Add address and contact fields to cases

Revision ID: a390bb4da27e
Revises: 20260112234500
Create Date: 2026-01-13 03:06:23.594321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a390bb4da27e'
down_revision = '20260112234500'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar nuevas columnas a la tabla cases
    with op.batch_alter_table('cases', schema=None) as batch_op:
        # Datos de contacto
        batch_op.add_column(sa.Column('telefono', sa.String(length=50), nullable=True))
        
        # Datos de dirección
        batch_op.add_column(sa.Column('calle_nombre', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('calle_nro', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('localidad', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('cp', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('provincia', sa.String(length=100), nullable=True))
        
        # Monto inicial
        batch_op.add_column(sa.Column('monto_inicial', sa.Numeric(precision=15, scale=2), nullable=True))


def downgrade() -> None:
    # Remover las columnas agregadas
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.drop_column('provincia')
        batch_op.drop_column('cp')
        batch_op.drop_column('localidad')
        batch_op.drop_column('calle_nro')
        batch_op.drop_column('calle_nombre')
        batch_op.drop_column('telefono')
        batch_op.drop_column('monto_inicial')

