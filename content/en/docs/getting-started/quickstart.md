---
title: Quickstart
description: Get DocPlatform running in under 5 minutes with a fully functional documentation workspace.
weight: 1
---

# Quickstart

Go from zero to a running documentation platform in under 5 minutes. This guide covers the fastest path — for detailed options, see the [Installation](installation.md) guide.

## Step 1: Install

```bash
# Recommended (auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh
```

Or download manually:

```bash
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform
```

Or with Docker:

```bash
docker run -d --name docplatform -p 3000:3000 -v docplatform-data:/data ghcr.io/valoryx-org/docplatform:latest
```

If using Docker, skip to [Step 3](#step-3-register-your-account) — the container auto-initializes.

## Step 2: Initialize a workspace

```bash
docplatform init --workspace-name "My Docs" --slug my-docs
```

This creates:

```
.docplatform/
├── data.db              # SQLite database
├── jwt-private.pem      # Auto-generated RS256 signing key
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Your documentation lives here
        └── .docplatform/
            └── config.yaml
```

### With git (optional)

Connect to an existing git repository during initialization:

```bash
docplatform init \
  --workspace-name "My Docs" \
  --slug my-docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

DocPlatform clones the repository and begins syncing. Any existing `.md` files are automatically indexed.

## Step 3: Start the server

```bash
docplatform serve
```

```
INFO  Server starting            addr=:3000 version=v0.5.2
INFO  Database initialized       path=.docplatform/data.db
INFO  Search index ready         documents=0
INFO  Workspace loaded           name="My Docs" slug=my-docs
INFO  Listening on               http://localhost:3000
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Step 4: Register your account

The first user to register automatically becomes the **SuperAdmin** with full platform access.

1. Click **Create Account**
2. Enter your name, email, and password
3. You're signed in and ready to write

> **Security note:** The first-user-becomes-admin flow only applies when no users exist. After the first registration, new accounts get the default role configured for the workspace.

## Step 5: Create your first page

1. Click **New Page** in the sidebar
2. Give it a title — the URL slug auto-generates from the title
3. Start writing in the rich editor
4. Changes autosave every few seconds

The page is stored as a Markdown file in your workspace's `docs/` directory. If you connected git, it auto-commits and pushes.

## Step 6: Try it out

Here are a few things to try right away:

| Action | How |
|---|---|
| **Switch to raw Markdown** | Click the `</>` toggle in the editor toolbar |
| **Search** | Press `Cmd+K` (or `Ctrl+K`) to open instant search |
| **Create a sub-page** | Click the `+` next to an existing page in the sidebar |
| **Preview published site** | Navigate to `http://localhost:3000/p/my-docs/` |
| **Run diagnostics** | Run `docplatform doctor` in your terminal |

## What's next

| Goal | Guide |
|---|---|
| Connect a git repository | [Git Integration](../guides/git-integration.md) |
| Invite your team | [Teams & Collaboration](../guides/collaboration.md) |
| Publish docs publicly | [Publishing](../guides/publishing.md) |
| Deploy to production | [Deployment](../deployment/binary.md) |
| Configure auth providers | [Authentication](../configuration/authentication.md) |
