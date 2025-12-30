# Guía de Despliegue en Oracle Cloud Infrastructure (OCI)

## Checklist Pre-Despliegue

### ✅ 1. Seguridad Crítica

- [ ] **SECRET_KEY**: Generar una clave secreta fuerte y única
- [ ] **Variables de entorno**: Configurar todas las variables sensibles en `.env`
- [ ] **SSL/TLS**: Configurar certificado SSL (Let's Encrypt o comercial)
- [ ] **Firewall**: Configurar Security List en OCI para permitir solo puertos necesarios
- [ ] **Credenciales**: Cambiar credenciales de ejemplo (admin/gestor/usuario)

### ✅ 2. Configuración de Servidor

- [ ] **Dominio**: Configurar DNS apuntando a la IP de la instancia
- [ ] **Puertos**: Exponer solo puertos necesarios (80, 443, 22)
- [ ] **Reverse Proxy**: Configurar Nginx como reverse proxy
- [ ] **Usuario no-root**: Verificar que Docker corre con usuario no-root

### ✅ 3. Configuración de Email

- [ ] **SMTP**: Verificar credenciales de Zoho Mail
- [ ] **App Password**: Usar contraseña de aplicación (no contraseña principal)
- [ ] **Puerto**: Verificar puerto correcto (465 SSL o 587 TLS)

### ✅ 4. Base de Datos (Opcional para MVP)

- [ ] **Persistencia**: Actualmente usa archivos JSON (considerar PostgreSQL/MySQL)
- [ ] **Backups**: Configurar backups automáticos si se usa BD

### ✅ 5. Monitoreo y Logs

- [ ] **Logs**: Configurar rotación de logs
- [ ] **Monitoreo**: Considerar herramientas de monitoreo (opcional)

## Configuración de Oracle Cloud

### Security List (Firewall)

Permitir solo estos puertos:
- **22** (SSH) - Solo desde tu IP
- **80** (HTTP) - Para Let's Encrypt y redirección
- **443** (HTTPS) - Tráfico web
- **5000** - Solo internamente (Nginx → Flask)

### Instancia Recomendada

- **Shape**: VM.Standard.E2.1.Micro (Free Tier) o VM.Standard.E2.1
- **OS**: Ubuntu 22.04 LTS o Oracle Linux 8
- **RAM**: Mínimo 1GB (recomendado 2GB+)
- **Disco**: 50GB mínimo

## Pasos de Despliegue

1. **Crear instancia en OCI**
2. **Configurar Security List**
3. **Conectar por SSH y actualizar sistema**
4. **Instalar Docker y Docker Compose**
5. **Clonar repositorio**
6. **Configurar variables de entorno (.env)**
7. **Configurar Nginx como reverse proxy**
8. **Configurar SSL con Let's Encrypt**
9. **Iniciar aplicación con docker-compose**
10. **Verificar funcionamiento**

## Archivos Necesarios

- `.env` - Variables de entorno (NO commitear)
- `docker-compose.prod.yml` - Configuración de producción
- `nginx.conf` - Configuración de Nginx
- `deploy.sh` - Script de despliegue automatizado

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f web

# Reiniciar aplicación
docker-compose restart

# Actualizar aplicación
git pull
docker-compose up -d --build

# Verificar estado
docker-compose ps
```

## Seguridad Post-Despliegue

- [ ] Cambiar contraseñas por defecto
- [ ] Configurar fail2ban para protección SSH
- [ ] Configurar actualizaciones automáticas de seguridad
- [ ] Revisar logs regularmente
- [ ] Configurar backups automáticos

## Troubleshooting

### La aplicación no inicia
- Verificar logs: `docker-compose logs web`
- Verificar variables de entorno
- Verificar puertos disponibles

### Email no funciona
- Verificar credenciales en `.env`
- Verificar puerto y SSL/TLS
- Revisar logs de Flask

### Certificado SSL no funciona
- Verificar que DNS apunta correctamente
- Verificar que puertos 80 y 443 están abiertos
- Verificar configuración de Nginx

