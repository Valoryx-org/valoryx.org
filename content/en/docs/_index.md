---
title: DocPlatform Community Edition
description: Self-hosted, git-backed documentation platform with a beautiful web editor. Own your docs. Control your workflow.
weight: 1
---

# DocPlatform Community Edition

DocPlatform is a self-hosted documentation platform that combines a rich web editor with bidirectional git synchronization — packaged as a single binary with zero external dependencies.

Write in your browser. Push from your IDE. Everything stays in sync.

## Why DocPlatform

Documentation platforms force you to choose: a polished web editor with vendor lock-in, or raw files in git with no collaboration features. DocPlatform eliminates that trade-off.

| What you get | How it works |
|---|---|
| **Single binary, zero dependencies** | One Go binary bundles the editor, database, search engine, and git engine. No Node.js runtime, no Postgres, no Elasticsearch. |
| **Every page is a `.md` file** | Your content lives as Markdown files in a real git repository. No proprietary formats. No export required. |
| **Bidirectional git sync** | Edit in the browser — changes auto-commit and push. Push from your IDE — the web UI updates automatically. |
| **Beautiful published docs** | One click to publish a documentation site with dark mode, syntax highlighting, and 7 built-in components. |
| **Team collaboration** | 6-level role hierarchy, workspace invitations, real-time presence indicators, and full audit trail. |
| **Full-text search** | Embedded search engine with instant results. No external service to configure. |

## Who it's for

DocPlatform Community Edition is built for:

- **Open-source maintainers** who keep project docs in-repo but want better editing UX than raw Markdown in GitHub
- **Internal platform / DevEx teams** who need docs-as-code with access control and a web editor — not one or the other
- **Small dev agencies** managing multiple client docs repos with git backup and no affordable self-hosted option
- **Technical writers** who need a polished authoring experience backed by version control
- **Solo developers** who want a personal knowledge base with public publishing — without a subscription

**Not targeting:** compliance-heavy enterprises requiring SAML/SCIM (see future Enterprise Edition), or non-technical content teams without git familiarity.

## How it works

```
┌──────────────────────────────────────────────────┐
│              DocPlatform (single binary)          │
│                                                  │
│   ┌────────────┐  ┌──────────┐  ┌────────────┐  │
│   │ Web Editor  │  │ SQLite   │  │ Bleve      │  │
│   │ (Next.js)   │  │ Database │  │ Search     │  │
│   └──────┬──────┘  └────┬─────┘  └──────┬─────┘  │
│          │              │               │        │
│          └──────┬───────┴───────┬───────┘        │
│                 │               │                │
│          ┌──────▼──────┐ ┌─────▼──────┐         │
│          │ Content     │ │ Git        │         │
│          │ Ledger      │ │ Engine     │         │
│          └──────┬──────┘ └─────┬──────┘         │
│                 │              │                 │
└─────────────────┼──────────────┼─────────────────┘
                  │              │
           ┌──────▼──────┐ ┌────▼──────┐
           │ Filesystem  │ │ Remote    │
           │ (.md files) │ │ Git Repo  │
           └─────────────┘ └───────────┘
```

Every content change — whether from the web editor, a git push, or an API call — flows through the **Content Ledger**, a single pipeline that keeps the filesystem, database, and search index in perfect sync.

## Quick start

Get DocPlatform running in under 5 minutes:

```bash
# Download the binary (recommended — auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh

# Initialize a workspace
docplatform init --workspace-name "My Docs" --slug my-docs

# Start the server
docplatform serve
```

