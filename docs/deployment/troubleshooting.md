# Guía de Solución de Problemas SSH para GitHub Actions

## Error: "Permission denied (publickey)"

Este error indica que la clave SSH no está siendo reconocida correctamente. Sigue estos pasos para resolverlo:

---

## ✅ Paso 1: Verificar que la Clave SSH Privada en GitHub Secrets está Correcta

### Formato Correcto

La clave privada debe incluir **TODO** el contenido, incluyendo las líneas de inicio y fin:

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
... (más líneas) ...
-----END OPENSSH PRIVATE KEY-----
```

### ❌ Errores Comunes

1. **Falta la línea BEGIN o END**: Debe incluir ambas líneas
2. **Espacios extra**: No debe tener espacios al inicio o final
3. **Saltos de línea incorrectos**: Debe tener saltos de línea (`\n`) entre cada línea
4. **Clave incorrecta**: Asegúrate de usar la clave PRIVADA, no la pública

### Cómo Obtener la Clave Correcta

```bash
# En Windows (Git Bash o PowerShell)
cat ~/.ssh/id_rsa
# o
cat ~/.ssh/id_ed25519

# Copia TODO desde -----BEGIN hasta -----END
```

---

## ✅ Paso 2: Verificar que la Clave Pública Está en el Servidor

1. **Obtén tu clave pública**:

```bash
# En tu máquina local
cat ~/.ssh/id_rsa.pub
# o
cat ~/.ssh/id_ed25519.pub
```

2. **Conéctate al servidor OCI**:

```bash
ssh usuario@tu-servidor-oci
```

3. **Verifica que el archivo `~/.ssh/authorized_keys` existe**:

```bash
ls -la ~/.ssh/authorized_keys
```

4. **Si no existe, créalo**:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

5. **Agrega tu clave pública**:

```bash
# Opción A: Manualmente
nano ~/.ssh/authorized_keys
# Pega tu clave pública (una línea completa)
# Guarda y cierra (Ctrl+X, luego Y, luego Enter)

# Opción B: Usando ssh-copy-id (desde tu máquina local)
ssh-copy-id usuario@tu-servidor-oci
```

6. **Verifica los permisos** (MUY IMPORTANTE):

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

## ✅ Paso 3: Verificar el Usuario SSH

El usuario SSH puede variar según el sistema operativo:

- **Ubuntu/Debian**: `ubuntu` o el usuario que creaste
- **Oracle Linux**: `opc`
- **CentOS/RHEL**: `centos` o `ec2-user`

### Verificar Usuario Correcto

1. Conéctate al servidor usando tu método actual (clave existente o contraseña)
2. Ejecuta:
```bash
whoami
echo $USER
```

Ese es el usuario que debes usar en `SSH_USER` en GitHub Secrets.

---

## ✅ Paso 4: Verificar que el Puerto 22 Está Abierto en OCI

1. Ve a **OCI Console** → **Networking** → **Virtual Cloud Networks**
2. Selecciona tu VCN
3. Ve a **Security Lists**
4. Verifica que hay una regla para **Ingress** permitiendo:
   - **Source**: `0.0.0.0/0` (o tu IP específica para más seguridad)
   - **IP Protocol**: `TCP`
   - **Destination Port Range**: `22`

Si no está, agrega la regla.

---

## ✅ Paso 5: Probar Conexión Manualmente

Desde tu máquina local, prueba conectarte:

```bash
ssh -v usuario@tu-servidor-oci
```

El flag `-v` mostrará información detallada. Busca mensajes como:
- `Authentications that can continue: publickey` - Esto es bueno
- `Offering public key` - La clave se está ofreciendo
- `Server accepts key` - La clave fue aceptada

Si ves `Permission denied (publickey)`, revisa los pasos anteriores.

---

## ✅ Paso 6: Verificar GitHub Secrets

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Verifica que estos secrets existen:
   - `SSH_HOST_DEV` - IP o hostname de staging
   - `SSH_HOST_PROD` - IP o hostname de producción
   - `SSH_USER` - Usuario SSH (ej: `ubuntu`, `opc`)
   - `SSH_KEY_DEV` - Clave privada SSH completa para staging
   - `SSH_KEY_PROD` - Clave privada SSH completa para producción

4. **Edita cada secret** y verifica:
   - No hay espacios al inicio/final
   - Incluye `-----BEGIN` y `-----END`
   - Todo el contenido está en una sola entrada (GitHub secrets maneja saltos de línea automáticamente)

---

## 🔍 Diagnóstico Avanzado

### Si el Problema Persiste

1. **Revisa los logs detallados de GitHub Actions**:
   - El workflow ahora incluye `-v` (verbose) en el test SSH
   - Busca mensajes de error específicos en los logs

2. **Genera una Nueva Clave SSH**:

```bash
# Generar nueva clave
ssh-keygen -t ed25519 -C "github-actions-$(date +%Y%m%d)" -f ~/.ssh/github_actions_oci

