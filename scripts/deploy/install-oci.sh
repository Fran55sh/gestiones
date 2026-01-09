# Script de Instalación Inicial para Oracle Cloud
# Ejecutar una sola vez en la instancia OCI

#!/bin/bash

set -e

echo "📦 Instalando dependencias en Oracle Cloud..."

# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Verificar Docker Compose (v2 incluido en Docker)
if ! docker compose version &> /dev/null; then
    echo "🐳 Docker Compose v2 debería estar incluido con Docker"
    echo "Si no funciona, instala manualmente desde: https://docs.docker.com/compose/install/"
fi

# Instalar Nginx
if ! command -v nginx &> /dev/null; then
    echo "🌐 Instalando Nginx..."
    sudo apt-get install -y nginx
fi

# Instalar Certbot (Let's Encrypt)
if ! command -v certbot &> /dev/null; then
    echo "🔒 Instalando Certbot..."
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Instalar fail2ban (seguridad SSH)
if ! command -v fail2ban &> /dev/null; then
    echo "🛡️  Instalando fail2ban..."
    sudo apt-get install -y fail2ban
fi

# Configurar firewall básico (UFW)
if ! command -v ufw &> /dev/null; then
    echo "🔥 Configurando firewall..."
    sudo apt-get install -y ufw
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
fi

echo "✅ Instalación completada"
echo ""
echo "⚠️  IMPORTANTE:"
echo "1. Reinicia la sesión SSH para que los cambios de grupo Docker surtan efecto"
echo "2. Configura el archivo .env.prod desde env/prod.env.example con tus credenciales"
echo "3. Configura Nginx con tu dominio (ver nginx.conf.example)"
echo "4. Ejecuta ./deploy.sh para desplegar la aplicación"

