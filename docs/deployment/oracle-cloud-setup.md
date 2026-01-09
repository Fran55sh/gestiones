# 🚀 Deploy Automático a Oracle Cloud con Docker

Guía completa para configurar el deploy automático a las instancias de Oracle Cloud usando Docker Compose.

## 📋 Arquitectura

```
GitHub Actions
    ↓
┌─────────────────────┐
│   Push to develop   │ → Tests → Build Docker → Deploy → Oracle Cloud (Develop - :5001)
└─────────────────────┘

┌─────────────────────┐
│   Push to main      │ → Tests → Backup → Build Docker → Deploy → Oracle Cloud (Prod - :5000)
└─────────────────────┘
                                    ↓ (si falla)
                                Rollback 🔄
```

## 🐳 Stack Tecnológico

- **Containerización**: Docker + Docker Compose
- **Web Server**: Gunicorn (dentro del container)
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx (opcional)
- **Portabilidad**: 100% - funciona en cualquier cloud provider

## 🔐 Paso 1: Configurar Secrets en GitHub

Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Secrets para Instancia DEVELOP

| Secret Name | Descripción | Ejemplo |
|------------|-------------|---------|
| `DEVELOP_HOST` | IP o dominio de la instancia | `123.45.67.89` |
| `DEVELOP_USER` | Usuario SSH | `ubuntu` |
| `DEVELOP_SSH_KEY` | Clave privada SSH completa | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DEVELOP_PATH` | Ruta del proyecto (opcional) | `/home/ubuntu/gestiones` (default si no se especifica) |

### Secrets para Instancia PRODUCTION

| Secret Name | Descripción | Ejemplo |
|------------|-------------|---------|
| `PROD_HOST` | IP o dominio de la instancia | `98.76.54.32` |
| `PROD_USER` | Usuario SSH | `ubuntu` |
| `PROD_SSH_KEY` | Clave privada SSH completa | `-----BEGIN RSA PRIVATE KEY-----...` |
| `PROD_PATH` | Ruta del proyecto (opcional) | `/home/ubuntu/gestiones` (default si no se especifica) |

### Secrets Compartidos

| Secret Name | Descripción | Ejemplo |
|------------|-------------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Flask secret key | Genera con `python -c "import secrets; print(secrets.token_hex(32))"` |
| `REDIS_URL` | URL de Redis (opcional) | `redis://localhost:6379/0` |

## 🖥️ Paso 2: Configurar Instancias en Oracle Cloud

### 2.1 Preparar el Entorno

En **cada instancia**, ejecuta:

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo apt install docker-compose -y

# Instalar Git (si no está)
sudo apt install git -y

# Verificar instalación
docker --version
docker-compose --version

# IMPORTANTE: Salir y volver a entrar para que el grupo docker tome efecto
exit
# (volver a conectar por SSH)

# Crear directorio del proyecto (si no existe)
mkdir -p /home/ubuntu/gestiones
```

### 2.2 Clonar el Repositorio

```bash
cd /home/ubuntu
git clone https://github.com/tu-usuario/gestiones.git gestiones
cd gestiones

# Para instancia develop
git checkout develop

# Para instancia prod (en la otra instancia)
git checkout main
```

### 2.3 Configurar Variables de Entorno

```bash
# Crear archivo .env para development
nano /home/ubuntu/gestiones/.env.dev
```

Contenido del `.env.dev`:

```env
# Flask
SECRET_KEY=tu_secret_key_muy_seguro_aqui
FLASK_ENV=development
FLASK_DEBUG=1

# Database (SQLite para dev)
DATABASE_URL=sqlite:///./data/gestiones.db

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu@email.com
MAIL_PASSWORD=tu_password_app
MAIL_USE_TLS=true
MAIL_USE_SSL=false

# Application
DEBUG=False
TESTING=False
```

Para **producción**, crea `.env.prod`:

```bash
nano /home/ubuntu/gestiones/.env.prod
```

```env
# Flask
SECRET_KEY=otro_secret_key_diferente_y_mas_seguro
FLASK_ENV=production
FLASK_DEBUG=0

# Database (PostgreSQL para prod - gestionado por Docker)
DATABASE_URL=postgresql://gestiones_user:password_seguro@db:5432/gestiones
DB_PASSWORD=password_seguro  # Generar con: openssl rand -base64 32

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu@email.com
MAIL_PASSWORD=tu_password_app
MAIL_USE_TLS=true
MAIL_USE_SSL=false

# Application
DEBUG=False
TESTING=False
```

### 2.4 Configurar Base de Datos PostgreSQL para Producción

La aplicación usa **SQLite para desarrollo** (simple y sin configuración) y **PostgreSQL para producción** (robusto y escalable).

#### PostgreSQL se levanta automáticamente con Docker Compose

El archivo `config/docker/docker-compose.prod.yml` incluye un contenedor de PostgreSQL que:
- Se inicia automáticamente con la aplicación
- Persiste los datos en un volumen Docker (`postgres_data`)
- Está configurado con health checks
- La aplicación espera a que esté listo antes de arrancar

**No necesitas instalar PostgreSQL manualmente en el servidor.**

#### Generar contraseña segura para la base de datos

```bash
# Generar password para DB_PASSWORD
openssl rand -base64 32
```

Copia la contraseña generada y úsala en `.env.prod` para `DB_PASSWORD`.

#### Inicializar la base de datos en producción

Después del primer deploy, ejecuta el script de inicialización:

```bash
cd /home/ubuntu/gestiones

