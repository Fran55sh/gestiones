# Sistema de Gestión de Deudas

Sistema completo de gestión de deudas con roles de usuario y dashboard administrativo.

## 🚀 Características

### Login System
- ✨ Interfaz moderna y responsive
- 🚀 HTMX para peticiones asíncronas
- 💅 Animaciones suaves
- ⚠️ Manejo de errores
- 🔐 Validación de formularios
- 👥 Sistema de roles (Admin/Usuario)

### Dashboard Administrativo
- 📊 KPIs en tiempo real (Monto recuperado, Tasa de recupero, Promesas cumplidas, Gestiones realizadas)
- 📈 Gráficos de rendimiento con Chart.js
- 🏆 Ranking de gestores interactivo
- 📉 Distribución por cartera (gráfico de dona)
- 📊 Estado actual de deudas
- ⚠️ Alertas e insights automáticos
- 🔍 Filtros dinámicos por fecha, cartera y gestor
- 📊 Comparativa temporal (mes actual vs anterior)
- 📥 Exportación de reportes (Excel, PDF)

### Dashboard de Gestor de Deudas 🆕
- 📋 Vista personalizada con casos asignados
- 💰 5 KPIs personales (Monto recuperado, Promesas cumplidas, Casos activos/finalizados, Tiempo promedio)
- 📊 Tabla interactiva de casos con ordenamiento y filtrado
- 🔍 Búsqueda por nombre o DNI
- ⚠️ Panel de alertas personales (promesas por vencer, pagos pendientes, sin contacto)
- 📈 Gráfico de desempeño personal (últimas 2 semanas)
- 🔧 Modal detallado de casos con pestañas (Info, Historial, Montos, Notas)
- ⚡ Acciones rápidas: Registrar llamada, Agregar promesa, Confirmar pago, Marcar incobrable, Agendar gestión
- 🎯 Resumen del día: Promesas nuevas, Pagos confirmados, Casos pendientes, Meta del día

### Panel de Usuario
- Panel básico para usuarios regulares
- Información de sesión
- Navegación simple

## 🐳 Dockerización

La aplicación está completamente dockerizada y lista para ejecutarse en contenedores.

### Requisitos
- Docker Engine 20.10+
- Docker Compose 2.0+

### 🚀 Ejecución con Docker Compose

#### Para Desarrollo Local (puerto 5001):
```bash
# Configurar variables de entorno
cp env/dev.env.example .env.dev
# Editar .env.dev con tus valores

# Construir y ejecutar en segundo plano
docker compose -f docker-compose.dev.yml --project-name gestiones-dev --env-file .env.dev up --build -d

# Ver logs
docker compose -f docker-compose.dev.yml --project-name gestiones-dev logs -f

# Detener
docker compose -f docker-compose.dev.yml --project-name gestiones-dev down

# Acceder: http://localhost:5001
```

#### Para Producción Local (puerto 5000):
```bash
# Configurar variables de entorno
cp env/prod.env.example .env.prod
# Editar .env.prod con tus valores (SECRET_KEY, MAIL_*, etc.)

# Construir y ejecutar en segundo plano
docker compose -f docker-compose.prod.yml --project-name gestiones-prod --env-file .env.prod up --build -d

# Ver logs
docker compose -f docker-compose.prod.yml --project-name gestiones-prod logs -f

# Detener
docker compose -f docker-compose.prod.yml --project-name gestiones-prod down

# Acceder: http://localhost:5000
```

### 📋 Archivos Docker incluidos

- `Dockerfile.prod` - Imagen optimizada para producción con Gunicorn
- `Dockerfile.dev` - Imagen de desarrollo con hot-reload
- `docker-compose.prod.yml` - Configuración para producción
- `docker-compose.dev.yml` - Configuración para desarrollo
- `.dockerignore` - Archivos excluidos del build

## 📦 Instalación Local (Sin Docker)

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Configura variables de entorno:
```bash
cp env/dev.env.example .env
# Editar .env con tus valores
```

3. Inicia el servidor:
```bash
# Opción 1: Usando Flask CLI
export FLASK_APP=app/wsgi.py
flask run

# Opción 2: Usando Python directamente
python -m app.wsgi

# Opción 3: Usando Gunicorn (producción)
gunicorn app.wsgi:app --bind 0.0.0.0:5000
```

