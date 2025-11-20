# Estructura del Proyecto - Gestión de Deudas MVP

```
Gestiones MVP/
│
├── 📦 PAQUETE PRINCIPAL (app/)
│   ├── __init__.py                    # Application factory
│   ├── wsgi.py                        # Entry point para Gunicorn
│   ├── routes/                         # Blueprints
│   │   ├── auth.py                    # Login/logout
│   │   ├── dashboards.py              # Dashboards por rol
│   │   ├── contact.py                 # Formulario de contacto
│   │   ├── admin.py                   # Endpoints admin
│   │   └── root.py                    # Páginas raíz
│   ├── services/                       # Lógica de negocio
│   │   ├── email_service.py           # Envío de emails
│   │   └── storage.py                 # Almacenamiento
│   ├── utils/                          # Utilidades
│   │   ├── security.py                # Decoradores y seguridad
│   │   └── validators.py              # Validaciones
│   └── templates/                      # Plantillas HTML
│       ├── index.html
│       ├── login.html
│       ├── dashboard-admin.html
│       ├── dashboard-gestor.html
│       └── dashboard-user.html
│
├── 📄 ARCHIVOS DE CONFIGURACIÓN
│   └── requirements.txt               # Dependencias Python
│
├── 🎨 ARCHIVOS ESTÁTICOS
│   ├── logo.png                        # Logo modo claro
│   └── logo-dark.png                   # Logo modo oscuro
│   │
│   └── static/                         # Archivos estáticos organizados
│       ├── css/                        # Hojas de estilo
│       │   ├── index.css
│       │   ├── login.css
│       │   ├── dashboard-admin.css
│       │   ├── dashboard-gestor.css
│       │   └── dashboard-user.css
│       │
│       └── js/                         # Archivos JavaScript
│           ├── index.js
│           ├── login.js
│           ├── dashboard-admin.js
│           ├── dashboard-gestor.js
│           └── dashboard-user.js
│
├── 🐳 ARCHIVOS DOCKER
│   ├── Dockerfile.prod                 # Producción optimizado
│   ├── Dockerfile.dev                  # Desarrollo
│   ├── docker-compose.prod.yml         # Producción
│   └── docker-compose.dev.yml         # Desarrollo
│
├── 📚 DOCUMENTACIÓN
│   ├── README.md                       # Documentación principal
│   ├── RESUMEN.md                      # Resumen del proyecto
│   ├── GUIA_DESPLIEGUE_OCI.md         # Guía completa despliegue OCI
│   ├── CONSIDERACIONES_PRE_DESPLIEGUE.md  # Checklist pre-despliegue
│   ├── CHECKLIST_SEGURIDAD.md         # Checklist de seguridad
│   ├── PASOS_DESPLIEGUE.md            # Pasos detallados
│   ├── PROXIMOS_PASOS.md              # Próximos pasos
│   ├── MEJORAS_BUENAS_PRACTICAS.md    # Mejoras aplicadas
│   └── MIGRACION_APP_REFACTORED.md    # Guía de migración
│
├── ⚙️ CONFIGURACIÓN Y SCRIPTS
│   ├── .gitignore                      # Archivos ignorados por Git
│   ├── .dockerignore                   # Archivos ignorados por Docker
│   ├── env/                            # Plantillas de variables de entorno
│   │   ├── dev.env.example
│   │   └── prod.env.example
│   ├── deploy.sh                       # Script de despliegue
│   ├── install-oci.sh                  # Script de instalación OCI
│   └── nginx.conf.example              # Configuración ejemplo de Nginx
│
└── 📁 ARCHIVOS GENERADOS EN RUNTIME (NO EN REPO)
    └── data/
        └── contact_submissions.json    # Solicitudes de contacto guardadas
```

## 📋 Descripción de Archivos por Categoría

