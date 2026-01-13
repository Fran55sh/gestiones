# 📘 DOCUMENTACIÓN COMPLETA DEL SISTEMA
## Sistema de Gestión de Deudas - NOVA Gestión de Cobranzas

**Última actualización:** 13 de Enero 2026  
**Versión:** 1.1.0  
**Propósito:** Documentación técnica completa para contexto y mantenimiento del sistema

### Cambios Recientes (13/01/2026)
- ✅ Scripts de exportación/importación de datos para producción
- ✅ Asignación automática de casos al gestor (ID 2) en importación
- ✅ Corrección de migraciones para soporte PostgreSQL (ON CONFLICT vs INSERT OR IGNORE)
- ✅ Proceso completo de migración de datos documentado
- ✅ Scripts de verificación de datos en producción

---

## 📋 TABLA DE CONTENIDOS

1. [Visión General](#visión-general)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Estructura de Directorios](#estructura-de-directorios)
5. [Modelos de Datos](#modelos-de-datos)
6. [Rutas y Endpoints](#rutas-y-endpoints)
7. [Servicios y Lógica de Negocio](#servicios-y-lógica-de-negocio)
8. [Frontend y UI](#frontend-y-ui)
9. [Base de Datos](#base-de-datos)
10. [Autenticación y Seguridad](#autenticación-y-seguridad)
11. [Deployment y DevOps](#deployment-y-devops)
12. [CI/CD Pipeline](#cicd-pipeline)
13. [Testing](#testing)
14. [Scripts y Utilidades](#scripts-y-utilidades)
15. [Variables de Entorno](#variables-de-entorno)
16. [Troubleshooting](#troubleshooting)

---

## 🎯 VISIÓN GENERAL

### Descripción
Sistema completo de gestión de deudas desarrollado en Flask (Python) con arquitectura modular, soporte multi-rol (admin, gestor, user), dashboards interactivos, y deployment automatizado en Oracle Cloud Infrastructure (OCI) mediante Docker.

### Características Principales
- ✅ **Sistema de autenticación** con roles y sesiones seguras
- ✅ **Dashboard administrativo** con KPIs, gráficos y análisis
- ✅ **Dashboard de gestor** personalizado con herramientas de productividad
- ✅ **Panel de usuario** básico
- ✅ **API REST** completa para gestión de casos, promesas y actividades
- ✅ **Base de datos** PostgreSQL (producción) / SQLite (desarrollo)
- ✅ **Deployment automatizado** con GitHub Actions
- ✅ **Containerización** completa con Docker
- ✅ **CI/CD** con tests, linting y deployment automático

### Entornos
- **Desarrollo:** Puerto 5001, SQLite, hot-reload
- **Producción:** Puerto 5000, PostgreSQL, Gunicorn

---

## 🛠️ STACK TECNOLÓGICO

### Backend
- **Flask 3.0.0** - Framework web Python
- **Flask-SQLAlchemy 3.1.1** - ORM para base de datos
- **Alembic 1.13.1** - Migraciones de base de datos
- **psycopg2-binary 2.9.9** - Driver PostgreSQL
- **Gunicorn 23.0.0** - Servidor WSGI para producción
- **Werkzeug 3.0.1** - Utilidades WSGI y seguridad

### Frontend
- **HTMX** - Peticiones asíncronas sin JavaScript complejo
- **Tailwind CSS** (CDN) - Framework CSS utility-first
- **Chart.js** - Gráficos interactivos
- **Lucide Icons** - Iconos modernos
- **JavaScript vanilla** - Lógica del frontend

### Seguridad y Performance
- **Flask-SeaSurf 1.1.1** - Protección CSRF
- **Flask-Limiter 3.5.0** - Rate limiting
- **Flask-Compress 1.14** - Compresión de respuestas
- **Redis 5.0.1** - Cache y rate limiting (opcional)

### Validación
- **marshmallow 3.21.0** - Serialización y validación
- **marshmallow-sqlalchemy 0.29.0** - Integración SQLAlchemy

### Testing
- **pytest 7.4.3** - Framework de testing
- **pytest-cov 4.1.0** - Cobertura de código
- **pytest-flask 1.3.0** - Helpers para testing Flask

### DevOps
- **Docker** - Containerización
- **Docker Compose** - Orquestación de contenedores
- **GitHub Actions** - CI/CD
- **Oracle Cloud Infrastructure (OCI)** - Hosting

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Patrón Arquitectónico
**Application Factory Pattern** con Flask Blueprints

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTE (Browser)                     │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Nginx (Opcional, futuro)                   │
│              Reverse Proxy + SSL                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Gunicorn (Producción)                       │
│              Flask Dev Server (Desarrollo)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Application (app/__init__.py)         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Blueprints:                                     │   │
│  │  - web.auth (Login/Logout)                       │   │
│  │  - web.dashboards (Dashboards por rol)         │   │
│  │  - web.contact (Formulario contacto)            │   │
│  │  - web.admin (Admin endpoints)                  │   │
│  │  - web.public (Páginas públicas)               │   │
│  │  - api.v1 (API REST)                            │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌────────────┴────────────┐
         ▼                         ▼
┌─────────────────┐      ┌──────────────────┐
│   Services      │      │   Models         │
│  - Dashboard    │      │  - User          │
│  - Email         │      │  - Case         │
│  - Cache         │      │  - Promise      │
│  - Audit         │      │  - Activity     │
│  - Storage       │      │  - Contact      │
└─────────────────┘      └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  SQLAlchemy ORM  │
                          └────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
          ┌──────────────────┐        ┌──────────────────┐
          │   PostgreSQL     │        │     SQLite       │
          │   (Producción)   │        │   (Desarrollo)    │
          └──────────────────┘        └──────────────────┘
```

### Flujo de Request

1. **Cliente** → Request HTTP
2. **Gunicorn/Flask** → Recibe request
3. **Flask App** → Routing según URL
4. **Blueprint** → Maneja la ruta específica
5. **Decorador de seguridad** → Verifica autenticación/rol
6. **Controlador/View** → Procesa request
7. **Service Layer** → Lógica de negocio
8. **Model Layer** → Acceso a base de datos
9. **Response** → JSON (API) o HTML (Web)
10. **Cliente** → Recibe respuesta

### Separación de Responsabilidades

- **`app/web/`** - Blueprints para páginas HTML (render_template)
- **`app/api/`** - Blueprints para API REST (jsonify)
- **`app/services/`** - Lógica de negocio reutilizable
- **`app/features/`** - Modelos organizados por dominio
- **`app/utils/`** - Utilidades (seguridad, validación, cache)
- **`app/core/`** - Componentes centrales (database)

---

## 📁 ESTRUCTURA DE DIRECTORIOS

```
Gestiones MVP/
│
├── app/                          # Paquete principal de la aplicación
│   ├── __init__.py              # Application factory (create_app)
│   ├── wsgi.py                  # Entry point para Gunicorn
│   │
│   ├── core/                    # Componentes centrales
│   │   ├── __init__.py
│   │   └── database.py         # Instancia SQLAlchemy (db)
│   │
│   ├── features/                # Modelos organizados por dominio
│   │   ├── users/
│   │   │   └── models.py       # User model
│   │   ├── cases/
│   │   │   ├── models.py       # Case model
│   │   │   └── promise.py     # Promise model
│   │   ├── activities/
│   │   │   └── models.py      # Activity model
│   │   └── contact/
│   │       └── models.py      # ContactSubmission model
│   │
│   ├── web/                     # Blueprints para páginas HTML
│   │   ├── auth.py             # Login/Logout
│   │   ├── dashboards.py       # Dashboards por rol
│   │   ├── contact.py          # Formulario de contacto
│   │   ├── admin.py            # Endpoints administrativos
│   │   └── public.py           # Páginas públicas (index, etc.)
│   │
│   ├── api/                     # Blueprints para API REST
│   │   └── v1/
│   │       ├── __init__.py     # Blueprint principal API v1
│   │       ├── cases.py        # Endpoints de casos
│   │       └── activities.py   # Endpoints de actividades
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── dashboard_service.py # Servicio de dashboard (legacy)
│   │   ├── dashboard.py        # Servicio de dashboard (nuevo)
│   │   ├── email_service.py    # Envío de emails
│   │   ├── storage.py          # Almacenamiento de datos
│   │   ├── cache.py            # Cache (legacy)
│   │   └── audit.py            # Auditoría (legacy)
│   │
│   ├── utils/                   # Utilidades
│   │   ├── security.py         # Decoradores de seguridad (@require_role)
│   │   ├── validators.py       # Validaciones de entrada
│   │   ├── cache.py            # Utilidades de cache
│   │   ├── audit.py            # Utilidades de auditoría
│   │   ├── error_handler.py    # Manejo de errores
│   │   └── exceptions.py       # Excepciones personalizadas
│   │
│   ├── templates/               # Plantillas HTML (Jinja2)
│   │   ├── index.html          # Página principal pública
│   │   ├── login.html          # Página de login
│   │   ├── dashboard-admin.html # Dashboard administrativo
│   │   ├── dashboard-gestor.html # Dashboard de gestor
│   │   └── dashboard-user.html  # Panel de usuario
│   │
│   └── models/                  # (Legacy, vacío, usar features/)
│
├── static/                      # Archivos estáticos
│   ├── assets/
│   │   └── images/
│   │       ├── logo.png
│   │       └── logo-dark.png
│   ├── css/
│   │   ├── base/               # Estilos base
│   │   ├── components/         # Componentes reutilizables
│   │   └── pages/              # Estilos por página
│   │       ├── index.css
│   │       ├── login.css
│   │       ├── admin.css
│   │       ├── gestor.css
│   │       └── user.css
│   └── js/
│       ├── lib/
│       │   └── htmx.min.js     # HTMX library
│       ├── components/         # Componentes JS reutilizables
│       ├── pages/              # JavaScript por página
│       │   ├── index.js
│       │   ├── login.js
│       │   ├── admin.js
│       │   ├── gestor.js
│       │   └── user.js
│       └── utils/              # Utilidades JS
│
├── config/                      # Configuración
│   ├── docker/
│   │   ├── Dockerfile          # Dockerfile base
│   │   ├── Dockerfile.dev      # Dockerfile desarrollo
│   │   ├── Dockerfile.prod     # Dockerfile producción
│   │   ├── docker-compose.dev.yml  # Compose desarrollo
│   │   └── docker-compose.prod.yml # Compose producción
│   ├── env/
│   │   ├── env.example         # Plantilla variables
│   │   ├── dev.env.example     # Plantilla desarrollo
│   │   └── prod.env.example    # Plantilla producción
│   ├── alembic.ini             # Configuración Alembic
│   └── pytest.ini              # Configuración pytest
│
├── data/                        # Datos en runtime (gitignored)
│   ├── gestiones.db            # SQLite (desarrollo)
│   └── contact_submissions.json # Submisiones de contacto
│
├── migrations/                  # Migraciones Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/               # Versiones de migraciones
│
├── scripts/                     # Scripts utilitarios
│   ├── deploy/
│   │   ├── deploy.sh           # Script de deployment
│   │   └── install-oci.sh      # Instalación en OCI
│   ├── dev/
│   │   └── create_sample_data.py # Datos de prueba
│   ├── migrations/
│   │   ├── migrate_dummy_data.py
│   │   └── update_existing_cases_management_status.py
│   └── setup/
│       ├── init-prod-db.sh     # Inicialización BD producción
│       ├── setup-oracle-cloud.sh
│       └── verify_setup.py
│
├── tests/                       # Tests
│   ├── conftest.py             # Configuración pytest
│   ├── fixtures/               # Fixtures compartidos
│   ├── unit/                   # Tests unitarios
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_validators.py
│   └── integration/            # Tests de integración
│       ├── test_auth.py
│       ├── test_api.py
│       ├── test_contact.py
│       └── test_dashboard_service.py
│
├── docs/                        # Documentación
│   ├── architecture/
│   ├── deployment/
│   ├── development/
│   └── setup/
│
├── .github/
│   └── workflows/               # GitHub Actions
│       ├── ci.yml              # CI (tests, linting)
│       ├── deploy-production.yml # Deploy producción
│       ├── deploy-develop.yml  # Deploy desarrollo
│       └── test-only.yml       # Solo tests
│
├── requirements.txt            # Dependencias Python
├── .env.dev                    # Variables desarrollo (gitignored)
├── .env.prod                   # Variables producción (gitignored)
├── .gitignore                  # Archivos ignorados
├── README.md                   # Documentación principal
└── SISTEMA.md                  # Este archivo
```

---

## 💾 MODELOS DE DATOS

### User (Usuario)
**Tabla:** `users`  
**Ubicación:** `app/features/users/models.py`

```python
- id: Integer (PK)
- username: String(80), unique, indexed
- password_hash: String(255)
- role: String(20), indexed  # 'admin', 'gestor', 'user'
- active: Boolean, default=True
- created_at: DateTime
- updated_at: DateTime

# Relaciones:
- cases: Relationship → Case (assigned_to_id)
- activities: Relationship → Activity (created_by_id)
```

**Métodos:**
- `set_password(password)` - Hashea y guarda contraseña
- `check_password(password)` - Verifica contraseña
- `to_dict()` - Serializa a diccionario

### Case (Caso/Deuda)
**Tabla:** `cases`  
**Ubicación:** `app/features/cases/models.py`

```python
- id: Integer (PK)
- entity: String(200), indexed  # Entidad que debe
- debtor_name: String(200), indexed
- dni: String(50), indexed, nullable
- amount: Numeric(15, 2)
- status: String(50), indexed, default='en_gestion'
  # Estados: 'en_gestion', 'promesa', 'pagada', 'incobrable'
- management_status: String(50), indexed, nullable, default='sin-gestion'
  # Estados: 'sin-gestion', 'contactado', 'con-arreglo', 'incobrable', 'de-baja'
- cartera: String(100), indexed  # 'A', 'B', 'C', etc.
- assigned_to_id: Integer, FK(users.id), nullable, indexed
- notes: Text, nullable
- created_at: DateTime, indexed
- updated_at: DateTime

# Relaciones:
- promises: Relationship → Promise (case_id)
- activities: Relationship → Activity (case_id)
- assigned_gestor: Backref → User
```

**Métodos:**
- `to_dict(include_relations=False)` - Serializa a diccionario

### Promise (Promesa de Pago)
**Tabla:** `promises`  
**Ubicación:** `app/features/cases/promise.py`

```python
- id: Integer (PK)
- case_id: Integer, FK(cases.id), indexed
- amount: Numeric(15, 2)
- promise_date: Date, indexed
- status: String(50), indexed, default='pending'
  # Estados: 'pending', 'fulfilled', 'broken'
- fulfilled_date: Date, nullable
- notes: Text, nullable
- created_at: DateTime
- updated_at: DateTime

# Relaciones:
- case: Backref → Case
```

**Métodos:**
- `to_dict()` - Serializa a diccionario

### Activity (Actividad/Gestión)
**Tabla:** `activities`  
**Ubicación:** `app/features/activities/models.py`

```python
- id: Integer (PK)
- case_id: Integer, FK(cases.id), indexed
- type: String(50), indexed
  # Tipos: 'call', 'email', 'visit', 'note', 'payment', 'promise'
- notes: Text, nullable
- created_by_id: Integer, FK(users.id), indexed
- created_at: DateTime, indexed

# Relaciones:
- case: Backref → Case
- creator: Backref → User
```

**Métodos:**
- `to_dict()` - Serializa a diccionario

### ContactSubmission (Formulario de Contacto)
**Tabla:** `contact_submissions`  
**Ubicación:** `app/features/contact/models.py`

```python
- id: Integer (PK)
- name: String(200)
- email: String(200)
- phone: String(50), nullable
- message: Text
- created_at: DateTime
```

---

## 🛣️ RUTAS Y ENDPOINTS

### Web Routes (HTML)
**Prefijo:** Ninguno (rutas directas)  
**Blueprint:** `app/web/*`

#### Autenticación (`web/auth.py`)
- `POST /api/login` - Login de usuario
- `GET /logout` - Cerrar sesión

#### Dashboards (`web/dashboards.py`)
- `GET /dashboard-admin` - Dashboard administrativo (requiere rol: admin)
- `GET /dashboard-gestor` - Dashboard de gestor (requiere rol: gestor)
- `GET /dashboard-user` - Panel de usuario (requiere rol: user)

#### Contacto (`web/contact.py`)
- `POST /contact` - Enviar formulario de contacto

#### Admin (`web/admin.py`)
- `GET /submissions` - Ver submisiones de contacto (requiere rol: admin)
- `POST /test-email-config` - Probar configuración de email (requiere rol: admin)

#### Público (`web/public.py`)
- `GET /` - Página principal (index.html)
- `GET /gestiones` - Alias de `/`
- `GET /logo.png` - Logo claro
- `GET /logo-dark.png` - Logo oscuro

### API Routes (REST JSON)
**Prefijo:** `/api/v1`  
**Blueprint:** `app/api/v1/*`

#### Dashboard (`api/v1/cases.py`)
- `GET /api/v1/dashboard/kpis` - KPIs del dashboard (admin)
- `GET /api/v1/dashboard/charts/performance` - Datos gráfico rendimiento (admin)
- `GET /api/v1/dashboard/charts/cartera` - Distribución por cartera (admin)
- `GET /api/v1/dashboard/gestores/ranking` - Ranking de gestores (admin)
- `GET /api/v1/dashboard/stats/comparison` - Comparativa temporal (admin)
- `GET /api/v1/dashboard/cases/status` - Distribución de estados (admin)

#### Casos (`api/v1/cases.py`)
- `GET /api/v1/cases` - Listar casos (con filtros)
- `POST /api/v1/cases` - Crear caso (admin)
- `GET /api/v1/cases/<id>` - Obtener caso específico
- `PUT /api/v1/cases/<id>` - Actualizar caso
- `DELETE /api/v1/cases/<id>` - Eliminar caso (admin)
- `GET /api/v1/cases/gestor` - Casos asignados al gestor actual (gestor)
- `POST /api/v1/update-status` - Actualizar estado de caso
- `POST /api/v1/register-management` - Registrar gestión de caso

#### Promesas (`api/v1/cases.py`)
- `POST /api/v1/cases/<id>/promises` - Crear promesa de pago

#### Actividades (`api/v1/cases.py`, `api/v1/activities.py`)
- `POST /api/v1/cases/<id>/activities` - Crear actividad
- `GET /api/v1/activities/case/<id>` - Listar actividades de un caso
- `DELETE /api/v1/activities/<id>` - Eliminar actividad

#### Health Check
- `GET /healthz` - Health check (público)

---

## 🔧 SERVICIOS Y LÓGICA DE NEGOCIO

### Dashboard Service (`app/services/dashboard.py`)
**Funciones principales:**

- `get_kpis(start_date, end_date, cartera, gestor_id)` - Calcula KPIs
  - Monto recuperado
  - Tasa de recupero
  - Promesas cumplidas (%)
  - Gestiones realizadas

- `get_performance_chart_data(start_date, end_date, cartera, gestor_id)` - Datos para gráfico de rendimiento

- `get_cartera_distribution(start_date, end_date)` - Distribución por cartera

- `get_gestores_ranking(start_date, end_date, limit)` - Ranking de gestores

- `get_cases_status_distribution()` - Distribución de estados de casos

- `get_comparison_data(start_date, end_date)` - Comparativa temporal

**Cache:** Las funciones usan `@cache_result(timeout=300)` para cachear resultados.

### Email Service (`app/services/email_service.py`)
- Envío de emails mediante Flask-Mail
- Configuración SMTP (Zoho por defecto)
- Templates de email

### Storage Service (`app/services/storage.py`)
- Almacenamiento de submisiones de contacto en JSON
- Manejo de archivos de datos

### Cache Service (`app/utils/cache.py`)
- Sistema de cache en memoria
- Decorador `@cache_result` para cachear resultados de funciones
- Invalidación de cache

### Audit Service (`app/services/audit.py`, `app/utils/audit.py`)
- Logging de acciones del sistema
- Auditoría de eventos importantes

---

## 🎨 FRONTEND Y UI

### Tecnologías Frontend
- **HTMX** - Peticiones asíncronas sin recargar página
- **Tailwind CSS** - Framework CSS (CDN)
- **Chart.js** - Gráficos interactivos
- **Lucide Icons** - Iconos
- **JavaScript Vanilla** - Lógica del cliente

### Estructura de Templates

#### `index.html`
- Página principal pública
- Formulario de contacto
- Tema claro/oscuro (localStorage)
- JavaScript: `static/js/pages/index.js`

#### `login.html`
- Formulario de login con HTMX
- Validación en tiempo real
- Manejo de errores
- JavaScript: `static/js/pages/login.js`

#### `dashboard-admin.html`
- Dashboard completo para administradores
- 4 KPIs principales
- 5 gráficos interactivos
- Filtros dinámicos
- Tabla de ranking
- JavaScript: `static/js/pages/admin.js`

#### `dashboard-gestor.html`
- Dashboard personalizado para gestores
- KPIs personales
- Tabla de casos asignados
- Panel de alertas
- Modal de detalles de caso
- Acciones rápidas
- JavaScript: `static/js/pages/gestor.js`

#### `dashboard-user.html`
- Panel básico para usuarios regulares
- Información de sesión
- JavaScript: `static/js/pages/user.js`

### Estilos CSS
- **Base:** Estilos globales y reset
- **Components:** Componentes reutilizables (botones, cards, etc.)
- **Pages:** Estilos específicos por página

### JavaScript
- **Modular:** Un archivo JS por página
- **HTMX:** Para peticiones asíncronas
- **Chart.js:** Para gráficos
- **Tema:** Soporte para tema claro/oscuro

---

## 🗄️ BASE DE DATOS

### Configuración
- **Desarrollo:** SQLite (`data/gestiones.db`)
- **Producción:** PostgreSQL 15 (Docker container)

### Conexión
- **Variable de entorno:** `DATABASE_URL`
- **Formato SQLite:** `sqlite:///path/to/db.db`
- **Formato PostgreSQL:** `postgresql://user:password@host:port/dbname`

### Inicialización
- Las tablas se crean automáticamente con `db.create_all()` en `app/__init__.py`
- Usuarios por defecto se crean automáticamente:
  - `admin` / `admin123` (rol: admin)
  - `gestor` / `gestor123` (rol: gestor)
  - `usuario` / `user123` (rol: user)

### Migraciones
- **Alembic** configurado en `config/alembic.ini`
- Migraciones en `migrations/versions/`
- **Importante:** Las migraciones detectan automáticamente el tipo de BD:
  - **PostgreSQL:** Usa `ON CONFLICT DO NOTHING` para inserts idempotentes
  - **SQLite:** Usa `INSERT OR IGNORE` para inserts idempotentes
- Comandos:
  ```bash
  alembic revision --autogenerate -m "descripción"
  alembic upgrade head
  alembic downgrade -1
  ```
- **Migraciones principales:**
  - `9064f0eb7540` - Add management_status (obsoleta, mantenida por compatibilidad)
  - `20260112225202` - Create carteras table
  - `20260112225203` - Migrate cases cartera to FK
  - `20260112233643` - Refactor cases table and create case_statuses
  - `20260112234500` - Add nro_cliente to cases
  - `a390bb4da27e` - Add address and contact fields to cases

### Scripts de Datos
- `scripts/dev/create_sample_data.py` - Crea datos de prueba
- `scripts/setup/init-prod-db.sh` - Inicializa BD producción

---

## 🔐 AUTENTICACIÓN Y SEGURIDAD

### Autenticación
- **Sesiones basadas en cookies** (Flask sessions)
- **Contraseñas hasheadas** con Werkzeug (`generate_password_hash`, `check_password_hash`)
- **Lifetime de sesión:** 8 horas por defecto (configurable)

### Autorización
- **Sistema de roles:** `admin`, `gestor`, `user`
- **Decorador:** `@require_role("admin")` en `app/utils/security.py`
- **Verificación:** Se verifica en cada request protegido

### Seguridad HTTP
- **Headers de seguridad** configurados en `app/__init__.py`:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: no-referrer`
  - `Content-Security-Policy` (configurado)

### CSRF Protection
- **Flask-SeaSurf** habilitado por defecto en producción
- **Variable:** `ENABLE_CSRF=true` (default: `not app.debug`)

### Rate Limiting
- **Flask-Limiter** configurado
- **Límites por defecto:** 200/día, 50/hora
- **Login:** 5 intentos por minuto
- **Storage:** Redis (si disponible) o memoria

### Validación
- **Validadores** en `app/utils/validators.py`
- **Sanitización** de entrada
- **Marshmallow** para validación de esquemas (futuro)

---

## 🚀 DEPLOYMENT Y DEVOPS

### Docker

#### Desarrollo (`config/docker/docker-compose.dev.yml`)
- **Imagen:** `Dockerfile.dev`
- **Puerto:** `127.0.0.1:5001:5000`
- **Volúmenes:** Código montado para hot-reload
- **Comando:** `flask run --host=0.0.0.0 --port=5000`
- **Base de datos:** SQLite (archivo local)

#### Producción (`config/docker/docker-compose.prod.yml`)
- **Servicios:**
  - `web`: Aplicación Flask con Gunicorn
  - `db`: PostgreSQL 15 Alpine
- **Puerto:** `127.0.0.1:5000:5000` (solo localhost, Nginx futuro)
- **Healthchecks:** Configurados para ambos servicios
- **Volúmenes:** PostgreSQL data persistente
- **Comando:** Gunicorn con 2 workers, 2 threads

### Dockerfiles

#### `Dockerfile.dev`
- Base: `python:3.11-slim`
- Hot-reload habilitado
- Sin optimizaciones

#### `Dockerfile.prod`
- Base: `python:3.11-slim`
- Usuario no-root (`appuser`)
- Optimizado para producción
- Healthcheck configurado
- Gunicorn como servidor

### Oracle Cloud Infrastructure (OCI)

#### Instancias
- **Producción:** `instance-20251104-2312` (puerto 5000)
- **Desarrollo:** `dev--instance-20251119-2332` (puerto 5001)

#### Configuración
- **Path:** `/home/ubuntu/gestiones`
- **Usuario:** `ubuntu`
- **SSH:** Autenticación por clave pública
- **Docker:** Instalado y configurado

### Variables de Entorno

#### Desarrollo (`.env.dev`)
```bash
SECRET_KEY=...
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///data/gestiones.db
```

#### Producción (`.env.prod`)
```bash
SECRET_KEY=...
FLASK_ENV=production
FLASK_DEBUG=0
DATABASE_URL=postgresql://user:password@db:5432/gestiones
DB_PASSWORD=...
MAIL_SERVER=smtp.zoho.com
MAIL_USERNAME=...
MAIL_PASSWORD=...
```

---

## 🔄 CI/CD PIPELINE

### GitHub Actions Workflows

#### `ci.yml`
- **Trigger:** Push a cualquier rama
- **Jobs:**
  - Tests
  - Linting (Flake8)
  - Format check (Black)

#### `deploy-production.yml`
- **Trigger:** Push a `main` o `workflow_dispatch`
- **Jobs:**
  1. **Test:** Tests + linting + coverage (mínimo 70%)
  2. **Deploy:**
     - Backup antes de deployment
     - Pull código desde `main`
     - Rebuild Docker images
     - Restart containers
     - Health check
     - Rollback automático en caso de fallo

#### `deploy-develop.yml`
- **Trigger:** Push a `develop` o `workflow_dispatch`
- **Jobs:**
  1. **Test:** Tests + linting (sin requerir coverage mínimo)
  2. **Deploy:**
     - Pull código desde `develop`
     - Rebuild Docker images
     - Restart containers
     - Health check

### Secrets de GitHub
- `SSH_HOST_PROD` - IP/hostname instancia producción
- `SSH_HOST_DEV` - IP/hostname instancia desarrollo
- `SSH_USER` - Usuario SSH (típicamente `ubuntu`)
- `SSH_KEY_PROD` - Clave privada SSH para producción
- `SSH_KEY_DEV` - Clave privada SSH para desarrollo
- `PROD_PATH` - Path del proyecto en producción (opcional)
- `DEVELOP_PATH` - Path del proyecto en desarrollo (opcional)

### Flujo de Deployment

1. **Push a rama** → GitHub Actions se activa
2. **Tests** → Ejecuta tests y linting
3. **Deploy** → Si tests pasan:
   - SSH a instancia
   - Backup (solo producción)
   - `git pull`
   - `docker-compose down`
   - `docker-compose build --no-cache`
   - `docker-compose up -d`
   - Health check
4. **Rollback** → Si falla, revierte a versión anterior

---

## 🧪 TESTING

### Framework
- **pytest** - Framework principal
- **pytest-cov** - Cobertura de código
- **pytest-flask** - Helpers para Flask

### Estructura de Tests
```
tests/
├── conftest.py              # Configuración y fixtures
├── unit/                    # Tests unitarios
│   ├── test_models.py
│   ├── test_services.py
│   └── test_validators.py
└── integration/             # Tests de integración
    ├── test_auth.py
    ├── test_api.py
    ├── test_contact.py
    └── test_dashboard_service.py
```

### Fixtures (`tests/conftest.py`)
- `app` - Instancia de Flask app para testing
- `client` - Cliente de testing
- `db_session` - Sesión de base de datos
- `admin_user`, `gestor_user`, `user_user` - Usuarios de prueba

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_auth.py -v

# Con más detalle
pytest -v --tb=short
```

### Cobertura Actual
- **Objetivo:** 70% mínimo
- **Actual:** ~71%

---

## 📜 SCRIPTS Y UTILIDADES

### Scripts de Deployment
- `scripts/deploy/deploy.sh` - Script de deployment manual
- `scripts/deploy/install-oci.sh` - Instalación en OCI

### Scripts de Desarrollo
- `scripts/dev/create_sample_data.py` - Crea datos de prueba
- `scripts/dev/import_cases.py` - Importa casos desde datos tabulares
- `scripts/dev/assign_cases.py` - Asigna casos a gestores
- `scripts/dev/update_fechas_pago.py` - Actualiza fechas de último pago
- `scripts/dev/update_dev_instance.sh` - Actualiza instancia de desarrollo (rebuild, migraciones)
- `scripts/dev/fix_migration_status.sh` - Corrige estado de migraciones

### Scripts de Migración de Datos (Producción)
- `scripts/prod/export_data_for_prod.py` - Exporta todos los datos desde develop a JSON
  - Exporta: carteras, case_statuses, casos, usuarios, actividades, promesas
  - Genera: `data/export_for_prod.json`
  - Uso: `python scripts/prod/export_data_for_prod.py`
  
- `scripts/prod/import_data_to_prod.py` - Importa datos exportados a producción
  - Importa: carteras, case_statuses, casos, actividades, promesas
  - **Asigna automáticamente casos al gestor (ID 2)** si no tienen `assigned_to_id`
  - Evita duplicados por `nro_cliente` y nombre
  - Mapea correctamente actividades y promesas usando `nro_cliente`
  - Uso: `docker exec gestiones-mvp-prod python3 scripts/prod/import_data_to_prod.py`
  
- `scripts/prod/verify_prod_data.py` - Verifica que los datos en producción están correctos
  - Muestra resumen de todas las tablas
  - Verifica relaciones y detecta problemas
  - Uso: `docker exec gestiones-mvp-prod python3 scripts/prod/verify_prod_data.py`

### Scripts de Migración (Alembic)
- `scripts/migrations/migrate_dummy_data.py` - Migra datos dummy
- `scripts/migrations/update_existing_cases_management_status.py` - Actualiza management_status

### Scripts de Setup
- `scripts/setup/init-prod-db.sh` - Inicializa BD producción
  - Espera a que PostgreSQL esté listo
  - Ejecuta migraciones de Alembic automáticamente
  - Crea datos por defecto (carteras, estados, usuarios)
- `scripts/setup/setup-oracle-cloud.sh` - Setup inicial en OCI
- `scripts/setup/verify_setup.py` - Verifica configuración

### Proceso de Migración a Producción

#### Paso 1: Exportar datos desde develop
```bash
git checkout develop
python scripts/prod/export_data_for_prod.py
# Genera: data/export_for_prod.json
```

#### Paso 2: Merge a main
```bash
git checkout main
git merge develop
git push origin main
# Dispara deployment automático
```

#### Paso 3: Importar datos en producción
```bash
# Copiar archivo a producción
scp -i privateKey.key data/export_for_prod.json ubuntu@<IP>:/home/ubuntu/gestiones/data/

# En producción, importar
docker exec gestiones-mvp-prod python3 scripts/prod/import_data_to_prod.py
```

#### Notas importantes:
- Los casos se asignan automáticamente al gestor (ID 2) si no tienen `assigned_to_id`
- Las actividades y promesas se mapean correctamente usando `nro_cliente`
- Los usuarios NO se importan (se mantienen separados por seguridad)

---

## 🔑 VARIABLES DE ENTORNO

### Variables Principales

#### Flask
- `SECRET_KEY` - Clave secreta para sesiones (requerida)
- `FLASK_ENV` - Entorno (`development` o `production`)
- `FLASK_APP` - Entry point (`app/wsgi.py`)
- `FLASK_DEBUG` - Modo debug (0 o 1)

#### Base de Datos
- `DATABASE_URL` - URL de conexión a BD
- `DB_PASSWORD` - Contraseña PostgreSQL (solo producción)
- `SQLALCHEMY_ECHO` - Log SQL queries (debug)

#### Sesiones
- `SESSION_COOKIE_SECURE` - Cookie segura (HTTPS)
- `SESSION_COOKIE_SAMESITE` - SameSite policy (`Lax`, `Strict`, `None`)
- `SESSION_LIFETIME_HOURS` - Duración de sesión (default: 8)

#### Email
- `MAIL_SERVER` - Servidor SMTP (default: `smtp.zoho.com`)
- `MAIL_PORT` - Puerto SMTP (default: 465)
- `MAIL_USE_TLS` - Usar TLS (default: False)
- `MAIL_USE_SSL` - Usar SSL (default: True)
- `MAIL_USERNAME` - Usuario SMTP
- `MAIL_PASSWORD` - Contraseña SMTP
- `MAIL_DEFAULT_SENDER` - Remitente por defecto

#### Seguridad
- `ENABLE_CSRF` - Habilitar CSRF (default: `not app.debug`)
- `REDIS_URL` - URL Redis para rate limiting (default: `memory://`)

#### Contacto
- `CONTACT_RECIPIENTS` - Destinatarios de contacto (separados por coma)

#### Testing
- `TESTING` - Modo testing (evita crear usuarios por defecto)

---

## 🔍 TROUBLESHOOTING

### Problemas Comunes

#### 1. Error: "ContainerConfig" en Docker Compose
**Causa:** Metadata corrupta de contenedor antiguo  
**Solución:**
```bash
docker rm <container_id>
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

#### 2. Error: "password authentication failed" PostgreSQL
**Causa:** Contraseña no coincide o BD recreada  
**Solución:**
- Verificar `DB_PASSWORD` en `.env.prod`
- Recrear volumen: `docker-compose down -v`
- Rebuild: `docker-compose up -d --build`

#### 3. Error: "ModuleNotFoundError" después de git pull
**Causa:** Dependencias nuevas no instaladas  
**Solución:**
```bash
docker-compose build --no-cache
docker-compose up -d
```

#### 4. Error: "syntax error at or near OR" en migraciones PostgreSQL
**Causa:** Migración usa sintaxis SQLite (`INSERT OR IGNORE`) en PostgreSQL  
**Solución:** Las migraciones ya están corregidas para detectar el tipo de BD automáticamente. Si persiste:
```bash
# Verificar migraciones aplicadas
docker exec gestiones-mvp-prod alembic -c config/alembic.ini current

# Si es necesario, marcar migración como aplicada
docker exec gestiones-mvp-prod alembic -c config/alembic.ini stamp <revision>
```

#### 5. Error: "duplicate key value violates unique constraint" en PostgreSQL
**Causa:** Restos de creación anterior fallida en PostgreSQL  
**Solución:**
```bash
# Eliminar volumen de PostgreSQL
docker-compose down
docker volume rm docker_postgres_data
docker-compose up -d
# Ejecutar migraciones nuevamente
docker exec gestiones-mvp-prod alembic -c config/alembic.ini upgrade head
```

#### 6. Error: "DB_PASSWORD variable is not set" en docker-compose
**Causa:** docker-compose no está leyendo `.env.prod`  
**Solución:**
```bash
# Usar flag --env-file explícitamente
docker-compose -f config/docker/docker-compose.prod.yml --env-file .env.prod up -d
```

#### 7. Casos no aparecen para gestores
**Causa:** Casos tienen `assigned_to_id = None`  
**Solución:**
```bash
# Asignar todos los casos al gestor (ID 2)
docker exec gestiones-mvp-prod python3 -c "import sqlite3; conn = sqlite3.connect('/app/data/gestiones.db'); c = conn.cursor(); c.execute('UPDATE cases SET assigned_to_id = 2 WHERE assigned_to_id IS NULL'); conn.commit(); conn.close()"
# O para PostgreSQL:
docker exec gestiones-mvp-prod python3 << 'PYTHON'
import sys; sys.path.insert(0, '/app')
from app import create_app
from app.core.database import db
from app.features.cases.models import Case
app = create_app()
with app.app_context():
    casos = Case.query.filter(Case.assigned_to_id.is_(None)).all()
    for caso in casos: caso.assigned_to_id = 2
    db.session.commit()
PYTHON
```

#### 4. Logo no aparece en producción
**Causa:** Ruta incorrecta en JavaScript o cache  
**Solución:**
- Verificar rutas absolutas en `static/js/pages/index.js`
- Rebuild contenedor
- Limpiar cache del navegador (Ctrl+Shift+R)

#### 5. Error: "Connection in use" puerto 5001/5000
**Causa:** Contenedor o proceso usando el puerto  
**Solución:**
```bash
docker ps
docker stop <container_name>
# O
sudo lsof -i :5001
sudo kill <PID>
```

#### 6. Error: "Failed to load environment files"
**Causa:** Archivo `.env.dev` o `.env.prod` no encontrado  
**Solución:**
- Verificar que existe en la raíz del proyecto
- Verificar ruta en `docker-compose.yml`

### Comandos Útiles

#### Docker
```bash
# Ver logs
docker logs gestiones-mvp-prod --tail=50 -f

# Entrar al contenedor
docker exec -it gestiones-mvp-prod bash

# Ver estado
docker ps | grep gestiones

# Rebuild
docker-compose -f config/docker/docker-compose.prod.yml build --no-cache
docker-compose -f config/docker/docker-compose.prod.yml up -d
```

#### Base de Datos
```bash
# Conectar a PostgreSQL
docker exec -it gestiones-db-prod psql -U gestiones_user -d gestiones

# Backup
docker exec gestiones-db-prod pg_dump -U gestiones_user gestiones > backup.sql

# Restore
docker exec -i gestiones-db-prod psql -U gestiones_user gestiones < backup.sql
```

#### Git
```bash
# Descartar cambios locales
git checkout -- <file>
git reset --hard origin/main

# Ver estado
git status
git log --oneline -10
```

---

## 📝 NOTAS IMPORTANTES

### Convenciones de Código
- **Python:** PEP 8, type hints donde sea posible
- **Nombres:** snake_case para funciones/variables, PascalCase para clases
- **Imports:** Organizados (stdlib, third-party, local)
- **Docstrings:** En funciones y clases importantes

### Estructura de Commits
- Prefijos: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Ejemplo: `fix: corregir rutas del logo en JavaScript`

### Branches
- `main` - Producción
- `develop` - Desarrollo
- Feature branches: `feature/nombre-feature`

### Archivos Ignorados (`.gitignore`)
- `.env*` - Variables de entorno
- `data/*.db` - Bases de datos SQLite
- `__pycache__/` - Cache Python
- `*.pyc` - Bytecode Python
- `venv/` - Entornos virtuales
- `*.log` - Logs

### Archivos Importantes NO Ignorados
- `static/js/lib/htmx.min.js` - HTMX library
- `static/assets/images/logo*.png` - Logos
- `requirements.txt` - Dependencias
- `config/` - Configuración (sin secrets)

---

## 🔄 FLUJOS PRINCIPALES

### Flujo de Login
1. Usuario accede a `/` → redirige a `/login` si no autenticado
2. Usuario ingresa credenciales → `POST /api/login`
3. Backend valida usuario y contraseña
4. Si válido: crea sesión, redirige según rol
5. Si inválido: retorna error, muestra mensaje

### Flujo de Dashboard Admin
1. Usuario autenticado como admin → `GET /dashboard-admin`
2. Template carga → JavaScript inicializa
3. JavaScript hace requests a `/api/v1/dashboard/*`
4. Backend calcula KPIs y datos
5. Frontend renderiza gráficos y tablas
6. Filtros actualizan datos dinámicamente

### Flujo de Gestión de Caso (Gestor)
1. Gestor accede a `/dashboard-gestor`
2. Ve lista de casos asignados
3. Click en caso → Modal con detalles
4. Realiza acción (llamada, promesa, pago) → `POST /api/v1/*`
5. Backend actualiza BD
6. Frontend actualiza UI sin recargar

### Flujo de Deployment
1. Developer hace push a `main` o `develop`
2. GitHub Actions se activa
3. Ejecuta tests y linting
4. Si pasa: SSH a instancia
5. Backup (solo producción)
6. `git pull`
7. Rebuild Docker images
8. **Ejecuta migraciones de Alembic automáticamente** (producción)
9. Restart containers
10. Health check
11. Si falla: Rollback automático

### Flujo de Migración de Datos a Producción
1. **Exportar datos desde develop:**
   ```bash
   python scripts/prod/export_data_for_prod.py
   ```
2. **Hacer merge a main:**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```
3. **Esperar deployment automático** (ejecuta migraciones)
4. **Copiar archivo JSON a producción:**
   ```bash
   scp -i privateKey.key data/export_for_prod.json ubuntu@<IP>:/home/ubuntu/gestiones/data/
   ```
5. **Importar datos:**
   ```bash
   docker exec gestiones-mvp-prod python3 scripts/prod/import_data_to_prod.py
   ```
6. **Verificar:**
   ```bash
   docker exec gestiones-mvp-prod python3 scripts/prod/verify_prod_data.py
   ```

---

## 📚 REFERENCIAS Y RECURSOS

### Documentación Externa
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [HTMX Documentation](https://htmx.org/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Documentación Interna
- `README.md` - Documentación principal del proyecto
- `docs/` - Documentación adicional
- `RESUMEN.md` - Resumen del sistema

---

## ✅ CHECKLIST DE MANTENIMIENTO

### Antes de Hacer Cambios
- [ ] Leer este documento (SISTEMA.md)
- [ ] Verificar branch correcta
- [ ] Hacer backup si es necesario
- [ ] Ejecutar tests localmente

### Después de Hacer Cambios
- [ ] Ejecutar tests: `pytest`
- [ ] Verificar linting: `flake8 app tests`
- [ ] Actualizar documentación si es necesario
- [ ] Commit con mensaje descriptivo
- [ ] Push y verificar CI/CD

### Migración de Datos a Producción
- [ ] Exportar datos desde develop: `python scripts/prod/export_data_for_prod.py`
- [ ] Hacer merge a main y push
- [ ] Esperar deployment automático (ejecuta migraciones)
- [ ] Copiar `export_for_prod.json` a producción
- [ ] Importar datos: `docker exec gestiones-mvp-prod python3 scripts/prod/import_data_to_prod.py`
- [ ] Verificar datos: `docker exec gestiones-mvp-prod python3 scripts/prod/verify_prod_data.py`
- [ ] Verificar que los casos están asignados al gestor correcto

### Deployment
- [ ] Verificar que tests pasan en CI
- [ ] Revisar logs de deployment
- [ ] Verificar health check
- [ ] Probar funcionalidad en producción
- [ ] Monitorear logs después del deployment

---

**FIN DEL DOCUMENTO**

*Este documento debe actualizarse cuando se realicen cambios significativos en la arquitectura, estructura o funcionamiento del sistema.*

