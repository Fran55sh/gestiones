#!/bin/bash
# Script para verificar la conexión SSH antes de usar GitHub Actions
# Ejecutar localmente para verificar que todo está configurado correctamente

set -e

echo "🔍 Verificando configuración SSH..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que existe SSH key
if [ ! -f ~/.ssh/id_rsa ] && [ ! -f ~/.ssh/id_ed25519 ]; then
    echo -e "${RED}❌ No se encontró clave SSH${NC}"
    echo "Genera una clave SSH con: ssh-keygen -t ed25519 -C 'tu-email@ejemplo.com'"
    exit 1
fi

echo -e "${GREEN}✅ Clave SSH encontrada${NC}"

# Solicitar información
read -p "🔐 Ingresa el host de staging (SSH_HOST_DEV): " SSH_HOST_DEV
read -p "🔐 Ingresa el host de producción (SSH_HOST_PROD): " SSH_HOST_PROD
read -p "👤 Ingresa el usuario SSH (SSH_USER): " SSH_USER

echo ""
echo "🧪 Probando conexión a STAGING..."

# Probar conexión a staging
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST_DEV} "echo 'Conexión SSH exitosa"; then
    echo -e "${GREEN}✅ Conexión a STAGING exitosa${NC}"
    
    # Verificar directorio del proyecto
    if ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST_DEV} "[ -d ~/gestiones-mvp ] && echo 'existe' || echo 'no existe'"; then
        echo -e "${GREEN}✅ Directorio del proyecto existe en staging${NC}"
    else
        echo -e "${YELLOW}⚠️  Directorio ~/gestiones-mvp no existe en staging${NC}"
        echo "   Verifica la ruta correcta del proyecto"
    fi
else
    echo -e "${RED}❌ No se pudo conectar a STAGING${NC}"
    echo "   Verifica:"
    echo "   - Que la IP/hostname sea correcta"
    echo "   - Que el puerto 22 esté abierto en OCI Security List"
    echo "   - Que tu clave pública esté en el servidor: ssh-copy-id ${SSH_USER}@${SSH_HOST_DEV}"
fi

echo ""
echo "🧪 Probando conexión a PRODUCCIÓN..."

# Probar conexión a producción
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST_PROD} "echo 'Conexión SSH exitosa"; then
    echo -e "${GREEN}✅ Conexión a PRODUCCIÓN exitosa${NC}"
    
    # Verificar directorio del proyecto
    if ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST_PROD} "[ -d ~/gestiones-mvp ] && echo 'existe' || echo 'no existe'"; then
        echo -e "${GREEN}✅ Directorio del proyecto existe en producción${NC}"
    else
        echo -e "${YELLOW}⚠️  Directorio ~/gestiones-mvp no existe en producción${NC}"
        echo "   Verifica la ruta correcta del proyecto"
    fi
else
    echo -e "${RED}❌ No se pudo conectar a PRODUCCIÓN${NC}"
    echo "   Verifica:"
    echo "   - Que la IP/hostname sea correcta"
    echo "   - Que el puerto 22 esté abierto en OCI Security List"
    echo "   - Que tu clave pública esté en el servidor: ssh-copy-id ${SSH_USER}@${SSH_HOST_PROD}"
fi

echo ""
echo "📋 Resumen para GitHub Secrets:"
echo ""
echo "SSH_HOST_DEV = ${SSH_HOST_DEV}"
echo "SSH_HOST_PROD = ${SSH_HOST_PROD}"
echo "SSH_USER = ${SSH_USER}"
echo ""
echo "Para obtener tu clave SSH privada (SSH_KEY_DEV y SSH_KEY_PROD):"
if [ -f ~/.ssh/id_ed25519 ]; then
    echo "  cat ~/.ssh/id_ed25519"
elif [ -f ~/.ssh/id_rsa ]; then
    echo "  cat ~/.ssh/id_rsa"
fi
echo ""
echo "⚠️  IMPORTANTE: Copia TODO el contenido de la clave (incluyendo -----BEGIN y -----END)"

