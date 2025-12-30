"""Test script to verify imports work"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    from app import create_app
    app = create_app()
    print("✓ App created successfully")
    print(f"✓ Blueprints registered: {len(app.blueprints)}")
    for name in app.blueprints:
        print(f"  - {name}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

