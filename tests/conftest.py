"""
Configuración compartida para todos los tests (fixtures).
"""

import os
import tempfile
import pytest
from pathlib import Path
from werkzeug.security import generate_password_hash

from app import create_app
from app.core.database import db
from app.models import User


@pytest.fixture
def app():
    """Crea una instancia de la aplicación para testing."""
    # Crear directorio temporal para datos de test
    test_data_dir = tempfile.mkdtemp()
    test_submissions_file = os.path.join(test_data_dir, "test_submissions.json")

    # Configurar variables de entorno para testing
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    os.environ["CONTACT_SUBMISSIONS_FILE"] = test_submissions_file
    os.environ["MAIL_USERNAME"] = "test@example.com"
    os.environ["MAIL_PASSWORD"] = "test-password"
    os.environ["MAIL_SERVER"] = "smtp.test.com"
    os.environ["MAIL_PORT"] = "587"
    os.environ["MAIL_USE_TLS"] = "true"
    os.environ["MAIL_USE_SSL"] = "false"
    os.environ["TESTING"] = "true"  # Set testing mode before creating app
    # Forzar SQLite en tests ANTES de crear la app (sobrescribe cualquier DATABASE_URL)
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Deshabilitar CSRF en tests

    with app.app_context():
        # Limpiar cualquier dato existente y recrear las tablas
        db.drop_all()
        db.create_all()

        # Crear usuarios de prueba para autenticación
        admin_user = User(username="admin", password_hash=generate_password_hash("admin123"), role="admin")
        gestor_user = User(username="gestor", password_hash=generate_password_hash("gestor123"), role="gestor")
        db.session.add_all([admin_user, gestor_user])
        db.session.commit()

        yield app

        # Limpiar la base de datos después de los tests
        db.session.remove()
        db.drop_all()

    # Limpiar después de los tests
    if os.path.exists(test_submissions_file):
        os.remove(test_submissions_file)
    if os.path.exists(test_data_dir):
        os.rmdir(test_data_dir)


@pytest.fixture
def client(app):
    """Cliente de prueba para hacer requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner para comandos CLI."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Headers de autenticación después de login."""
    # Hacer login como admin
    response = client.post("/api/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)

    # Retornar cookies de sesión
    return {"Cookie": response.headers.get("Set-Cookie", "")}


@pytest.fixture
def authenticated_client(client):
    """Cliente autenticado como admin."""
    client.post("/api/login", data={"username": "admin", "password": "admin123"})
    return client


@pytest.fixture
def sample_submission():
    """Datos de ejemplo para una solicitud de contacto."""
    return {
        "entity": "Empresa Test",
        "name": "Juan Pérez",
        "email": "juan@test.com",
        "phone": "1234567890",
        "message": "Mensaje de prueba para testing",
    }