4. Abre tu navegador en: `http://localhost:5000`

## 🔑 Credenciales de Prueba

### Administrador (Dashboard Completo)
- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Acceso:** Dashboard completo con métricas, gráficos y análisis detallados

### Gestor de Deudas 🆕 (Dashboard de Gestor)
- **Usuario:** `gestor`
- **Contraseña:** `gestor123`
- **Acceso:** Dashboard personalizado para gestión individual de casos con todas las herramientas de productividad

### Usuario Regular (Panel Básico)
- **Usuario:** `usuario`
- **Contraseña:** `user123`
- **Acceso:** Panel básico de información

## 📁 Estructura de Archivos

```
Gestiones MVP/
├── app/                          # Paquete principal de la aplicación
│   ├── __init__.py              # Application factory
│   ├── wsgi.py                  # Entry point para Gunicorn
│   ├── routes/                  # Blueprints (rutas)
│   │   ├── auth.py             # Login/logout
│   │   ├── dashboards.py       # Dashboards por rol
│   │   ├── contact.py          # Formulario de contacto
│   │   ├── admin.py            # Endpoints administrativos
│   │   └── root.py             # Páginas raíz
│   ├── services/               # Lógica de negocio
│   │   ├── email_service.py    # Envío de emails
│   │   └── storage.py          # Almacenamiento de datos
│   ├── utils/                  # Utilidades
│   │   ├── security.py         # Decoradores y seguridad
│   │   └── validators.py       # Validaciones
│   └── templates/              # Plantillas HTML
│       ├── index.html
│       ├── login.html
│       ├── dashboard-admin.html
│       ├── dashboard-gestor.html
│       └── dashboard-user.html
├── static/                      # Archivos estáticos
│   ├── css/                    # Hojas de estilo
│   ├── js/                     # JavaScript (incluye htmx.min.js)
│   └── ...
├── data/                        # Datos en runtime (gitignored)
├── env/                         # Plantillas de variables de entorno
│   ├── dev.env.example
│   └── prod.env.example
├── docs/                        # Documentación
├── Dockerfile.prod              # Docker para producción
├── Dockerfile.dev              # Docker para desarrollo
├── docker-compose.prod.yml     # Compose para producción
├── docker-compose.dev.yml      # Compose para desarrollo
├── requirements.txt            # Dependencias Python
└── README.md                   # Este archivo
```

## 🎨 Tecnologías Utilizadas

- **Flask 3.0** - Backend Python con Application Factory pattern
- **HTMX** - Peticiones asíncronas sin JavaScript complejo (servido localmente)
- **Tailwind CSS** - Framework CSS utility-first (CDN en desarrollo)
- **Lucide Icons** - Iconos modernos
- **Chart.js** - Gráficos interactivos y visualizaciones
- **Gunicorn** - Servidor WSGI para producción
- **Docker** - Containerización

## 📊 Funcionalidades del Dashboard

### KPIs Principales
1. **Monto Total Recuperado** - Suma global del período
2. **Tasa de Recupero** - Porcentaje de deuda recuperada
3. **Promesas Cumplidas** - Tasa de cumplimiento de promesas
4. **Gestiones Realizadas** - Total de contactos/caso

### Visualizaciones
- **Gráfico de barras apiladas** - Rendimiento por semana y cartera
- **Gráfico de dona** - Distribución por cartera
- **Tabla de ranking** - Desempeño de gestores
- **Barras horizontales** - Estado de deudas
- **Gráfico de líneas** - Comparativa temporal

### Filtros y Controles (Admin)
- Selector de rango de fechas
- Filtro por cartera
- Filtro por gestor
- Chips de filtro rápidos
- Exportación a Excel/PDF

### Funcionalidades del Dashboard de Gestor
1. **Header Personalizado**: Nombre del gestor, fecha actual, resumen del día
2. **5 KPIs Personales**: Monto del mes, Promesas cumplidas, Casos activos/finalizados, Tiempo promedio
3. **Tabla de Casos**: Lista completa con ordenamiento por columnas
4. **Panel Lateral de Alertas**: Promesas por vencer, casos sin contacto, pagos pendientes
5. **Modal de Detalles**: Pestañas para Info, Historial, Montos y Notas
6. **Acciones Rápidas**: Botones para todas las acciones comunes
7. **Búsqueda**: Por nombre o DNI con filtros por estado
8. **Gráfico Personal**: Evolución de desempeño de las últimas 2 semanas