# Esperar a que los contenedores estén corriendo
docker ps

# Ejecutar script de inicialización
bash scripts/setup/init-prod-db.sh
```

Este script:
1. Espera a que PostgreSQL esté listo
2. Crea las tablas de la base de datos
3. Carga los usuarios de prueba (admin, gestor, usuario)
4. Carga datos de ejemplo para testing

#### Ver datos en PostgreSQL

```bash
# Conectarse a PostgreSQL
docker exec -it gestiones-db-prod psql -U gestiones_user -d gestiones

# Dentro de psql:
# \dt  - Listar tablas
# SELECT * FROM users;  - Ver usuarios
# \q  - Salir
```

#### Backup de la base de datos

```bash
# Backup
docker exec gestiones-db-prod pg_dump -U gestiones_user gestiones > backup_$(date +%Y%m%d).sql

# Restaurar
cat backup_20240109.sql | docker exec -i gestiones-db-prod psql -U gestiones_user -d gestiones
```

### 2.5 Verificar Docker Compose Files

Los archivos de Docker Compose están en `config/docker/`:
- `config/docker/docker-compose.dev.yml` - Desarrollo (SQLite)
- `config/docker/docker-compose.prod.yml` - Producción (PostgreSQL)

### 2.6 Iniciar la Aplicación con Docker

```bash
cd /home/ubuntu/gestiones

# Para DEVELOPMENT (SQLite, puerto 5001)
docker-compose -f config/docker/docker-compose.dev.yml up -d --build

# Para PRODUCTION (PostgreSQL, puerto 5000)
docker-compose -f config/docker/docker-compose.prod.yml up -d --build

# Verificar que está corriendo
docker ps

# Ver logs
docker-compose -f config/docker/docker-compose.dev.yml logs -f

# Para producción
docker-compose -f config/docker/docker-compose.prod.yml logs -f
```

## ⚙️ Paso 3: Configurar Permisos (Opcional)

Si necesitas que Docker arranque automáticamente al reiniciar el servidor, puedes agregar un servicio systemd simple:

```bash
sudo nano /etc/systemd/system/gestiones-docker.service
```

```ini
[Unit]
Description=Gestiones Docker Container
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/gestiones
ExecStart=/usr/bin/docker-compose -f config/docker/docker-compose.dev.yml up -d
ExecStop=/usr/bin/docker-compose -f config/docker/docker-compose.dev.yml down
User=ubuntu

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable gestiones-docker
```

> **Nota**: Esto es opcional. Docker ya reinicia los containers automáticamente con `restart: always`.

## 🌐 Paso 4: Configurar Nginx (Opcional pero Recomendado)

### 4.1 Instalar Nginx

```bash
sudo apt install nginx -y
```

### 4.2 Configurar Nginx como Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/gestiones
```

**Para instancia DEVELOP** (puerto 5001):

