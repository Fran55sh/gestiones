"""
Tests para utilidades de seguridad.
"""
import pytest
from flask import Flask, session

from app.utils.security import require_role


def test_require_role_decorator_allows_admin(client):
    """Test que el decorador permite acceso a admin."""
    # Login como admin
    client.post('/api/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    # Acceder a endpoint que requiere admin
    response = client.get('/api/submissions')
    assert response.status_code == 200


def test_require_role_decorator_blocks_user(client):
    """Test que el decorador bloquea acceso a usuario regular."""
    # Login como usuario regular
    client.post('/api/login', data={
        'username': 'usuario',
        'password': 'user123'
    })
    
    # Intentar acceder a endpoint admin
    response = client.get('/api/submissions')
    assert response.status_code in [403, 302, 401]


def test_require_role_decorator_blocks_gestor(client):
    """Test que el decorador bloquea acceso a gestor para endpoints admin."""
    # Login como gestor
    client.post('/api/login', data={
        'username': 'gestor',
        'password': 'gestor123'
    })
    
    # Intentar acceder a endpoint admin
    response = client.get('/api/submissions')
    assert response.status_code in [403, 302, 401]


def test_require_role_decorator_blocks_unauthenticated(client):
    """Test que el decorador bloquea acceso sin autenticación."""
    # Sin login
    response = client.get('/api/submissions')
    assert response.status_code in [403, 302, 401, 404]


def test_dashboard_access_by_role(client):
    """Test que cada dashboard solo es accesible por su rol."""
    # Admin puede acceder a su dashboard
    client.post('/api/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    response = client.get('/dashboard-admin')
    assert response.status_code == 200
    
    # Usuario no puede acceder a dashboard admin
    client.get('/logout')
    client.post('/api/login', data={
        'username': 'usuario',
        'password': 'user123'
    })
    response = client.get('/dashboard-admin')
    assert response.status_code in [403, 302, 401]

