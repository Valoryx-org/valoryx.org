---
title: Getting Started
description: Install DocPlatform, create your first workspace, and start writing documentation in under 10 minutes.
weight: 1
---

# Getting Started

This section walks you through installing DocPlatform, running it for the first time, and creating a workspace where your team can start writing.

## Choose your path

| Path | Time | Best for |
|---|---|---|
| [Quickstart](quickstart.md) | 5 minutes | Evaluate the product fast — single command, see it running |
| [Installation](installation.md) | 10 minutes | Full setup — choose your method (binary, Docker, source), understand what's happening |
| [Your First Workspace](first-workspace.md) | 10 minutes | Already running — learn to create workspaces, connect git, invite your team |

## Before you begin

DocPlatform has no external dependencies. You don't need to install a database, a search engine, or a Node.js runtime. The single binary includes everything.

**Optional dependencies:**

- **Git 2.30+** — only required if you want to sync with a remote git repository
- **SSH key** — only required for private git repos over SSH
- **Email provider (SMTP or Resend)** — only required for email invitations and password reset (without email configured, reset emails are simply not sent and links are **not** logged; admins generate them with `docplatform reset-password`)

## Architecture at a glance

When you run `docplatform serve`, a single process starts that includes:

- **HTTP server** — serves the web editor and API on port 3000
- **SQLite database** — stores users, workspaces, pages metadata, and audit logs
- **Bleve search engine** — indexes all content for instant full-text search
- **Git engine** — syncs content bidirectionally with remote repositories
- **Static frontend** — the Tiptap-based web editor, embedded in the binary

All data lives in a single directory, making backups and migrations straightforward — just copy the directory. On a fresh install this defaults to an OS-standard per-user location (`~/.local/share/docplatform` on Linux, `~/Library/Application Support/DocPlatform` on macOS, `%LOCALAPPDATA%\DocPlatform` on Windows) — set `DATA_DIR` to use a different location, or run `docplatform doctor` to see which directory is actually in use and why.
