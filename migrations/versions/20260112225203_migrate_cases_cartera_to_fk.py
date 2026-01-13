"""Migrate cases.cartera from String to Foreign Key

Revision ID: 20260112225203
Revises: 20260112225202
Create Date: 2026-01-12 22:52:03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, inspect


# revision identifiers, used by Alembic.
revision = '20260112225203'
down_revision = '20260112225202'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite doesn't support ALTER TABLE for foreign keys, so we use batch mode
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Check current state of the table
    columns = [col['name'] for col in inspector.get_columns('cases')]
    cartera_id_exists = 'cartera_id' in columns
    cartera_exists = 'cartera' in columns
    
    # Step 1: Add cartera_id column if it doesn't exist
    if not cartera_id_exists:
        with op.batch_alter_table('cases', schema=None) as batch_op:
            batch_op.add_column(sa.Column('cartera_id', sa.Integer(), nullable=True))
            batch_op.create_index('ix_cases_cartera_id', ['cartera_id'], unique=False)
    
    # Step 2: Migrate existing data from cartera (String) to cartera_id (if cartera still exists)
    if cartera_exists:
        # Get all unique cartera values from cases that don't have cartera_id set
        result = connection.execute(text("""
            SELECT DISTINCT cartera 
            FROM cases 
            WHERE cartera IS NOT NULL 
            AND (cartera_id IS NULL OR cartera_id = 0)
        """))
        cartera_strings = [row[0] for row in result]
        
        # For each unique cartera string, find or create cartera record
        cartera_mapping = {}
        for cartera_str in cartera_strings:
            # Try to find existing cartera by name
            cartera_result = connection.execute(
                text("SELECT id FROM carteras WHERE nombre = :nombre"),
                {"nombre": cartera_str}
            )
            cartera_row = cartera_result.fetchone()
            
            if cartera_row:
                cartera_id = cartera_row[0]
            else:
                # Create new cartera if it doesn't exist
                connection.execute(
                    text("INSERT INTO carteras (nombre, activo, created_at) VALUES (:nombre, 1, CURRENT_TIMESTAMP)"),
                    {"nombre": cartera_str}
                )
                cartera_result = connection.execute(
                    text("SELECT id FROM carteras WHERE nombre = :nombre"),
                    {"nombre": cartera_str}
                )
                cartera_id = cartera_result.fetchone()[0]
            
            cartera_mapping[cartera_str] = cartera_id
        
        # Update all cases with cartera_id based on mapping
        for cartera_str, cartera_id in cartera_mapping.items():
            connection.execute(
                text("UPDATE cases SET cartera_id = :cartera_id WHERE cartera = :cartera_str AND (cartera_id IS NULL OR cartera_id = 0)"),
                {"cartera_id": cartera_id, "cartera_str": cartera_str}
            )
    
    # Step 3: Set default cartera_id for any NULL values
    default_cartera_result = connection.execute(text("SELECT id FROM carteras ORDER BY id LIMIT 1"))
    default_cartera_row = default_cartera_result.fetchone()
    if default_cartera_row:
        default_cartera_id = default_cartera_row[0]
        connection.execute(
            text("UPDATE cases SET cartera_id = :cartera_id WHERE cartera_id IS NULL"),
            {"cartera_id": default_cartera_id}
        )
    
    # Step 4: Make cartera_id NOT NULL and drop old cartera column (if it exists)
    if cartera_exists:
        with op.batch_alter_table('cases', schema=None) as batch_op:
            # Ensure all rows have cartera_id before making it NOT NULL
            if default_cartera_row:
                connection.execute(
                    text("UPDATE cases SET cartera_id = :cartera_id WHERE cartera_id IS NULL"),
                    {"cartera_id": default_cartera_row[0]}
                )
            batch_op.alter_column('cartera_id', nullable=False)
            # Drop old cartera column and its index
            try:
                batch_op.drop_index('ix_cases_cartera')
            except:
                pass  # Index might not exist
            batch_op.drop_column('cartera')
    elif cartera_id_exists:
        # If cartera_id exists but cartera doesn't, just ensure it's NOT NULL
        with op.batch_alter_table('cases', schema=None) as batch_op:
            if default_cartera_row:
                connection.execute(
                    text("UPDATE cases SET cartera_id = :cartera_id WHERE cartera_id IS NULL"),
                    {"cartera_id": default_cartera_row[0]}
                )
            batch_op.alter_column('cartera_id', nullable=False)


def downgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Check current state
    columns = [col['name'] for col in inspector.get_columns('cases')]
    cartera_exists = 'cartera' in columns
    cartera_id_exists = 'cartera_id' in columns
    
    # Step 1: Add back cartera column (String) if it doesn't exist
    if not cartera_exists and cartera_id_exists:
        with op.batch_alter_table('cases', schema=None) as batch_op:
            batch_op.add_column(sa.Column('cartera', sa.String(length=100), nullable=True))
            batch_op.create_index('ix_cases_cartera', ['cartera'], unique=False)
        
        # Step 2: Migrate data back from cartera_id to cartera string
        # SQLite doesn't support JOIN in UPDATE, so we do it in Python
        result = connection.execute(text("SELECT id, cartera_id FROM cases"))
        for row in result:
            case_id, cartera_id = row
            if cartera_id:
                cartera_result = connection.execute(
                    text("SELECT nombre FROM carteras WHERE id = :id"),
                    {"id": cartera_id}
                )
                cartera_row = cartera_result.fetchone()
                if cartera_row:
                    connection.execute(
                        text("UPDATE cases SET cartera = :nombre WHERE id = :case_id"),
                        {"nombre": cartera_row[0], "case_id": case_id}
                    )
        
        # Step 3: Set default for any NULL values
        connection.execute(text("UPDATE cases SET cartera = 'Cartera A' WHERE cartera IS NULL"))
        
        # Step 4: Make cartera NOT NULL and drop cartera_id
        with op.batch_alter_table('cases', schema=None) as batch_op:
            batch_op.alter_column('cartera', nullable=False)
            try:
                batch_op.drop_index('ix_cases_cartera_id')
            except:
                pass
            batch_op.drop_column('cartera_id')
