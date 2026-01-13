# 🚀 Guía de Migración a Producción

Esta guía explica cómo migrar todos los datos de **develop** a **producción** de forma segura.

## 📋 Checklist Pre-Migración

Antes de hacer el merge a producción, asegúrate de:

- [ ] **Backup de producción**: Hacer backup completo de la base de datos de producción actual
- [ ] **Verificar migraciones**: Todas las migraciones de Alembic están en `migrations/versions/`
- [ ] **Exportar datos de develop**: Ejecutar script de exportación
- [ ] **Revisar cambios**: Verificar que no haya conflictos en el código

## 🔄 Proceso de Migración

### Paso 1: Exportar Datos desde Develop

En tu entorno local (con la base de datos de develop):

```bash
# Asegúrate de estar en la rama develop
git checkout develop
git pull origin develop

# Activa el entorno virtual (si usas uno)
# source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate      # Windows

# Ejecuta el script de exportación
python scripts/prod/export_data_for_prod.py
```

Esto creará el archivo `data/export_for_prod.json` con todos los datos:
- ✅ Carteras
- ✅ Estados de caso (case_statuses)
- ✅ Casos (cases)
- ✅ Usuarios (solo estructura, sin contraseñas)
- ✅ Actividades (activities)
- ✅ Promesas (promises)

### Paso 2: Hacer Merge a Producción

```bash
# Cambiar a rama main
git checkout main
git pull origin main

# Hacer merge de develop
git merge develop

# Resolver conflictos si los hay
# Luego hacer push
git push origin main
```

### Paso 3: Desplegar en Producción

El workflow de GitHub Actions se ejecutará automáticamente al hacer push a `main`, o puedes ejecutarlo manualmente desde la pestaña "Actions" en GitHub.

El deployment incluye:
1. ✅ Ejecución de tests
2. ✅ Backup automático
3. ✅ Pull del código
4. ✅ Rebuild de Docker images
5. ✅ Ejecución de migraciones de Alembic
6. ✅ Creación de datos por defecto

### Paso 4: Importar Datos en Producción

Una vez que el deployment esté completo, conecta a la instancia de producción y ejecuta:

```bash
# Conectarse a la instancia de producción
ssh ubuntu@<IP_PRODUCCION>

# Ir al directorio del proyecto
cd /home/ubuntu/gestiones

# Copiar el archivo export_for_prod.json a la instancia
# (desde tu máquina local)
scp data/export_for_prod.json ubuntu@<IP_PRODUCCION>:/home/ubuntu/gestiones/data/

# O crear el archivo directamente en el servidor si tienes acceso
```

Luego, dentro del contenedor de producción:

```bash
# Importar los datos
docker exec gestiones-mvp-prod python3 scripts/prod/import_data_to_prod.py
```

Este script:
- ✅ Importa carteras (evita duplicados)
- ✅ Importa estados de caso (mantiene IDs si es posible)
- ✅ Importa casos (evita duplicados por `nro_cliente`)
- ⚠️ Actividades y promesas requieren mapeo manual de `case_id` (ver sección siguiente)

### Paso 5: Verificar Migración

```bash
# Verificar que los datos se importaron correctamente
docker exec gestiones-mvp-prod python3 << 'PYTHON'
from app import create_app
from app.core.database import db
from app.features.carteras.models import Cartera
from app.features.cases.models import Case, CaseStatus

app = create_app()
with app.app_context():
    print(f"Carteras: {Cartera.query.count()}")
    print(f"Estados: {CaseStatus.query.count()}")
    print(f"Casos: {Case.query.count()}")
PYTHON
```

## ⚠️ Notas Importantes

### Actividades y Promesas

El script de importación actual **NO** importa automáticamente actividades y promesas porque requieren mapear los `case_id` antiguos a los nuevos.

Si necesitas importar actividades y promesas:

1. **Opción 1: Importar manualmente después**
   - Las actividades y promesas se pueden recrear desde la interfaz web
   - O crear un script personalizado que mapee `case_id` por `nro_cliente`

2. **Opción 2: Crear script de mapeo**
   - Crear un script que mapee `case_id` antiguo → `case_id` nuevo usando `nro_cliente` como clave

### Usuarios

Los usuarios **NO** se importan automáticamente por seguridad. Los usuarios de producción se mantienen separados.

Si necesitas crear usuarios en producción:

```bash
docker exec gestiones-mvp-prod python3 << 'PYTHON'
from app import create_app
from app.core.database import db
from app.features.users.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Crear usuario gestor
    gestor = User(
        username='gestor',
        password_hash=generate_password_hash('gestor123'),
        role='gestor',
        active=True
    )
    db.session.add(gestor)
    db.session.commit()
    print("Usuario creado")
PYTHON
```

### Migraciones de Alembic

Las migraciones se ejecutan automáticamente durante el deployment. El orden de ejecución es:

1. `20260112225202_create_carteras_table.py` - Crea tabla carteras
2. `20260112225203_migrate_cases_cartera_to_fk.py` - Migra cartera de string a FK
3. `20260112233643_refactor_cases_table_and_create_statuses.py` - Refactor completo de cases
4. `20260112234500_add_nro_cliente_to_cases.py` - Agrega nro_cliente
5. `a390bb4da27e_add_address_and_contact_fields_to_cases.py` - Agrega campos de dirección

## 🔄 Rollback

Si algo sale mal, puedes hacer rollback:

```bash
# En la instancia de producción
cd /home/ubuntu/gestiones

# Revertir código
git reset --hard HEAD~1

# Rebuild y restart
docker-compose -f config/docker/docker-compose.prod.yml down
docker-compose -f config/docker/docker-compose.prod.yml up -d --build
```

## 📊 Resumen de Datos Migrados

| Tipo | Se Importa | Notas |
|------|-----------|-------|
| Carteras | ✅ Sí | Evita duplicados por nombre |
| Case Statuses | ✅ Sí | Mantiene IDs si es posible |
| Casos | ✅ Sí | Evita duplicados por `nro_cliente` |
| Usuarios | ❌ No | Por seguridad, se mantienen separados |
| Actividades | ⚠️ Manual | Requiere mapeo de `case_id` |
| Promesas | ⚠️ Manual | Requiere mapeo de `case_id` |

## 🆘 Troubleshooting

### Error: "Table already exists"
- Las migraciones ya se ejecutaron. Esto es normal si la base de datos ya existía.

### Error: "Foreign key constraint failed"
- Verifica que las carteras y estados de caso se importaron antes que los casos.

### Error: "Duplicate entry"
- El script evita duplicados automáticamente. Si aparece este error, verifica los datos.

### Datos no aparecen en producción
- Verifica que el archivo `export_for_prod.json` esté en `data/` dentro del contenedor
- Verifica los logs del contenedor: `docker logs gestiones-mvp-prod`

## ✅ Checklist Post-Migración

- [ ] Verificar que todas las carteras están presentes
- [ ] Verificar que todos los estados de caso están presentes
- [ ] Verificar que todos los casos se importaron correctamente
- [ ] Verificar que los usuarios pueden iniciar sesión
- [ ] Probar crear/editar un caso
- [ ] Probar registrar una gestión
- [ ] Verificar que los dashboards muestran datos correctos

---

**Última actualización**: 2025-01-13

