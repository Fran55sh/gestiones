# Configuración de CI/CD con GitHub Actions

## 📋 Resumen

Este proyecto tiene dos workflows de GitHub Actions configurados:

1. **CI (Continuous Integration)** - `.github/workflows/ci.yml`
   - Se ejecuta en cada push/PR a `main` o `develop`
   - Tests, linting, security scans

2. **CD (Continuous Deployment)** - `.github/workflows/deploy.yml`
   - Se ejecuta solo en push a `main` o tags `v*`
   - Deployment automático al servidor

---

## 🚀 Paso 1: Configurar Secrets en GitHub

### Secrets Necesarios

Ve a tu repositorio en GitHub → Settings → Secrets and variables → Actions → New repository secret

#### Para CI (Opcional):

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `DOCKER_USERNAME` | Usuario de Docker Hub | `tu-usuario` |
| `DOCKER_PASSWORD` | Password o token de Docker Hub | `dckr_pat_xxxxx` |

> **Nota:** Estos son opcionales. El CI funciona sin ellos, solo no pusheará imágenes a Docker Hub.

#### Para CD (Requerido para deployment):

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `SSH_PRIVATE_KEY` | Llave SSH privada para conectar al servidor | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DEPLOY_HOST` | IP o dominio del servidor | `123.45.67.89` o `miapp.com` |
| `DEPLOY_USER` | Usuario SSH del servidor | `ubuntu` o `opc` |
| `DEPLOY_PATH` | Ruta en el servidor donde está el proyecto | `/home/ubuntu/gestiones-mvp` |

---

## 🔐 Paso 2: Generar y Configurar SSH Key

### En tu máquina local:

```bash
# 1. Generar nueva SSH key (si no tienes)
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/deploy_key

# 2. Copiar la clave pública al servidor
ssh-copy-id -i ~/.ssh/deploy_key.pub usuario@servidor

# 3. Copiar la clave PRIVADA para GitHub (TODA, incluyendo BEGIN/END)
cat ~/.ssh/deploy_key
```

### En GitHub:

1. Ve a Settings → Secrets → New secret
2. Nombre: `SSH_PRIVATE_KEY`
3. Pega TODO el contenido del archivo `deploy_key` (incluyendo `-----BEGIN RSA PRIVATE KEY-----` y `-----END RSA PRIVATE KEY-----`)

---

## ✅ Paso 3: Verificar CI (Ya Funciona)

El CI se ejecuta automáticamente en cada push. Para verificar:

1. Haz un push a `develop`:
   ```bash
   git push origin develop
   ```

2. Ve a GitHub → Actions → Verás el workflow ejecutándose

3. El workflow hace:
   - ✅ Instala dependencias
   - ✅ Ejecuta linting (flake8, black)
   - ✅ Ejecuta tests con pytest
   - ✅ Genera coverage report
   - ✅ Security scan con Bandit
   - ✅ Build de Docker (solo en `main`)

---

## 🚀 Paso 4: Preparar el Servidor para CD

### En tu servidor (Oracle Cloud, AWS, etc.):

```bash
# 1. Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 2. Clonar el repositorio
cd ~
git clone https://github.com/tu-usuario/gestiones-mvp.git
cd gestiones-mvp

# 3. Configurar variables de entorno
cp config/env/prod.env.example .env
nano .env  # Editar con tus valores

# 4. Verificar que Docker Compose funciona
docker compose -f config/docker/docker-compose.prod.yml config
```

---

## 🎯 Paso 5: Activar Deployment Automático

### Opción A: Deploy en cada push a main

Simplemente haz push a `main`:

```bash
git checkout main
git merge develop
git push origin main
```

El workflow automáticamente:
1. ✅ Se conecta al servidor via SSH
2. ✅ Hace `git pull`
3. ✅ Rebuild de contenedores Docker
4. ✅ Reinicia la aplicación

### Opción B: Deploy con tags (Recomendado para producción)

```bash
# Crear un tag de versión
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## 📊 Paso 6: Monitorear los Workflows

### Ver el estado:

1. GitHub → Actions
2. Click en el workflow que se está ejecutando
3. Ver logs en tiempo real

### Si falla:

1. Ve al workflow que falló
2. Expande el paso que dio error
3. Lee los logs
4. Corrige el problema
5. Push de nuevo

---

## 🔧 Troubleshooting

### CI falla en tests:

```bash
# Ejecutar tests localmente primero
pytest -v

# Verificar coverage
pytest --cov=app

# Verificar linting
flake8 app tests
black --check app tests
```

### CD falla en SSH:

```bash
# Verificar conexión SSH desde tu máquina
ssh -i ~/.ssh/deploy_key usuario@servidor

# Verificar que la clave está en el servidor
cat ~/.ssh/authorized_keys  # En el servidor
```

### CD falla en Docker:

```bash
# En el servidor, verificar Docker
docker ps
docker compose -f config/docker/docker-compose.prod.yml logs

# Verificar permisos
sudo usermod -aG docker $USER
```

---

## 📈 Mejoras Opcionales

### 1. Codecov (Coverage Reports)

1. Ve a [codecov.io](https://codecov.io)
2. Conecta tu repo de GitHub
3. El workflow ya está configurado para subir reports

### 2. Docker Hub (Imágenes públicas)

1. Crea cuenta en [Docker Hub](https://hub.docker.com)
2. Genera un access token
3. Agrega secrets `DOCKER_USERNAME` y `DOCKER_PASSWORD`
4. Modifica `ci.yml` para hacer `push: true`

### 3. Slack/Discord Notifications

Agrega al final de los workflows:

```yaml
    - name: Notify Slack
      if: always()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## ✅ Checklist de Configuración

- [ ] Secrets de GitHub configurados (SSH_PRIVATE_KEY, DEPLOY_HOST, DEPLOY_USER, DEPLOY_PATH)
- [ ] SSH key generada y copiada al servidor
- [ ] Servidor preparado (Docker, Git, proyecto clonado)
- [ ] Variables de entorno configuradas en el servidor (.env)
- [ ] Primer push a `develop` para probar CI ✅
- [ ] Primer push/merge a `main` para probar CD
- [ ] Monitoring configurado (opcional)

---

## 📚 Referencias

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [SSH Key Setup](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Pytest Coverage](https://pytest-cov.readthedocs.io/)

---

**Estado Actual:** ✅ CI configurado y funcionando | ⚠️ CD requiere secrets configurados

