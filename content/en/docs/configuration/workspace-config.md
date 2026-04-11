---
title: Workspace Settings
description: Configure workspace-level settings — git remote, theme, navigation order, publishing defaults, and more.
weight: 4
---

# Workspace Settings

Each workspace has its own configuration file at `.docplatform/workspaces/{workspace-id}/.docplatform/config.yaml`. Edit this file directly or use the web UI (**Settings** → **Workspace**).

## Full configuration reference

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

## Settings reference

### Identity

| Key | Type | Description |
|---|---|---|
| `workspace_id` | string | ULID auto-generated at creation. Do not change. |
| `name` | string | Display name shown in the UI and published site header |
| `slug` | string | URL segment for published docs: `/p/{slug}/`. Changing this breaks existing URLs. |
| `description` | string | Optional description for internal reference |

### Git

| Key | Type | Default | Description |
|---|---|---|---|
| `git_remote` | string | — | Remote repository URL (SSH or HTTPS) |
| `git_branch` | string | `main` | Branch to sync with |
| `git_auto_commit` | bool | `true` | Auto-commit saves from the web editor |
| `sync_interval` | int | `300` | Seconds between polling the remote. Set to `0` to disable polling (webhook-only). |

### Theme

| Key | Type | Default | Description |
|---|---|---|---|
| `theme.mode` | string | `auto` | Color scheme for published docs: `light`, `dark`, `auto` |
| `theme.accent` | string | `blue` | Accent color used in published docs for links, buttons, and highlights |

### Publishing

| Key | Type | Default | Description |
|---|---|---|---|
| `publishing.default_published` | bool | `false` | Whether new pages are published by default |
| `publishing.require_explicit_unpublish` | bool | `false` | When true, pages must be explicitly unpublished (prevents accidental exclusion) |

### Permissions

| Key | Type | Default | Description |
|---|---|---|---|
| `permissions.default_role` | string | `viewer` | Role assigned to users who accept a workspace invitation |

### Navigation

The `navigation` array controls the sidebar order in published docs. Without it, pages are ordered alphabetically.

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

**Rules:**

- Each entry needs a `title`
- Entries with a `path` are page links
- Entries without a `path` but with `children` are section headers
- Nesting depth is unlimited
- Pages not listed in `navigation` still exist but don't appear in the sidebar

## Editing settings

### Via web UI

1. Open the workspace in the web editor
2. Click **Settings** (gear icon)
3. Modify settings through the form interface
4. Changes save automatically

### Via config file

Edit the YAML file directly:

```bash
# Find your workspace config
ls .docplatform/workspaces/*/. docplatform/config.yaml

# Edit
nano .docplatform/workspaces/01KJJ.../. docplatform/config.yaml
```

Restart the server for changes to take effect, or trigger a reload via the API:

```bash
curl -X POST http://localhost:3000/api/v1/admin/reload \
  -H "Authorization: Bearer {token}"
```

### Via git

If the workspace config file is tracked in git, push changes from your IDE and they'll be picked up on the next sync cycle. This is useful for managing documentation configuration as code.

## Multiple workspaces

DocPlatform supports multiple workspaces on a single instance. Each workspace is fully isolated:

- Separate content directories
- Separate git repositories
- Separate member lists and roles
- Separate search indexes
- Separate published sites (different slugs)

Create additional workspaces via CLI:

```bash
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git
```

Or via the web UI workspace switcher.
