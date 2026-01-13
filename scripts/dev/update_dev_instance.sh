#!/bin/bash
set -e

echo "🚀 Actualizando instancia de desarrollo..."

# Navegar al directorio del proyecto
cd /home/ubuntu/gestiones || cd ~/gestiones

# Detener contenedores
echo "🐳 Deteniendo contenedores..."
docker-compose -f config/docker/docker-compose.dev.yml down

# Rebuild de imágenes (sin cache para asegurar cambios)
echo "🔨 Reconstruyendo imágenes..."
docker-compose -f config/docker/docker-compose.dev.yml build --no-cache

# Iniciar contenedores
echo "🚀 Iniciando contenedores..."
docker-compose -f config/docker/docker-compose.dev.yml up -d

# Esperar a que el contenedor esté listo
echo "⏳ Esperando a que el contenedor esté listo..."
sleep 10

# Ejecutar migraciones de Alembic
echo "🔄 Ejecutando migraciones de base de datos..."
docker exec gestiones-mvp-dev alembic -c config/alembic.ini upgrade head || echo "⚠️  Migraciones ya aplicadas o error (puede ser normal)"

# Verificar estado
echo "📊 Estado de contenedores:"
docker ps | grep gestiones || echo "Contenedor no encontrado"

# Mostrar logs recientes
echo "📝 Logs recientes:"
docker-compose -f config/docker/docker-compose.dev.yml logs --tail=30

echo ""
echo "✅ Actualización completada!"
echo "🌐 Aplicación disponible en: http://localhost:5001"

