---
title: Solución de problemas
description: Problemas comunes y soluciones para DocPlatform — inicio del servidor, sincronización git, autenticación, búsqueda y recuperación de datos.
weight: 3
---

# Solución de problemas

Esta guía cubre problemas comunes y sus soluciones. Para información de diagnóstico, siempre comience con:

```bash
docplatform doctor
```

## Inicio del servidor

### El servidor no arranca: "address already in use"

**Causa:** Otro proceso está usando el puerto configurado.

**Solución:**

```bash
# Find what's using port 3000
lsof -i :3000  # macOS/Linux
ss -tlnp | grep 3000  # Linux

# Option 1: Stop the other process
# Option 2: Use a different port
docplatform serve --port 8080
```

### El servidor no arranca: "permission denied"

**Causa:** El proceso no tiene acceso de lectura/escritura al directorio de datos.

**Solución:**

```bash
# Check ownership
ls -la .docplatform/

# Fix ownership (if running as docplatform user)
sudo chown -R docplatform:docplatform .docplatform/

# Fix permissions
chmod 700 .docplatform/
```

### El servidor no arranca: "database is locked"

**Causa:** Otro proceso de DocPlatform está ejecutándose, o un proceso anterior no se cerró correctamente.

**Solución:**

```bash
# Check for other docplatform processes
ps aux | grep docplatform

# If a process is stuck, kill it
kill -SIGTERM <pid>

# If the lock file persists after no processes are running
# SQLite WAL mode handles this automatically on restart
docplatform serve
```

## Sincronización git

### "Permission denied (publickey)" durante la sincronización git

**Causa:** La clave SSH no está configurada o no tiene acceso al repositorio.

**Solución:**

1. Verifique que la clave existe:
   ```bash
   ls -la $GIT_SSH_KEY_PATH
   ```

2. Verifique que la clave ha sido agregada a las claves de deploy del repositorio:
   ```bash
   ssh -T -i $GIT_SSH_KEY_PATH git@github.com
   ```

3. Asegúrese de que el acceso de escritura esté habilitado en la clave de deploy (requerido para push)

### La sincronización git muestra "no changes" pero los archivos fueron actualizados

**Causa:** Los cambios se realizaron en archivos fuera del directorio `docs/`, que DocPlatform no indexa.

**Solución:** Asegúrese de que sus archivos Markdown estén en el directorio `docs/` del workspace. Los archivos en otros directorios se preservan en git pero no son rastreados por DocPlatform.

### Conflicto: HTTP 409 al guardar

**Causa:** La página fue modificada por otro usuario o mediante git push entre su carga y guardado.

**Solución:**

1. La interfaz web muestra un banner de conflicto con ambas versiones
2. Haga clic en **Download both** para obtener ambos archivos
3. Haga merge de los cambios manualmente
4. Guarde la versión fusionada

**Prevención:**

- Habilite webhooks para sincronización más rápida (reduce la ventana de conflictos)
- Use los indicadores de presencia para ver quién está editando qué
- Asigne propiedad de páginas para evitar ediciones simultáneas

### Git push falla: "remote rejected"

**Causa:** La clave de deploy no tiene acceso de escritura, o las reglas de protección de rama previenen pushes directos.

**Solución:**

1. Verifique que la clave de deploy tenga acceso de escritura en la configuración de su repositorio
2. Verifique las reglas de protección de rama — DocPlatform hace push directamente a la rama configurada
3. Si la protección de rama es necesaria, configure DocPlatform para hacer push a una rama no protegida

## Autenticación

### "401 Unauthorized" en cada solicitud

**Causa:** El token de acceso JWT ha expirado (15 minutos de vida por defecto).

**Solución:** El editor web maneja la actualización de tokens automáticamente. Si usa la API directamente, llame al endpoint de actualización:

