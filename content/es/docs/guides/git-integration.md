---
title: Integración con Git
description: Sincronización bidireccional de git — edite en el navegador o haga push desde su IDE, todo se mantiene sincronizado.
weight: 3
---

# Integración con Git

La sincronización bidireccional de git de DocPlatform permite que su equipo trabaje como prefiera. Los redactores técnicos usan el editor web. Los desarrolladores hacen push desde su IDE. Todos ven el mismo contenido.

## Cómo funciona

```
        ┌─────────────┐
        │ Web Editor   │
        │ (browser)    │
        └──────┬───────┘
               │ save
               ▼
        ┌─────────────┐          ┌──────────────┐
        │ Content     │  commit  │ Local Git    │  push    ┌──────────────┐
        │ Ledger      │ ───────► │ Repository   │ ───────► │ Remote Repo  │
        │             │          │ (.git)       │          │ (GitHub etc) │
        └─────────────┘          └──────┬───────┘          └──────┬───────┘
               ▲                        │                         │
               │ reconcile              │ pull                    │
               │                 ┌──────▼───────┐                 │
               └──────────────── │ Sync Engine  │ ◄───────────────┘
                                 │ (polling /   │   webhook / poll
                                 │  webhook)    │
                                 └──────────────┘
```

### Web → Git (salida)

1. Usted guarda una página en el editor web
2. El Content Ledger escribe el archivo `.md` en disco
3. El motor git auto-confirma: `docs: update {page-title}`
4. Los commits se envían al repositorio remoto

### Git → Web (entrada)

1. Alguien hace push de un commit al remoto (desde IDE, CI, etc.)
2. El motor de sincronización detecta el cambio (polling o webhook)
3. Los cambios se descargan al repositorio local
4. El Content Ledger reconcilia: sistema de archivos → base de datos → índice de búsqueda
5. WebSocket transmite la actualización a los navegadores conectados

## Configuración

### Conectar un repositorio remoto

**Durante la inicialización:**

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

**Después de la inicialización** — edite la configuración del workspace:

```yaml
# .docplatform/workspaces/{id}/.docplatform/config.yaml
git_remote: git@github.com:your-org/docs.git
git_branch: main
git_auto_commit: true
sync_interval: 300
```

Reinicie el servidor o active una sincronización manual.

### Autenticación

#### SSH (recomendado)

Genere una clave de deploy y agréguela a su repositorio:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""
```

Establezca la variable de entorno:

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

Agregue la clave pública (`~/.ssh/docplatform_deploy_key.pub`) a las claves de deploy de su repositorio. **Habilite el acceso de escritura** si desea que DocPlatform haga push de commits.

#### HTTPS con token

Para repositorios HTTPS, incluya el token en la URL:

```yaml
git_remote: https://x-access-token:ghp_xxxxxxxxxxxx@github.com/your-org/docs.git
```

O use un Git credential helper configurado en el host.

## Comportamiento de sincronización

### Auto-commit

Cuando `git_auto_commit: true` (predeterminado), cada guardado en el editor web produce un git commit. Las ediciones rápidas dentro de una ventana corta se agrupan en un solo commit.

Formato del mensaje de commit:

```
docs: update Getting Started

Edited via DocPlatform web editor
Author: jane@example.com
```

Establezca `git_auto_commit: false` para desactivar el auto-commit. En este modo, el editor web escribe en el sistema de archivos pero no crea git commits — útil si desea confirmar manualmente o según un horario.

### Polling

DocPlatform consulta el repositorio remoto en el intervalo configurado (predeterminado: 300 segundos / 5 minutos). Ajústelo con:

```yaml
sync_interval: 60  # check every minute
```

Intervalos más cortos significan sincronización más rápida pero más tráfico de red.

### Webhooks

Para sincronización instantánea, configure un webhook en su repositorio:

**GitHub:**

1. Vaya a **Settings** → **Webhooks** → **Add webhook**
2. Payload URL: `https://your-domain.com/api/v1/webhooks/github`
3. Content type: `application/json`
4. Secret: Establezca la variable de entorno `GIT_WEBHOOK_SECRET` con el mismo valor
5. Events: Seleccione **Push events**

**GitLab:**

1. Vaya a **Settings** → **Webhooks**
2. URL: `https://your-domain.com/api/v1/webhooks/gitlab`
3. Secret token: Debe coincidir con `GIT_WEBHOOK_SECRET`
4. Trigger: **Push events**

**Bitbucket:**

1. Vaya a **Repository settings** → **Webhooks** → **Add webhook**
2. URL: `https://your-domain.com/api/v1/webhooks/bitbucket`
3. Triggers: **Repository push**

### Sincronización manual

Active una sincronización desde la interfaz web (**Settings** → **Git** → **Sync Now**) o mediante la API:

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{id}/sync \
  -H "Authorization: Bearer {token}"
