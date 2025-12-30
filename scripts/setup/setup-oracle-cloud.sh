#!/bin/bash
#
# Script de configuración automática para Oracle Cloud
# Uso: sudo ./setup-oracle-cloud.sh [develop|production]
#

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar argumentos
if [ "$#" -ne 1 ]; then
    log_error "Uso: $0 [develop|production]"
    exit 1
fi

ENVIRONMENT=$1
if [ "$ENVIRONMENT" != "develop" ] && [ "$ENVIRONMENT" != "production" ]; then
    log_error "Ambiente debe ser 'develop' o 'production'"
    exit 1
fi

# Configuración según ambiente
if [ "$ENVIRONMENT" == "develop" ]; then
    PROJECT_DIR="/home/ubuntu/gestiones"
    SERVICE_NAME="gestiones-develop"
    PORT="8000"
    BRANCH="develop"
else
    PROJECT_DIR="/home/ubuntu/gestiones"
    SERVICE_NAME="gestiones-prod"
    PORT="8001"
    BRANCH="main"
fi

log_info "Configurando ambiente: $ENVIRONMENT"
log_info "Directorio: $PROJECT_DIR"
log_info "Puerto: $PORT"
log_info "Rama: $BRANCH"

# 1. Actualizar sistema
log_info "Actualizando sistema..."
apt update
apt upgrade -y

# 2. Instalar dependencias del sistema
log_info "Instalando dependencias del sistema..."
apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    nginx \
    postgresql-client \
    curl \
    ufw \
    fail2ban

# 3. Configurar firewall
log_info "Configurando firewall..."
ufw --force enable
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow $PORT
log_info "Firewall configurado"

# 4. Crear directorio del proyecto
log_info "Creando directorio del proyecto..."
mkdir -p $PROJECT_DIR
chown ubuntu:ubuntu $PROJECT_DIR

# 5. Pedir URL del repositorio
read -p "Ingresa la URL del repositorio (https://github.com/usuario/gestiones.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    log_error "URL del repositorio es requerida"
    exit 1
fi

# 6. Clonar repositorio (como usuario ubuntu)
log_info "Clonando repositorio..."
su - ubuntu -c "
    if [ -d $PROJECT_DIR/.git ]; then
        cd $PROJECT_DIR
        git fetch origin
        git checkout $BRANCH
        git pull origin $BRANCH
    else
        git clone $REPO_URL $PROJECT_DIR
        cd $PROJECT_DIR
        git checkout $BRANCH
    fi
"

# 7. Crear virtual environment
log_info "Creando virtual environment..."
su - ubuntu -c "
    cd $PROJECT_DIR
    python3.11 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
"

# 8. Crear archivo .env
log_info "Creando archivo .env..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cat > "$PROJECT_DIR/.env" << EOF
# Flask
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=$ENVIRONMENT

# Database
DATABASE_URL=postgresql://usuario:password@localhost:5432/gestiones_$ENVIRONMENT

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Application
DEBUG=False
TESTING=False
EOF
    chown ubuntu:ubuntu "$PROJECT_DIR/.env"
    log_warn "Archivo .env creado. ¡EDÍTALO con tus credenciales reales!"
else
    log_info "Archivo .env ya existe, saltando..."
fi

# 9. Crear servicio systemd
log_info "Creando servicio systemd..."
cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=Gestiones MVP - ${ENVIRONMENT^}
After=network.target postgresql.service

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
    --workers 4 \\
    --worker-class gthread \\
    --threads 2 \\
    --bind 0.0.0.0:$PORT \\
    --access-logfile /var/log/$SERVICE_NAME-access.log \\
    --error-logfile /var/log/$SERVICE_NAME-error.log \\
    --log-level info \\
    app.wsgi:app

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

# 10. Configurar permisos sudo
log_info "Configurando permisos sudo..."
cat > "/etc/sudoers.d/$SERVICE_NAME" << EOF
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart $SERVICE_NAME
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl status $SERVICE_NAME
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl stop $SERVICE_NAME
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl start $SERVICE_NAME
EOF
chmod 0440 "/etc/sudoers.d/$SERVICE_NAME"

