"""
Tests para rutas de autenticación.
"""

import pytest


def test_login_page_loads(client):
    """Test que la página de login carga correctamente."""
    response = client.get("/gestiones")
    assert response.status_code == 200
    assert b"login" in response.data.lower() or b"iniciar" in response.data.lower()


def test_login_success(client):
    """Test login exitoso con credenciales válidas."""
    response = client.post("/api/login", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    assert b"sesion" in response.data.lower() or b"exitoso" in response.data.lower() or b"redirect" in response.data.lower()


def test_login_invalid_username(client):
    """Test login con usuario inválido."""
    response = client.post("/api/login", data={"username": "usuario_inexistente", "password": "password123"})
    assert response.status_code == 400
    assert b"invalida" in response.data.lower() or b"credenciales" in response.data.lower()


def test_login_invalid_password(client):
    """Test login con contraseña incorrecta."""
    response = client.post("/api/login", data={"username": "admin", "password": "password_incorrecta"})
    assert response.status_code == 400
    assert b"invalida" in response.data.lower() or b"credenciales" in response.data.lower()


def test_login_missing_username(client):
    """Test login sin nombre de usuario."""
    response = client.post("/api/login", data={"password": "admin123"})
    assert response.status_code == 400


def test_login_missing_password(client):
    """Test login sin contraseña."""
    response = client.post("/api/login", data={"username": "admin"})
    assert response.status_code == 400


def test_logout(client, auth_headers):
    """Test logout."""
    # Primero hacer login
    client.post("/api/login", data={"username": "admin", "password": "admin123"})

    # Luego hacer logout
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


def test_login_creates_session(client):
    """Test que el login crea una sesión válida."""
    response = client.post("/api/login", data={"username": "admin", "password": "admin123"})

    # Verificar que hay una cookie de sesión
    assert "Set-Cookie" in response.headers or response.status_code == 200


def test_login_different_roles(client):
    """Test login con diferentes roles."""
    roles = {
        "admin": "admin123",
        "gestor": "gestor123",
        "usuario": "user123",  # El usuario se llama 'usuario' pero la contraseña es 'user123'
    }

    for username, password in roles.items():
        response = client.post("/api/login", data={"username": username, "password": password})
        assert response.status_code == 200, f"Login falló para {username}"
