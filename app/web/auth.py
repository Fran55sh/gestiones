import logging
from flask import Blueprint, request, session, redirect
from flask import current_app as app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..features.users.models import User
from ..services.audit import audit_log

logger = logging.getLogger(__name__)
bp = Blueprint("auth", __name__)

# Rate limiter para login
try:
    limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["5 per minute"])
except Exception:
    limiter = None


@bp.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute") if limiter else lambda f: f
def login():
    try:
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Validar entrada
        if not username:
            return _login_error_response("El nombre de usuario es requerido")
        if not password:
            return _login_error_response("La contraseña es requerida")

        logger.info(f"Intento de login para usuario: {username}")

        # Buscar usuario en base de datos
        user = User.query.filter_by(username=username, active=True).first()

        if not user:
            logger.warning(f"Usuario {username} no encontrado o inactivo")
            audit_log("login_attempt", {"username": username, "success": False, "reason": "user_not_found"})
            return _login_error_response("Credenciales inválidas. Por favor, intenta de nuevo.")

        # Verificar contraseña
        if not user.check_password(password):
            logger.warning(f"Contraseña incorrecta para usuario {username}")
            audit_log("login_attempt", {"username": username, "success": False, "reason": "invalid_password"})
            return _login_error_response("Credenciales inválidas. Por favor, intenta de nuevo.")

        # Login exitoso
        logger.info(f"Login exitoso para usuario: {username} (rol: {user.role})")

        try:
            session.clear()
            session.permanent = True
            session["username"] = username
            session["role"] = user.role
            session["user_id"] = user.id

            # Log de auditoría
            audit_log("login", {"username": username, "role": user.role, "success": True})
        except Exception as e:
            logger.error(f"Error al establecer sesión: {e}", exc_info=True)
            audit_log("login", {"username": username, "success": False, "error": str(e)})
            return _login_error_response("Error al iniciar sesión. Por favor, intenta de nuevo.")

        role_routes = {"admin": "/dashboard-admin", "gestor": "/dashboard-gestor", "user": "/dashboard-user"}
        redirect_url = role_routes.get(user.role, "/dashboard-user")
        return _login_success_response(user.role, redirect_url)

    except Exception as e:
        logger.error(f"Error inesperado en login: {e}", exc_info=True)
        return _login_error_response("Error inesperado al iniciar sesión. Por favor, intenta de nuevo.")


@bp.route("/logout")
def logout():
    username = session.get("username")
    audit_log("logout", {"username": username})
    session.clear()
    return redirect("/")


def _login_success_response(role, redirect_url):
    role_name = {"admin": "Administrador", "gestor": "Gestor", "user": "Usuario"}.get(role, "Usuario")

    # Respuesta HTML para mostrar mensaje de éxito
    html_response = (
        f'<div style="color: #10b981; background: #d1fae5; padding: 12px; border-radius: 8px; margin-top: 20px;">'
        f"✓ Inicio de sesión exitoso como {role_name}. Redirigiendo...</div>"
    )

    # Crear respuesta y agregar header HX-Redirect
    from flask import make_response

    response = make_response(html_response)
    response.headers["HX-Redirect"] = redirect_url
    return response


def _login_error_response(message):
    """Formatea respuesta de error para HTMX."""
    return (
        f'<div style="color: #dc2626; background: #fee2e2; padding: 12px; border-radius: 8px; margin-top: 20px;">'
        f"✗ {message}</div>"
    ), 400
