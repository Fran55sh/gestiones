"""
Configuración compartida para todos los tests (fixtures).
"""

import os
import tempfile
import pytest
from pathlib import Path

from app import create_app


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

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Deshabilitar CSRF en tests

    yield app

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
