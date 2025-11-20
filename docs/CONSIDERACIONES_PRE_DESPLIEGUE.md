# Consideraciones Críticas ANTES de Desplegar en Oracle Cloud

## 🚨 CRÍTICO - Hacer ANTES del despliegue

### 1. SECRET_KEY (OBLIGATORIO)
```bash
# Generar una clave secreta fuerte:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
- **NO usar** la clave por defecto `change-me-in-production`
- Configurar en `.env` como `SECRET_KEY=tu_clave_generada_aqui`
- Sin esto, las sesiones son vulnerables

### 2. Credenciales de Usuario
**CAMBIAR OBLIGATORIAMENTE** en `app/__init__.py` (diccionario `USERS`):
- `admin/admin123` → Contraseña segura (ya hasheada con Werkzeug)
- `gestor/gestor123` → Contraseña segura (ya hasheada con Werkzeug)
- `usuario/user123` → Contraseña segura (ya hasheada con Werkzeug)

**Nota:** Las contraseñas ya están hasheadas usando `generate_password_hash` de Werkzeug.

**En producción idealmente:**
- Usar base de datos con hash de contraseñas (bcrypt)
- Implementar autenticación real con base de datos

### 3. Variables de Entorno (.env)
- Copiar `env/prod.env.example` a `.env.prod`
- Configurar TODAS las variables (SECRET_KEY, MAIL_*, CONTACT_RECIPIENTS, etc.)
- **NUNCA commitear `.env.prod` o `.env.dev` al repositorio**
- Verificar que están en `.gitignore`

### 4. Firewall en Oracle Cloud
En Security List de OCI:
- ✅ Puerto 22 (SSH) - Solo desde tu IP
- ✅ Puerto 80 (HTTP) - Para Let's Encrypt
- ✅ Puerto 443 (HTTPS) - Tráfico web
- ❌ Puerto 5000 - NO exponer públicamente (solo Nginx → Flask)

### 5. SSL/TLS (OBLIGATORIO en producción)
- Configurar Nginx como reverse proxy
- Obtener certificado SSL (Let's Encrypt gratis)
- Configurar redirección HTTP → HTTPS
- Sin HTTPS, las cookies de sesión no son seguras

## ⚠️ IMPORTANTE

### 6. Email
- Usar **contraseña de aplicación** de Zoho (no contraseña principal)
- Verificar puerto correcto (465 SSL o 587 TLS)
- Probar envío antes de producción

### 7. Base de Datos
- Actualmente usa archivos JSON (`data/contact_submissions.json`)
- Para producción, considerar PostgreSQL/MySQL
- Implementar backups automáticos

### 8. Logs y Monitoreo
- Configurar rotación de logs
- Revisar logs regularmente
- Considerar herramientas de monitoreo (opcional)

### 9. Backup
- Backup automático de `data/contact_submissions.json`
- Backup de configuración (.env.prod)
- Estrategia de recuperación

### 10. Performance
- Gunicorn configurado con workers apropiados
- Nginx caching para archivos estáticos
- Considerar CDN para assets estáticos (opcional)

## 📋 Checklist Rápido

- [ ] SECRET_KEY generada y configurada
- [ ] Credenciales de usuario cambiadas
- [ ] Archivo .env configurado completamente
- [ ] Firewall configurado en OCI
- [ ] Nginx instalado y configurado
- [ ] SSL/TLS configurado (Let's Encrypt)
- [ ] Email probado y funcionando
- [ ] Dominio DNS configurado
- [ ] Backup configurado
- [ ] Logs configurados

## 🔧 Comandos Rápidos

```bash
# En la instancia OCI:

# 1. Instalar dependencias (una vez)
./install-oci.sh

# 2. Configurar .env.prod
cp env/prod.env.example .env.prod
nano .env.prod  # Editar y configurar

# 3. Configurar Nginx
sudo nano /etc/nginx/sites-available/gestiones
# Copiar contenido de nginx.conf.example y ajustar dominio

# 4. Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com

# 5. Desplegar aplicación
./deploy.sh

# 6. Ver logs
docker compose -f docker-compose.prod.yml --project-name gestiones-prod logs -f
```

## 🆘 Troubleshooting

### La aplicación no inicia
```bash
docker compose -f docker-compose.prod.yml --project-name gestiones-prod logs
```

### Verificar configuración
```bash
docker compose -f docker-compose.prod.yml --project-name gestiones-prod ps
curl http://localhost:5000/healthz  # Healthcheck
```

### Reiniciar todo
```bash
docker compose -f docker-compose.prod.yml --project-name gestiones-prod down
docker compose -f docker-compose.prod.yml --project-name gestiones-prod --env-file .env.prod up -d --build
```

## 📚 Documentación Creada

1. **GUIA_DESPLIEGUE_OCI.md** - Guía completa paso a paso
2. **CHECKLIST_SEGURIDAD.md** - Checklist de seguridad detallado
3. **env/prod.env.example** - Plantilla de variables de entorno para producción
4. **env/dev.env.example** - Plantilla de variables de entorno para desarrollo
4. **docker-compose.prod.yml** - Configuración de producción
5. **nginx.conf.example** - Configuración de Nginx
6. **deploy.sh** - Script de despliegue automatizado
7. **install-oci.sh** - Script de instalación inicial
8. **Dockerfile.prod** - Dockerfile optimizado para producción

## ⚡ Próximos Pasos Recomendados

1. Revisar todos los archivos de documentación
2. Configurar .env con valores reales
3. Probar despliegue en un entorno de staging primero
4. Configurar monitoreo y alertas
5. Implementar autenticación real con base de datos
6. Configurar CI/CD para despliegues automáticos

