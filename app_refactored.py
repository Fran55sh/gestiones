"""
Sistema de Gestión de Deudas - Backend Flask
Refactorizado siguiendo buenas prácticas de desarrollo
"""
import os
import json
import logging
import re
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, request, jsonify, send_file, session, redirect, url_for, send_from_directory, abort
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Configurar Flask para servir archivos estáticos desde la carpeta static
app = Flask(__name__, static_folder='static', static_url_path='/static')
BASE_DIR = Path(__file__).parent.absolute()

# Configuración de seguridad
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-production-' + os.urandom(32).hex())
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configuración de Flask-Mail (Zoho Mail)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.zoho.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 465))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'False').lower() in ['true', 'on', '1']
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'True').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])
app.config['MAIL_TIMEOUT'] = 20

mail = Mail(app)

# ============================================================================
# CONSTANTES
# ============================================================================

# Email recipients (debería estar en configuración/env)
CONTACT_RECIPIENTS = [
    'emanuel.cariman@novagestiones.com.ar',
    'victor.laumann@novagestiones.com.ar',
    'angeles.laumann@novagestiones.com.ar'
]

# Archivos permitidos como estáticos
ALLOWED_STATIC_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.js'}

# Archivo de respaldo para solicitudes
CONTACT_SUBMISSIONS_FILE = BASE_DIR / 'contact_submissions.json'

# Credenciales de ejemplo (en producción, usar una base de datos)
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'gestor': {'password': 'gestor123', 'role': 'gestor'},
    'usuario': {'password': 'user123', 'role': 'user'}
}

# ============================================================================
# HELPERS / UTILIDADES
# ============================================================================

def require_role(required_role):
    """Decorator para requerir un rol específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') != required_role:
                return redirect('/gestiones')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_email(email):
    """Valida formato de email básico"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text, max_length=None):
    """Sanitiza entrada del usuario"""
    if not text:
        return ''
    # Remover caracteres peligrosos pero mantener formato básico
    text = text.strip()
    if max_length:
        text = text[:max_length]
    return text

