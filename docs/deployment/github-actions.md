# Guía de GitHub Actions - Prueba y Configuración

## 🔐 Paso 1: Configurar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Clic en **Settings** (Configuración)
3. En el menú lateral, ve a **Secrets and variables** → **Actions**
4. Clic en **New repository secret** para cada uno de estos:

### Secrets Requeridos:

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `SSH_HOST_DEV` | IP o hostname de la instancia de staging | `123.45.67.89` o `staging.tudominio.com` |
| `SSH_HOST_PROD` | IP o hostname de la instancia de producción | `98.76.54.32` o `app.tudominio.com` |
| `SSH_KEY_DEV` | **Contenido completo** de tu clave SSH privada para staging | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SSH_KEY_PROD` | **Contenido completo** de tu clave SSH privada para producción | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SSH_USER` | Usuario SSH (común para ambas instancias) | `ubuntu`, `opc`, o `admin` |

### ⚠️ Importante sobre SSH_KEY:

- Copia **TODO** el contenido de tu archivo de clave privada (incluyendo `-----BEGIN...` y `-----END...`)
- Si tu clave tiene passphrase, necesitarás configurarla también
- No incluyas espacios extra al inicio o final

### 📝 Cómo obtener tu clave SSH:

```bash
# En Windows (PowerShell o Git Bash):
cat ~/.ssh/id_rsa
# o
cat ~/.ssh/id_ed25519

# Si no tienes clave, genera una:
ssh-keygen -t ed25519 -C "tu-email@ejemplo.com"
```

**Luego copia la clave pública a tu servidor OCI:**
```bash
# Copiar clave pública al servidor
ssh-copy-id usuario@tu-servidor-oci
```

---

## 🧪 Paso 2: Probar el Workflow

### Opción A: Probar solo los Tests (Recomendado para empezar)

1. El workflow se ejecutará automáticamente al hacer push a `develop` o `main`
2. O puedes ejecutarlo manualmente:
   - Ve a la pestaña **Actions** en GitHub
   - Selecciona el workflow "CI/CD Pipeline - Oracle Cloud Infrastructure"
   - Clic en **Run workflow**
   - Selecciona la branch que quieres probar
   - Clic en **Run workflow**

### Opción B: Hacer un commit pequeño de prueba

```bash
# Desde tu repositorio local
git checkout develop
# Haz un cambio pequeño (por ejemplo, añade un comentario en cualquier archivo)
git add .
git commit -m "test: probar workflow de CI/CD"
git push origin develop
```

Luego ve a la pestaña **Actions** para ver el progreso.

---

## 📊 Paso 3: Ver los Resultados

1. Ve a la pestaña **Actions** en tu repositorio GitHub
2. Verás una lista de ejecuciones del workflow
3. Clic en la ejecución que quieras ver
4. Verás el progreso en tiempo real:
   - ✅ Verde = éxito
   - ❌ Rojo = error
   - 🟡 Amarillo = en progreso

### Ver Logs Detallados:

- Clic en cada job (ej: "Run Tests", "Deploy to Staging")
- Clic en cada step para ver los logs detallados

---

## 🔍 Paso 4: Troubleshooting

### Error: "SSH connection failed"

**Problema**: No puede conectarse al servidor

**Soluciones**:
1. Verifica que `SSH_HOST_DEV` o `SSH_HOST_PROD` sea correcto
2. Verifica que `SSH_USER` sea el usuario correcto
3. Asegúrate de que la clave SSH está correctamente copiada en GitHub secrets
4. Verifica que la instancia OCI tiene el puerto 22 abierto en el Security List
5. Verifica que la clave pública está en `~/.ssh/authorized_keys` del servidor

### Error: "Directory del proyecto no encontrado"

**Problema**: El directorio `~/gestiones-mvp` no existe en el servidor

**Solución**:
1. Conéctate por SSH al servidor
2. Verifica dónde está tu proyecto:
   ```bash
   find ~ -name "docker-compose.prod.yml" -type f
   ```
3. Si el directorio es diferente, edita `.github/workflows/deploy.yml` y cambia:
   ```yaml
   cd ~/gestiones-mvp
   ```
   por tu ruta real.

### Error: "Tests failed"

**Problema**: Los tests no pasan

**Solución**:
1. Ejecuta los tests localmente:
   ```bash
   pytest -v
   ```
2. Arregla los errores de tests antes de hacer push

### Error: "No such file or directory: deploy.sh"

**Problema**: El script `deploy.sh` no existe en el servidor

**Solución**:
1. Asegúrate de que `deploy.sh` está en el repositorio
2. Verifica los permisos: `chmod +x deploy.sh`
3. Asegúrate de que está en la raíz del proyecto

---

## ✅ Checklist de Verificación

Antes de probar el deploy completo, verifica:

- [ ] Todos los secrets están configurados en GitHub
- [ ] Puedes conectarte por SSH manualmente desde tu máquina
- [ ] El proyecto está clonado en el servidor OCI
- [ ] El archivo `.env.prod` existe en cada servidor
- [ ] El script `deploy.sh` tiene permisos de ejecución
- [ ] Los tests pasan localmente

---

## 🚀 Ejecución por Primera Vez

1. **Primero**: Ejecuta solo los tests (sin deploy) para verificar que funciona
2. **Luego**: Si los tests pasan, haz un commit pequeño a `develop` para probar el deploy a staging
3. **Finalmente**: Una vez que staging funciona, haz merge a `main` para probar producción

---

## 📝 Notas Adicionales

- El workflow **solo se ejecutará** si los tests pasan
- Los deploys a producción requieren que el branch sea `main`
- Los deploys a staging requieren que el branch sea `develop`
- Puedes cancelar una ejecución en progreso desde la interfaz de GitHub Actions

---

## 🔗 Recursos

- [Documentación de GitHub Actions](https://docs.github.com/en/actions)
- [SSH Keys Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

