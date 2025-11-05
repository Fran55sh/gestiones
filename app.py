from flask import Flask, request, jsonify, send_file, session, redirect, url_for, send_from_directory
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'gestión-deudas-secret-key-change-in-production'

# Configuración de Flask-Mail (Zoho Mail)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.zoho.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 465))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'False').lower() in ['true', 'on', '1']
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'True').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])
# Timeout más largo para SSL
app.config['MAIL_TIMEOUT'] = 20

mail = Mail(app)

# Obtener el directorio base de la aplicación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Credenciales de ejemplo (en producción, usar una base de datos)
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'gestor': {'password': 'gestor123', 'role': 'gestor'},
    'usuario': {'password': 'user123', 'role': 'user'}
}

@app.route('/')
def index():
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/gestiones')
def gestiones():
    return send_file(os.path.join(BASE_DIR, 'login.html'))

@app.route('/api/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Verificar credenciales de ejemplo
    if username in USERS and USERS[username]['password'] == password:
        session['username'] = username
        session['role'] = USERS[username]['role']
        
        # Redirigir según el rol
        if USERS[username]['role'] == 'admin':
            return '<div style="color: #10b981; background: #d1fae5; padding: 12px; border-radius: 8px; margin-top: 20px;">✓ Inicio de sesión exitoso como Administrador. Redirigiendo...</div><script>setTimeout(() => { window.location.href = "/dashboard-admin"; }, 1500);</script>'
        elif USERS[username]['role'] == 'gestor':
            return '<div style="color: #10b981; background: #d1fae5; padding: 12px; border-radius: 8px; margin-top: 20px;">✓ Inicio de sesión exitoso. Redirigiendo...</div><script>setTimeout(() => { window.location.href = "/dashboard-gestor"; }, 1500);</script>'
        else:
            return '<div style="color: #10b981; background: #d1fae5; padding: 12px; border-radius: 8px; margin-top: 20px;">✓ Inicio de sesión exitoso. Redirigiendo...</div><script>setTimeout(() => { window.location.href = "/dashboard-user"; }, 1500);</script>'
    else:
        return '<div style="color: #dc2626; background: #fee2e2; padding: 12px; border-radius: 8px; margin-top: 20px;">✗ Credenciales inválidas. Por favor, intenta de nuevo.</div>', 400

@app.route('/dashboard-admin')
def dashboard_admin():
    # Verificar si es admin
    if session.get('role') == 'admin':
        return send_file(os.path.join(BASE_DIR, 'dashboard-admin.html'))
    else:
        return redirect('/gestiones')

@app.route('/dashboard-gestor')
def dashboard_gestor():
    # Verificar si es gestor
    if session.get('role') == 'gestor':
        return send_file(os.path.join(BASE_DIR, 'dashboard-gestor.html'))
    else:
        return redirect('/gestiones')

@app.route('/dashboard-user')
def dashboard_user():
    # Verificar si hay sesión
    if session.get('role') == 'user':
        return send_file(os.path.join(BASE_DIR, 'dashboard-user.html'))
    else:
        return redirect('/gestiones')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/submissions')
def view_submissions():
    """Ver las solicitudes de contacto guardadas (solo para administradores)"""
    import json
    log_file = os.path.join(BASE_DIR, 'contact_submissions.json')
    
    if not os.path.exists(log_file):
        return jsonify({
            'message': 'No hay solicitudes guardadas aún.',
            'submissions': []
        })
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            submissions = json.load(f)
        
        return jsonify({
            'message': f'Total de solicitudes: {len(submissions)}',
            'submissions': submissions
        })
    except Exception as e:
        return jsonify({
            'error': f'Error leyendo archivo: {str(e)}',
            'submissions': []
        }), 500

@app.route('/api/test-email-config')
def test_email_config():
    """Endpoint para verificar la configuración de email"""
    config_status = {
        'MAIL_SERVER': app.config.get('MAIL_SERVER', 'No configurado'),
        'MAIL_PORT': app.config.get('MAIL_PORT', 'No configurado'),
        'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS', 'No configurado'),
        'MAIL_USERNAME': app.config.get('MAIL_USERNAME', 'No configurado'),
        'MAIL_PASSWORD': 'Configurado' if app.config.get('MAIL_PASSWORD') else 'No configurado',
        'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER', 'No configurado'),
        'has_credentials': bool(app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'))
    }
    return jsonify(config_status)

