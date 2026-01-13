# 🚀 Guía Rápida: Migración a Producción

## ⚡ Pasos Rápidos

### 1. Exportar datos desde develop (local)

```bash
git checkout develop
python scripts/prod/export_data_for_prod.py
```

Esto crea `data/export_for_prod.json`

### 2. Hacer merge a main

```bash
git checkout main
git merge develop
git push origin main
```

### 3. Esperar deployment automático

El workflow de GitHub Actions ejecutará:
- ✅ Tests
- ✅ Migraciones de Alembic
- ✅ Creación de datos por defecto

### 4. Importar datos en producción

```bash
# Conectarse a producción
ssh ubuntu@<IP_PRODUCCION>

# Copiar archivo export (desde tu máquina local)
scp data/export_for_prod.json ubuntu@<IP_PRODUCCION>:/home/ubuntu/gestiones/data/

# Importar datos
cd /home/ubuntu/gestiones
docker exec gestiones-mvp-prod python3 scripts/prod/import_data_to_prod.py
```

### 5. Verificar

```bash
docker exec gestiones-mvp-prod python3 scripts/prod/verify_prod_data.py
```

## 📋 Checklist

- [ ] Datos exportados desde develop
- [ ] Merge a main completado
- [ ] Deployment automático exitoso
- [ ] Archivo `export_for_prod.json` copiado a producción
- [ ] Datos importados en producción
- [ ] Verificación exitosa

## 📚 Documentación Completa

Ver `docs/deployment/MIGRACION_PRODUCCION.md` para detalles completos.

