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

    def test_save_submission_creates_file(self, app):
        """Test que crea el archivo si no existe."""
        with app.app_context():
            # Usar archivo temporal
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
                temp_path = f.name

            try:
                app.config["CONTACT_SUBMISSIONS_FILE"] = temp_path

                save_submission_to_file("Test Entity", "Test Name", "test@example.com", "1234567890", "Test message")

                assert os.path.exists(temp_path)

                with open(temp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                assert isinstance(data, list)
                assert len(data) == 1
                assert data[0]["entity"] == "Test Entity"
                assert data[0]["email"] == "test@example.com"
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def test_save_submission_appends_to_existing(self, app):
        """Test que agrega a archivo existente."""
        with app.app_context():
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
                temp_path = f.name
                json.dump([{"entity": "Existing"}], f)

            try:
                app.config["CONTACT_SUBMISSIONS_FILE"] = temp_path

                save_submission_to_file("New Entity", "New Name", "new@example.com", "0987654321", "New message")

                with open(temp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                assert len(data) == 2
                assert data[0]["entity"] == "Existing"
                assert data[1]["entity"] == "New Entity"
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def test_save_submission_missing_config(self, app):
        """Test error cuando falta configuración."""
        with app.app_context():
            app.config["CONTACT_SUBMISSIONS_FILE"] = None

            with pytest.raises(StorageError) as exc_info:
                save_submission_to_file("Test", "Test", "test@test.com", "123", "Msg")

            assert "CONTACT_SUBMISSIONS_FILE" in str(exc_info.value)

    def test_save_submission_sanitizes_input(self, app):
        """Test que sanitiza la entrada."""
        with app.app_context():
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
                temp_path = f.name

            try:
                app.config["CONTACT_SUBMISSIONS_FILE"] = temp_path

                save_submission_to_file("  Entity with spaces  ", "Name", "test@example.com", "123", "Message")

                with open(temp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                assert data[0]["entity"] == "Entity with spaces"
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def test_save_submission_handles_corrupt_json(self, app):
        """Test que maneja JSON corrupto."""
        with app.app_context():
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
                temp_path = f.name
                f.write("invalid json content")

            try:
                app.config["CONTACT_SUBMISSIONS_FILE"] = temp_path

                # Debe inicializar nueva lista si el JSON está corrupto
                save_submission_to_file("Test", "Test", "test@test.com", "123", "Msg")

                with open(temp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                assert isinstance(data, list)
                assert len(data) == 1
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)


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