```bash
curl -X POST http://localhost:3000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

### No puede iniciar sesión después de la rotación de clave JWT

**Causa:** Todos los tokens fueron invalidados cuando la clave JWT fue eliminada y regenerada.

**Solución:** Este es el comportamiento esperado. Todos los usuarios deben iniciar sesión nuevamente después de la rotación de clave. Limpie las cookies/almacenamiento de su navegador e inicie sesión con su contraseña.

### El inicio de sesión OIDC redirige a una página de error

**Causa:** La URL de callback de OAuth no coincide con lo configurado en Google/GitHub.

**Solución:**

1. Verifique la URL de callback en la configuración de su proveedor OAuth
2. Debería ser: `https://your-domain.com/api/v1/auth/callback/google` (o `/github`)
3. Asegúrese de que las variables de entorno `OIDC_*_CLIENT_ID` y `OIDC_*_CLIENT_SECRET` estén configuradas correctamente
4. Reinicie el servidor después de cambiar las variables de entorno OIDC

### El primer usuario no es SuperAdmin

**Causa:** La base de datos ya contenía registros de usuarios de una instalación anterior.

**Solución:**

```bash
# WARNING: This deletes all data
docplatform serve  # stop first
rm .docplatform/data.db
docplatform serve
# Register your admin account
```

Solo haga esto en una instalación nueva. Para instalaciones existentes, use la base de datos para actualizar roles de usuario directamente (avanzado).

## Búsqueda

### La búsqueda no devuelve resultados

**Causa:** El índice de búsqueda puede estar vacío o desincronizado.

**Solución:**

```bash
# Check search health
docplatform doctor

# If the index is out of sync, rebuild
docplatform rebuild
```

### Los resultados de búsqueda están desactualizados (no reflejan ediciones recientes)

**Causa:** El trabajo de indexación asíncrono aún no se ha procesado (típicamente < 1 segundo de retraso).

**Solución:** Espere un momento y reintente. Si el problema persiste:

1. Verifique los logs del servidor en busca de errores de indexación
2. Ejecute `docplatform rebuild` para forzar una re-indexación completa

### La búsqueda es lenta

**Causa:** Workspaces muy grandes (más de 1000 páginas) con consultas complejas.

**Solución:**

- Use términos de búsqueda más específicos
- Use filtros de etiquetas para reducir el alcance
- Las versiones futuras soportarán Meilisearch para búsqueda de alto rendimiento

## Recuperación de datos

### Se eliminó una página accidentalmente

**Opción 1: Historial de git** (si la sincronización git está habilitada)

```bash
cd .docplatform/workspaces/{id}/docs/
git log --all -- path/to/deleted-page.md
git checkout <commit-hash> -- path/to/deleted-page.md
```

Luego ejecute `docplatform rebuild` para re-indexar.

**Opción 2: Copia de seguridad de base de datos**

```bash
# List backups
ls .docplatform/backups/

# Restore from backup (stops the server first)
cp .docplatform/backups/{latest}.db .docplatform/data.db
docplatform serve
```

### La base de datos está corrupta

**Solución:**

1. Detenga el servidor
2. Busque una copia de seguridad reciente:
   ```bash
   ls -la .docplatform/backups/
   ```
3. Restaure desde la copia de seguridad:
   ```bash
   cp .docplatform/backups/{latest}.db .docplatform/data.db
   ```
4. Si no hay copia de seguridad disponible, reconstruya desde el sistema de archivos:
   ```bash
   rm .docplatform/data.db
   docplatform rebuild
   ```
5. Inicie el servidor

El sistema de archivos (archivos `.md`) es la fuente de verdad. Incluso si se pierde la base de datos, `rebuild` la recrea a partir de sus archivos.

### Se perdió la clave JWT

**Causa:** El archivo `jwt-key.pem` fue eliminado.

**Impacto:** Todas las sesiones de usuario se invalidan. Los usuarios deben iniciar sesión nuevamente.

**Solución:** Inicie el servidor — se genera una nueva clave automáticamente. No se pierden datos, pero todos los usuarios necesitan re-autenticarse.

