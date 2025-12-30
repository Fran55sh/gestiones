# 🚀 Inicio Rápido - Nueva Implementación

Guía rápida para probar la nueva implementación en 5 minutos.

## ⚡ Pasos Rápidos

### 1. Instalar Dependencias (2 min)

```bash
pip install -r requirements.txt
```

### 2. Verificar Configuración (1 min)

```bash
python scripts/test_setup.py
```

Este script verifica que todo esté correcto.

### 3. Iniciar la Aplicación (1 min)

```bash
# Opción 1: Directo
python -m app.wsgi

# Opción 2: Con Flask CLI
export FLASK_APP=app/wsgi.py  # Linux/Mac
set FLASK_APP=app/wsgi.py     # Windows
flask run
```

### 4. Probar Login (1 min)

1. Abre: `http://localhost:5000/gestiones`
2. Login con:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. Deberías ver el dashboard con datos reales (aunque esté vacío inicialmente)

### 5. Ejecutar Tests (opcional)

```bash
pytest -v
```

## ✅ Verificación Rápida

### ¿Funciona la base de datos?

```bash
# Verificar que existe
ls data/gestiones.db  # Linux/Mac
dir data\gestiones.db # Windows
```

### ¿Funcionan las APIs?

Abre el dashboard y presiona F12 (consola del navegador). Deberías ver:
- ✅ Peticiones a `/api/dashboard/kpis`
- ✅ Peticiones a `/api/dashboard/charts/*`
- ❌ Sin errores en rojo

### ¿Los gráficos se cargan?

En el dashboard deberías ver:
- ✅ Gráficos de Chart.js (aunque estén vacíos sin datos)
- ✅ KPIs mostrando 0 o valores iniciales
- ✅ Ranking de gestores (vacío si no hay gestores con casos)

## 🐛 Problemas Comunes

### "No module named 'flask_sqlalchemy'"
```bash
pip install -r requirements.txt
```

### "Table already exists"
La base de datos ya existe. Está bien, continúa.

### Los gráficos están vacíos
Es normal si no hay datos. Crea algunos casos para ver datos.

## 📝 Crear Datos de Prueba

Para ver el dashboard con datos, puedes crear casos manualmente o usar la API:

```python
# En Python shell (python -m app.wsgi y luego abre shell)
from app import create_app
from app.db import db
from app.models import Case, User

app = create_app()
with app.app_context():
    gestor = User.query.filter_by(username='gestor').first()
    case = Case(
        entity='Empresa Test',
        debtor_name='Juan Pérez',
        amount=50000.00,
        status='en_gestion',
        cartera='Cartera A',
        assigned_to_id=gestor.id if gestor else None
    )
    db.session.add(case)
    db.session.commit()
    print("Caso creado!")
```

## 📚 Documentación Completa

Para más detalles, consulta:
- `GUIA_PRUEBAS.md` - Guía completa de pruebas
- `README.md` - Documentación general

---

**¿Todo funciona?** 🎉 ¡Ahora puedes explorar todas las nuevas funcionalidades!

