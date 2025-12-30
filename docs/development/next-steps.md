# Próximos Pasos - Despliegue en Oracle Cloud

## ✅ COMPLETADO
- [x] Commit realizado
- [x] Push al repositorio

## 📋 SIGUIENTE PASO: Configurar Instancia en Oracle Cloud

### Opción A: Si ya tienes la instancia creada

1. **Conectar por SSH:**
   ```bash
   ssh usuario@tu-ip-oci
   ```

2. **Clonar repositorio:**
   ```bash
   git clone https://github.com/Fran55sh/gestiones.git
   cd gestiones
   ```

3. **Ejecutar instalación:**
   ```bash
   chmod +x install-oci.sh
   ./install-oci.sh
   ```

4. **Reiniciar sesión SSH** (para que Docker funcione):
   ```bash
   exit
   ssh usuario@tu-ip-oci
   ```

### Opción B: Si aún no tienes la instancia

1. **Crear instancia en Oracle Cloud:**
   - Ve a Oracle Cloud Console
   - Compute → Instances → Create Instance
   - Shape: VM.Standard.E2.1.Micro (Free Tier)
   - OS: Ubuntu 22.04 LTS
   - Configurar SSH key
   - Anotar IP pública

2. **Configurar Security List (Firewall):**
   - Permitir puerto 22 (SSH) desde tu IP
   - Permitir puerto 80 (HTTP)
   - Permitir puerto 443 (HTTPS)

3. **Continuar con Opción A**

## 🔧 PASO CRÍTICO: Configurar .env

**Antes de desplegar, debes configurar el archivo `.env.prod`:**

```bash
cd gestiones
cp env/prod.env.example .env.prod
nano .env.prod
```

**Valores que DEBES configurar:**

```bash
# 1. SECRET_KEY (OBLIGATORIO)
SECRET_KEY=-_S0Te_v-IyEZeShfkBBehUYvL-j9wa45615EnuicNE

# 2. Email (OBLIGATORIO)
MAIL_USERNAME=administracion@novagestiones.com.ar
MAIL_PASSWORD=tu_contraseña_de_aplicacion_zoho
MAIL_DEFAULT_SENDER=administracion@novagestiones.com.ar

# 3. Cookies seguras (true cuando tengas HTTPS)
SESSION_COOKIE_SECURE=false  # Cambiar a true cuando tengas SSL
```

## 🚀 Desplegar

```bash
chmod +x deploy.sh
./deploy.sh
```

## 🌐 Configurar Dominio y SSL (Opcional pero recomendado)

Si tienes dominio:

1. **Configurar DNS:** Apuntar dominio a IP de la instancia
2. **Configurar Nginx:** Ver `nginx.conf.example`
3. **Obtener SSL:** `sudo certbot --nginx -d tu-dominio.com`
4. **Actualizar .env:** `SESSION_COOKIE_SECURE=true`

## 📝 ¿Qué necesitas ahora?

1. **¿Tienes la instancia de Oracle Cloud creada?**
   - Si NO → Crear instancia primero
   - Si SÍ → Continuar con SSH

2. **¿Tienes dominio configurado?**
   - Si NO → Puedes usar IP directamente (menos seguro)
   - Si SÍ → Configurar Nginx y SSL

3. **¿Tienes las credenciales de email?**
   - Si NO → Obtener contraseña de aplicación de Zoho
   - Si SÍ → Configurar en .env

## 🆘 Comandos Útiles

```bash
# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml --project-name gestiones-prod logs -f

# Ver estado
docker compose -f docker-compose.prod.yml --project-name gestiones-prod ps

# Reiniciar
docker compose -f docker-compose.prod.yml --project-name gestiones-prod restart

# Reconstruir
docker compose -f docker-compose.prod.yml --project-name gestiones-prod --env-file .env.prod up -d --build
```

## ⚠️ IMPORTANTE ANTES DE DESPLEGAR

- [ ] SECRET_KEY configurada en .env.prod (generar con: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] Credenciales de email configuradas (MAIL_USERNAME, MAIL_PASSWORD)
- [ ] CONTACT_RECIPIENTS configurado (separados por coma)
- [ ] Firewall configurado en OCI (puertos 22, 80, 443)
- [ ] Dominio configurado (opcional pero recomendado)
- [ ] Healthcheck funcionando: `curl http://localhost:5000/healthz`

---

**¿Qué tienes listo? ¿Necesitas ayuda con algún paso específico?**


