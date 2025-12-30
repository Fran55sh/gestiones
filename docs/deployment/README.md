# 📦 Deployment Documentation

Esta carpeta contiene toda la documentación relacionada con el deployment de la aplicación.

## 📑 Archivos

### `oracle-cloud-setup.md`
Guía completa paso a paso para configurar el deploy automático a Oracle Cloud:
- Configuración de secrets en GitHub
- Setup de instancias DEVELOP y PRODUCTION
- Configuración de systemd services
- Setup de Nginx como reverse proxy
- Configuración de SSL con Let's Encrypt
- Troubleshooting y comandos útiles

## 🚀 Workflows Disponibles

### Deploy to Develop
- **Archivo**: `.github/workflows/deploy-develop.yml`
- **Trigger**: Push a rama `develop`
- **Target**: Oracle Cloud instancia DEVELOP (puerto 5001)
- **Features**:
  - Tests automáticos antes de deploy
  - Deploy automático si tests pasan
  - Health check post-deployment

### Deploy to Production
- **Archivo**: `.github/workflows/deploy-production.yml`
- **Trigger**: Push a rama `main`
- **Target**: Oracle Cloud instancia PRODUCTION (puerto 5000)
- **Features**:
  - Tests automáticos antes de deploy
  - Backup automático antes de deploy
  - Deploy automático si tests pasan
  - Health check post-deployment
  - **Rollback automático si falla**

## 🛠️ Scripts de Setup

### `scripts/setup/setup-oracle-cloud.sh`
Script automatizado para configurar una instancia nueva de Oracle Cloud:

```bash
# Para instancia DEVELOP
sudo ./scripts/setup/setup-oracle-cloud.sh develop

# Para instancia PRODUCTION
sudo ./scripts/setup/setup-oracle-cloud.sh production
```

**Lo que hace:**
- Actualiza el sistema
- Instala todas las dependencias (Python, Nginx, PostgreSQL client, etc.)
- Configura firewall (UFW)
- Clona el repositorio
- Crea virtual environment
- Genera archivo .env con SECRET_KEY seguro
- Crea servicio systemd
- Configura Nginx como reverse proxy
- (Opcional) Configura SSL con Let's Encrypt

## 🎯 Quick Start

### 1. Configurar Secrets en GitHub
Ve a tu repo → Settings → Secrets → Actions → New secret

Necesitas configurar:
- `DEVELOP_HOST`, `DEVELOP_USER`, `DEVELOP_SSH_KEY`
- `PROD_HOST`, `PROD_USER`, `PROD_SSH_KEY`
- `DEVELOP_PATH` y `PROD_PATH` son opcionales (default: `/home/ubuntu/gestiones`)

Ver detalles en `oracle-cloud-setup.md`

### 2. Preparar Instancias

En cada instancia de Oracle Cloud, ejecuta:

```bash
# Descargar script
curl -O https://raw.githubusercontent.com/tu-usuario/gestiones/develop/scripts/setup/setup-oracle-cloud.sh

# Dar permisos de ejecución
chmod +x setup-oracle-cloud.sh

# Ejecutar (para develop o production)
sudo ./setup-oracle-cloud.sh develop
```

### 3. Configurar Base de Datos

```bash
# En cada instancia
sudo -u postgres psql
CREATE DATABASE gestiones_develop;  -- o gestiones_prod
CREATE USER gestor WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE gestiones_develop TO gestor;
\q
```

### 4. Editar .env

```bash
nano /home/ubuntu/gestiones/.env
```

Actualiza `DATABASE_URL` y otras variables necesarias.

### 5. Ejecutar Migraciones

```bash
cd /home/ubuntu/gestiones
source venv/bin/activate
alembic upgrade head
```

### 6. Reiniciar Servicio

```bash
sudo systemctl restart gestiones-develop  # o gestiones-prod según la instancia
```

### 7. ¡Deploy Automático Listo!

Ahora cada push activará el deploy automático:

```bash
# Deploy a DEVELOP
git push origin develop

# Deploy a PRODUCTION
git push origin main
```

## 📊 Monitoreo

### Ver Logs en Tiempo Real
```bash
# En la instancia
sudo journalctl -u gestiones-develop -f
```

### Verificar Estado
```bash
sudo systemctl status gestiones-develop
```

### Health Check
```bash
curl http://localhost:5001/healthz  # Para DEVELOP
curl http://localhost:5000/healthz  # Para PRODUCTION
```

## 🔒 Seguridad

El script de setup configura automáticamente:
- ✅ Firewall (UFW) con reglas básicas
- ✅ Permisos sudo restringidos para GitHub Actions
- ✅ Fail2ban para protección contra brute force
- ✅ SSH con autenticación por clave
- ✅ Variables de entorno en archivo .env (no en código)

## 📝 Notas

- Los workflows están configurados para usar `appleboy/ssh-action@v1.0.0`
- El puerto 5001 es para DEVELOP, 5000 para PRODUCTION
- Los backups se guardan en `$HOME/backups/` en producción
- Los logs se guardan en `/var/log/gestiones-*`
- Se usa Gunicorn con 4 workers y 2 threads por worker

## 🆘 Soporte

Si algo falla:
1. Revisa `oracle-cloud-setup.md` para troubleshooting
2. Verifica logs: `sudo journalctl -u gestiones-develop -n 100`
3. Verifica conexión SSH desde GitHub Actions
4. Verifica que los secrets estén correctamente configurados

## 🔗 Enlaces Útiles

- [GitHub Actions SSH Action](https://github.com/appleboy/ssh-action)
- [Oracle Cloud Documentation](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- [Gunicorn Deployment](https://docs.gunicorn.org/en/stable/deploy.html)
- [Nginx Configuration](https://nginx.org/en/docs/)

