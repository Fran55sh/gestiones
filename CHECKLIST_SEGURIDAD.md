# Checklist de Seguridad Pre-Despliegue

## 🔐 SEGURIDAD CRÍTICA

### Variables de Entorno
- [ ] `SECRET_KEY` generada con: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] `SESSION_COOKIE_SECURE=true` (con HTTPS)
- [ ] Credenciales de email configuradas correctamente
- [ ] Archivo `.env` NO está en el repositorio (verificado en .gitignore)

### Credenciales de Usuario
- [ ] Cambiar contraseñas por defecto de usuarios de ejemplo:
  - admin/admin123 → NUEVA_CONTRASEÑA_SEGURA
  - gestor/gestor123 → NUEVA_CONTRASEÑA_SEGURA
  - usuario/user123 → NUEVA_CONTRASEÑA_SEGURA
- [ ] Considerar implementar autenticación real con hash de contraseñas

### Configuración de Servidor
- [ ] Firewall configurado:
  - Puerto 22 (SSH) solo desde IPs confiables
  - Puerto 80 (HTTP) abierto
  - Puerto 443 (HTTPS) abierto
  - Puerto 5000 solo desde localhost (Nginx)
- [ ] Fail2ban instalado y configurado
- [ ] Actualizaciones automáticas de seguridad habilitadas

### SSL/TLS
- [ ] Certificado SSL configurado (Let's Encrypt recomendado)
- [ ] Redirección HTTP → HTTPS configurada
- [ ] Headers de seguridad configurados en Nginx

### Email
- [ ] Usar contraseña de aplicación (no contraseña principal)
- [ ] Verificar que puerto y SSL/TLS son correctos
- [ ] Probar envío de email antes de producción

## 📋 CONFIGURACIÓN

### Docker
- [ ] Docker instalado y funcionando
- [ ] Docker Compose instalado
- [ ] Usuario no-root configurado en Dockerfile
- [ ] Healthcheck configurado

### Nginx
- [ ] Nginx instalado y configurado
- [ ] Reverse proxy configurado correctamente
- [ ] SSL configurado
- [ ] Logs configurados

### DNS
- [ ] Dominio apunta a IP de la instancia
- [ ] Registros A y AAAA configurados
- [ ] TTL configurado apropiadamente

## 🔍 MONITOREO

### Logs
- [ ] Rotación de logs configurada
- [ ] Logs de aplicación accesibles
- [ ] Logs de Nginx configurados

### Backup
- [ ] Estrategia de backup definida
- [ ] Backup de archivos de datos (contact_submissions.json)
- [ ] Automatización de backups configurada

## ✅ VERIFICACIÓN POST-DESPLIEGUE

- [ ] Aplicación accesible vía HTTPS
- [ ] Formulario de contacto funciona
- [ ] Login funciona correctamente
- [ ] Dashboards funcionan
- [ ] Email se envía correctamente
- [ ] Logs sin errores críticos
- [ ] Performance aceptable

## 🚨 MANTENIMIENTO

### Regular
- [ ] Revisar logs semanalmente
- [ ] Actualizar dependencias mensualmente
- [ ] Verificar backups semanalmente
- [ ] Revisar seguridad trimestralmente

### Actualizaciones
- [ ] Mantener sistema operativo actualizado
- [ ] Actualizar Docker y dependencias
- [ ] Revisar vulnerabilidades de seguridad

