# 🚀 Deploy Automático a Oracle Cloud

Guía completa para configurar el deploy automático a las instancias de Oracle Cloud.

## 📋 Arquitectura

```
GitHub Actions
    ↓
┌─────────────────────┐
│   Push to develop   │ → Tests → Deploy → Oracle Cloud (Develop - :8000)
└─────────────────────┘

┌─────────────────────┐
│   Push to main      │ → Tests → Deploy → Oracle Cloud (Prod - :8001)
└─────────────────────┘
```

## 🔐 Paso 1: Configurar Secrets en GitHub

Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Secrets para Instancia DEVELOP

| Secret Name | Descripción | Ejemplo |
|------------|-------------|---------|
| `DEVELOP_HOST` | IP o dominio de la instancia | `123.45.67.89` |
| `DEVELOP_USER` | Usuario SSH | `ubuntu` |
| `DEVELOP_SSH_KEY` | Clave privada SSH completa | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DEVELOP_PATH` | Ruta del proyecto | `/home/ubuntu/gestiones-develop` |

### Secrets para Instancia PRODUCTION

| Secret Name | Descripción | Ejemplo |
|------------|-------------|---------|
| `PROD_HOST` | IP o dominio de la instancia | `98.76.54.32` |
| `PROD_USER` | Usuario SSH | `ubuntu` |
| `PROD_SSH_KEY` | Clave privada SSH completa | `-----BEGIN RSA PRIVATE KEY-----...` |
| `PROD_PATH` | Ruta del proyecto | `/home/ubuntu/gestiones-prod` |

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

# Instalar dependencias
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx postgresql-client

# Crear directorio del proyecto
sudo mkdir -p /home/ubuntu/gestiones-develop  # o gestiones-prod
sudo chown ubuntu:ubuntu /home/ubuntu/gestiones-develop
```

### 2.2 Clonar el Repositorio

```bash
cd /home/ubuntu
git clone https://github.com/tu-usuario/gestiones.git gestiones-develop
cd gestiones-develop

# Para develop
git checkout develop

# Para prod (en la otra instancia)
git checkout main
```

### 2.3 Configurar Virtual Environment

```bash
cd /home/ubuntu/gestiones-develop  # o gestiones-prod

# Crear venv
python3.11 -m venv venv

# Activar
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Configurar Variables de Entorno

```bash
# Crear archivo .env
nano /home/ubuntu/gestiones-develop/.env
```

Contenido del `.env`:

```env
# Flask
SECRET_KEY=tu_secret_key_muy_seguro_aqui
FLASK_ENV=development  # o production

# Database
DATABASE_URL=postgresql://usuario:password@localhost:5432/gestiones_dev

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Email (si usas)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu@email.com
MAIL_PASSWORD=tu_password_app

# Application
DEBUG=False
TESTING=False
```

### 2.5 Inicializar Base de Datos

```bash
# Crear base de datos PostgreSQL
sudo -u postgres psql
CREATE DATABASE gestiones_dev;  -- o gestiones_prod
CREATE USER gestor WITH PASSWORD 'password_seguro';
GRANT ALL PRIVILEGES ON DATABASE gestiones_dev TO gestor;
\q

# Ejecutar migraciones
cd /home/ubuntu/gestiones-develop
source venv/bin/activate
alembic upgrade head
```

## ⚙️ Paso 3: Configurar Systemd

### 3.1 Crear Servicio para DEVELOP

```bash
sudo nano /etc/systemd/system/gestiones-develop.service
```

Contenido:

```ini
[Unit]
Description=Gestiones MVP - Development
After=network.target postgresql.service

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/gestiones-develop
Environment="PATH=/home/ubuntu/gestiones-develop/venv/bin"
EnvironmentFile=/home/ubuntu/gestiones-develop/.env
ExecStart=/home/ubuntu/gestiones-develop/venv/bin/gunicorn \
    --workers 4 \
    --worker-class gthread \
    --threads 2 \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/gestiones-develop-access.log \
    --error-logfile /var/log/gestiones-develop-error.log \
    --log-level info \
    app.wsgi:app

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=gestiones-develop

