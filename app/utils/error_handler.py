"""
Manejo centralizado de errores y logging estructurado.
"""

import logging
import traceback
from typing import Optional, Dict, Any
from flask import request, jsonify, current_app
from werkzeug.exceptions import HTTPException

from .exceptions import AppError

logger = logging.getLogger(__name__)


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Registra un error con contexto estructurado.

    Args:
        error: La excepción que ocurrió
        context: Diccionario con contexto adicional
    """
    context = context or {}

    # Información de la solicitud
    request_info = {
        "method": request.method if request else None,
        "path": request.path if request else None,
        "remote_addr": request.remote_addr if request else None,
        "user_agent": request.headers.get("User-Agent") if request else None,
    }

    # Información del usuario si está en sesión
    if request and hasattr(request, "session"):
        try:
            session = request.session
            if hasattr(session, "get"):
                request_info["username"] = session.get("username")
                request_info["role"] = session.get("role")
        except Exception:
            pass

    # Construir mensaje de log
    error_type = type(error).__name__
    error_message = str(error)

    # Log con nivel apropiado
    if isinstance(error, AppError):
        log_level = logging.WARNING if error.status_code < 500 else logging.ERROR
        log_message = f"[{error_type}] {error_message}"

        # Agregar detalles si existen
        if hasattr(error, "details") and error.details:
            log_message += f" | Details: {error.details}"
        if hasattr(error, "field") and error.field:
            log_message += f" | Field: {error.field}"
    else:
        log_level = logging.ERROR
        log_message = f"[{error_type}] {error_message}"

    # Agregar contexto
    if context:
        log_message += f" | Context: {context}"

    # Agregar información de la solicitud
    log_message += f" | Request: {request_info}"

    # Log con el nivel apropiado
    logger.log(log_level, log_message)

    # Para errores críticos, también loguear el traceback
    if log_level >= logging.ERROR:
        logger.debug(f"Traceback:\n{traceback.format_exc()}")


def handle_app_error(error: AppError):
    """
    Maneja errores de la aplicación (AppError y subclases).

    Returns:
        Respuesta JSON con el error
    """
    log_error(error)

    response_data = {"success": False, "error": error.message, "status_code": error.status_code}

    # Agregar detalles si existen
    if error.details:
        response_data["details"] = error.details

    # En desarrollo, agregar más información
    if current_app.config.get("DEBUG", False):
        response_data["error_type"] = type(error).__name__
        if hasattr(error, "field"):
            response_data["field"] = error.field

    return jsonify(response_data), error.status_code


def handle_http_exception(error: HTTPException):
    """
    Maneja excepciones HTTP de Werkzeug.

    Returns:
        Respuesta JSON o HTML según el tipo de ruta
    """
    log_error(error)

    # Si es una ruta API, devolver JSON
    if request and request.path.startswith("/api/"):
        return jsonify({"success": False, "error": error.description or "Error HTTP", "status_code": error.code}), error.code

    # Para rutas no-API, dejar que Flask maneje el error normalmente
    return error


def handle_generic_exception(error: Exception):
    """
    Maneja excepciones genéricas no esperadas.

    Returns:
        Respuesta JSON con error genérico
    """
    log_error(error, {"unexpected": True})

    # Si es una ruta API, devolver JSON
    if request and request.path.startswith("/api/"):
        error_message = "Error interno del servidor"
        if current_app.config.get("DEBUG", False):
            error_message = str(error)

        return jsonify({"success": False, "error": error_message, "status_code": 500}), 500

    # Para rutas no-API, re-lanzar para que Flask lo maneje
    raise error


def format_error_response(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> tuple:
    """
    Formatea una respuesta de error consistente.

    Args:
        message: Mensaje de error
        status_code: Código HTTP de estado
        details: Detalles adicionales del error

    Returns:
        Tupla (response, status_code)
    """
    response_data = {"success": False, "error": message, "status_code": status_code}

    if details:
        response_data["details"] = details

    return jsonify(response_data), status_code
