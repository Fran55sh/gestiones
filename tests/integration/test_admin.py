"""
Tests para endpoints administrativos.
"""

import pytest
import json


def test_admin_submissions_requires_auth(client):
    """Test que el endpoint de submissions requiere autenticación."""
    response = client.get("/api/submissions")
    # Debe redirigir o retornar error de autorización
    assert response.status_code in [401, 403, 302, 404]


def test_admin_submissions_with_auth(client, auth_headers):
    """Test acceso a submissions con autenticación."""
    # Primero hacer login
    client.post("/api/login", data={"username": "admin", "password": "admin123"})

    response = client.get("/api/submissions")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "submissions" in data
    assert isinstance(data["submissions"], list)


def test_admin_submissions_empty(client, auth_headers):
    """Test submissions cuando no hay datos."""
    # Hacer login
    client.post("/api/login", data={"username": "admin", "password": "admin123"})

    response = client.get("/api/submissions")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert isinstance(data["submissions"], list)


def test_admin_submissions_with_data(client, auth_headers, sample_submission):
    """Test submissions con datos existentes."""
    # Hacer login
    client.post("/api/login", data={"username": "admin", "password": "admin123"})

    # Crear una solicitud primero
    client.post("/api/contact", data=sample_submission)

    # Luego obtener submissions
    response = client.get("/api/submissions")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["submissions"]) > 0


def test_admin_test_email_config(client, auth_headers):
    """Test endpoint de configuración de email."""
    # Hacer login
    client.post("/api/login", data={"username": "admin", "password": "admin123"})

    response = client.get("/api/test-email-config")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "MAIL_SERVER" in data
    assert "MAIL_PORT" in data
    assert "has_credentials" in data


def test_admin_requires_admin_role(client):
    """Test que endpoints admin requieren rol de admin."""
    # Login como usuario regular
    client.post("/api/login", data={"username": "usuario", "password": "user123"})

    # Intentar acceder a endpoint admin
    response = client.get("/api/submissions")
    # Debe rechazar o redirigir
    assert response.status_code in [403, 302, 401]
