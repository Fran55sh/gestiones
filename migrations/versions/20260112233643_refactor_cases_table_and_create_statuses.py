"""Refactor cases table and create case_statuses

Revision ID: 20260112233643
Revises: 20260112225203
Create Date: 2026-01-12 23:36:43

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '20260112233643'
down_revision = '20260112225203'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    # Step 1: Create case_statuses table if it doesn't exist
    if 'case_statuses' not in tables:
        op.create_table(
            'case_statuses',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nombre', sa.String(length=100), nullable=False),
            sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_case_statuses_nombre'), 'case_statuses', ['nombre'], unique=True)
        op.create_index(op.f('ix_case_statuses_id'), 'case_statuses', ['id'], unique=False)

    # Insert default case statuses
    connection = op.get_bind()
    statuses = [
        {'id': 1, 'nombre': 'Sin Arreglo', 'activo': True, 'created_at': datetime.utcnow()},
        {'id': 2, 'nombre': 'En gestión', 'activo': True, 'created_at': datetime.utcnow()},
        {'id': 3, 'nombre': 'Incobrable', 'activo': True, 'created_at': datetime.utcnow()},
        {'id': 4, 'nombre': 'Contactado', 'activo': True, 'created_at': datetime.utcnow()},
        {'id': 5, 'nombre': 'Con Arreglo', 'activo': True, 'created_at': datetime.utcnow()},
        {'id': 6, 'nombre': 'A Juicio', 'activo': True, 'created_at': datetime.utcnow()},
        {'id': 7, 'nombre': 'De baja', 'activo': True, 'created_at': datetime.utcnow()},
    ]
    
    # Use ON CONFLICT DO NOTHING for PostgreSQL, INSERT OR IGNORE for SQLite
    if connection.dialect.name == 'postgresql':
        for status in statuses:
            connection.execute(
                text("""
                    INSERT INTO case_statuses (id, nombre, activo, created_at)
                    VALUES (:id, :nombre, :activo, :created_at)
                    ON CONFLICT (id) DO NOTHING
                """),
                status
            )
    else:
        # SQLite
        for status in statuses:
            connection.execute(
                text("""
                    INSERT OR IGNORE INTO case_statuses (id, nombre, activo, created_at)
                    VALUES (:id, :nombre, :activo, :created_at)
                """),
                status
            )

    # Step 2: Drop old cases table (this will cascade delete foreign keys from promises and activities)
    # First, drop foreign key constraints from promises and activities
    op.drop_table('promises')
    op.drop_table('activities')
    
    # Now drop cases table
    op.drop_table('cases')

    # Step 3: Create new cases table with new structure
    op.create_table(
        'cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('lastname', sa.String(length=200), nullable=False),
        sa.Column('dni', sa.String(length=50), nullable=True),
        sa.Column('total', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('fecha_ultimo_pago', sa.Date(), nullable=True),
        sa.Column('status_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('cartera_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['status_id'], ['case_statuses.id'], ),
        sa.ForeignKeyConstraint(['cartera_id'], ['carteras.id'], ),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cases_name'), 'cases', ['name'], unique=False)
    op.create_index(op.f('ix_cases_lastname'), 'cases', ['lastname'], unique=False)
    op.create_index(op.f('ix_cases_dni'), 'cases', ['dni'], unique=False)
    op.create_index(op.f('ix_cases_status_id'), 'cases', ['status_id'], unique=False)
    op.create_index(op.f('ix_cases_cartera_id'), 'cases', ['cartera_id'], unique=False)
    op.create_index(op.f('ix_cases_assigned_to_id'), 'cases', ['assigned_to_id'], unique=False)
    op.create_index(op.f('ix_cases_created_at'), 'cases', ['created_at'], unique=False)

    # Step 4: Recreate promises and activities tables
    op.create_table(
        'promises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('promise_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('fulfilled_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promises_case_id'), 'promises', ['case_id'], unique=False)
    op.create_index(op.f('ix_promises_promise_date'), 'promises', ['promise_date'], unique=False)

    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activities_case_id'), 'activities', ['case_id'], unique=False)
    op.create_index(op.f('ix_activities_type'), 'activities', ['type'], unique=False)
    op.create_index(op.f('ix_activities_created_by_id'), 'activities', ['created_by_id'], unique=False)
    op.create_index(op.f('ix_activities_created_at'), 'activities', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop new tables
    op.drop_table('activities')
    op.drop_table('promises')
    op.drop_table('cases')
    op.drop_table('case_statuses')
    
    # Note: The old cases table structure cannot be fully restored
    # as we don't have the original data. This is intentional per user's request.

