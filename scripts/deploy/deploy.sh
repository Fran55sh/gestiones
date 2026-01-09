#!/bin/bash
# Script de despliegue para Oracle Cloud
# Ejecutar en la instancia OCI después de clonar el repositorio

set -e  # Salir si hay algún error

echo "🚀 Iniciando despliegue en Oracle Cloud..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}Error: No se encuentra docker-compose.prod.yml${NC}"
    echo "Asegúrate de estar en el directorio del proyecto"
    exit 1
fi

# Verificar que existe .env.prod
if [ ! -f ".env.prod" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env.prod no encontrado${NC}"
    echo "Creando .env.prod desde env/prod.env.example..."
    if [ -f "env/prod.env.example" ]; then
        cp env/prod.env.example .env.prod
        echo -e "${RED}⚠️  IMPORTANTE: Edita .env.prod y configura todas las variables antes de continuar${NC}"
        exit 1
    else
        echo -e "${RED}Error: No se encuentra env/prod.env.example${NC}"
        exit 1
    fi
fi

# Verificar SECRET_KEY
if grep -q "GENERAR_UNA_CLAVE_SECRETA_FUERTE_AQUI" .env.prod || grep -q "dev-secret-key-cambia-esto" .env.prod; then
    echo -e "${RED}Error: Debes configurar SECRET_KEY en .env.prod${NC}"
    echo "Genera una con: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    exit 1
fi

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker compose -f docker-compose.prod.yml --project-name gestiones-prod down || true

# Construir y levantar contenedores
echo "🔨 Construyendo imagen Docker..."
docker compose -f docker-compose.prod.yml --project-name gestiones-prod --env-file .env.prod build --no-cache

echo "🚀 Iniciando aplicación..."
docker compose -f docker-compose.prod.yml --project-name gestiones-prod --env-file .env.prod up -d

# Esperar a que la aplicación esté lista
echo "⏳ Esperando a que la aplicación esté lista..."
sleep 10

# Verificar healthcheck
echo "🏥 Verificando healthcheck..."
if curl -f http://localhost:5000/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthcheck OK${NC}"
else
    echo -e "${YELLOW}⚠️  Healthcheck no responde aún, esperando...${NC}"
    sleep 5
fi

# Verificar estado
if docker compose -f docker-compose.prod.yml --project-name gestiones-prod ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Aplicación desplegada correctamente${NC}"
    echo ""
    echo "📊 Estado de contenedores:"
    docker compose -f docker-compose.prod.yml --project-name gestiones-prod ps
    echo ""
    echo "📝 Logs recientes:"
    docker compose -f docker-compose.prod.yml --project-name gestiones-prod logs --tail=20
else
    echo -e "${RED}❌ Error al iniciar la aplicación${NC}"
    echo "Revisa los logs con: docker compose -f docker-compose.prod.yml --project-name gestiones-prod logs"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Despliegue completado${NC}"
echo ""
echo "Comandos útiles:"
echo "  Ver logs: docker compose -f docker-compose.prod.yml --project-name gestiones-prod logs -f"
echo "  Reiniciar: docker compose -f docker-compose.prod.yml --project-name gestiones-prod restart"
echo "  Detener: docker compose -f docker-compose.prod.yml --project-name gestiones-prod down"
echo "  Healthcheck: curl http://localhost:5000/healthz"