## 🔒 Seguridad

- Sesiones basadas en cookies con lifetime configurable
- Autenticación por roles con decoradores
- Protección de rutas por rol
- Contraseñas hasheadas con Werkzeug
- Content Security Policy (CSP) configurada
- Headers de seguridad (X-Frame-Options, X-Content-Type-Options, etc.)
- CSRF opcional (Flask-SeaSurf, activable vía `ENABLE_CSRF=true`)
- Validación y sanitización de entrada
- ProxyFix para detrás de Nginx/Load Balancer

## 📝 Próximos Pasos (Para Producción)

- [x] Docker containerization ✅
- [x] Estructura modular con blueprints ✅
- [x] Contraseñas hasheadas ✅
- [x] Headers de seguridad ✅
- [x] CSRF opcional ✅
- [ ] Integración con base de datos (PostgreSQL/MySQL)
- [ ] Rate limiting (Flask-Limiter)
- [x] Tests unitarios básicos ✅
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoreo y logging estructurado
- [ ] Nginx reverse proxy con SSL
- [ ] Implementar visualización de solicitudes de contacto en dashboard admin

## 🛠️ Desarrollo

### Estructura del Código

La aplicación usa una arquitectura modular con **Application Factory**:

- **`app/__init__.py`**: Crea la instancia de Flask y configura la aplicación
- **`app/wsgi.py`**: Entry point para Gunicorn (`app.wsgi:app`)
- **`app/routes/`**: Blueprints organizados por funcionalidad
- **`app/services/`**: Lógica de negocio reutilizable
- **`app/utils/`**: Utilidades y helpers

### Agregar Nuevas Rutas

1. Crea un nuevo blueprint en `app/routes/`:
```python
from flask import Blueprint
bp = Blueprint('mi_feature', __name__)

@bp.route('/mi-ruta')
def mi_funcion():
    return "Hola"
```

2. Regístralo en `app/__init__.py`:
```python
from .routes.mi_feature import bp as mi_feature_bp
app.register_blueprint(mi_feature_bp)
```

### Variables de Entorno

Copia las plantillas y configura:
- `env/dev.env.example` → `.env.dev` (desarrollo)
- `env/prod.env.example` → `.env.prod` (producción)

Variables críticas:
- `SECRET_KEY`: Genera con `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `MAIL_*`: Credenciales de email
- `CONTACT_RECIPIENTS`: Destinatarios separados por coma

## 🧪 Testing

### Ejecutar Tests

```bash
# Instalar dependencias de testing (ya incluidas en requirements.txt)
pip install -r requirements.txt

# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app --cov-report=html

# Ejecutar tests específicos
pytest tests/test_auth.py
pytest tests/test_contact.py -v

# Ejecutar con más detalle
pytest -v --tb=short
```

### Estructura de Tests

```
tests/
├── conftest.py           # Configuración y fixtures compartidos
├── test_auth.py          # Tests de autenticación
├── test_contact.py       # Tests de formulario de contacto
├── test_admin.py         # Tests de endpoints administrativos
├── test_validators.py    # Tests de validadores
├── test_services.py      # Tests de servicios (email, storage)
├── test_security.py      # Tests de seguridad y roles
├── test_error_handling.py # Tests de manejo de errores
└── test_health.py        # Tests de endpoints de salud
```

### Cobertura de Tests

Los tests cubren:
- ✅ Autenticación y autorización
- ✅ Validación de entrada
- ✅ Servicios (email, storage)
- ✅ Manejo de errores
- ✅ Endpoints administrativos
- ✅ Formulario de contacto
- ✅ Health checks

Para ver el reporte de cobertura:
```bash
pytest --cov=app --cov-report=html
# Abrir htmlcov/index.html en el navegador
```

## 📧 Soporte

Para dudas o problemas, revisa la documentación de:
- [HTMX](https://htmx.org)
- [Chart.js](https://www.chartjs.org)
- [Flask](https://flask.palletsprojects.com)