### 🔧 Backend (Python/Flask)
- **app/__init__.py**: Application factory - crea y configura la app Flask
- **app/wsgi.py**: Entry point para Gunicorn (`app.wsgi:app`)
- **app/routes/**: Blueprints organizados por funcionalidad
- **app/services/**: Lógica de negocio (email, storage)
- **app/utils/**: Utilidades (validators, security)
- **requirements.txt**: Dependencias Python

### 🎨 Frontend (HTML/CSS/JS)
- **app/templates/**: Plantillas HTML (index, login, dashboards)
- **static/css/**: Estilos separados por página
- **static/js/**: JavaScript separado por página (incluye htmx.min.js)
- **logo.png / logo-dark.png**: Logos según tema

### 🐳 Docker
- **Dockerfile.prod**: Imagen optimizada para producción (Gunicorn)
- **Dockerfile.dev**: Imagen para desarrollo (Flask dev server)
- **docker-compose.prod.yml**: Orquestación para producción (puerto 5000)
- **docker-compose.dev.yml**: Orquestación para desarrollo (puerto 5001, hot-reload)

### 📚 Documentación
- **README.md**: Documentación principal
- **GUIA_DESPLIEGUE_OCI.md**: Guía paso a paso para Oracle Cloud
- **CHECKLIST_SEGURIDAD.md**: Checklist de seguridad
- Otros archivos .md con documentación específica

### ⚙️ Configuración
- **env/dev.env.example**: Plantilla para desarrollo
- **env/prod.env.example**: Plantilla para producción
- **.env.dev / .env.prod**: Variables de entorno (LOCAL, NO commitear)
- **.gitignore**: Archivos ignorados por Git
- **nginx.conf.example**: Configuración ejemplo de Nginx

### 🚀 Scripts
- **deploy.sh**: Script de despliegue automatizado
- **install-oci.sh**: Script de instalación en Oracle Cloud

## 📊 Estadísticas del Proyecto

- **Total archivos**: ~50+ archivos
- **Líneas de código Python**: ~800+ (distribuido en módulos)
- **Estructura**: Modular con Application Factory
- **Blueprints**: 5 (auth, dashboards, contact, admin, root)
- **Archivos HTML**: 5 páginas principales
- **Archivos CSS**: 5 archivos
- **Archivos JS**: 5 archivos + htmx.min.js
- **Documentación**: 8+ archivos MD

## 🔍 Archivos Críticos por Función

### Para Desarrollo Local
- `docker-compose.dev.yml`
- `Dockerfile.dev`
- `.env.dev` (local)

### Para Producción
- `docker-compose.prod.yml`
- `Dockerfile.prod`
- `.env.prod` (en servidor)
- `nginx.conf.example`

### Para Despliegue
- `deploy.sh`
- `install-oci.sh`
- `GUIA_DESPLIEGUE_OCI.md`

### Para Seguridad
- `.env` (nunca commitear)
- `.gitignore`
- `CHECKLIST_SEGURIDAD.md`

## 📁 Estructura de Carpetas

```
static/
├── css/          # Estilos CSS separados
└── js/           # JavaScript separado
```

## ⚠️ Archivos que NO deben commitearse

- `.env`, `.env.dev`, `.env.prod` (variables sensibles)
- `data/contact_submissions.json` (datos de usuarios)
- `*.log` (logs)
- `*.db`, `*.sqlite` (bases de datos)
- `*.pem`, `*.key` (certificados SSL)
- `__pycache__/`, `*.pyc` (caché de Python)

## 🔄 Flujo de Archivos

```
1. Desarrollo Local
   ├── app/ (paquete Python)
   │   ├── routes/ (blueprints)
   │   ├── services/ (lógica de negocio)
   │   └── templates/ (HTML)
   ├── static/css/*.css (estilos)
   └── static/js/*.js (scripts)

2. Docker Build
   ├── Dockerfile.prod (instrucciones)
   ├── requirements.txt (dependencias)
   └── app/ (código completo)

3. Despliegue
   ├── docker-compose.prod.yml (orquestación)
   ├── .env.prod (configuración - en servidor)
   └── deploy.sh (automatización)
```


