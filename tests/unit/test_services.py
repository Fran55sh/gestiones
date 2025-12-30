"""
Tests para servicios (email, storage).
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from flask import current_app

from app.services.storage import save_submission_to_file
from app.services.email_service import send_email_smtp
from app.utils.exceptions import StorageError, EmailError, ConfigurationError


class TestStorageService:
    """Tests para el servicio de almacenamiento."""

    def test_save_submission_creates_record(self, app):
        """Test que crea un registro en la base de datos."""
        with app.app_context():
            from app.core.database import db
            from app.features.contact.models import ContactSubmission

            result = save_submission_to_file("Test Entity", "Test Name", "test@example.com", "1234567890", "Test message")

            assert result is True

            # Verificar que se guardó en la base de datos
            submissions = ContactSubmission.query.all()
            assert len(submissions) == 1
            assert submissions[0].entity == "Test Entity"
            assert submissions[0].email == "test@example.com"

    def test_save_submission_appends_to_existing(self, app):
        """Test que agrega a registros existentes."""
        with app.app_context():
            from app.core.database import db
            from app.features.contact.models import ContactSubmission

            # Crear un registro existente
            existing = ContactSubmission(entity="Existing", name="Old", email="old@test.com", phone="111", message="Old")
            db.session.add(existing)
            db.session.commit()

            # Guardar un nuevo registro
            save_submission_to_file("New Entity", "New Name", "new@example.com", "0987654321", "New message")

            # Verificar que hay 2 registros
            submissions = ContactSubmission.query.all()
            assert len(submissions) == 2
            assert submissions[0].entity == "Existing"
            assert submissions[1].entity == "New Entity"

    def test_save_submission_missing_config(self, app):
        """Test que el servicio funciona sin configuración de archivo."""
        with app.app_context():
            # El servicio ahora usa la base de datos, no necesita configuración de archivo
            result = save_submission_to_file("Test", "Test", "test@test.com", "123", "Msg")
            assert result is True

    def test_save_submission_sanitizes_input(self, app):
        """Test que sanitiza la entrada."""
        with app.app_context():
            from app.features.contact.models import ContactSubmission

            save_submission_to_file("  Entity with spaces  ", "Name", "test@example.com", "123", "Message")

            submissions = ContactSubmission.query.all()
            assert len(submissions) == 1
            assert submissions[0].entity == "Entity with spaces"

    def test_save_submission_handles_database_errors(self, app):
        """Test que maneja errores de base de datos."""
        with app.app_context():
            from app.core.database import db

            # Forzar un error cerrando la sesión
            db.session.close()

            # El servicio debería lanzar StorageError
            with pytest.raises(StorageError):
                save_submission_to_file("Test", "Test", "test@test.com", "123", "Msg")


class TestEmailService:
    """Tests para el servicio de email."""

    @patch("app.services.email_service.smtplib.SMTP_SSL")
    @patch("app.services.email_service.smtplib.SMTP")
    def test_send_email_smtp_success_ssl(self, mock_smtp, mock_smtp_ssl, app):
        """Test envío exitoso con SSL."""
        with app.app_context():
            app.config.update(
                {
                    "MAIL_SERVER": "smtp.test.com",
                    "MAIL_PORT": 465,
                    "MAIL_USE_SSL": True,
                    "MAIL_USE_TLS": False,
                    "MAIL_USERNAME": "test@test.com",
                    "MAIL_PASSWORD": "password",
                    "MAIL_TIMEOUT": 20,
                }
            )

            # Mock del servidor SMTP
            mock_server = MagicMock()
            mock_smtp_ssl.return_value = mock_server

            result = send_email_smtp(
                recipients=["recipient@test.com"], subject="Test Subject", body_text="Test body", body_html="<p>Test body</p>"
            )

            assert result is True
            mock_smtp_ssl.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()

    @patch("app.services.email_service.smtplib.SMTP")
    def test_send_email_smtp_success_tls(self, mock_smtp, app):
        """Test envío exitoso con TLS."""
        with app.app_context():
            app.config.update(
                {
                    "MAIL_SERVER": "smtp.test.com",
                    "MAIL_PORT": 587,
                    "MAIL_USE_SSL": False,
                    "MAIL_USE_TLS": True,
                    "MAIL_USERNAME": "test@test.com",
                    "MAIL_PASSWORD": "password",
                    "MAIL_TIMEOUT": 20,
                }
            )

            mock_server = MagicMock()
            mock_smtp.return_value = mock_server

            result = send_email_smtp(
                recipients=["recipient@test.com"], subject="Test Subject", body_text="Test body", body_html="<p>Test body</p>"
            )

            assert result is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()

    def test_send_email_no_credentials(self, app):
        """Test cuando no hay credenciales."""
        with app.app_context():
            app.config.update({"MAIL_USERNAME": "", "MAIL_PASSWORD": ""})

            result = send_email_smtp(recipients=["test@test.com"], subject="Test", body_text="Test", body_html="<p>Test</p>")

            assert result is False

    def test_send_email_missing_server_config(self, app):
        """Test error cuando falta configuración del servidor."""
        with app.app_context():
            app.config.update({"MAIL_SERVER": None, "MAIL_USERNAME": "test@test.com", "MAIL_PASSWORD": "password"})

            with pytest.raises(ConfigurationError) as exc_info:
                send_email_smtp(recipients=["test@test.com"], subject="Test", body_text="Test", body_html="<p>Test</p>")

            assert "MAIL_SERVER" in str(exc_info.value)

    def test_send_email_no_recipients(self, app):
        """Test error cuando no hay destinatarios."""
        with app.app_context():
            app.config.update({"MAIL_SERVER": "smtp.test.com", "MAIL_USERNAME": "test@test.com", "MAIL_PASSWORD": "password"})

            with pytest.raises(EmailError) as exc_info:
                send_email_smtp(recipients=[], subject="Test", body_text="Test", body_html="<p>Test</p>")

            assert "destinatarios" in str(exc_info.value).lower()

    @patch("app.services.email_service.smtplib.SMTP_SSL")
    def test_send_email_authentication_error(self, mock_smtp_ssl, app):
        """Test error de autenticación SMTP."""
        import smtplib

        with app.app_context():
            app.config.update(
                {
                    "MAIL_SERVER": "smtp.test.com",
                    "MAIL_PORT": 465,
                    "MAIL_USE_SSL": True,
                    "MAIL_USERNAME": "test@test.com",
                    "MAIL_PASSWORD": "wrong",
                    "MAIL_TIMEOUT": 20,
                }
            )

            mock_server = MagicMock()
            mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Auth failed")
            mock_smtp_ssl.return_value = mock_server

            with pytest.raises(EmailError) as exc_info:
                send_email_smtp(recipients=["test@test.com"], subject="Test", body_text="Test", body_html="<p>Test</p>")

            assert "autenticación" in str(exc_info.value).lower()