## Errores de frontmatter

### La página se vuelve inaccesible después de editar el frontmatter

**Causa:** YAML inválido en el bloque de frontmatter. DocPlatform usa **modo estricto** por defecto — si el análisis del frontmatter falla, la página se restringe a acceso solo de WorkspaceAdmin para evitar que un error tipográfico en YAML haga accidentalmente pública una página privada.

**Síntomas:**

- La página desaparece de los resultados de búsqueda
- La página se excluye de la documentación publicada
- Los usuarios no administradores obtienen 403 Forbidden
- El administrador ve un banner de advertencia en la página

**Solución:**

1. Inicie sesión como WorkspaceAdmin o SuperAdmin
2. Abra la página afectada en el editor web
3. Cambie al modo Markdown sin procesar (botón `</>`)
4. Corrija el frontmatter YAML (problemas comunes: comillas faltantes alrededor de valores con dos puntos, indentación incorrecta, corchetes sin cerrar)
5. Guarde — la página se re-indexa y el acceso se restaura

**Si no puede acceder al editor web**, corrija el archivo directamente en disco:

```bash
# Edit the Markdown file
nano .docplatform/workspaces/{id}/docs/{path-to-page}.md

# Rebuild to re-index
docplatform rebuild
```

### Comprensión de los modos de error de frontmatter

| Modo | Comportamiento con YAML inválido | Cuándo usarlo |
|---|---|---|
| **Strict** (predeterminado) | Página restringida solo a WorkspaceAdmin, excluida de búsqueda y documentación publicada | Producción — previene exposición accidental |
| **Lenient** | Mantiene el último frontmatter válido conocido de la base de datos, muestra advertencia | Desarrollo — menos disrupciones durante la edición |

El modo estricto asegura que un error tipográfico en YAML nunca haga accidentalmente pública una página restringida. Este es un diseño de seguridad deliberado.

## Espacio en disco

### Advertencia "Low disk space" del doctor

**Causa:** DocPlatform advierte cuando el espacio libre en disco cae por debajo de 1 GB.

**Impacto:** SQLite requiere espacio libre en disco para operaciones WAL (write-ahead log). Si el disco se llena completamente, las escrituras fallan y los datos pueden corromperse.

**Solución:**

1. Verifique el uso de disco: `df -h`
2. Limpie copias de seguridad antiguas: reduzca `BACKUP_RETENTION_DAYS` o elimine manualmente archivos antiguos en `{DATA_DIR}/backups/`
3. Mueva el directorio de datos a un disco más grande: actualice `DATA_DIR` y mueva el directorio
4. Si usa Docker, aumente el tamaño del volumen

## Rendimiento

### Alto uso de memoria

**Esperado:** < 80 MB inactivo, < 200 MB bajo carga.

Si el uso de memoria excede 200 MB:

1. Verifique el número de conexiones WebSocket activas
2. Verifique el conteo de workspaces y el conteo total de páginas
3. Los repositorios git grandes (>5.000 archivos) usan más memoria — el motor híbrido auto-cambia al CLI nativo de git cuando go-git excede 512 MB RSS

### Renderizado lento de páginas

**Esperado:** < 50ms p99.

Si el renderizado de páginas es lento:

1. Verifique la E/S de disco — el rendimiento de SQLite depende de la velocidad del disco
2. Use un SSD para el directorio de datos
3. Verifique si el archivo de base de datos está en un sistema de archivos de red (NFS/CIFS) — muévalo a disco local

## Obtener ayuda

Si no puede resolver un problema:

1. Ejecute `docplatform doctor --bundle` para generar un paquete de diagnóstico
2. Verifique los logs del servidor en busca de mensajes de error
3. Abra un issue en GitHub con el paquete de diagnóstico y las entradas de log relevantes

El paquete de diagnóstico **no** contiene su contenido, contraseñas ni tokens de API — solo metadatos estructurales y configuración (con secretos redactados).
