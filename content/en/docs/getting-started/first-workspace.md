---
title: Your First Workspace
description: Create and configure a documentation workspace — connect git, set up the content structure, and invite your team.
weight: 3
---

# Your First Workspace

A workspace is the top-level container for a documentation project. Each workspace maps to a directory of Markdown files and optionally syncs with a git repository.

## Workspace concepts

| Concept | Description |
|---|---|
| **Workspace** | A documentation project containing pages, members, and settings |
| **Page** | A Markdown file with YAML frontmatter (title, description, tags, access) |
| **Slug** | The URL-safe identifier for your workspace (e.g., `my-docs` → `/p/my-docs/`) |
| **Member** | A user with a role in the workspace (Viewer through Admin) |

## Create a workspace

### Via web UI (recommended)

1. Sign in as your organization's Super Admin
2. Open the workspace switcher (top-left dropdown)
3. Click **Create Workspace**
4. Enter a name and slug
5. Optionally configure a git remote

### Via CLI

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs
```

> **Note:** `docplatform init` attaches the workspace to a server-level *default organization*, not to any web account's organization. Use it for headless/bootstrap scenarios (e.g., pre-cloning a git repo before first run). For day-to-day use, create workspaces from the web UI so they belong to your organization.

## Connect a git repository

Bidirectional sync keeps your workspace files and a remote git repository in lockstep.

### During initialization

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs \
  --git-url git@github.com:your-org/eng-docs.git \
  --branch main
```

### After creation

Connect a repository from the web UI: **Workspace Settings → Git**. Validate a GitHub personal access token, pick the repository and branch, and DocPlatform stores the connection (the token is encrypted at rest with AES-256-GCM). Git settings — remote, branch, auto-commit, and sync interval — live in the workspace record and can be changed there at any time; no server restart is required.

### SSH key setup

For private repositories, DocPlatform uses a dedicated SSH deploy key:

```bash
# Generate a deploy key (no passphrase)
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""

# Add the public key to your repository's deploy keys
cat ~/.ssh/docplatform_deploy_key.pub
# → Copy this to GitHub/GitLab Settings → Deploy Keys (enable write access)
```

Set the environment variable:

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

### How sync works

```
┌─────────────┐     auto-commit + push      ┌──────────────┐
│ Web Editor   │ ──────────────────────────► │ Remote Repo  │
│ (browser)    │                             │ (GitHub, etc)│
│              │ ◄────────────────────────── │              │
└─────────────┘     polling / webhook        └──────────────┘
```

**Web → Git:** When you save in the editor, DocPlatform writes the `.md` file, auto-commits with a descriptive message, and pushes to the remote.

**Git → Web:** DocPlatform polls the remote (default: every 5 minutes) or listens for webhooks. New commits are pulled and the web UI updates in real-time via WebSocket.

**Conflicts:** If both sides change the same file between syncs, DocPlatform detects the collision using content hashes, returns HTTP 409, and makes both versions downloadable so you can resolve manually.

## Organize your content

### Page hierarchy

Pages can be nested to any depth. The file structure in the workspace directory maps directly to the URL structure:

```
(workspace root)
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

Every page starts with YAML frontmatter:

```yaml
---
title: Authentication
description: How to authenticate with the API using JWT tokens.
tags: [api, auth, jwt]
publish: true         # include this page on the published site
status: draft         # optional editorial status
nav_order: 2          # optional ordering hint for sidebar navigation
---
```

The `title` is required. All other fields are optional. `tags` accepts either a YAML list or a comma-separated string. An `access` block is parsed and preserved if present, but per-page access control is **not enforced** — permissions are role-based at the workspace level.

## Invite your team

### Via web UI

1. Open **Workspace Settings** → **Members**
2. Click **Invite**
3. Enter the person's email address
4. Select a role (Viewer, Commenter, Editor, Admin)
5. Click **Send Invitation**

If SMTP is configured, the invitation is sent by email. Otherwise, a shareable invitation link is displayed.

### Roles

| Role | Can view | Can comment | Can edit | Can manage members | Can manage workspace |
|---|---|---|---|---|---|
| **Viewer** | Yes | | | | |
| **Commenter** | Yes | Yes | | | |
| **Editor** | Yes | Yes | Yes | | |
| **Admin** | Yes | Yes | Yes | Yes | Yes |
| **Super Admin** | Full platform access across all workspaces |

For detailed permission configuration, see [Roles & Permissions](../configuration/permissions.md).

## Workspace settings

Access workspace settings through the web UI (**Settings** gear icon).

Key settings:

| Setting | Description | Default |
|---|---|---|
| `name` | Display name of the workspace | — |
| `slug` | URL slug for published docs | — |
| `git_remote` | Remote git repository URL | (none) |
| `git_branch` | Branch to sync | `main` |
| `git_auto_commit` | Auto-commit editor saves | `true` |
| `sync_interval` | Git polling interval (seconds) | `300` |
| `theme` | Published-site theme (7 available) | `default` |
| `visibility` | Published-site access: `authenticated` or `public` | `authenticated` |

For the complete configuration reference, see [Workspace Settings](../configuration/workspace-config.md).

## What's next

Your workspace is ready. Here's where to go from here:

| Goal | Guide |
|---|---|
| Learn the web editor | [The Web Editor](../guides/editor.md) |
| Set up published docs | [Publishing](../guides/publishing.md) |
| Configure authentication | [Authentication](../configuration/authentication.md) |
| Deploy to production | [Production Checklist](../deployment/production.md) |
