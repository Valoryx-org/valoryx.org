---
title: Workspace Settings
description: Configure workspace-level settings — git remote, theme, navigation, publishing overlay, and the .docplatform manifest files.
weight: 4
---

# Workspace Settings

Workspace settings live in two places:

1. **The database** — identity, git connection, and permission settings, edited through the web UI (**Settings** gear icon) or the REST API. These are not stored in a config file.
2. **Manifest files** under `.docplatform/` in the workspace's content directory — display and publishing configuration that versions alongside your content and flows through git sync like any other file.

## Database-backed settings

Edited via **Settings** in the web UI, or `PATCH /api/v1/workspaces/:id`:

| Setting | Type | Default | Description |
|---|---|---|---|
| `name` | string | — | Display name shown in the UI and published site header |
| `slug` | string | — | URL segment for published docs: `/p/{slug}/`. Changing this breaks existing URLs. |
| `description` | string | — | Optional description for internal reference |
| `git_remote` | string | — | Remote repository URL (SSH or HTTPS) |
| `git_branch` | string | `main` | Branch to sync with |
| `git_auto_commit` | bool | `true` | Auto-commit saves from the web editor (requires a git remote) |
| `sync_interval` | int | `300` | Seconds between polling the remote (minimum 10) |
| `editor_can_create_pages` | bool | `true` | Whether Editors may create pages |
| `editor_can_delete_pages` | bool | `false` | Whether Editors may delete pages |

The published site has its own settings — theme (7 built-in themes), visibility (`authenticated` or `public`), navigation groups, and custom domain — managed under **Settings → Publishing** (`PUT /api/v1/workspaces/:id/admin/settings`). See the [Publishing guide](../guides/publishing.md).

## Manifest files (`.docplatform/`)

Each workspace's content directory contains a `.docplatform/` folder with up to four YAML manifests. Because they are regular files in the git tree, you can edit them from your IDE and push — changes are picked up on the next sync.

| File | Purpose |
|---|---|
| `workspace.yaml` | Display settings: name, description, published-site theme, custom CSS, editor defaults |
| `publish.yaml` | Publishing overlay: per-path publish decisions, landing page, SEO and robots settings |
| `nav.yaml` | Published-site sidebar navigation tree |
| `redirects.yaml` | URL redirects for the published site |

### `workspace.yaml`

```yaml
version: 1
name: "Engineering Docs"
description: "Internal engineering documentation"
theme: default              # one of the 7 built-in themes
custom_css_path: ""         # optional path to a custom stylesheet
editor_defaults:
  collapse_sidebar: false
  show_line_numbers_in_code: false
```

### `publish.yaml`

The publish overlay has the **final say** on whether a page appears on the published site — an entry here overrides the page's frontmatter `publish:` flag. A malformed overlay never knocks pages offline; DocPlatform logs the problem and falls back to frontmatter.

```yaml
version: 1
landing:
  mode: page                # what / serves: a page or custom markdown
  page: index.md
pages:
  - path: internal/draft.md
    public: false           # overrides frontmatter publish: true
  - path: announcements/launch.md
    public: true
```

### `nav.yaml`

Controls the published-site sidebar. Without it, navigation is derived from the page tree.

```yaml
version: 1
tree:
  - file: index.md
  - section: "Guides"
    collapsed: false
    children:
      - file: guides/editor.md
      - file: guides/git-integration.md
  - heading: "Resources"
  - link: "Status page"
    url: https://status.example.com
```

Node types: `file` (a page link), `section` (a collapsible group with `children`), `heading` (a non-clickable label), and `link`/`url` (an external link).

### Conflict behavior during git sync

If both the web editor and a git push change the same manifest, DocPlatform three-way-merges `workspace.yaml`, `publish.yaml`, and `redirects.yaml` automatically. Conflicts in `nav.yaml` — and in **all** Markdown pages — are never auto-merged; they are surfaced for a human to resolve. See [Git Integration](../guides/git-integration.md).

## Editing settings

### Via web UI

1. Open the workspace in the web editor
2. Click **Settings** (gear icon)
3. Modify settings through the form interface — changes apply immediately

### Via git

Edit the `.docplatform/` manifests from your IDE and push. They're picked up on the next sync cycle — useful for managing documentation configuration as code, with publish decisions visible in code review.

## Multiple workspaces

DocPlatform supports multiple workspaces on a single instance. Each workspace is fully isolated:

- Separate content directories
- Separate git repositories
- Separate member lists and roles
- Search results scoped per workspace
- Separate published sites (different slugs)

Create additional workspaces from the web UI workspace switcher (org Super Admin).
