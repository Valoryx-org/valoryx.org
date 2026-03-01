---
title: Referencia CLI
description: Referencia completa de todos los comandos CLI de DocPlatform — serve, init, rebuild, doctor y version.
weight: 2
---

# Referencia CLI

DocPlatform proporciona 5 comandos CLI para gestión del servidor, inicialización de workspaces, diagnósticos y mantenimiento.

## Opciones globales

Estas opciones aplican a todos los comandos:

| Flag | Descripción |
|---|---|
| `--help`, `-h` | Mostrar ayuda para cualquier comando |
| `--version`, `-v` | Imprimir información de versión |

## `docplatform serve`

Iniciar el servidor HTTP.

```bash
docplatform serve [flags]
```

### Flags

| Flag | Predeterminado | Descripción |
|---|---|---|
| `--port` | `3000` | Puerto de escucha HTTP (anula la variable de entorno `PORT`) |
| `--host` | `0.0.0.0` | Dirección de escucha HTTP (anula la variable de entorno `HOST`) |
| `--data-dir` | `.docplatform` | Ruta del directorio de datos (anula la variable de entorno `DATA_DIR`) |

### Comportamiento

- Carga variables de entorno del archivo `.env` (si está presente)
- Inicializa la base de datos SQLite con modo WAL
- Ejecuta las migraciones pendientes de base de datos
- Carga las políticas de permisos de Casbin en memoria
- Construye o abre el índice de búsqueda Bleve
- Inicia el motor de sincronización git para todos los workspaces configurados
- Inicia el programador de copias de seguridad (si está habilitado)
- Sirve el editor web y la API en el puerto configurado

### Secuencia de inicio

Cuando `docplatform serve` se ejecuta, sucede lo siguiente en orden:

1. Cargar configuración (variables de entorno + archivo `.env` + valores predeterminados)
2. Abrir base de datos SQLite (modo WAL) y ejecutar migraciones pendientes
3. Crear la organización predeterminada si es la primera ejecución
4. Inicializar servicios: Content Ledger, Git Engine (pool de 4 workers), Search Engine, Permission Service, Auth Service, WebSocket Hub
5. Iniciar goroutines en segundo plano: WebSocket hub, polling de sincronización git, programador de copias de seguridad, telemetría (si está habilitada)
6. Comenzar a escuchar en el host:port configurado

Las solicitudes de lectura se sirven inmediatamente. Si los workspaces tienen contenido existente, la reconciliación se ejecuta en segundo plano sin bloquear.

### Señales

| Señal | Efecto |
|---|---|
| `SIGTERM` | Apagado graceful — dejar de aceptar solicitudes, finalizar operaciones en curso, vaciar base de datos |
| `SIGINT` | Igual que SIGTERM (Ctrl+C) |

**Secuencia de apagado** (límite de 15 segundos):

1. Cancelar el contexto de la aplicación (señala a todas las goroutines que se detengan)
2. Detener el WebSocket hub (cerrar todas las conexiones de clientes)
3. Detener el gestor de sincronización git (finalizar operaciones de sincronización en curso)
4. Cerrar el motor de búsqueda (vaciar el índice Bleve a disco)
5. Drenar el pool de workers git (esperar operaciones git en curso)
6. Apagar el servidor HTTP (timeout de 10 segundos para solicitudes en curso)

Si el apagado excede los 15 segundos, el proceso se cierra forzosamente.

### Ejemplo

```bash
# Start on default port
docplatform serve

# Start on custom port
docplatform serve --port 8080

# Start with explicit data directory
docplatform serve --data-dir /var/lib/docplatform
```

### Salida

```
INFO  Server starting            port=3000 version=v0.5.0
INFO  Database initialized       path=.docplatform/data.db wal=true
INFO  Migrations applied         count=1
INFO  Search index ready         documents=42
INFO  Workspace loaded           name="Docs" slug=docs git_remote=git@github.com:...
INFO  Backup scheduler started   retention_days=7
INFO  Listening on               http://0.0.0.0:3000
```