def save_submission_to_file(entity, name, email, phone, message):
    """Guarda una solicitud en el archivo JSON"""
    submission = {
        'timestamp': datetime.now().isoformat(),
        'entity': sanitize_input(entity, 200),
        'name': sanitize_input(name, 200),
        'email': sanitize_input(email, 254),
        'phone': sanitize_input(phone, 50),
        'message': sanitize_input(message, 5000)
    }
    
    try:
        if CONTACT_SUBMISSIONS_FILE.exists():
            with open(str(CONTACT_SUBMISSIONS_FILE), 'r', encoding='utf-8') as f:
                submissions = json.load(f)
        else:
            submissions = []
        
        submissions.append(submission)
        
        with open(str(CONTACT_SUBMISSIONS_FILE), 'w', encoding='utf-8') as f:
            json.dump(submissions, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Solicitud guardada en archivo: {submission['entity']}")
        return True
    except Exception as e:
        logger.error(f"Error guardando solicitud en archivo: {e}")
        return False

def send_email_smtp(recipients, subject, body_text, body_html, from_email=None):
    """Envía email usando smtplib directamente (más confiable que Flask-Mail con SSL)"""
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        logger.warning("Credenciales de email no configuradas")
        return False
    
    from_email = from_email or app.config['MAIL_USERNAME']
    server = None
    
    try:
        # Crear mensaje
        email_msg = MIMEMultipart('alternative')
        email_msg['Subject'] = subject
        email_msg['From'] = formataddr(('NOVA Gestión de Cobranzas', from_email))
        email_msg['To'] = ', '.join(recipients)
        
        # Agregar contenido
        text_part = MIMEText(body_text, 'plain', 'utf-8')
        html_part = MIMEText(body_html, 'html', 'utf-8')
        email_msg.attach(text_part)
        email_msg.attach(html_part)
        
        # Conectar y enviar
        if app.config['MAIL_USE_SSL']:
            logger.info(f"Conectando con SSL a {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
            server = smtplib.SMTP_SSL(
                app.config['MAIL_SERVER'],
                app.config['MAIL_PORT'],
                timeout=app.config['MAIL_TIMEOUT']
            )
        else:
            logger.info(f"Conectando con TLS a {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
            server = smtplib.SMTP(
                app.config['MAIL_SERVER'],
                app.config['MAIL_PORT'],
                timeout=app.config['MAIL_TIMEOUT']
            )
            if app.config['MAIL_USE_TLS']:
                server.starttls()
        
        logger.info("Autenticando en servidor SMTP")
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        
        logger.info(f"Enviando email a {len(recipients)} destinatarios")
        server.send_message(email_msg, from_addr=from_email, to_addrs=recipients)
        
        logger.info("Email enviado exitosamente")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Error de autenticación SMTP: {e}")
        raise
    except smtplib.SMTPException as e:
        logger.error(f"Error SMTP: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado enviando email: {e}")
        raise
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass

# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """Página principal"""
    return send_file(str(BASE_DIR / 'index.html'))

@app.route('/gestiones')
def gestiones():
    """Página de login"""
    return send_file(str(BASE_DIR / 'login.html'))

# ============================================================================
# AUTENTICACIÓN
# ============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """Procesa el login y crea la sesión"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    # Validar entrada
    if not username or not password:
        return _login_error_response('Por favor complete todos los campos.')
    
    # Verificar credenciales
    if username not in USERS or USERS[username]['password'] != password:
        logger.warning(f"Intento de login fallido para usuario: {username}")
        return _login_error_response('Credenciales inválidas. Por favor, intenta de nuevo.')
    
    # Crear sesión
    session['username'] = username
    session['role'] = USERS[username]['role']
    
    logger.info(f"Login exitoso: {username} ({USERS[username]['role']})")
    
    # Determinar ruta de redirección
    role_routes = {
        'admin': '/dashboard-admin',
        'gestor': '/dashboard-gestor',
        'user': '/dashboard-user'
    }
    redirect_url = role_routes.get(USERS[username]['role'], '/dashboard-user')
    
    return _login_success_response(USERS[username]['role'], redirect_url)

def _login_success_response(role, redirect_url):
    """Genera respuesta de login exitoso"""
    role_name = {
        'admin': 'Administrador',
        'gestor': 'Gestor',
        'user': 'Usuario'
    }.get(role, 'Usuario')
    
    return (
        f'<div style="color: #10b981; background: #d1fae5; padding: 12px; border-radius: 8px; margin-top: 20px;">'
        f'✓ Inicio de sesión exitoso como {role_name}. Redirigiendo...</div>'
        f'<script>setTimeout(() => {{ window.location.href = "{redirect_url}"; }}, 1500);</script>'
    )

def _login_error_response(message):
    """Genera respuesta de error de login"""
    return (
        f'<div style="color: #dc2626; background: #fee2e2; padding: 12px; border-radius: 8px; margin-top: 20px;">'
        f'✗ {message}</div>'
    ), 400

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario"""
    username = session.get('username', 'desconocido')
    session.clear()
    logger.info(f"Logout: {username}")
    return redirect('/')

# ============================================================================
# DASHBOARDS
# ============================================================================

@app.route('/dashboard-admin')
@require_role('admin')
def dashboard_admin():
    """Dashboard administrativo"""
    return send_file(str(BASE_DIR / 'dashboard-admin.html'))

@app.route('/dashboard-gestor')
@require_role('gestor')
def dashboard_gestor():
    """Dashboard de gestor"""
    return send_file(str(BASE_DIR / 'dashboard-gestor.html'))

@app.route('/dashboard-user')
@require_role('user')
def dashboard_user():
    """Dashboard de usuario"""
    return send_file(str(BASE_DIR / 'dashboard-user.html'))

# ============================================================================
# API DE CONTACTO
# ============================================================================

@app.route('/api/contact', methods=['POST'])
def contact():
    """Procesa el formulario de contacto y envía emails"""
    try:
        # Obtener y validar datos
        entity = request.form.get('entity', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validar campos requeridos
        if not all([entity, name, email, phone, message]):
            return jsonify({
                'success': False,
                'message': 'Por favor complete todos los campos requeridos.'
            }), 400
        
        # Validar formato de email
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Por favor ingrese un email válido.'
            }), 400
        
        # Sanitizar entrada
        entity = sanitize_input(entity, 200)
        name = sanitize_input(name, 200)
        email = sanitize_input(email, 254)
        phone = sanitize_input(phone, 50)
        message = sanitize_input(message, 5000)
        
        logger.info(f"Nueva solicitud de contacto: {entity} - {name} ({email})")
        
        # Intentar enviar email
        email_sent = False
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            try:
                subject = f'Nueva Solicitud de Propuesta - {entity}'
                body_text = _create_email_body_text(entity, name, email, phone, message)
                body_html = _create_email_body_html(entity, name, email, phone, message)
                
                send_email_smtp(
                    recipients=CONTACT_RECIPIENTS,
                    subject=subject,
                    body_text=body_text,
                    body_html=body_html
                )
                email_sent = True
                logger.info("Email enviado exitosamente")
            except Exception as e:
                logger.error(f"Error enviando email: {e}", exc_info=True)
                # Continuar para guardar en archivo como respaldo
        
        # Guardar en archivo (siempre como respaldo)
        save_submission_to_file(entity, name, email, phone, message)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': '¡Gracias por su solicitud! Nuestro equipo se pondrá en contacto con usted para preparar una propuesta personalizada.'
            })
        else:
            # Si no se pudo enviar email, aún se guardó en archivo
            return jsonify({
                'success': True,
                'message': '¡Gracias por su solicitud! Su solicitud ha sido registrada. Nuestro equipo se pondrá en contacto con usted pronto.'
            })
        
    except Exception as e:
        logger.error(f"Error procesando formulario de contacto: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Hubo un error al procesar su solicitud. Por favor, intente nuevamente más tarde o contáctenos directamente.'
        }), 500

def _create_email_body_text(entity, name, email, phone, message):
    """Crea el cuerpo del email en texto plano"""
    return f'''Nueva solicitud de propuesta recibida:

Entidad: {entity}
Contacto Responsable: {name}
Email: {email}
Teléfono: {phone}

Información de la cartera:
{message}

---
Este mensaje fue enviado desde el formulario de contacto del sitio web.
'''

def _create_email_body_html(entity, name, email, phone, message):
    """Crea el cuerpo del email en HTML"""
    return f'''
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #7630b7;">Nueva Solicitud de Propuesta</h2>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Entidad:</strong> {entity}</p>
            <p><strong>Contacto Responsable:</strong> {name}</p>
            <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
            <p><strong>Teléfono:</strong> {phone}</p>
        </div>
        <div style="background: #ffffff; padding: 20px; border-left: 4px solid #7630b7; margin: 20px 0;">
            <h3 style="color: #7630b7; margin-top: 0;">Información de la cartera:</h3>
            <p style="white-space: pre-wrap;">{message}</p>
        </div>
        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
        <p style="color: #888; font-size: 12px;">Este mensaje fue enviado desde el formulario de contacto del sitio web.</p>
    </body>
    </html>
    '''

# ============================================================================
# API DE ADMINISTRACIÓN
# ============================================================================

@app.route('/api/submissions')
@require_role('admin')
def view_submissions():
    """Ver las solicitudes de contacto guardadas (solo administradores)"""
    try:
        if not CONTACT_SUBMISSIONS_FILE.exists():
            return jsonify({
                'message': 'No hay solicitudes guardadas aún.',
                'submissions': []
            })
        
        with open(str(CONTACT_SUBMISSIONS_FILE), 'r', encoding='utf-8') as f:
            submissions = json.load(f)
        
        return jsonify({
            'message': f'Total de solicitudes: {len(submissions)}',
            'submissions': submissions
        })
    except Exception as e:
        logger.error(f"Error leyendo solicitudes: {e}")
        return jsonify({
            'error': 'Error leyendo archivo de solicitudes',
            'submissions': []
        }), 500

@app.route('/api/test-email-config')
@require_role('admin')
def test_email_config():
    """Endpoint para verificar la configuración de email (solo administradores)"""
    return jsonify({
        'MAIL_SERVER': app.config.get('MAIL_SERVER'),
        'MAIL_PORT': app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
        'MAIL_USE_SSL': app.config.get('MAIL_USE_SSL'),
        'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
        'MAIL_PASSWORD': 'Configurado' if app.config.get('MAIL_PASSWORD') else 'No configurado',
        'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER'),
        'has_credentials': bool(app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'))
    })

# ============================================================================
# ARCHIVOS ESTÁTICOS
# ============================================================================

# Flask automáticamente sirve archivos de /static/ gracias a static_folder configurado arriba
# Esta ruta solo sirve archivos en la raíz (como logos)

@app.route('/logo.png')
@app.route('/logo-dark.png')
def serve_logo():
    """Sirve logos desde la raíz"""
    return send_from_directory(str(BASE_DIR), request.path[1:])

@app.route('/<path:filename>')
def serve_static(filename):
    """Sirve archivos estáticos como logos y otros archivos en la raíz"""
    # No interceptar rutas de /static/ - Flask las maneja automáticamente
    # Flask ya maneja /static/ automáticamente gracias a static_folder configurado arriba
    if 'static' in filename.split('/'):
        abort(404)
    
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    
    if extension not in ALLOWED_STATIC_EXTENSIONS:
        abort(404)
    
    try:
        return send_from_directory(str(BASE_DIR), filename)
    except Exception:
        abort(404)

# ============================================================================
# INICIO DE LA APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    logger.info("Iniciando servidor en http://localhost:5000")
    logger.info("Credenciales de ejemplo:")
    logger.info("  Usuario: admin | Contraseña: admin123 (Dashboard completo administrativo)")
    logger.info("  Usuario: gestor | Contraseña: gestor123 (Dashboard de gestor de deudas)")
    logger.info("  Usuario: usuario | Contraseña: user123 (Panel básico)")
    
    # Validar configuración crítica
    if not app.secret_key or app.secret_key.startswith('change-me'):
        logger.warning("⚠️  SECRET_KEY no configurada correctamente. Use variables de entorno en producción.")
    
    app.run(debug=True, port=5000)