Open [http://localhost:3000](http://localhost:3000) and register your first user — they automatically become the SuperAdmin.

For the complete walkthrough, see the [Getting Started](getting-started/index.md) guide.

## Feature overview

### Core platform

- **Rich web editor** — Tiptap-based editor with frontmatter form, raw Markdown toggle, and autosave
- **Bidirectional git sync** — Web → git commit → push; CLI push → polling → web update
- **Conflict detection** — Hash-based optimistic concurrency with downloadable diff on collision
- **Full-text search** — Embedded Bleve engine with permission-filtered results and Cmd+K shortcut
- **RBAC permissions** — 6 roles: SuperAdmin, WorkspaceAdmin, Admin, Editor, Commenter, Viewer
- **Authentication** — Local (argon2id) + optional Google/GitHub OIDC
- **Workspace model** — Org → Workspace → Pages hierarchy with team invitations
- **Audit trail** — Every mutation logged with user, timestamp, and operation type

### Published documentation

- **Public site** — Serve docs at `/p/{workspace-slug}/{page-path}`
- **Dark mode** — Automatic light/dark theme with manual toggle
- **7 built-in components** — Callout, Code (200+ languages), Tabs, Accordion, Cards, Steps, API Block
- **SEO ready** — OpenGraph tags, canonical URLs, sitemap.xml, robots.txt

### Operations

- **Health diagnostics** — 9-point `doctor` command checks FS/DB consistency, search health, broken links
- **Daily backups** — Automated SQLite backups with configurable retention
- **Graceful shutdown** — Clean signal handling for zero-downtime deployments
- **Structured logging** — JSON logs with request IDs for observability

## System requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| **OS** | Linux (amd64/arm64), macOS (amd64/arm64) | Linux amd64 |
| **Memory** | 128 MB | 512 MB |
| **Disk** | 200 MB (binary + data) | 1 GB |
| **Git** | Optional (for remote sync) | Git 2.30+ |
| **Network** | None (runs offline) | Port 3000 open |

## What's next

| Guide | Description |
|---|---|
| [Getting Started](getting-started/index.md) | Install, configure, and create your first workspace |
| [User Guides](guides/editor.md) | Learn the editor, git sync, publishing, and search |
| [Configuration](configuration/index.md) | Environment variables, auth, permissions, and workspace settings |
| [Deployment](deployment/binary.md) | Production deployment with binary, Docker, or containers |
| [CLI Reference](reference/cli.md) | Complete command reference |
| [API Reference](reference/api.md) | REST API endpoints and examples |
| [Troubleshooting](reference/troubleshooting.md) | Common issues and how to resolve them |

## Performance

Measured on Apple M2, NVMe SSD, 1,000-page workspace:

| Operation | Latency |
|---|---|
| Page save (sync core) | < 30ms |
| Page render (API response) | < 50ms p99 |
| Full-text search | < 8ms p99 |
| Permission check | < 0.1ms |
| Permission batch (100 pages) | < 1ms |
| Server cold start | < 1 second |
| Full reconciliation (1,000 files) | < 5 seconds |
| Git commit (single file) | < 2 seconds |
| Memory (idle) | < 80 MB |
| Memory (10 concurrent users) | < 200 MB |
| Binary size | ~120 MB |

## How DocPlatform compares

| Capability | DocPlatform | GitBook | Notion | Docusaurus | Confluence | Wiki.js |
|---|---|---|---|---|---|---|
| Self-hosted | Yes | No | No | Yes | No | Yes |
| Git-backed | Yes | Partial | No | Yes | No | No |
| Web editor | Yes | Yes | Yes | No | Yes | Yes |
| Bidirectional git sync | Yes | No | No | N/A | No | No |
| Single binary (zero deps) | Yes | N/A | N/A | No (Node.js) | N/A | Docker |
| Built-in RBAC | Yes | Paid | Paid | No | Yes | Yes |
| Published docs site | Yes | Yes | Yes | Yes | Yes | Yes |
| Open source | Yes | No | No | Yes | No | Yes |
| Offline capable | Yes | No | No | Yes | No | No |

## Community Edition limits

Community Edition is the fully functional, self-hosted core of DocPlatform. It includes everything documented on this site with the following limits:

| Resource | Community Edition |
|---|---|
| **Editors** (users who can create/edit pages) | Up to 5 |
| **Workspaces** | Up to 3 |
| **Viewers and Commenters** | Unlimited (never counted) |
| **Pages per workspace** | Unlimited |
| **Published docs** | Unlimited |

These limits cover the majority of small-to-medium teams. Future Enterprise Edition will offer unlimited editors, unlimited workspaces, SAML/SSO, PostgreSQL support, and advanced search via Meilisearch — but Community Edition will always remain the complete, self-hostable foundation.
