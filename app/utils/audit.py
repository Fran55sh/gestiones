"""
Utilidades para logging de auditoría.
"""

import logging
from datetime import datetime
from flask import request, session
from functools import wraps

logger = logging.getLogger("audit")


def audit_log(action: str, details: dict = None):
    """
    Registra un evento de auditoría.

    Args:
        action: Acción realizada (ej: 'login', 'create_case', 'update_case')
        details: Detalles adicionales del evento
    """
    user_id = session.get("user_id")
    username = session.get("username")
    role = session.get("role")
    ip_address = request.remote_addr if request else None
    user_agent = request.headers.get("User-Agent") if request else None

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": user_id,
        "username": username,
        "role": role,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "details": details or {},
    }

    logger.info(f"AUDIT: {action} | User: {username} ({role}) | IP: {ip_address} | Details: {log_data['details']}")


def audit_decorator(action: str):
    """
    Decorador para registrar automáticamente acciones.

    Args:
        action: Nombre de la acción a registrar
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                audit_log(action, {"status": "success", "args": str(args), "kwargs": str(kwargs)})
                return result
            except Exception as e:
                audit_log(action, {"status": "error", "error": str(e)})
                raise

        return decorated_function

    return decorator
