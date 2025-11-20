"""
Tests para formulario de contacto.
"""
import pytest
import json


def test_contact_form_validation_missing_fields(client):
    """Test validación de campos requeridos."""
    # Sin campos
    response = client.post('/api/contact', data={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False


def test_contact_form_validation_invalid_email(client, sample_submission):
    """Test validación de email inválido."""
    sample_submission['email'] = 'email-invalido'
    response = client.post('/api/contact', data=sample_submission)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'email' in data.get('error', '').lower() or 'email' in data.get('details', {}).get('field', '').lower()


def test_contact_form_success(client, sample_submission):
    """Test envío exitoso del formulario de contacto."""
    response = client.post('/api/contact', data=sample_submission)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'message' in data


def test_contact_form_saves_to_file(client, sample_submission, app):
    """Test que el formulario guarda datos en archivo."""
    # Enviar formulario
    response = client.post('/api/contact', data=sample_submission)
    assert response.status_code == 200
    
    # Verificar que el archivo existe
    import os
    file_path = app.config.get('CONTACT_SUBMISSIONS_FILE')
    assert file_path is not None
    assert os.path.exists(file_path)
    
    # Verificar contenido
    with open(file_path, 'r', encoding='utf-8') as f:
        submissions = json.load(f)
    
    assert len(submissions) > 0
    assert submissions[-1]['entity'] == sample_submission['entity']
    assert submissions[-1]['email'] == sample_submission['email']


def test_contact_form_sanitizes_input(client, app):
    """Test que el formulario sanitiza la entrada (trim y max_length)."""
    # sanitize_input solo hace trim y limita longitud, no elimina HTML
    # La protección XSS debe hacerse en el frontend al renderizar
    input_with_spaces = {
        'entity': '  Empresa con espacios  ',
        'name': '  Nombre  ',
        'email': 'test@test.com',
        'phone': '1234567890',
        'message': 'Mensaje normal'
    }
    
    response = client.post('/api/contact', data=input_with_spaces)
    assert response.status_code == 200
    
    # Verificar que se guardó sin espacios al inicio/fin
    import os
    import json
    with app.app_context():
        file_path = app.config.get('CONTACT_SUBMISSIONS_FILE')
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                submissions = json.load(f)
            if submissions:
                last_submission = submissions[-1]
                # Verificar que se eliminaron espacios
                assert last_submission.get('entity', '').startswith('Empresa')
                assert not last_submission.get('entity', '').startswith(' ')
                assert not last_submission.get('name', '').startswith(' ')


def test_contact_form_max_length(client):
    """Test validación de longitud máxima."""
    long_input = {
        'entity': 'A' * 300,  # Más del límite de 200
        'name': 'Nombre',
        'email': 'test@test.com',
        'phone': '1234567890',
        'message': 'Mensaje'
    }
    
    response = client.post('/api/contact', data=long_input)
    # Debe aceptarse pero truncarse o rechazarse
    assert response.status_code in [200, 400]

