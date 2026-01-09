# Guía de Pruebas - Nueva Implementación

Esta guía te ayudará a probar todas las nuevas funcionalidades implementadas.

## 📋 Prerequisitos

- Python 3.11+
- pip actualizado
- Git (opcional, para CI/CD)

## 🚀 Paso 1: Instalar Dependencias

```bash
# Instalar todas las nuevas dependencias
pip install -r requirements.txt
```

**Dependencias nuevas agregadas:**
- Flask-SQLAlchemy (base de datos)
- alembic (migraciones)
- Flask-Limiter (rate limiting)
- Flask-Compress (compresión)
- redis (cache, opcional)
- marshmallow (validación)

## 🗄️ Paso 2: Configurar Base de Datos

### Opción A: SQLite (Recomendado para desarrollo)

La aplicación usará SQLite por defecto si no se configura `DATABASE_URL`. La base de datos se creará automáticamente en `data/gestiones.db`.

```bash
# No necesitas hacer nada, se crea automáticamente
```

### Opción B: PostgreSQL (Para producción)

```bash
# Configurar variable de entorno
export DATABASE_URL="postgresql://usuario:password@localhost:5432/gestiones_db"

# O en Windows PowerShell:
$env:DATABASE_URL="postgresql://usuario:password@localhost:5432/gestiones_db"
```

## 🔧 Paso 3: Inicializar Base de Datos

La aplicación creará automáticamente las tablas y migrará los usuarios por defecto al iniciar.

```bash
# Iniciar la aplicación (esto creará las tablas automáticamente)
python -m app.wsgi
```

O con Flask CLI:
```bash
export FLASK_APP=app/wsgi.py
flask run
```

**Usuarios por defecto creados automáticamente:**
- `admin` / `admin123` (rol: admin)
- `gestor` / `gestor123` (rol: gestor)
- `usuario` / `user123` (rol: user)

## ✅ Paso 4: Verificar que Todo Funciona

### 4.1 Verificar Base de Datos

```bash
# Verificar que el archivo de base de datos existe
ls data/gestiones.db  # Linux/Mac
dir data\gestiones.db  # Windows
```

### 4.2 Probar Login

1. Abre el navegador en `http://localhost:5000/gestiones`
2. Intenta hacer login con:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. Deberías ser redirigido a `/dashboard-admin`

### 4.3 Verificar APIs del Dashboard

Abre la consola del navegador (F12) en el dashboard y verifica que:
- Los KPIs se cargan correctamente
- Los gráficos se muestran con datos
- No hay errores en la consola

O prueba manualmente con curl:

```bash
# Obtener KPIs (necesitas estar autenticado)
curl -X GET http://localhost:5000/api/dashboard/kpis \
  -H "Cookie: session=tu_session_cookie"
```

## 🧪 Paso 5: Ejecutar Tests

### 5.1 Ejecutar Todos los Tests

```bash
# Ejecutar todos los tests
pytest

# Con más detalle
pytest -v

# Con cobertura
pytest --cov=app --cov-report=html --cov-report=term
```

### 5.2 Ejecutar Tests Específicos

```bash
# Tests de modelos
pytest tests/test_models.py -v

# Tests de APIs
pytest tests/test_api.py -v

# Tests de servicios
pytest tests/test_dashboard_service.py -v
```

### 5.3 Ver Reporte de Cobertura

```bash
# Generar reporte HTML
pytest --cov=app --cov-report=html

# Abrir en navegador
# Linux/Mac:
open htmlcov/index.html
# Windows:
start htmlcov/index.html
```

## 🔍 Paso 6: Probar Funcionalidades Específicas

### 6.1 Probar CRUD de Casos

**Crear un caso:**
```bash
curl -X POST http://localhost:5000/api/cases \
  -H "Content-Type: application/json" \
  -H "Cookie: session=tu_session_cookie" \
  -d '{
    "entity": "Empresa Test",
    "debtor_name": "Juan Pérez",
    "dni": "12345678",
    "amount": 50000.00,
    "status": "en_gestion",
    "cartera": "Cartera A"
  }'
```

**Listar casos:**
```bash
curl http://localhost:5000/api/cases?page=1&per_page=10 \
  -H "Cookie: session=tu_session_cookie"
```

### 6.2 Probar Dashboard APIs

**KPIs:**
```bash
curl http://localhost:5000/api/dashboard/kpis \
  -H "Cookie: session=tu_session_cookie"
```

**Gráfico de rendimiento:**
```bash
curl http://localhost:5000/api/dashboard/charts/performance \
  -H "Cookie: session=tu_session_cookie"
```

