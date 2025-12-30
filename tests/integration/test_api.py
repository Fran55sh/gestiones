"""
Tests para endpoints API.
"""
import pytest
from decimal import Decimal
from datetime import date

from app.core.database import db
from app.models import User, Case, Promise, Activity


@pytest.fixture
def admin_user(app):
    """Crea usuario admin para tests."""
    user = User.query.filter_by(username='admin').first()
    if not user:
        user = User(username='admin', role='admin', active=True)
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
    return user


@pytest.fixture
def test_case(app, admin_user):
    """Crea caso de prueba."""
    case = Case(
        entity='Test Entity',
        debtor_name='Test Debtor',
        amount=Decimal('5000.00'),
        status='en_gestion',
        cartera='Cartera A',
        assigned_to_id=admin_user.id
    )
    db.session.add(case)
    db.session.commit()
    return case


def test_dashboard_kpis(client, authenticated_client):
    """Test endpoint de KPIs."""
    response = authenticated_client.get('/api/dashboard/kpis')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data
    assert 'monto_recuperado' in data['data']
    assert 'tasa_recupero' in data['data']


def test_dashboard_performance_chart(client, authenticated_client):
    """Test endpoint de gráfico de rendimiento."""
    response = authenticated_client.get('/api/dashboard/charts/performance')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data
    assert 'labels' in data['data']
    assert 'datasets' in data['data']


def test_dashboard_cartera_chart(client, authenticated_client):
    """Test endpoint de gráfico de cartera."""
    response = authenticated_client.get('/api/dashboard/charts/cartera')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data


def test_dashboard_gestores_ranking(client, authenticated_client):
    """Test endpoint de ranking de gestores."""
    response = authenticated_client.get('/api/dashboard/gestores/ranking')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data
    assert isinstance(data['data'], list)


def test_list_cases(client, authenticated_client, test_case):
    """Test listado de casos."""
    response = authenticated_client.get('/api/cases')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data
    assert 'pagination' in data
    assert len(data['data']) > 0


def test_create_case(client, authenticated_client):
    """Test creación de caso."""
    case_data = {
        'entity': 'New Entity',
        'debtor_name': 'New Debtor',
        'amount': 10000.50,
        'status': 'en_gestion',
        'cartera': 'Cartera B'
    }
    response = authenticated_client.post(
        '/api/cases',
        json=case_data,
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['entity'] == 'New Entity'


def test_get_case(client, authenticated_client, test_case):
    """Test obtener caso por ID."""
    response = authenticated_client.get(f'/api/cases/{test_case.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['id'] == test_case.id


def test_update_case(client, authenticated_client, test_case):
    """Test actualización de caso."""
    update_data = {
        'status': 'pagada',
        'notes': 'Updated notes'
    }
    response = authenticated_client.put(
        f'/api/cases/{test_case.id}',
        json=update_data,
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['status'] == 'pagada'


def test_delete_case(client, authenticated_client, test_case):
    """Test eliminación de caso."""
    case_id = test_case.id
    response = authenticated_client.delete(f'/api/cases/{case_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    
    # Verificar que fue eliminado
    response = authenticated_client.get(f'/api/cases/{case_id}')
    assert response.status_code == 404


def test_create_promise(client, authenticated_client, test_case):
    """Test creación de promesa."""
    promise_data = {
        'amount': 2000.00,
        'promise_date': date.today().isoformat(),
        'status': 'pending'
    }
    response = authenticated_client.post(
        f'/api/cases/{test_case.id}/promises',
        json=promise_data,
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert float(data['data']['amount']) == 2000.00


def test_create_activity(client, authenticated_client, test_case):
    """Test creación de actividad."""
    activity_data = {
        'type': 'call',
        'notes': 'Test call activity'
    }
    response = authenticated_client.post(
        f'/api/cases/{test_case.id}/activities',
        json=activity_data,
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['type'] == 'call'


def test_api_requires_auth(client):
    """Test que los endpoints API requieren autenticación."""
    endpoints = [
        '/api/dashboard/kpis',
        '/api/dashboard/charts/performance',
        '/api/cases'
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        # Debe redirigir a login
        assert response.status_code in [302, 401, 403]

