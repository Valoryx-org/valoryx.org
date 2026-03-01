---
title: Su primer workspace
description: Cree y configure un workspace de documentación — conecte git, establezca la estructura de contenido e invite a su equipo.
weight: 3
---

# Su primer workspace

Un workspace es el contenedor de nivel superior para un proyecto de documentación. Cada workspace se corresponde con un directorio de archivos Markdown y opcionalmente se sincroniza con un repositorio git.

## Conceptos del workspace

| Concepto | Descripción |
|---|---|
| **Workspace** | Un proyecto de documentación que contiene páginas, miembros y configuraciones |
| **Página** | Un archivo Markdown con frontmatter YAML (título, descripción, etiquetas, acceso) |
| **Slug** | El identificador seguro para URL de su workspace (por ejemplo, `my-docs` → `/p/my-docs/`) |
| **Miembro** | Un usuario con un rol en el workspace (desde Viewer hasta WorkspaceAdmin) |

## Crear un workspace

### Mediante CLI

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs
```

### Mediante la interfaz web

1. Inicie sesión como SuperAdmin o WorkspaceAdmin
2. Abra el selector de workspaces (menú desplegable superior izquierdo)
3. Haga clic en **Create Workspace**
4. Ingrese un nombre y un slug
5. Opcionalmente configure un repositorio git remoto

## Conectar un repositorio git

La sincronización bidireccional mantiene los archivos de su workspace y un repositorio git remoto en perfecta sincronía.

### Durante la inicialización

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs \
  --git-url git@github.com:your-org/eng-docs.git \
  --branch main
```

### Después de la creación

Actualice la configuración del workspace en `.docplatform/workspaces/{id}/.docplatform/config.yaml`:

```yaml
git_remote: git@github.com:your-org/eng-docs.git
git_branch: main
git_auto_commit: true
sync_interval: 300  # seconds
```

Luego reinicie el servidor o active una sincronización manual desde la interfaz web.

### Configuración de clave SSH

Para repositorios privados, DocPlatform usa una clave SSH de deploy dedicada:

```bash
# Generate a deploy key (no passphrase)
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""

# Add the public key to your repository's deploy keys
cat ~/.ssh/docplatform_deploy_key.pub
# → Copy this to GitHub/GitLab Settings → Deploy Keys (enable write access)
```

Establezca la variable de entorno:

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

### Cómo funciona la sincronización

```
┌─────────────┐     auto-commit + push      ┌──────────────┐
│ Web Editor   │ ──────────────────────────► │ Remote Repo  │
│ (browser)    │                             │ (GitHub, etc)│
│              │ ◄────────────────────────── │              │
└─────────────┘     polling / webhook        └──────────────┘
```

**Web → Git:** Cuando guarda en el editor, DocPlatform escribe el archivo `.md`, auto-confirma con un mensaje descriptivo y hace push al remoto.

**Git → Web:** DocPlatform consulta el remoto (por defecto: cada 5 minutos) o escucha webhooks. Los nuevos commits se descargan y la interfaz web se actualiza en tiempo real mediante WebSocket.

**Conflictos:** Si ambos lados modifican el mismo archivo entre sincronizaciones, DocPlatform detecta la colisión usando hashes de contenido, devuelve HTTP 409, y pone ambas versiones disponibles para descarga para que pueda resolver manualmente.

## Organizar su contenido

### Jerarquía de páginas

Las páginas se pueden anidar a cualquier profundidad. La estructura de archivos en `docs/` se corresponde directamente con la estructura de URLs:

```
docs/
├── index.md                → /p/eng-docs/
├── getting-started.md      → /p/eng-docs/getting-started
├── api/
│   ├── index.md            → /p/eng-docs/api/
│   ├── authentication.md   → /p/eng-docs/api/authentication
│   └── endpoints.md        → /p/eng-docs/api/endpoints
└── guides/
    ├── deployment.md       → /p/eng-docs/guides/deployment
    └── contributing.md     → /p/eng-docs/guides/contributing
```

### Frontmatter

Cada página comienza con frontmatter YAML:

```yaml
---
title: Authentication
description: How to authenticate with the API using JWT tokens.
tags: [api, auth, jwt]
published: true
access: public        # public, workspace, restricted
allowed_roles: []     # only used when access: restricted
---
```

El campo `title` es obligatorio. Todos los demás campos son opcionales y tienen valores predeterminados razonables.

## Invitar a su equipo

### Mediante la interfaz web

1. Abra **Workspace Settings** → **Members**
2. Haga clic en **Invite**
3. Ingrese la dirección de correo electrónico de la persona
4. Seleccione un rol (Viewer, Commenter, Editor, Admin)
5. Haga clic en **Send Invitation**

Si SMTP está configurado, la invitación se envía por correo electrónico. De lo contrario, se muestra un enlace de invitación que puede compartir.

### Roles

| Rol | Puede ver | Puede comentar | Puede editar | Puede gestionar miembros | Puede gestionar workspace |
|---|---|---|---|---|---|
| **Viewer** | Sí | | | | |
| **Commenter** | Sí | Sí | | | |
| **Editor** | Sí | Sí | Sí | | |
| **Admin** | Sí | Sí | Sí | Sí | |
| **WorkspaceAdmin** | Sí | Sí | Sí | Sí | Sí |
| **SuperAdmin** | Acceso completo a la plataforma en todos los workspaces |

Para la configuración detallada de permisos, consulte [Roles y permisos](../configuration/permissions.md).

## Configuración del workspace

Acceda a la configuración del workspace a través de la interfaz web (icono de engranaje **Settings**) o editando directamente el archivo de configuración.

Configuraciones clave:

| Configuración | Descripción | Predeterminado |
|---|---|---|
| `name` | Nombre visible del workspace | — |
| `slug` | Slug de URL para documentación publicada | — |
| `git_remote` | URL del repositorio git remoto | (ninguno) |
| `git_branch` | Rama a sincronizar | `main` |
| `git_auto_commit` | Auto-confirmar las ediciones guardadas | `true` |
| `sync_interval` | Intervalo de polling de git (segundos) | `300` |
| `theme.mode` | Esquema de color: `light`, `dark`, `auto` | `auto` |
| `theme.accent` | Color de acento | `blue` |
| `permissions.default_role` | Rol para nuevos miembros | `viewer` |

Para la referencia completa de configuración, consulte [Configuración del workspace](../configuration/workspace-config.md).

## Próximos pasos

Su workspace está listo. A continuación:

| Objetivo | Guía |
|---|---|
| Aprender a usar el editor web | [El editor web](../guides/editor.md) |
| Configurar la documentación publicada | [Publicación](../guides/publishing.md) |
| Configurar la autenticación | [Autenticación](../configuration/authentication.md) |
| Desplegar en producción | [Lista de verificación de producción](../deployment/production.md) |