# 11. Crear archivos de log
log_info "Creando archivos de log..."
touch "/var/log/$SERVICE_NAME-access.log"
touch "/var/log/$SERVICE_NAME-error.log"
chown ubuntu:ubuntu "/var/log/$SERVICE_NAME-access.log"
chown ubuntu:ubuntu "/var/log/$SERVICE_NAME-error.log"

# 12. Configurar Nginx
log_info "Configurando Nginx..."
read -p "¿Tienes un dominio para este ambiente? (déjalo vacío para usar solo IP): " DOMAIN

if [ -z "$DOMAIN" ]; then
    SERVER_NAME="_"
else
    SERVER_NAME="$DOMAIN"
fi

cat > "/etc/nginx/sites-available/$SERVICE_NAME" << EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $PROJECT_DIR/static;
        expires 30d;
    }

    location /healthz {
        proxy_pass http://127.0.0.1:$PORT/healthz;
        access_log off;
    }
}
EOF

# Habilitar sitio
ln -sf "/etc/nginx/sites-available/$SERVICE_NAME" "/etc/nginx/sites-enabled/"
nginx -t
systemctl restart nginx

# 13. Habilitar y arrancar servicio
log_info "Habilitando y arrancando servicio..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# 14. Esperar que arranque
sleep 5

# 15. Verificar estado
log_info "Verificando estado del servicio..."
if systemctl is-active --quiet $SERVICE_NAME; then
    log_info "✅ Servicio $SERVICE_NAME está activo"
else
    log_error "❌ Servicio $SERVICE_NAME falló al iniciar"
    log_info "Ver logs con: sudo journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

# 16. Configurar SSL (opcional)
if [ ! -z "$DOMAIN" ]; then
    read -p "¿Deseas configurar SSL con Let's Encrypt? (y/n): " SETUP_SSL
    if [ "$SETUP_SSL" == "y" ]; then
        log_info "Instalando Certbot..."
        apt install -y certbot python3-certbot-nginx
        certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || log_warn "SSL setup falló, hazlo manualmente más tarde"
    fi
fi

# 17. Resumen final
echo ""
echo "================================================"
log_info "✅ Configuración completada!"
echo "================================================"
echo ""
log_info "Ambiente: $ENVIRONMENT"
log_info "Servicio: $SERVICE_NAME"
log_info "Puerto: $PORT"
log_info "Directorio: $PROJECT_DIR"
echo ""
log_info "Próximos pasos:"
echo "  1. Edita el archivo .env con tus credenciales:"
echo "     nano $PROJECT_DIR/.env"
echo ""
echo "  2. Configura la base de datos:"
echo "     sudo -u postgres psql"
echo "     CREATE DATABASE gestiones_$ENVIRONMENT;"
echo "     CREATE USER gestor WITH PASSWORD 'password';"
echo "     GRANT ALL PRIVILEGES ON DATABASE gestiones_$ENVIRONMENT TO gestor;"
echo ""
echo "  3. Ejecuta las migraciones:"
echo "     cd $PROJECT_DIR"
echo "     source venv/bin/activate"
echo "     alembic upgrade head"
echo ""
echo "  4. Reinicia el servicio:"
echo "     sudo systemctl restart $SERVICE_NAME"
echo ""
echo "  5. Verifica que funcione:"
echo "     curl http://localhost:$PORT/healthz"
echo ""
log_info "Comandos útiles:"
echo "  - Ver logs: sudo journalctl -u $SERVICE_NAME -f"
echo "  - Estado: sudo systemctl status $SERVICE_NAME"
echo "  - Reiniciar: sudo systemctl restart $SERVICE_NAME"
echo ""
if [ ! -z "$DOMAIN" ]; then
    log_info "Tu aplicación estará disponible en: http://$DOMAIN"
else
    log_info "Tu aplicación estará disponible en: http://$(curl -s ifconfig.me):$PORT"
fi
echo "================================================"

