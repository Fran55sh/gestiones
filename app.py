from flask import Flask, request, jsonify, send_file, session, redirect, url_for
from werkzeug.security import check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'gestión-deudas-secret-key-change-in-production'

# Credenciales de ejemplo (en producción, usar una base de datos)
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'gestor': {'password': 'gestor123', 'role': 'gestor'},
    'usuario': {'password': 'user123', 'role': 'user'}
}

@app.route('/')
def index():
    return send_file('login.html')

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
        return send_file('dashboard-admin.html')
    else:
        return redirect('/')

@app.route('/dashboard-gestor')
def dashboard_gestor():
    # Verificar si es gestor
    if session.get('role') == 'gestor':
        return send_file('dashboard-gestor.html')
    else:
        return redirect('/')

@app.route('/dashboard-user')
def dashboard_user():
    # Verificar si hay sesión
    if session.get('role') == 'user':
        return send_file('dashboard-user.html')
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("Iniciando servidor en http://localhost:5000")
    print("Credenciales de ejemplo:")
    print("  Usuario: admin | Contraseña: admin123 (Dashboard completo administrativo)")
    print("  Usuario: gestor | Contraseña: gestor123 (Dashboard de gestor de deudas)")
    print("  Usuario: usuario | Contraseña: user123 (Panel básico)")
    app.run(debug=True, port=5000)