---

## `docplatform init`

Inicializar un nuevo workspace.

```bash
docplatform init [flags]
```

### Flags

| Flag | Obligatorio | Predeterminado | Descripción |
|---|---|---|---|
| `--workspace-name` | Sí | — | Nombre visible del workspace |
| `--slug` | Sí | — | Identificador seguro para URL (usado en la URL de documentación publicada) |
| `--git-url` | No | — | URL del repositorio git remoto (SSH o HTTPS) |
| `--branch` | No | `main` | Rama de git a sincronizar |
| `--data-dir` | No | `.docplatform` | Ruta del directorio de datos |

### Comportamiento

1. Crea la estructura del directorio de datos (`{DATA_DIR}/`)
2. Inicializa la base de datos SQLite (si no está presente)
3. Genera una clave de firma JWT RS256 (si no está presente)
4. Crea el directorio del workspace (`{DATA_DIR}/workspaces/{ulid}/`)
5. Si se proporciona `--git-url`, clona el repositorio
6. Crea el archivo de configuración del workspace
7. Indexa cualquier archivo `.md` existente

### Ejemplo

```bash
# Local workspace (no git)
docplatform init \
  --workspace-name "Internal Wiki" \
  --slug wiki

# With git
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git \
  --branch main
```

### Salida

```
INFO  Data directory created     path=.docplatform
INFO  Database initialized       path=.docplatform/data.db
INFO  JWT key generated          path=.docplatform/jwt-key.pem
INFO  Workspace created          id=01KJJ10NTF... name="API Docs" slug=api-docs
INFO  Repository cloned          url=git@github.com:your-org/api-docs.git branch=main
INFO  Pages indexed              count=15
INFO  Ready. Run 'docplatform serve' to start.
```

---

## `docplatform rebuild`

Reconstruir la base de datos y el índice de búsqueda desde el sistema de archivos. Úselo cuando la base de datos esté desincronizada con los archivos reales en disco.

```bash
docplatform rebuild [flags]
```

### Flags

| Flag | Obligatorio | Predeterminado | Descripción |
|---|---|---|---|
| `--workspace-id` | No | todos | ULID de un workspace específico a reconstruir. Sin este flag, se reconstruyen todos los workspaces. |
| `--search` | No | `false` | También eliminar y reconstruir el índice de búsqueda Bleve |
| `--data-dir` | No | `.docplatform` | Ruta del directorio de datos |

### Comportamiento

1. Crea una copia de seguridad de la base de datos actual
2. Elimina la tabla `pages`
3. Escanea el sistema de archivos en busca de todos los archivos `.md` en los directorios `docs/` de los workspaces
4. Analiza el frontmatter y contenido de cada archivo
5. Inserta registros de páginas en la base de datos
6. Reconstruye el índice de búsqueda Bleve
7. Reporta los resultados de la reconciliación

### Cuándo usarlo

- Después de agregar, mover o eliminar manualmente archivos `.md` fuera de DocPlatform
- Después de un fallo que pueda haber dejado la base de datos inconsistente
- Después de restaurar archivos desde una copia de seguridad git
- Cuando `docplatform doctor` reporta discrepancias entre FS/DB

### Ejemplo

```bash
# Rebuild all workspaces
docplatform rebuild

# Rebuild a specific workspace
docplatform rebuild --workspace-id 01KJJ10NTF31Z1QJTG4ZRQZ2Z2
```

### Salida

```
INFO  Backup created             path=.docplatform/backups/pre-rebuild-20250115.db
INFO  Rebuilding workspace       id=01KJJ10NTF... name="API Docs"
INFO  Scanning filesystem        path=.docplatform/workspaces/01KJJ.../docs/
INFO  Pages found                count=42
INFO  Database rebuilt            inserted=42 updated=0 orphaned=3
INFO  Search index rebuilt        documents=42
INFO  Ghost recovery             matched=2 unmatched=1
INFO  Rebuild complete
```

