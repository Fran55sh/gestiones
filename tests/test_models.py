"""
Tests para modelos de base de datos.
"""
import pytest
from datetime import datetime, date
from decimal import Decimal

from app.db import db
from app.models import User, Case, Promise, Activity, ContactSubmission


@pytest.fixture
def sample_user(app):
    """Crea un usuario de prueba."""
    user = User(
        username='testuser',
        role='gestor',
        active=True
    )
    user.set_password('testpass123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_case(app, sample_user):
    """Crea un caso de prueba."""
    case = Case(
        entity='Test Entity',
        debtor_name='John Doe',
        dni='12345678',
        amount=Decimal('10000.50'),
        status='en_gestion',
        cartera='Cartera A',
        assigned_to_id=sample_user.id
    )
    db.session.add(case)
    db.session.commit()
    return case


def test_user_creation(sample_user):
    """Test creación de usuario."""
    assert sample_user.username == 'testuser'
    assert sample_user.role == 'gestor'
    assert sample_user.active is True
    assert sample_user.check_password('testpass123')
    assert not sample_user.check_password('wrongpass')


def test_user_to_dict(sample_user):
    """Test conversión de usuario a diccionario."""
    user_dict = sample_user.to_dict()
    assert 'id' in user_dict
    assert 'username' in user_dict
    assert 'role' in user_dict
    assert 'password_hash' not in user_dict  # No debe incluir contraseña


def test_case_creation(sample_case):
    """Test creación de caso."""
    assert sample_case.entity == 'Test Entity'
    assert sample_case.debtor_name == 'John Doe'
    assert float(sample_case.amount) == 10000.50
    assert sample_case.status == 'en_gestion'
    assert sample_case.cartera == 'Cartera A'


def test_case_to_dict(sample_case):
    """Test conversión de caso a diccionario."""
    case_dict = sample_case.to_dict()
    assert 'id' in case_dict
    assert 'entity' in case_dict
    assert 'amount' in case_dict
    assert isinstance(case_dict['amount'], float)


def test_promise_creation(app, sample_case):
    """Test creación de promesa."""
    promise = Promise(
        case_id=sample_case.id,
        amount=Decimal('5000.00'),
        promise_date=date.today(),
        status='pending'
    )
    db.session.add(promise)
    db.session.commit()
    
    assert promise.case_id == sample_case.id
    assert float(promise.amount) == 5000.00
    assert promise.status == 'pending'


def test_activity_creation(app, sample_case, sample_user):
    """Test creación de actividad."""
    activity = Activity(
        case_id=sample_case.id,
        type='call',
        notes='Llamada realizada',
        created_by_id=sample_user.id
    )
    db.session.add(activity)
    db.session.commit()
    
    assert activity.case_id == sample_case.id
    assert activity.type == 'call'
    assert activity.created_by_id == sample_user.id


def test_contact_submission_creation(app):
    """Test creación de solicitud de contacto."""
    submission = ContactSubmission(
        entity='Test Company',
        name='Jane Doe',
        email='jane@test.com',
        phone='1234567890',
        message='Test message'
    )
    db.session.add(submission)
    db.session.commit()
    
    assert submission.entity == 'Test Company'
    assert submission.email == 'jane@test.com'


def test_case_relationships(app, sample_case, sample_user):
    """Test relaciones de caso."""
    # Crear promesa
    promise = Promise(
        case_id=sample_case.id,
        amount=Decimal('1000'),
        promise_date=date.today()
    )
    db.session.add(promise)
    
    # Crear actividad
    activity = Activity(
        case_id=sample_case.id,
        type='call',
        created_by_id=sample_user.id
    )
    db.session.add(activity)
    db.session.commit()
    
    # Verificar relaciones
    assert sample_case.promises.count() == 1
    assert sample_case.activities.count() == 1
    assert sample_user.cases.count() == 1

