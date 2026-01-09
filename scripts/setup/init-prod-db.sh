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

# Create database tables using Flask-SQLAlchemy
echo "📊 Creating database tables..."
docker exec gestiones-mvp-prod python3 << 'PYTHON_SCRIPT'
from app import create_app
from app.core.database import db

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Database tables created successfully!")
PYTHON_SCRIPT

# Populate with sample data
echo "📦 Populating database with sample data..."
docker exec gestiones-mvp-prod python3 scripts/dev/create_sample_data.py

echo ""
echo "🎉 Production database initialized successfully!"
echo "✅ Tables created"
echo "✅ Sample data loaded"
echo ""

