"""Add management_status field to Case model

Revision ID: 9064f0eb7540
Revises: 
Create Date: 2025-12-29 22:23:47.977177

NOTA: Esta migración es obsoleta. El campo management_status fue reemplazado por status_id
en la refactorización completa. Se mantiene por compatibilidad pero es idempotente.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '9064f0eb7540'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Verificar si la tabla cases existe y si la columna ya existe
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Verificar si la tabla existe
    if 'cases' not in inspector.get_table_names():
        # Si la tabla no existe, esta migración no aplica (será creada por migraciones posteriores)
        return
    
    # Verificar si la columna ya existe
    columns = [col['name'] for col in inspector.get_columns('cases')]
    if 'management_status' in columns:
        # La columna ya existe, no hacer nada
        print("   [SKIP] Columna 'management_status' ya existe, saltando...")
        return
    
    # Agregar columna solo si no existe
    op.add_column('cases', sa.Column('management_status', sa.String(length=50), nullable=True))
    
    # Verificar si el índice ya existe antes de crearlo
    indexes = [idx['name'] for idx in inspector.get_indexes('cases')]
    if 'ix_cases_management_status' not in indexes:
        op.create_index(op.f('ix_cases_management_status'), 'cases', ['management_status'], unique=False)


def downgrade() -> None:
    # Verificar si la columna existe antes de eliminarla
    connection = op.get_bind()
    inspector = inspect(connection)
    
    if 'cases' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('cases')]
    if 'management_status' not in columns:
        return
    
    # Eliminar índice si existe
    indexes = [idx['name'] for idx in inspector.get_indexes('cases')]
    if 'ix_cases_management_status' in indexes:
        op.drop_index(op.f('ix_cases_management_status'), table_name='cases')
    
    # Eliminar columna
    op.drop_column('cases', 'management_status')

