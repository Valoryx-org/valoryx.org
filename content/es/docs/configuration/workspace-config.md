---
title: Configuración del workspace
description: Configure las opciones a nivel de workspace — repositorio git remoto, tema, orden de navegación, valores predeterminados de publicación y más.
weight: 4
---

# Configuración del workspace

Cada workspace tiene su propio archivo de configuración en `.docplatform/workspaces/{workspace-id}/.docplatform/config.yaml`. Edite este archivo directamente o use la interfaz web (**Settings** → **Workspace**).

## Referencia completa de configuración

```yaml
# Workspace identity
workspace_id: 01KJJ10NTF31Z1QJTG4ZRQZ2Z2    # Auto-generated ULID
name: "Engineering Docs"                        # Display name
slug: eng-docs                                  # URL slug for published docs
description: "Internal engineering documentation"

# Git synchronization
git_remote: git@github.com:your-org/eng-docs.git
git_branch: main
git_auto_commit: true       # Auto-commit editor saves to git
sync_interval: 300          # Polling interval in seconds (0 = disabled)

# Theme
theme:
  mode: auto                # light, dark, auto (follows system preference)
  accent: blue              # Accent color for published site

# Publishing defaults
publishing:
  default_published: false  # New pages published by default?
  require_explicit_unpublish: false

# Permissions
permissions:
  default_role: viewer      # Role assigned to new workspace members

# Navigation (for published docs sidebar)
navigation:
  - title: "Overview"
    path: "index.md"
  - title: "Getting Started"
    path: "getting-started/index.md"
    children:
      - title: "Installation"
        path: "getting-started/installation.md"
      - title: "Configuration"
        path: "getting-started/configuration.md"
```

## Referencia de configuración

### Identidad

| Clave | Tipo | Descripción |
|---|---|---|
| `workspace_id` | string | ULID auto-generado en la creación. No lo cambie. |
| `name` | string | Nombre visible mostrado en la interfaz y el encabezado del sitio publicado |
| `slug` | string | Segmento de URL para documentación publicada: `/p/{slug}/`. Cambiarlo rompe las URLs existentes. |
| `description` | string | Descripción opcional para referencia interna |

### Git

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `git_remote` | string | — | URL del repositorio remoto (SSH o HTTPS) |
| `git_branch` | string | `main` | Rama con la que sincronizar |
| `git_auto_commit` | bool | `true` | Auto-confirmar los guardados del editor web |
| `sync_interval` | int | `300` | Segundos entre consultas al remoto. Establezca `0` para desactivar polling (solo webhook). |

### Tema

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `theme.mode` | string | `auto` | Esquema de color para documentación publicada: `light`, `dark`, `auto` |
| `theme.accent` | string | `blue` | Color de acento usado en documentación publicada para enlaces, botones y resaltados |

### Publicación

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `publishing.default_published` | bool | `false` | Si las nuevas páginas se publican por defecto |
| `publishing.require_explicit_unpublish` | bool | `false` | Cuando es true, las páginas deben despublicarse explícitamente (previene exclusión accidental) |

### Permisos

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `permissions.default_role` | string | `viewer` | Rol asignado a los usuarios que aceptan una invitación al workspace |

### Navegación

El array `navigation` controla el orden de la barra lateral en la documentación publicada. Sin él, las páginas se ordenan alfabéticamente.

```yaml
navigation:
  - title: "Overview"       # Display label
    path: "index.md"        # File path relative to docs/
  - title: "Guides"         # Section header (no path = non-clickable group)
    children:
      - title: "Editor"
        path: "guides/editor.md"
      - title: "Git Sync"
        path: "guides/git-integration.md"
```

**Reglas:**

- Cada entrada necesita un `title`
- Las entradas con `path` son enlaces a páginas
- Las entradas sin `path` pero con `children` son encabezados de sección
- La profundidad de anidamiento es ilimitada
- Las páginas no listadas en `navigation` siguen existiendo pero no aparecen en la barra lateral

## Editar la configuración

### Mediante la interfaz web

1. Abra el workspace en el editor web
2. Haga clic en **Settings** (icono de engranaje)
3. Modifique la configuración a través de la interfaz de formulario
4. Los cambios se guardan automáticamente

### Mediante archivo de configuración

Edite el archivo YAML directamente:

```bash
# Find your workspace config
ls .docplatform/workspaces/*/. docplatform/config.yaml

# Edit
nano .docplatform/workspaces/01KJJ.../. docplatform/config.yaml
```

Reinicie el servidor para que los cambios surtan efecto, o active una recarga mediante la API:

```bash
curl -X POST http://localhost:3000/api/v1/admin/reload \
  -H "Authorization: Bearer {token}"
```

### Mediante git

Si el archivo de configuración del workspace está rastreado en git, haga push de los cambios desde su IDE y se recogerán en el siguiente ciclo de sincronización. Esto es útil para gestionar la configuración de documentación como código.

## Múltiples workspaces

DocPlatform soporta múltiples workspaces en una sola instancia. Cada workspace está completamente aislado:

- Directorios de contenido separados
- Repositorios git separados
- Listas de miembros y roles separados
- Índices de búsqueda separados
- Sitios publicados separados (diferentes slugs)

Cree workspaces adicionales mediante CLI:

```bash
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git
```

O mediante el selector de workspaces en la interfaz web.