**Ranking de gestores:**
```bash
curl http://localhost:5000/api/dashboard/gestores/ranking \
  -H "Cookie: session=tu_session_cookie"
```

### 6.3 Probar Rate Limiting

Intenta hacer login más de 5 veces en un minuto con credenciales incorrectas:

```bash
# Hacer 6 intentos rápidos
for i in {1..6}; do
  curl -X POST http://localhost:5000/api/login \
    -d "username=admin&password=wrong"
done
```

Deberías recibir un error 429 (Too Many Requests) después del 5to intento.

## 🐳 Paso 7: Probar con Docker (Opcional)

### 7.1 Construir Imagen

```bash
docker build -f Dockerfile.prod -t gestiones-mvp:latest .
```

### 7.2 Ejecutar con Docker Compose

```bash
# Desarrollo
docker compose -f docker-compose.dev.yml up --build

# Producción
docker compose -f docker-compose.prod.yml up --build
```

## 🔐 Paso 8: Verificar Seguridad

### 8.1 Verificar CSRF

En producción (o con `ENABLE_CSRF=true`), las peticiones POST deben incluir token CSRF.

### 8.2 Verificar Logging de Auditoría

Revisa los logs después de hacer login o crear/modificar casos:

```bash
# Los logs deberían mostrar eventos de auditoría
# Busca líneas que contengan "AUDIT:"
```

### 8.3 Verificar Headers de Seguridad

```bash
curl -I http://localhost:5000/

# Deberías ver:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Content-Security-Policy: ...
```

## 📊 Paso 9: Probar Frontend

### 9.1 Dashboard Admin

1. Login como `admin`
2. Verifica que:
   - Los KPIs se muestran con datos reales
   - Los gráficos se cargan correctamente
   - Los filtros funcionan
   - El ranking de gestores se muestra

### 9.2 Filtros

Prueba cambiar:
- Período (semana, mes, trimestre)
- Filtro por cartera
- Filtro por gestor

Los datos deberían actualizarse automáticamente.

## 🗄️ Paso 10: Verificar Migraciones (Opcional)

Si quieres usar Alembic para migraciones:

```bash
# Inicializar (solo la primera vez)
alembic init migrations

# Crear migración
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

**Nota:** La aplicación crea las tablas automáticamente con `db.create_all()`, pero Alembic es útil para migraciones más complejas.

## 🐛 Solución de Problemas

### Error: "No module named 'flask_sqlalchemy'"

```bash
pip install -r requirements.txt
```

### Error: "Table already exists"

La base de datos ya existe. Puedes:
- Eliminar `data/gestiones.db` y reiniciar
- O usar Alembic para migraciones

### Error: "Rate limit exceeded"

Espera 1 minuto o reinicia la aplicación.

### Los gráficos no se cargan

1. Abre la consola del navegador (F12)
2. Verifica errores en la pestaña "Console"
3. Verifica la pestaña "Network" para ver si las peticiones API fallan

### No puedo hacer login

1. Verifica que la base de datos existe: `data/gestiones.db`
2. Verifica que los usuarios fueron creados (se crean automáticamente)
3. Revisa los logs de la aplicación

## ✅ Checklist de Verificación

- [ ] Dependencias instaladas correctamente
- [ ] Base de datos creada (`data/gestiones.db`)
- [ ] Login funciona con usuarios por defecto
- [ ] Dashboard muestra datos (no hardcodeados)
- [ ] APIs responden correctamente
- [ ] Tests pasan (`pytest`)
- [ ] Rate limiting funciona
- [ ] Logging de auditoría funciona
- [ ] Frontend se actualiza con datos reales
- [ ] CRUD de casos funciona

## 📝 Notas Adicionales

### Variables de Entorno Recomendadas

Crea un archivo `.env` (o usa las variables de entorno):

```bash
# Base de datos (opcional, SQLite por defecto)
DATABASE_URL=sqlite:///data/gestiones.db

# Secret key (OBLIGATORIO en producción)
SECRET_KEY=tu-secret-key-super-segura

# CSRF (habilitado por defecto en producción)
ENABLE_CSRF=true

# Redis para cache (opcional)
REDIS_URL=redis://localhost:6379/0

# Email (opcional)
MAIL_USERNAME=tu-email@example.com
MAIL_PASSWORD=tu-password
```

### Próximos Pasos

1. **Agregar datos de prueba:** Crea algunos casos, promesas y actividades para ver datos reales en el dashboard
2. **Configurar Redis:** Para mejor performance con cache
3. **Configurar PostgreSQL:** Para producción
4. **Revisar logs:** Verificar que todo funciona correctamente

---

**¿Problemas?** Revisa los logs de la aplicación y la consola del navegador para más detalles.

