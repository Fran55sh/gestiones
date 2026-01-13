"""Create carteras table

Revision ID: 20260112225202
Revises: 9064f0eb7540
Create Date: 2026-01-12 22:52:02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20260112225202'
down_revision = '9064f0eb7540'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if table already exists (in case db.create_all() created it)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'carteras' not in tables:
        # Create carteras table
        op.create_table(
            'carteras',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nombre', sa.String(length=200), nullable=False),
            sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_carteras_nombre'), 'carteras', ['nombre'], unique=True)
    
    # Insert default carteras (if they don't exist)
    # Use ON CONFLICT DO NOTHING for PostgreSQL, INSERT OR IGNORE for SQLite
    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':
        op.execute("""
            INSERT INTO carteras (nombre, activo, created_at)
            VALUES 
                ('Cristal Cash', true, CURRENT_TIMESTAMP),
                ('Favacard', true, CURRENT_TIMESTAMP)
            ON CONFLICT (nombre) DO NOTHING
        """)
    else:
        # SQLite
        op.execute("""
            INSERT OR IGNORE INTO carteras (nombre, activo, created_at)
            VALUES 
                ('Cristal Cash', 1, CURRENT_TIMESTAMP),
                ('Favacard', 1, CURRENT_TIMESTAMP)
        """)


def downgrade() -> None:
    op.drop_index(op.f('ix_carteras_nombre'), table_name='carteras')
    op.drop_table('carteras')

