# 🔄 Cambio a app_refactored.py

## Estado Actual

✅ **La aplicación ahora usa `app_refactored.py`** para pruebas
✅ **`app.py` se mantiene intacto** como respaldo

## Archivos Actualizados

- ✅ `Dockerfile` - Usa `app_refactored.py`
- ✅ `Dockerfile.dev` - Usa `app_refactored.py`
- ✅ `docker-compose.yml` - Configurado para `app_refactored.py`

## Para Probar

```powershell
# Reconstruir y ejecutar
docker-compose down
docker-compose up -d --build

# Ver logs en tiempo real
docker-compose logs -f web
```

## Para Volver a app.py (si hay problemas)

### Opción 1: Script PowerShell (recomendado)
```powershell
.\switch-app.ps1 original
docker-compose down
docker-compose up -d --build
```

### Opción 2: Manual
Editar manualmente:
- `Dockerfile`: Cambiar `app_refactored.py` → `app.py` y `app_refactored:app` → `app:app`
- `Dockerfile.dev`: Cambiar `app_refactored.py` → `app.py`
- `docker-compose.yml`: Cambiar `FLASK_APP=app_refactored.py` → `FLASK_APP=app.py`

## Verificar Funcionamiento

1. **Página principal**: http://localhost:5000/
2. **Login**: http://localhost:5000/gestiones
3. **Formulario de contacto**: Probar envío desde http://localhost:5000/
4. **Configuración email**: http://localhost:5000/api/test-email-config (requiere login admin)

## Diferencias Principales

### ✅ Mejoras en app_refactored.py:

1. **Seguridad mejorada**
   - Secret key desde variables de entorno
   - Cookies seguras configuradas
   - Validación y sanitización de entrada

2. **Código más limpio**
   - Funciones helper reutilizables
   - Logging profesional
   - Manejo de errores específico

3. **Mejor estructura**
   - Código organizado por secciones
   - Constantes centralizadas
   - Decoradores para protección de rutas

## Si Algo No Funciona

1. Verificar logs: `docker-compose logs -f web`
2. Verificar configuración: `http://localhost:5000/api/test-email-config`
3. Volver a app.py usando el script: `.\switch-app.ps1 original`

## Notas

- Las rutas y funcionalidades son idénticas
- El comportamiento debería ser el mismo
- Solo cambia la estructura interna del código