**Recuperación fantasma:** Cuando se encuentran registros huérfanos en la base de datos (sin archivo correspondiente), DocPlatform intenta emparejarlos con archivos no indexados por hash de contenido. Esto recupera páginas que fueron movidas o renombradas fuera de DocPlatform.

---

## `docplatform doctor`

Ejecutar 9 verificaciones de diagnóstico sobre la salud de la plataforma.

```bash
docplatform doctor [flags]
```

### Flags

| Flag | Obligatorio | Predeterminado | Descripción |
|---|---|---|---|
| `--bundle` | No | `false` | Crear un archivo ZIP con la salida de diagnóstico para soporte |
| `--data-dir` | No | `.docplatform` | Ruta del directorio de datos |

### Verificaciones

| # | Verificación | Descripción |
|---|---|---|
| 1 | **Conexión de base de datos** | El archivo SQLite existe, es legible, modo WAL habilitado |
| 2 | **Versión del esquema** | Las migraciones están actualizadas |
| 3 | **Consistencia FS/DB** | Cada archivo en `docs/` tiene un registro en la base de datos, y viceversa |
| 4 | **Archivos huérfanos** | Archivos en disco sin registro en la base de datos |
| 5 | **Registros huérfanos** | Registros en la base de datos sin archivo en disco |
| 6 | **Salud del índice de búsqueda** | El conteo de documentos del índice Bleve coincide con el conteo de páginas |
| 7 | **Enlaces internos rotos** | Enlaces Markdown que apuntan a páginas inexistentes |
| 8 | **Validez del frontmatter** | Todas las páginas tienen frontmatter YAML válido con un título |
| 9 | **Conectividad del repositorio git remoto** | Si git está configurado, ¿se puede alcanzar el remoto? |

### Códigos de salida

| Código | Significado |
|---|---|
| `0` | Todas las verificaciones pasaron (saludable) |
| `1` | Una o más verificaciones fallaron o tuvieron advertencias |

Use el código de salida en scripts y monitorización:

```bash
docplatform doctor || echo "Health check failed"
```

### Ejemplo

```bash
docplatform doctor
```

### Salida

```
DocPlatform Health Check
========================

✓ Database connection          OK (WAL mode, 42 pages, 3 users)
✓ Schema version               OK (v1, up to date)
✓ FS/DB consistency            OK (42 files, 42 records)
✓ Orphaned files               OK (0 found)
✓ Orphaned records             OK (0 found)
✓ Search index health          OK (42 indexed, 42 expected)
⚠ Broken internal links        WARNING (2 broken links found)
  → guides/editor.md:15 → "old-page.md" (file not found)
  → api/endpoints.md:42 → "deprecated.md" (file not found)
✓ Frontmatter validity         OK (42/42 valid)
✓ Git remote connectivity      OK (git@github.com:your-org/docs.git)

Result: 8/9 passed, 1 warning
```

### Modo bundle

```bash
docplatform doctor --bundle
# Creates: docplatform-doctor-20250115.zip
```

El bundle se guarda en `{DATA_DIR}/diagnostics/docplatform-diagnostics-{timestamp}.zip` y contiene:

- `report.json` — resultados de diagnóstico estructurados
- Información del esquema (definiciones de tablas, sin datos de filas)
- Listado de archivos (rutas y tamaños, sin contenido)
- Información del sistema (SO, arquitectura, versión de Go)
- Últimas 1.000 líneas de logs de error
- Versión del servidor y configuración (con secretos redactados)

El bundle **nunca** incluye contenido de páginas, contraseñas, tokens ni claves privadas.

---

## `docplatform version`

Imprimir versión, hash de commit y fecha de compilación.

```bash
docplatform version
```

### Salida

```
docplatform v0.5.0 (commit: abc1234, built: 2025-01-15T10:00:00Z)
```

La información de versión se incrusta en tiempo de compilación mediante flags del linker. Útil para verificar qué versión está desplegada y para solicitudes de soporte.
