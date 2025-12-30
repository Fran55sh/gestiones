"""
Tests para manejo de errores.
"""

import pytest
import json

from app.utils.exceptions import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    StorageError,
    EmailError,
    ConfigurationError,
)
from app.utils.error_handler import format_error_response


class TestExceptions:
    """Tests para excepciones personalizadas."""

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Campo requerido", field="email")
        assert error.message == "Campo requerido"
        assert error.status_code == 400
        assert error.field == "email"

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Credenciales inválidas")
        assert error.message == "Credenciales inválidas"
        assert error.status_code == 401

    def test_authorization_error(self):
        """Test AuthorizationError."""
        error = AuthorizationError("Sin permisos")
        assert error.message == "Sin permisos"
        assert error.status_code == 403

    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError("Recurso no encontrado", resource="user")
        assert error.message == "Recurso no encontrado"
        assert error.status_code == 404
        assert error.resource == "user"

    def test_storage_error(self):
        """Test StorageError."""
        error = StorageError("Error al guardar", operation="save")
        assert error.message == "Error al guardar"
        assert error.status_code == 500
        assert error.operation == "save"

    def test_email_error(self):
        """Test EmailError."""
        error = EmailError("Error al enviar")
        assert error.message == "Error al enviar"
        assert error.status_code == 500

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Config faltante", config_key="SECRET_KEY")
        assert error.message == "Config faltante"
        assert error.status_code == 500
        assert error.config_key == "SECRET_KEY"


class TestErrorHandler:
    """Tests para el manejador de errores."""

    def test_format_error_response(self, app):
        """Test formateo de respuesta de error."""
        with app.app_context():
            response, status_code = format_error_response("Error de prueba", 400)

            # Convertir a dict para verificar
            data = json.loads(response.data)
            assert data["success"] is False
            assert data["error"] == "Error de prueba"
            assert data["status_code"] == 400
            assert status_code == 400

    def test_format_error_response_with_details(self, app):
        """Test formateo con detalles adicionales."""
        with app.app_context():
            details = {"field": "email", "reason": "invalid format"}
            response, status_code = format_error_response("Error", 400, details)

            data = json.loads(response.data)
            assert data["details"] == details


class TestErrorHandlersInApp:
    """Tests para error handlers en la aplicación."""

    def test_404_handler_for_api(self, client):
        """Test que 404 retorna JSON para rutas API."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data or "success" in data

    def test_validation_error_in_contact(self, client):
        """Test que ValidationError se maneja correctamente."""
        # Enviar formulario sin campos requeridos
        response = client.post("/api/contact", data={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "error" in data

    def test_storage_error_handling(self, app):
        """Test que StorageError se propaga correctamente."""
        from app.services.storage import save_submission_to_file
        from app.core.database import db
        from unittest.mock import patch

        with app.app_context():
            # Forzar un error usando mock para que commit falle
            with patch.object(db.session, "commit", side_effect=Exception("Database error")):
                with pytest.raises(StorageError):
                    save_submission_to_file("Test", "Test", "test@test.com", "123", "Msg")
