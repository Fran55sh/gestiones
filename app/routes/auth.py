import logging
from flask import Blueprint, request, session, redirect
from flask import current_app as app
from werkzeug.security import check_password_hash

from ..utils.exceptions import AuthenticationError, ValidationError

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__)


@bp.route('/api/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validar entrada
        if not username:
            return _login_error_response('El nombre de usuario es requerido')
        if not password:
            return _login_error_response('La contraseña es requerida')

        logger.info(f"Intento de login para usuario: {username}")
        users = app.config.get('USERS', {})
        
        if not users:
            logger.error("Configuración de usuarios no encontrada")
            return _login_error_response('Error de configuración del sistema. Por favor, contacte al administrador.')
        
        if username not in users:
            logger.warning(f"Usuario {username} no encontrado")
            return _login_error_response('Credenciales inválidas. Por favor, intenta de nuevo.')
        
        # Verificar contraseña
        user_data = users[username]
        if 'password_hash' not in user_data:
            logger.error(f"Usuario {username} no tiene password_hash configurado")
            return _login_error_response('Error de configuración del sistema. Por favor, contacte al administrador.')
        
        if not check_password_hash(user_data['password_hash'], password):
            logger.warning(f"Contraseña incorrecta para usuario {username}")
            return _login_error_response('Credenciales inválidas. Por favor, intenta de nuevo.')
        
        # Login exitoso
        logger.info(f"Login exitoso para usuario: {username} (rol: {user_data.get('role')})")
        
        try:
            session.clear()
            session.permanent = True
            session['username'] = username
            session['role'] = user_data.get('role', 'user')
        except Exception as e:
            logger.error(f"Error al establecer sesión: {e}", exc_info=True)
            return _login_error_response('Error al iniciar sesión. Por favor, intenta de nuevo.')

        role_routes = {'admin': '/dashboard-admin', 'gestor': '/dashboard-gestor', 'user': '/dashboard-user'}
        redirect_url = role_routes.get(user_data.get('role', 'user'), '/dashboard-user')
        return _login_success_response(user_data.get('role', 'user'), redirect_url)
        
    except Exception as e:
        logger.error(f"Error inesperado en login: {e}", exc_info=True)
        return _login_error_response('Error inesperado al iniciar sesión. Por favor, intenta de nuevo.')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')


def _login_success_response(role, redirect_url):
    role_name = {'admin': 'Administrador', 'gestor': 'Gestor', 'user': 'Usuario'}.get(role, 'Usuario')
    
    # Respuesta HTML para mostrar mensaje de éxito
    html_response = (
        f'<div style="color: #10b981; background: #d1fae5; padding: 12px; border-radius: 8px; margin-top: 20px;">'
        f'✓ Inicio de sesión exitoso como {role_name}. Redirigiendo...</div>'
    )
    
    # Crear respuesta y agregar header HX-Redirect
    from flask import make_response
    response = make_response(html_response)
    response.headers['HX-Redirect'] = redirect_url
    return response


def _login_error_response(message):
    """Formatea respuesta de error para HTMX."""
    return (
        f'<div style="color: #dc2626; background: #fee2e2; padding: 12px; border-radius: 8px; margin-top: 20px;">'
        f'✗ {message}</div>'
    ), 400
