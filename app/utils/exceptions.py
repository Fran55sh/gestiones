"""
Excepciones personalizadas para la aplicación.
"""

from typing import Optional


class AppError(Exception):
    """Excepción base para errores de la aplicación."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppError):
    """Error de validación de entrada."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, status_code=400, details=details)
        self.field = field


class AuthenticationError(AppError):
    """Error de autenticación."""

    def __init__(self, message: str = "Credenciales inválidas", details: Optional[dict] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(AppError):
    """Error de autorización (permisos insuficientes)."""

    def __init__(self, message: str = "No tiene permisos para realizar esta acción", details: Optional[dict] = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(AppError):
    """Recurso no encontrado."""

    def __init__(self, message: str = "Recurso no encontrado", resource: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, status_code=404, details=details)
        self.resource = resource


class StorageError(AppError):
    """Error al guardar o leer datos."""

    def __init__(
        self, message: str = "Error al procesar datos", operation: Optional[str] = None, details: Optional[dict] = None
    ):
        super().__init__(message, status_code=500, details=details)
        self.operation = operation


class EmailError(AppError):
    """Error al enviar email."""

    def __init__(self, message: str = "Error al enviar email", details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)


class ConfigurationError(AppError):
    """Error de configuración."""

    def __init__(
        self, message: str = "Error de configuración", config_key: Optional[str] = None, details: Optional[dict] = None
    ):
        super().__init__(message, status_code=500, details=details)
        self.config_key = config_key
