# Estructura del Proyecto - Gestiones MVP

## Estructura Reorganizada

```
Gestiones-MVP/
├── app/                        # Aplicación Flask
│   ├── api/                    # API REST endpoints
│   │   └── v1/                 # API v1
│   │       ├── cases.py        # Endpoints de casos
│   │       └── activities.py   # Endpoints de actividades
│   │
│   ├── web/                    # Rutas web (HTML)
│   │   ├── auth.py             # Login/logout
│   │   ├── dashboards.py       # Dashboards
│   │   ├── admin.py            # Admin views
│   │   ├── public.py           # Páginas públicas
│   │   └── contact.py          # Contacto
│   │
│   ├── core/                   # Core framework
│   │   └── database.py         # SQLAlchemy db instance
│   │
│   ├── features/               # Domain logic
│   │   ├── cases/              # Casos y promesas
│   │   ├── activities/         # Gestiones
│   │   ├── users/              # Usuarios
│   │   └── contact/            # Contacto
│   │
│   ├── services/               # Servicios compartidos
│   │   ├── dashboard.py        # Agregación de datos
│   │   ├── cache.py            # Caché Redis
│   │   ├── audit.py            # Auditoría
│   │   ├── storage.py          # Almacenamiento
│   │   └── email_service.py    # Envío de emails
│   │
│   ├── utils/                  # Utilidades
│   │   ├── exceptions.py       # Excepciones custom
│   │   ├── validators.py       # Validadores
│   │   ├── security.py         # Seguridad
│   │   └── error_handler.py    # Manejo de errores
│   │
│   ├── templates/              # Templates Jinja2
│   └── __init__.py             # Application factory
│
├── static/                     # Assets estáticos
│   ├── css/
│   │   ├── base/               # Estilos base
│   │   ├── components/         # Componentes
│   │   └── pages/              # Por página
│   ├── js/
│   │   ├── lib/                # Librerías (htmx)
│   │   ├── utils/              # Utilidades JS
│   │   ├── components/         # Componentes JS
│   │   └── pages/              # Por página
│   └── assets/
│       └── images/             # Imágenes y logos
│
├── config/                     # Configuración
│   ├── docker/                 # Docker files
│   ├── env/                    # Environment examples
│   ├── alembic.ini             # Alembic config
│   └── pytest.ini              # Pytest config
│
├── docs/                       # Documentación
│   ├── setup/                  # Setup e instalación
│   ├── deployment/             # Despliegue
│   ├── architecture/           # Arquitectura
│   └── development/            # Para desarrolladores
│
├── migrations/                 # Alembic migrations
│   └── versions/
│
├── scripts/                    # Scripts de utilidad
│   ├── setup/                  # Setup inicial
│   ├── migrations/             # Data migrations
│   ├── dev/                    # Desarrollo
│   └── deploy/                 # Deployment
│
├── tests/                      # Tests
│   ├── unit/                   # Tests unitarios
│   ├── integration/            # Tests de integración
│   ├── fixtures/               # Test fixtures
│   └── conftest.py
│
├── data/                       # Runtime data
│   ├── gestiones.db            # SQLite database
│   └── contact_submissions.json
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Beneficios de la Nueva Estructura

### 1. Claridad
- Código organizado por dominio/feature
- Fácil encontrar archivos relacionados
- Separación clara entre API y Web

### 2. Escalabilidad
- Fácil agregar nuevos módulos
- Features independientes
- API versionada (v1, v2, etc.)

### 3. Mantenibilidad
- Código relacionado está junto
- Tests organizados por tipo
- Documentación categorizada

### 4. Estándares
- Sigue convenciones Flask modernas
- Estructura feature-based
- Separación de responsabilidades

## Imports

### Antes
```python
from ..db import db
from ..models import User, Case
```

### Después
```python
from ..core.database import db
from ..features.users.models import User
from ..features.cases.models import Case
```

## Rutas Estáticas

### Antes
```html
<script src="/static/js/dashboard-admin.js"></script>
<link rel="stylesheet" href="/static/css/dashboard-admin.css">
```

### Después
```html
<script src="/static/js/pages/admin.js"></script>
<link rel="stylesheet" href="/static/css/pages/admin.css">
```

## Migración Completada

✅ Backend reorganizado (app/)
✅ Frontend reorganizado (static/)
✅ Documentación reorganizada (docs/)
✅ Configuración reorganizada (config/)
✅ Scripts reorganizados (scripts/)
✅ Tests reorganizados (tests/)
✅ Todos los imports actualizados
✅ Todas las rutas verificadas
✅ Aplicación funcional

## Próximos Pasos

1. Revisar y actualizar README.md principal
2. Actualizar referencias en CI/CD si es necesario
3. Documentar nuevos patrones para el equipo
4. Considerar crear schemas (Pydantic/Marshmallow) para validación

