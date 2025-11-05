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
- Docker Compose 2.0+ (opcional pero recomendado)

### 🚀 Ejecución con Docker Compose (Recomendado)

#### Para Producción:
```bash
# Construir y ejecutar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener los contenedores
docker-compose down
```

#### Para Desarrollo (con hot-reload):
```bash
# Construir y ejecutar con recarga automática
docker-compose -f docker-compose.dev.yml up

# Detener
docker-compose -f docker-compose.dev.yml down
```

### 🔧 Ejecución con Docker directamente

```bash
# Construir la imagen
docker build -t gestiones-mvp .

# Ejecutar contenedor
docker run -d -p 5000:5000 --name gestiones-mvp gestiones-mvp

# Ver logs
docker logs -f gestiones-mvp

# Detener y eliminar contenedor
docker stop gestiones-mvp && docker rm gestiones-mvp
```

### 📋 Archivos Docker incluidos

- `Dockerfile` - Imagen de producción con Gunicorn
- `Dockerfile.dev` - Imagen de desarrollo con hot-reload
- `docker-compose.yml` - Configuración para producción
- `docker-compose.dev.yml` - Configuración para desarrollo
- `.dockerignore` - Archivos excluidos del build

## 📦 Instalación Local (Sin Docker)

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 🎮 Uso Local

1. Inicia el servidor:
```bash
python app.py
```

2. Abre tu navegador en: `http://localhost:5000`

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

- `login.html` - Página de login con HTMX
- `dashboard-admin.html` - Dashboard completo para administradores
- `dashboard-gestor.html` 🆕 - Dashboard personalizado para gestores de deudas
- `dashboard-user.html` - Panel básico para usuarios regulares
- `app.py` - Backend Flask con autenticación y manejo de sesiones
- `requirements.txt` - Dependencias de Python
- `Dockerfile` - Configuración Docker para producción
- `Dockerfile.dev` - Configuración Docker para desarrollo
- `docker-compose.yml` - Orquestación Docker (producción)
- `docker-compose.dev.yml` - Orquestación Docker (desarrollo)
- `README.md` - Este archivo

## 🎨 Tecnologías Utilizadas

- **HTMX** - Peticiones asíncronas sin JavaScript complejo
- **Chart.js** - Gráficos interactivos y visualizaciones
- **Flask** - Backend Python con manejo de sesiones
- **CSS Grid & Flexbox** - Layout responsive

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

- Sesiones basadas en cookies
- Autenticación por roles
- Protección de rutas
- Validación de credenciales

## 📝 Próximos Pasos (Para Producción)

- [ ] Integración con base de datos (PostgreSQL/MySQL)
- [ ] Autenticación JWT
- [ ] Protección CSRF
- [ ] Rate limiting
- [ ] Encriptación de contraseñas con bcrypt
- [ ] Logging y auditoría
- [ ] Tests unitarios
- [x] Docker containerization ✅
- [ ] Configuración de producción

## 🛠️ Desarrollo

Para contribuir o modificar el sistema:

1. Los datos están hardcodeados en `dashboard-admin.html`
2. Reemplaza con llamadas a tu API en producción
3. Personaliza los colores en las secciones `<style>`
4. Añade más gráficos según necesidad

## 📧 Soporte

Para dudas o problemas, revisa la documentación de:
- [HTMX](https://htmx.org)
- [Chart.js](https://www.chartjs.org)
- [Flask](https://flask.palletsprojects.com)