```

## Resolución de conflictos

Los conflictos ocurren cuando el mismo archivo se modifica tanto en el editor web como mediante git push entre intervalos de sincronización.

### Cómo se detectan los conflictos

DocPlatform rastrea hashes de contenido (SHA-256) para cada página. Al descargar cambios remotos, compara el hash entrante contra el hash local. Si ambos difieren del ancestro común, se declara un conflicto.

### Qué sucede en un conflicto

1. La operación de guardado o sincronización devuelve **HTTP 409 Conflict**
2. Ambas versiones (local y remota) se preservan
3. La interfaz web muestra un banner de conflicto con opciones:
   - **Keep local** — descartar la versión remota
   - **Keep remote** — descartar la versión local
   - **Download both** — obtener ambos archivos para merge manual
4. Se crea una rama de conflicto (`conflict/{page-slug}-{timestamp}`) con la versión local

### Prevenir conflictos

- **Use webhooks** en lugar de polling — una sincronización más rápida significa ventanas de conflicto más pequeñas
- **Asigne propiedad de páginas** — un escritor por página reduce el riesgo de colisión
- **Use el editor web para contenido**, IDE para código — separación natural
- **Intervalos de sincronización cortos** — `sync_interval: 30` en entornos de alta colaboración

## Sincronización por lotes

Cuando un push remoto contiene más de 20 archivos modificados, DocPlatform cambia a modo por lotes:

1. Obtiene todos los archivos modificados en un solo diff
2. Adquiere mutexes por ruta para todas las rutas afectadas (ordenadas para prevenir deadlock)
3. Procesa todos los archivos en una sola transacción de base de datos
4. Invalida la caché de permisos una vez (no por archivo)
5. Emite un solo mensaje WebSocket `bulk-sync` con el conteo total de cambios

Esto previene tormentas de notificaciones y sobrecarga de base de datos cuando se envían cambios grandes (por ejemplo, importación inicial del repositorio o reestructuración masiva).

## Almacenamiento de conflictos

Cuando se detecta un conflicto, ambas versiones se almacenan en disco:

```
.docplatform/conflicts/
└── {page-id}/
    └── 20250115T103045Z/
        ├── ours.md      # Local version (web editor)
        └── theirs.md    # Remote version (git push)
```

Los conflictos persisten hasta que se resuelven explícitamente mediante la interfaz web o la API. El comando `docplatform doctor` reporta conflictos sin resolver.

## Detalles del motor git

DocPlatform usa un motor git híbrido que selecciona automáticamente el mejor backend:

| Condición | Motor | Por qué |
|---|---|---|
| Menos de 5.000 archivos | **go-git** (en proceso) | Rápido, sin dependencia externa, Go puro |
| Más de 5.000 archivos | **Native git CLI** (subproceso) | Mejor manejo de repositorios grandes, clones superficiales |
| go-git RSS > 512 MB | **Native git CLI** (fallback) | Seguridad de memoria — previene OOM en repositorios grandes |

Un pool de trabajadores de **4 workers concurrentes** maneja las operaciones git en todos los workspaces. Cada workspace tiene su propio mutex — las operaciones en diferentes workspaces se ejecutan en paralelo, mientras que las operaciones en el mismo workspace se serializan.

Los mensajes de auto-commit usan este formato:

```
docs: update {page-title}

Edited via DocPlatform web editor
Author: user@example.com
Committer: DocPlatform <docplatform@local>
```

## Trabajar con repositorios existentes

DocPlatform funciona con repositorios de documentación existentes. Cuando conecta un repositorio:

1. El repositorio se clona (o se actualiza si ya existe localmente)
2. Todos los archivos `.md` en el directorio `docs/` se indexan
3. El frontmatter se analiza y los metadatos de páginas se almacenan en SQLite
4. El índice de búsqueda se construye incrementalmente

Los archivos fuera de `docs/` no se indexan ni se muestran en el editor, pero permanecen en el repositorio git sin modificar.

### Importar desde otras plataformas

DocPlatform funciona con cualquier contenido Markdown. Así puede migrar desde plataformas comunes:

| Origen | Método de exportación | Notas |
|---|---|---|
| **Docusaurus** | Copia directa | Ya está basado en `.md` — copie el directorio `docs/` tal cual, agregue frontmatter si falta |
| **GitBook** | Exportación JSON → convertir | Exporte mediante la API de GitBook, convierta a Markdown |
| **Notion** | Exportación Markdown | Exporte el workspace como Markdown, reestructure en jerarquía `docs/` |
| **Confluence** | Exportación HTML → convertir | Exporte espacios como HTML, convierta a Markdown con pandoc o similar |
| **Wiki.js** | Exportación de base de datos | Exporte páginas como Markdown desde el panel de administración |

**Pasos generales de migración:**

1. Exporte su contenido como archivos Markdown
2. Colóquelos en un repositorio git bajo `docs/`
3. Agregue frontmatter YAML (como mínimo, `title`) a cada archivo
4. Conecte el repositorio a DocPlatform
5. Ejecute `docplatform rebuild` para forzar una reconciliación completa

El reconciliador de DocPlatform descubre automáticamente todos los archivos `.md`, analiza su frontmatter, asigna ULIDs a las páginas que carecen de un campo `id` y construye el índice de búsqueda.