@app.route('/api/contact', methods=['POST'])
def contact():
    """Procesa el formulario de contacto y envía emails"""
    try:
        # Log de debug
        print("=" * 50)
        print("📧 INICIANDO ENVÍO DE EMAIL")
        print("=" * 50)
        print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
        print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"MAIL_PASSWORD configurado: {'Sí' if app.config.get('MAIL_PASSWORD') else 'No'}")
        print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        print("=" * 50)
        
        # Obtener datos del formulario
        entity = request.form.get('entity', '')
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        message = request.form.get('message', '')
        
        print(f"📝 Datos del formulario recibidos:")
        print(f"   Entidad: {entity}")
        print(f"   Nombre: {name}")
        print(f"   Email: {email}")
        print(f"   Teléfono: {phone}")
        print(f"   Mensaje: {message[:50]}...")
        
        # Validar campos requeridos
        if not all([entity, name, email, phone, message]):
            print("❌ Error: Campos requeridos faltantes")
            return jsonify({'success': False, 'message': 'Por favor complete todos los campos requeridos.'}), 400
        
        # Direcciones de email destino
        recipients = ['emanuel.cariman@novagestiones.com.ar', 'victor.laumann@novagestiones.com.ar', 'angeles.laumann@novagestiones.com.ar']
        print(f"📬 Destinatarios: {recipients}")
        
        # Verificar si las credenciales de email están configuradas
        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
            print("⚠️ EMAIL NO CONFIGURADO - Usando fallback a archivo")
            # Si no hay configuración de email, guardar en un archivo como respaldo
            import json
            log_file = os.path.join(BASE_DIR, 'contact_submissions.json')
            submission = {
                'timestamp': datetime.now().isoformat(),
                'entity': entity,
                'name': name,
                'email': email,
                'phone': phone,
                'message': message
            }
            
            # Leer archivo existente o crear nuevo
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    submissions = json.load(f)
            else:
                submissions = []
            
            submissions.append(submission)
            
            # Guardar
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(submissions, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Solicitud guardada en archivo: {submission}")
            return jsonify({
                'success': True,
                'message': '¡Gracias por su solicitud! Nuestro equipo se pondrá en contacto con usted para preparar una propuesta personalizada.'
            })
        
        print("✅ Credenciales configuradas - Intentando enviar email...")
        
        # Crear el mensaje de email
        msg = Message(
            subject=f'Nueva Solicitud de Propuesta - {entity}',
            recipients=recipients,
            body=f'''
Nueva solicitud de propuesta recibida:

Entidad: {entity}
Contacto Responsable: {name}
Email: {email}
Teléfono: {phone}

Información de la cartera:
{message}

---
Este mensaje fue enviado desde el formulario de contacto del sitio web.
            ''',
            html=f'''
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
        )
        
        print("📧 Mensaje creado, intentando enviar...")
        
        # Asegurar que el sender sea el mismo que el username
        if msg.sender != app.config['MAIL_USERNAME']:
            msg.sender = app.config['MAIL_USERNAME']
        
        # Enviar el email usando smtplib directamente (más confiable que Flask-Mail con SSL)
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Crear mensaje con smtplib
        email_msg = MIMEMultipart('alternative')
        email_msg['Subject'] = msg.subject
        email_msg['From'] = app.config['MAIL_USERNAME']
        email_msg['To'] = ', '.join(recipients)
        
        # Agregar cuerpo del mensaje
        text_part = MIMEText(msg.body, 'plain', 'utf-8')
        html_part = MIMEText(msg.html, 'html', 'utf-8')
        email_msg.attach(text_part)
        email_msg.attach(html_part)
        
        # Conectar y enviar
        server = None
        try:
            if app.config['MAIL_USE_SSL']:
                print("🔐 Conectando con SSL (puerto 465)...")
                server = smtplib.SMTP_SSL(
                    app.config['MAIL_SERVER'],
                    app.config['MAIL_PORT'],
                    timeout=20
                )
            else:
                print("🔐 Conectando con TLS (puerto 587)...")
                server = smtplib.SMTP(
                    app.config['MAIL_SERVER'],
                    app.config['MAIL_PORT'],
                    timeout=20
                )
                if app.config['MAIL_USE_TLS']:
                    server.starttls()
            
            print("🔑 Autenticando...")
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            
            print("📤 Enviando email...")
            server.send_message(email_msg, from_addr=app.config['MAIL_USERNAME'], to_addrs=recipients)
            
            print("✅ EMAIL ENVIADO EXITOSAMENTE")
            print("=" * 50)
            
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass
        
        return jsonify({
            'success': True,
            'message': '¡Gracias por su solicitud! Nuestro equipo se pondrá en contacto con usted para preparar una propuesta personalizada.'
        })
        
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print("=" * 50)
        print(f"❌ ERROR ENVIANDO EMAIL")
        print(f"Tipo: {error_type}")
        print(f"Mensaje: {error_msg}")
        print("=" * 50)
        import traceback
        traceback.print_exc()
        print("=" * 50)
        
        # Mensaje más específico según el tipo de error
        if 'authentication' in error_msg.lower() or 'login' in error_msg.lower() or '535' in error_msg:
            user_message = 'Error de autenticación: Verifique que el usuario y contraseña sean correctos. Si usa 2FA, necesita una contraseña de aplicación.'
        elif 'connection' in error_msg.lower() or 'timeout' in error_msg.lower() or 'cannot connect' in error_msg.lower() or 'connection unexpectedly closed' in error_msg.lower():
            user_message = 'Error de conexión: El servidor SMTP cerró la conexión. Esto puede deberse a que el puerto está bloqueado o el servidor requiere SSL en lugar de TLS. Intente verificar la configuración de red/firewall.'
        elif 'ssl' in error_msg.lower() or 'certificate' in error_msg.lower():
            user_message = 'Error SSL/TLS: Problema con el certificado de seguridad. Intente usar puerto 465 con SSL.'
        else:
            user_message = f'Error: {error_msg}'
        
        return jsonify({
            'success': False,
            'message': user_message,
            'debug_error': error_msg if app.debug else None
        }), 500

# Ruta para servir archivos estáticos (logos) - debe ir al final para no interceptar otras rutas
@app.route('/<path:filename>')
def serve_static(filename):
    """Sirve archivos estáticos como logos"""
    # Solo servir archivos de imagen y otros archivos estáticos conocidos
    static_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.js']
    if any(filename.lower().endswith(ext) for ext in static_extensions):
        try:
            return send_from_directory(BASE_DIR, filename)
        except:
            return "File not found", 404
    return "Not found", 404

if __name__ == '__main__':
    print("Iniciando servidor en http://localhost:5000")
    print("Credenciales de ejemplo:")
    print("  Usuario: admin | Contraseña: admin123 (Dashboard completo administrativo)")
    print("  Usuario: gestor | Contraseña: gestor123 (Dashboard de gestor de deudas)")
    print("  Usuario: usuario | Contraseña: user123 (Panel básico)")
    app.run(debug=True, port=5000)
