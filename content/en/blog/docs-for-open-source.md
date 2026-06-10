---
title: "Documentation for Open Source Projects"
description: "OSS maintainers need docs but can't afford paid tools. Here's how to set up free, self-hosted documentation with git sync in under 5 minutes."
date: "2026-04-06"
author: "Valoryx Team"
tags: ["open-source", "documentation", "free", "tutorial"]
---

Open source projects live or die by their documentation. A library with great docs gets adopted. A library with a bare README and a "see the code" attitude gets forked by someone who writes better docs — or just ignored.

But most documentation tools are built for companies, not OSS maintainers. They charge per seat, per page, or per workspace. For a project maintained by volunteers with zero budget, that's a non-starter.

We built DocPlatform's Community Edition to be free forever, with no limits. Unlimited users, unlimited pages, unlimited workspaces. No "free tier" that nudges you to upgrade — the Community Edition is the full product without cloud hosting. Here's how to set it up for your open source project.

## The Typical OSS Docs Setup

Most open source projects end up with one of these approaches:

**GitHub Pages + static site generator.** You write markdown files, configure a build pipeline, and deploy to GitHub Pages. The most common stack is [Docusaurus](https://docusaurus.io/) (React-based) or MkDocs (Python-based).

**Pros:** Free hosting, version-controlled content, familiar git workflow.

**Cons:** No web editor (contributors must know git, markdown, and the build system), no real-time preview, no search without third-party services (Algolia DocSearch has a waitlist and approval process), no collaboration features.

**Hosted platform with a free tier.** GitBook, ReadMe, or Notion with a public page. You get a web editor and hosted search.

**Pros:** Easy to start, web editor lowers the barrier for non-technical contributors.

**Cons:** Free tiers are limited (GitBook: 1 space, limited integrations; ReadMe: limited API references). Your content lives on someone else's server. If they change pricing or shut down, you're migrating under pressure.

**Raw markdown in the repo.** A `docs/` folder with markdown files. No build step, no hosting, no search.

**Pros:** Zero setup. Content is version-controlled.

**Cons:** No way for users to browse docs without going to GitHub. No search. No navigation structure beyond file names.

## A Better Approach

DocPlatform gives you the best of all three: content stored as markdown in your git repo, a web editor for non-technical contributors, full-text search, and a published documentation site — all from a single binary you can host anywhere.

Here's the setup.

### Step 1: Install DocPlatform

On any Linux, macOS, or Windows machine:

```bash
curl -fsSL https://get.valoryx.org | sh
```

Or download the binary directly from the [install page](/install/). There's nothing else to install — no database, no Docker, no runtime.

### Step 2: Start the Server

```bash
docplatform serve
```

Open `http://localhost:3000`. Create your admin account. That's your server running.

For a permanent setup, use a systemd service:

```ini
[Unit]
Description=DocPlatform
After=network.target

[Service]
ExecStart=/opt/docplatform/bin/docplatform serve
WorkingDirectory=/opt/docplatform
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 3: Create a Workspace

A workspace in DocPlatform is a documentation project. For an open source project, you'll typically have one workspace for your public docs.

1. Go to Settings → Workspaces → Create
2. Name it after your project (e.g., "MyProject Docs")
3. Choose a theme — there are 7 built-in themes, all designed for technical documentation

### Step 4: Connect Your GitHub Repository

This is where it gets interesting. DocPlatform supports bidirectional git sync — edits made in the web UI are committed to your repo, and changes pushed to the repo appear in the UI.

1. Go to Workspace Settings → Git Sync
2. Add your repository URL: `https://github.com/yourorg/yourproject.git`
3. Configure the docs path (e.g., `docs/` if your markdown lives in a subfolder)
4. Add a deploy key or personal access token for push access

Once connected, DocPlatform pulls your existing markdown files and indexes them for search. Any `.md` file in the configured path becomes a page.

### Step 5: Publish Your Docs

Toggle "Publish" in workspace settings. DocPlatform generates a browsable documentation site with:

- Navigation tree based on your folder structure
- Full-text search with typo tolerance
- Responsive design that works on mobile
- Syntax highlighting for code blocks
- Dark mode toggle

Your published docs are accessible at `http://yourserver:3000/docs/workspace-slug/`.

## The Git Workflow

Here's what the workflow looks like in practice for an open source project with multiple contributors:

**Maintainers** use the web editor for quick fixes — typo corrections, restructuring pages, updating screenshots. Every save creates a git commit automatically.

**External contributors** submit PRs to the docs directory in your GitHub repo, exactly like they would for code. When you merge the PR, DocPlatform picks up the changes via git sync and updates the published site.

**Non-technical contributors** (community managers, technical writers) use the WYSIWYG editor in the browser. They don't need to know git or markdown syntax. Their edits still get committed to the repo.

This means your documentation has the same review process as your code. Want someone to review a docs change before it goes live? Have them submit a PR. Want to let trusted contributors edit directly? Give them editor access in DocPlatform.

## Comparison: DocPlatform vs. Docusaurus

Since Docusaurus is the most popular OSS docs tool, here's a direct comparison:

| Feature | Docusaurus | DocPlatform CE |
|---|---|---|
| Web editor | No — edit markdown, commit, wait for build | Yes — WYSIWYG, changes live immediately |
| Search | Requires Algolia DocSearch (waitlist) or Lunr.js (client-side, limited) | Built-in full-text search (Bleve) |
| Build step | Yes — React build, can take 30+ seconds | No — pages render on save |
| Git integration | Native (it's a static site generator) | Bidirectional sync (web ↔ git) |
| Multiple versions | Yes (versioned docs) | Workspace-based (one workspace per version) |
| Setup time | 10-30 minutes (Node.js, npm, config) | 2 minutes (download binary, run) |
| Hosting | GitHub Pages, Netlify, Vercel (free) | Self-hosted (you need a server) |
| RBAC | None (it's a build tool) | 5 roles (admin, manager, editor, reviewer, viewer) |
| i18n | Plugin-based | Workspace-based |

Docusaurus wins if you want zero-cost hosting on GitHub Pages and your contributors are all comfortable with git and React. DocPlatform wins if you want a web editor, built-in search, access control, or if your contributors aren't all developers.

## Hosting on a Budget

A common objection: "Docusaurus is free because GitHub Pages hosts it. Self-hosted means I need a server."

True. But servers are cheap:

- **Hetzner CX22:** 2 vCPU, 4GB RAM, 40GB disk — EUR 3.99/month
- **Oracle Cloud Free Tier:** ARM instance, 24GB RAM — free forever
- **Old laptop in a closet:** Free if you already have one

DocPlatform uses roughly 50MB of RAM at idle and 100-200MB under load. Any server that can run a Go binary can run it.

If you're already running a CI server, a Discord bot, or any other service for your project, DocPlatform can run on the same machine.

## Real Setup: From Zero to Published Docs

Let's walk through a concrete example. You maintain a CLI tool called `fastgrep` and want to move from a README to proper docs.

```bash
# Install DocPlatform
curl -fsSL https://get.valoryx.org | sh

# Start the server
docplatform serve &

# Open browser, create admin account, create workspace
# Connect to github.com/yourname/fastgrep, docs path: docs/

# Create your first pages in the web editor:
# - Getting Started
# - Installation
# - Configuration
# - CLI Reference
# - Contributing
```

Every page you create in the web editor gets committed to `docs/` in your repo. Your existing `docs/` markdown files (if any) get imported automatically.

Publish the workspace, point your domain at the server, and your project has searchable documentation with a web editor — set up in under 5 minutes.

For the full publishing setup, see the [publishing guide](/docs/guides/publishing/).

## Free Means Free

The [Community Edition](/open-source/) is not a trial. It's not a limited free tier. It's the full product:

- Unlimited users and editors
- Unlimited workspaces and pages
- Full-text search
- Git sync
- RBAC with 5 roles
- All 7 themes
- WebAuthn/passkey authentication
- MCP server with 26 AI tools

The only thing the Community Edition doesn't include is cloud hosting — you run it on your own infrastructure. For open source projects that already manage their own infrastructure, that's not a limitation; it's a feature.

[Download DocPlatform](/install/) and give your project the docs it deserves.