[Install]
WantedBy=multi-user.target
```

### 3.2 Crear Servicio para PRODUCTION

```bash
sudo nano /etc/systemd/system/gestiones-prod.service
```

Contenido (similar a develop pero en puerto 8001):

```ini
[Unit]
Description=Gestiones MVP - Production
After=network.target postgresql.service

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/gestiones-prod
Environment="PATH=/home/ubuntu/gestiones-prod/venv/bin"
EnvironmentFile=/home/ubuntu/gestiones-prod/.env
ExecStart=/home/ubuntu/gestiones-prod/venv/bin/gunicorn \
    --workers 4 \
    --worker-class gthread \
    --threads 2 \
    --bind 0.0.0.0:8001 \
    --access-logfile /var/log/gestiones-prod-access.log \
    --error-logfile /var/log/gestiones-prod-error.log \
    --log-level warning \
    app.wsgi:app

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=gestiones-prod

[Install]
WantedBy=multi-user.target
```

### 3.3 Habilitar y Arrancar Servicios

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio (autostart en boot)
sudo systemctl enable gestiones-develop  # o gestiones-prod

# Iniciar servicio
sudo systemctl start gestiones-develop

# Verificar estado
sudo systemctl status gestiones-develop

# Ver logs en tiempo real
sudo journalctl -u gestiones-develop -f
```

## 🔒 Paso 4: Configurar Permisos Sudo

GitHub Actions necesita poder reiniciar el servicio sin password.

```bash
sudo visudo
```

Agregar al final:

```
# Para instancia DEVELOP
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart gestiones-develop
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl status gestiones-develop
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl stop gestiones-develop
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl start gestiones-develop

# Para instancia PROD (en la otra instancia)
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart gestiones-prod
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl status gestiones-prod
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl stop gestiones-prod
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl start gestiones-prod
```

## 🌐 Paso 5: Configurar Nginx (Opcional pero Recomendado)

### 5.1 Instalar Nginx

```bash
sudo apt install nginx -y
```

### 5.2 Configurar para DEVELOP

```bash
sudo nano /etc/nginx/sites-available/gestiones-develop
```

Contenido:

```nginx
server {
    listen 80;
    server_name develop.tu-dominio.com;  # o la IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ubuntu/gestiones-develop/static;
        expires 30d;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/gestiones-develop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5.3 Configurar SSL con Let's Encrypt (Recomendado)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d develop.tu-dominio.com
```

## 🧪 Paso 6: Probar el Deploy

### 6.1 Deploy Manual (Primera vez)

```bash
# En tu máquina local
git add .
git commit -m "test: Configurar deploy automático"
git push origin develop
```

Ve a GitHub → Actions → Verás el workflow ejecutándose

### 6.2 Verificar Logs

```bash
# En la instancia de Oracle Cloud
sudo journalctl -u gestiones-develop -f
```

## 🔄 Flujo de Deploy

### Para DEVELOP
1. `git push origin develop`
2. GitHub Actions ejecuta tests
3. Si pasan, deploy automático a instancia DEVELOP
4. Aplicación disponible en `http://IP:8000`

### Para PRODUCTION
1. Merge de `develop` a `main`
2. GitHub Actions ejecuta tests
3. Si pasan, deploy automático a instancia PROD
4. Se crea backup antes del deploy
5. Si falla, rollback automático
6. Aplicación disponible en `http://IP:8001`

## 🛠️ Comandos Útiles

```bash
# Ver estado del servicio
sudo systemctl status gestiones-develop

# Ver logs
sudo journalctl -u gestiones-develop -n 100

# Reiniciar manualmente
sudo systemctl restart gestiones-develop

# Detener servicio
sudo systemctl stop gestiones-develop

# Ver logs de error
sudo tail -f /var/log/gestiones-develop-error.log

# Ver logs de acceso
sudo tail -f /var/log/gestiones-develop-access.log

# Verificar configuración de Nginx
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx

# Ver procesos de Gunicorn
ps aux | grep gunicorn
```

## 🔍 Troubleshooting

### El servicio no arranca

```bash
# Ver logs detallados
sudo journalctl -u gestiones-develop -xe

# Verificar permisos
ls -la /home/ubuntu/gestiones-develop

# Verificar variables de entorno
sudo systemctl show gestiones-develop --property=Environment
```

### El deploy falla en GitHub Actions

1. Verificar que los secrets están configurados correctamente
2. Verificar que la clave SSH funciona:
   ```bash
   ssh -i tu_clave.pem ubuntu@IP
   ```
3. Verificar permisos sudo (paso 4)

### Base de datos no conecta

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -l

# Probar conexión
psql "postgresql://usuario:password@localhost:5432/gestiones_dev"
```

## 📊 Monitoreo

### Health Check Endpoint

La aplicación expone `/healthz` para verificar estado:

```bash
curl http://localhost:8000/healthz
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