# Copiar clave pública al servidor
ssh-copy-id -i ~/.ssh/github_actions_oci.pub usuario@tu-servidor-oci

# Obtener clave privada para GitHub
cat ~/.ssh/github_actions_oci

# Obtener clave pública para verificar
cat ~/.ssh/github_actions_oci.pub
```

3. **Verifica en el Servidor que la Clave se Agregó**:

```bash
ssh usuario@tu-servidor-oci
cat ~/.ssh/authorized_keys
# Debe aparecer tu clave pública
```

---

## 📝 Checklist de Verificación

Antes de ejecutar el workflow nuevamente, verifica:

- [ ] La clave privada en GitHub Secrets incluye `-----BEGIN` y `-----END`
- [ ] La clave pública correspondiente está en `~/.ssh/authorized_keys` del servidor
- [ ] Los permisos de `~/.ssh` son `700` en el servidor
- [ ] Los permisos de `~/.ssh/authorized_keys` son `600` en el servidor
- [ ] El usuario SSH (`SSH_USER`) es correcto
- [ ] El host/IP (`SSH_HOST_DEV`/`SSH_HOST_PROD`) es correcto
- [ ] El puerto 22 está abierto en OCI Security List
- [ ] Puedes conectarte manualmente desde tu máquina con `ssh usuario@host`

---

## 🚨 Problemas Comunes y Soluciones

### "No such file or directory: /home/usuario/.ssh/authorized_keys"

**Solución**: Crea el directorio y archivo:
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### "Bad permissions"

**Solución**: Corrige los permisos:
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### "Too many authentication failures"

**Solución**: Especifica la clave explícitamente:
```bash
ssh -o IdentitiesOnly=yes -i ~/.ssh/tu_clave usuario@servidor
```

### La conexión funciona manualmente pero falla en GitHub Actions

**Solución**: 
- Verifica que copiaste la clave privada COMPLETA en GitHub Secrets
- Asegúrate de que no hay espacios extra
- Verifica que el formato es correcto (BEGIN/END incluidos)

---

## 💡 Tips Adicionales

1. **Usa claves diferentes para dev y prod**: Más seguro
2. **Restringe IPs en OCI Security List**: Solo permite conexiones desde IPs conocidas
3. **Usa fail2ban**: Para protección adicional contra ataques de fuerza bruta
4. **Monitorea logs**: Revisa `/var/log/auth.log` en el servidor para ver intentos de conexión

---

## 📞 Si Nada Funciona

Si después de seguir todos estos pasos el problema persiste:

1. **Regenera completamente las claves SSH**
2. **Verifica que estás usando la clave correcta** (puede haber múltiples claves)
3. **Prueba con una conexión SSH simple** primero antes del workflow completo
4. **Revisa los logs detallados** del workflow en GitHub Actions (ahora incluyen `-v`)

