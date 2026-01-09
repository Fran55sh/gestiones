# Migración a Estructura Modular

## Estado Actual

✅ **La aplicación ahora usa una estructura modular con Application Factory**
✅ **Código organizado en blueprints, services y utils**

## Nueva Estructura

```
app/
├── __init__.py          # Application factory
├── wsgi.py              # Entry point para Gunicorn
├── routes/              # Blueprints
│   ├── auth.py
│   ├── dashboards.py
│   ├── contact.py
│   ├── admin.py
│   └── root.py
├── services/            # Lógica de negocio
│   ├── email_service.py
│   └── storage.py
├── utils/               # Utilidades
│   ├── security.py
│   └── validators.py
└── templates/           # Plantillas HTML
```

## Cambios Principales

### Antes (app_refactored.py)
- Todo el código en un solo archivo
- Funciones mezcladas
- Difícil de mantener y escalar

### Ahora (Estructura Modular)
- Código separado por responsabilidad
- Blueprints para rutas
- Services para lógica de negocio
- Utils para funciones reutilizables
- Fácil de mantener y escalar

## Cómo Usar

### Desarrollo Local
```bash
# Configurar variables
cp env/dev.env.example .env.dev

# Levantar desarrollo (puerto 5001)
docker compose -f docker-compose.dev.yml --project-name gestiones-dev --env-file .env.dev up --build -d

# Ver logs
docker compose -f docker-compose.dev.yml --project-name gestiones-dev logs -f
```

### Producción Local
```bash
# Configurar variables
cp env/prod.env.example .env.prod

# Levantar producción (puerto 5000)
docker compose -f docker-compose.prod.yml --project-name gestiones-prod --env-file .env.prod up --build -d
```

### Sin Docker
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables
cp env/dev.env.example .env

# Ejecutar
export FLASK_APP=app/wsgi.py
flask run

# O con Gunicorn
gunicorn app.wsgi:app --bind 0.0.0.0:5000
```

## Entry Point

El entry point para Gunicorn es: `app.wsgi:app`

Esto se configura en:
- `Dockerfile.prod`: `CMD ["gunicorn", ..., "app.wsgi:app"]`
- `docker-compose.prod.yml`: `FLASK_APP=app/wsgi.py`

## Agregar Nuevas Funcionalidades

### 1. Nuevo Blueprint
```python
# app/routes/mi_feature.py
from flask import Blueprint
bp = Blueprint('mi_feature', __name__)

@bp.route('/mi-ruta')
def mi_funcion():
    return "Hola"
```

### 2. Registrar en app/__init__.py
```python
from .routes.mi_feature import bp as mi_feature_bp
app.register_blueprint(mi_feature_bp)
```

### 3. Nuevo Service
```python
# app/services/mi_service.py
def mi_funcion_servicio():
    # Lógica aquí
    pass
```

## Ventajas de la Nueva Estructura

1. **Mantenibilidad**: Código organizado y fácil de encontrar
2. **Escalabilidad**: Fácil agregar nuevas funcionalidades
3. **Testabilidad**: Módulos independientes fáciles de testear
4. **Colaboración**: Múltiples desarrolladores pueden trabajar en paralelo
5. **Best Practices**: Sigue estándares de Flask

## Verificar Funcionamiento

1. **Healthcheck**: `http://localhost:5001/healthz`
2. **Página principal**: `http://localhost:5001/`
3. **Login**: `http://localhost:5001/gestiones`
4. **Dashboards**: Después de login según rol

## Troubleshooting

### Error: "No module named 'app'"
- Verifica que estés en el directorio raíz del proyecto
- Verifica que `app/__init__.py` existe

### Error: "ModuleNotFoundError"
- Verifica que todas las dependencias estén en `requirements.txt`
- Ejecuta `pip install -r requirements.txt`

### Error en Docker
- Verifica que `FLASK_APP=app/wsgi.py` esté configurado
- Verifica que el comando sea `app.wsgi:app` para Gunicorn

