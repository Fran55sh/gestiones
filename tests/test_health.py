"""
Tests para endpoints de salud y configuración.
"""
import pytest
import json


def test_healthz_endpoint(client):
    """Test que el endpoint healthz funciona."""
    response = client.get('/healthz')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_healthz_returns_json(client):
    """Test que healthz retorna JSON."""
    response = client.get('/healthz')
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert 'status' in data

