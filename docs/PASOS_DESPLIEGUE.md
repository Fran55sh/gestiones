# Checklist de Pasos para Despliegue en Oracle Cloud

## ✅ PASO 1: Commit realizado
- [x] Cambios commiteados localmente
- [ ] Push al repositorio remoto (opcional ahora, pero necesario antes de clonar en OCI)

## 📋 PASO 2: Preparar Oracle Cloud Infrastructure (OCI)

### 2.1 Crear Instancia Compute
- [ ] Acceder a Oracle Cloud Console
- [ ] Crear nueva instancia Compute (VM)
- [ ] Seleccionar Shape: VM.Standard.E2.1.Micro (Free Tier) o VM.Standard.E2.1
- [ ] Seleccionar OS: Ubuntu 22.04 LTS o Oracle Linux 8
- [ ] Configurar SSH key para acceso
- [ ] Anotar la IP pública asignada

### 2.2 Configurar Security List (Firewall)
- [ ] Permitir puerto 22 (SSH) - Solo desde tu IP
- [ ] Permitir puerto 80 (HTTP)
- [ ] Permitir puerto 443 (HTTPS)
- [ ] NO permitir puerto 5000 públicamente

### 2.3 Configurar DNS (si tienes dominio)
- [ ] Crear registro A apuntando a IP de la instancia
- [ ] Crear registro AAAA si usas IPv6
- [ ] Esperar propagación DNS (puede tardar minutos/horas)

## 🔧 PASO 3: Conectar y Configurar Servidor

### 3.1 Conectar por SSH
```bash
ssh usuario@tu-ip-oci
```

### 3.2 Ejecutar Script de Instalación
```bash
# Clonar repositorio
git clone https://github.com/Fran55sh/gestiones.git
cd gestiones

# Ejecutar script de instalación
chmod +x install-oci.sh
./install-oci.sh

# IMPORTANTE: Reiniciar sesión SSH después de instalar Docker
exit
ssh usuario@tu-ip-oci
```

### 3.3 Configurar Variables de Entorno
```bash
cd gestiones

# Copiar plantilla
cp env.example .env

# Editar .env con tus valores
nano .env
```

**Valores críticos a configurar:**
- SECRET_KEY (ya la generamos: `-_S0Te_v-IyEZeShfkBBehUYvL-j9wa45615EnuicNE`)
- MAIL_USERNAME
- MAIL_PASSWORD (contraseña de aplicación de Zoho)
- MAIL_DEFAULT_SENDER

## 🌐 PASO 4: Configurar Nginx (si tienes dominio)

### 4.1 Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/gestiones
# Copiar contenido de nginx.conf.example y ajustar dominio
```

### 4.2 Habilitar Sitio
```bash
sudo ln -s /etc/nginx/sites-available/gestiones /etc/nginx/sites-enabled/
sudo nginx -t  # Verificar configuración
sudo systemctl restart nginx
```

### 4.3 Obtener Certificado SSL
```bash
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

## 🚀 PASO 5: Desplegar Aplicación

```bash
cd gestiones

# Ejecutar script de despliegue
chmod +x deploy.sh
./deploy.sh
```

## ✅ PASO 6: Verificar Funcionamiento

- [ ] Acceder a http://tu-dominio.com o http://tu-ip:5000
- [ ] Verificar que carga correctamente
- [ ] Probar login
- [ ] Probar formulario de contacto
- [ ] Verificar logs: `docker-compose -f docker-compose.prod.yml logs -f`

## 🆘 Troubleshooting

### Si algo falla:
```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs

# Reiniciar
docker-compose -f docker-compose.prod.yml restart

# Reconstruir
docker-compose -f docker-compose.prod.yml up -d --build
```


