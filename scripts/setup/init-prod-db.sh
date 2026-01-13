#!/bin/bash
set -e

echo "🔧 Initializing Production Database..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker exec gestiones-db-prod pg_isready -U gestiones_user -d gestiones > /dev/null 2>&1; do
    echo "Waiting for database connection..."
    sleep 2
done

echo "✅ PostgreSQL is ready!"

# Run Alembic migrations
echo "🔄 Running database migrations..."
docker exec gestiones-mvp-prod alembic -c config/alembic.ini upgrade head
echo "✅ Migrations completed!"

# Create default data (carteras, case_statuses, users)
echo "📦 Creating default data (carteras, estados, usuarios)..."
docker exec gestiones-mvp-prod python3 << 'PYTHON_SCRIPT'
from app import create_app
from app.core.database import db

app = create_app()

with app.app_context():
    # This will create default carteras, case_statuses, and users
    # if they don't exist (handled in app/__init__.py)
    db.create_all()
    print("✅ Default data created!")
PYTHON_SCRIPT

echo ""
echo "🎉 Production database initialized successfully!"
echo "✅ Migrations applied"
echo "✅ Default data created"
echo ""
echo "📝 Next steps:"
echo "   1. If you have data from develop, run:"
echo "      docker exec gestiones-mvp-prod python3 scripts/prod/import_data_to_prod.py"
echo "   2. Verify the database is working correctly"
echo ""