```nginx
server {
    listen 80;
    server_name develop.tu-dominio.com;  # o la IP

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /static {
        alias /home/ubuntu/gestiones/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Para instancia PRODUCTION** (puerto 5000):

```nginx
server {
    listen 80;
    server_name tu-dominio.com;  # o la IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /static {
        alias /home/ubuntu/gestiones/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Habilitar el sitio:

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/gestiones /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4.3 Configurar SSL con Let's Encrypt (Recomendado)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com
```

## 🧪 Paso 5: Probar el Deploy

### 5.1 Arrancar Docker Localmente (Primera vez)

```bash
# En la instancia de Oracle Cloud
cd /home/ubuntu/gestiones

# Para DEVELOP
docker-compose -f config/docker/docker-compose.dev.yml up -d --build

# Verificar que arrancó
docker ps
docker-compose -f config/docker/docker-compose.dev.yml logs -f
```

### 5.2 Deploy Automático desde GitHub

```bash
# En tu máquina local
git add .
git commit -m "test: Configurar deploy automático con Docker"
git push origin develop
```

Ve a GitHub → Actions → Verás el workflow ejecutándose

### 5.3 Verificar Logs

```bash
# En la instancia de Oracle Cloud
cd /home/ubuntu/gestiones

# Ver logs en tiempo real
docker-compose -f config/docker/docker-compose.dev.yml logs -f

# Ver solo los últimos 50 logs
docker-compose -f config/docker/docker-compose.dev.yml logs --tail=50
```

## 🔄 Flujo de Deploy

### Para DEVELOP
1. `git push origin develop`
2. GitHub Actions ejecuta tests
3. Si pasan, deploy automático a instancia DEVELOP
4. Aplicación disponible en `http://IP:5001`

### Para PRODUCTION
1. Merge de `develop` a `main`
2. GitHub Actions ejecuta tests
3. Si pasan, deploy automático a instancia PROD
4. Se crea backup antes del deploy
5. Si falla, rollback automático
6. Aplicación disponible en `http://IP:5000`

## 🛠️ Comandos Útiles

### Docker

```bash
# Ver contenedores corriendo
docker ps

# Ver todos los contenedores (incluyendo detenidos)
docker ps -a

# Ver logs en tiempo real
docker-compose -f config/docker/docker-compose.dev.yml logs -f

# Ver logs de un servicio específico
docker-compose -f config/docker/docker-compose.dev.yml logs -f web

# Reiniciar contenedores
docker-compose -f config/docker/docker-compose.dev.yml restart

# Detener contenedores
docker-compose -f config/docker/docker-compose.dev.yml down

# Iniciar contenedores
docker-compose -f config/docker/docker-compose.dev.yml up -d

# Rebuilar y reiniciar
docker-compose -f config/docker/docker-compose.dev.yml up -d --build

# Entrar al contenedor (para debug)
docker-compose -f config/docker/docker-compose.dev.yml exec web bash

# Ver estadísticas de uso de recursos
docker stats

# Limpiar imágenes no usadas
docker system prune -a

# Ver imágenes Docker
docker images
```

### Nginx

```bash
# Verificar configuración de Nginx
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx

# Reiniciar Nginx
sudo systemctl restart nginx

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Sistema

```bash
# Ver puertos en uso
sudo ss -tlnp | grep -E "5000|5001"

# Ver uso de disco
df -h

# Ver uso de memoria
free -h
```

## 🔍 Troubleshooting

### Los contenedores no arrancan

```bash
# Ver logs detallados
docker-compose -f config/docker/docker-compose.dev.yml logs

# Ver estado de contenedores
docker ps -a

# Verificar imágenes
docker images

# Rebuild desde cero
docker-compose -f config/docker/docker-compose.dev.yml down
docker-compose -f config/docker/docker-compose.dev.yml build --no-cache
docker-compose -f config/docker/docker-compose.dev.yml up -d
```

### Puerto en uso

```bash
# Ver qué está usando el puerto
sudo ss -tlnp | grep 5001

# Si es otro contenedor Docker
docker ps
docker stop <container_id>

# Si es un proceso del sistema
sudo kill -9 <pid>
```

### El deploy falla en GitHub Actions

1. **Verificar secrets en GitHub**
   - `DEVELOP_HOST`, `DEVELOP_USER`, `DEVELOP_SSH_KEY`
   
2. **Verificar SSH funciona**:
   ```bash
   ssh -i tu_clave.pem ubuntu@IP
   ```

3. **Verificar que Docker está instalado en el servidor**:
   ```bash
   docker --version
   docker-compose --version
   ```

4. **Ver logs del workflow en GitHub Actions**

### Contenedor se reinicia constantemente

```bash
# Ver por qué falla
docker-compose -f config/docker/docker-compose.dev.yml logs --tail=100

# Verificar archivo .env existe
ls -la /home/ubuntu/gestiones/.env.dev

# Verificar variables de entorno
docker-compose -f config/docker/docker-compose.dev.yml config
```

### Error "No space left on device"

```bash
# Limpiar imágenes y contenedores viejos
docker system prune -a -f

# Ver uso de disco
df -h

# Ver espacio usado por Docker
docker system df
```

## 📊 Monitoreo

### Health Check Endpoint

La aplicación expone `/healthz` para verificar estado:

```bash
# Para DEVELOP
curl http://localhost:5001/healthz
# Respuesta: {"status": "healthy"}

# Para PRODUCTION
curl http://localhost:5000/healthz
# Respuesta: {"status": "healthy"}
```

### Logs Centralizados

```bash
# Ver todos los logs relacionados
sudo journalctl -u gestiones-* -f
```

## 🔐 Seguridad

1. **Firewall**: Configura UFW
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

2. **SSH**: Desactiva login con password
   ```bash
   sudo nano /etc/ssh/sshd_config
   # PasswordAuthentication no
   sudo systemctl restart sshd
   ```

3. **Fail2ban**: Protección contra brute force
   ```bash
   sudo apt install fail2ban -y
   sudo systemctl enable fail2ban
   ```

## 📝 Notas Adicionales

- Los logs se rotan automáticamente con `logrotate`
- Los backups se guardan en `$HOME/backups/` antes de cada deploy a producción
- El servicio se reinicia automáticamente si falla (configurado en systemd)
- Se recomienda configurar alertas con servicios como UptimeRobot

## 🎉 ¡Listo!

Ahora tienes un pipeline de CI/CD completamente funcional:

✅ Tests automáticos
✅ Deploy automático a DEVELOP
✅ Deploy automático a PRODUCTION
✅ Rollback automático en caso de fallo
✅ Health checks
✅ Logs centralizados

