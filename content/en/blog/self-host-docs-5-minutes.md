---
title: "Self-Host Your Docs in 5 Minutes"
description: "A step-by-step tutorial: download DocPlatform, run a single binary, create your first workspace, and publish documentation. No Docker, no database."
date: "2026-03-02"
author: "Valoryx Team"
tags: ["self-hosted", "tutorial", "documentation"]
---

Most self-hosted documentation tools require a database, a reverse proxy, and half an afternoon of YAML editing before you see a welcome screen. DocPlatform is a single Go binary with zero external dependencies. This tutorial takes you from nothing to published documentation in about five minutes.

## Prerequisites

You need a Linux, macOS, or Windows machine. That's it. No Docker, no PostgreSQL, no Node.js runtime. DocPlatform compiles to a single static binary — the Go runtime is embedded. If you're curious about the implementation language, [Go](https://go.dev/) produces self-contained executables that run without installing anything on the host.

## Step 1: Download and Install

On Linux or macOS, the install script handles everything:

```bash
curl -fsSL https://valoryx.org/install.sh | bash
```

This downloads the latest release binary to `/usr/local/bin/docplatform` (or `~/.local/bin/` if you don't have root access). On macOS with Homebrew, you can also run:

```bash
brew install valoryx/tap/docplatform
```

On Windows, grab the `.exe` from the [releases page](/install/) and add it to your PATH.

Verify the installation:

```bash
docplatform version
# DocPlatform v1.x.x (linux/amd64)
```

## Step 2: Start the Server

Run the server with default settings:

```bash
docplatform serve
```

You'll see output like this:

```
INFO  Starting DocPlatform server
INFO  Data directory: ./data
INFO  Listening on http://localhost:3000
INFO  Full-text search index: ready
INFO  Admin setup required — visit http://localhost:3000 to create your account
```

Open `http://localhost:3000` in your browser. DocPlatform serves both the editor and the published site from the same binary on the same port. No separate frontend build step.

On first launch, you'll see the admin setup screen. Pick a username and password. This creates the super admin account — the one that can manage everything. You can add more users later through the admin panel.

## Step 3: Create Your First Workspace

After logging in, the dashboard shows an empty workspace list. Click **New Workspace** and fill in:

- **Name:** `engineering-handbook` (or whatever you're documenting)
- **Slug:** `engineering-handbook` (this becomes the URL path)
- **Theme:** Pick one of the 5 built-in themes — you can change it later

Click **Create**. You now have a workspace with a root page ready to edit.

## Step 4: Write Some Documentation

Click into your new workspace and you'll land in the [WYSIWYG editor](/docs/getting-started/first-workspace/). It supports markdown shortcuts — type `##` followed by a space to create an H2, use backticks for inline code, triple backticks for code blocks. Everything you'd expect from a modern editor, but rendered as rich text as you type.

Create a few pages to get a feel for it:

1. Click **New Page** in the sidebar
2. Give it a title: "Getting Started"
3. Write some content — paste in existing markdown if you have it
4. Hit **Ctrl+S** (or Cmd+S on macOS) to save

The page is saved to DocPlatform's local SQLite database (embedded in the binary — no external database to manage). Every save creates a version you can roll back to.

Try creating a child page: hover over "Getting Started" in the sidebar and click the **+** icon. Now you have a page hierarchy.

## Step 5: Publish Your Docs

To make your documentation publicly accessible, go to **Workspace Settings > Publishing** and toggle the published state to **On**. Your docs are now live at:

```
http://localhost:3000/s/engineering-handbook
```

The `/s/` prefix serves the published, read-only view. It uses the theme you selected, has full-text search powered by Bleve, and includes a sidebar navigation tree built from your page hierarchy.

That's it. Five commands, no configuration files, and you have a running documentation site.

## What's Running Under the Hood

When you ran `docplatform serve`, you started a single process that handles:

- **HTTP server** — serves the editor UI, the API, and the published documentation site
- **SQLite database** — stores users, workspaces, pages, and versions
- **Bleve search index** — full-text search with typo tolerance and relevance ranking
- **WebAuthn/passkey authentication** — modern passwordless auth alongside traditional username/password
- **RBAC** — 5 roles (super admin, admin, editor, viewer, guest) with granular permissions

All of this runs in a single process using about 50–80 MB of RAM. No background workers, no message queues, no microservices.

## Step 6: Connect Git (Optional)

If you want your documentation stored in a git repository — version-controlled, reviewable, editable from your IDE — DocPlatform supports bidirectional git sync. Read the [quickstart guide](/docs/getting-started/quickstart/) for the full setup, but the short version is:

1. Go to **Workspace Settings > Git Sync**
2. Paste your repository URL and deploy key
3. Pick a branch
4. Click **Enable Sync**

From that point, every save in the editor creates a git commit, and every push to the repo from an IDE or CI pipeline is reflected in the editor. This isn't a one-way mirror — it's true bidirectional sync using the Content Ledger pattern (see [Why Git Docs Tools Break Sync](/blog/why-git-sync-breaks/) for the technical explanation).

## Running in Production

For a production deployment, you'll want to set a few environment variables:

```bash
export DOCPLATFORM_PORT=3000
export DOCPLATFORM_DATA_DIR=/var/lib/docplatform
export DOCPLATFORM_BASE_URL=https://docs.yourcompany.com

docplatform serve
```

Put it behind a reverse proxy (Nginx, Caddy, or Cloudflare Tunnel) for HTTPS termination. Use a systemd unit or similar to keep it running:

```ini
[Unit]
Description=DocPlatform Documentation Server
After=network.target

[Service]
ExecStart=/usr/local/bin/docplatform serve
WorkingDirectory=/var/lib/docplatform
Restart=always
User=docplatform

[Install]
WantedBy=multi-user.target
```

Back up the data directory periodically — it contains the SQLite database and the search index. A simple `cp` or `rsync` while the server is running works fine (SQLite handles concurrent reads).

## Next Steps

You now have a working documentation platform. Here's where to go from here:

- [Full quickstart guide](/docs/getting-started/quickstart/) — covers git sync, themes, and user management
- [Creating your first workspace](/docs/getting-started/first-workspace/) — detailed workspace configuration
- [Installation options](/install/) — all download methods, including ARM builds

DocPlatform's Community Edition is free, with no user limits, no page limits, and no feature gates. Download the binary and start writing. Everything you need ships in that one file.
