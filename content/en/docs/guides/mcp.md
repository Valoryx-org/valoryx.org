---
title: MCP Server — AI Integration Guide
description: Connect AI tools like Claude Code, Claude Desktop, Cursor, and VS Code Copilot to your DocPlatform documentation using the built-in MCP server.
weight: 999
---

# MCP Server — AI Integration Guide

DocPlatform includes a built-in [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that lets AI assistants read, write, search, and manage your documentation directly. Instead of copy-pasting content into chat windows, your AI tools work with your docs natively.

## Prerequisites

- DocPlatform running (binary, Docker, or Fly.io)
- An API key (create one in **Workspace Settings** → **API Keys**)

## Quick start

### 1. Create an API key

In your DocPlatform instance, go to **Workspace Settings** → **API Keys** → **Create Key**. Copy the key — it starts with `dp_live_` and is shown only once.

### 2. Choose your transport

DocPlatform offers two MCP transports:

| Transport | Command | Use case |
|---|---|---|
| **stdio** | `docplatform mcp` | Local AI tools (Claude Desktop, Claude Code, Cursor) |
| **Streamable HTTP** | `docplatform mcp-server` | Remote/cloud access, multi-workspace |

### 3. Configure your AI tool

#### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docplatform": {
      "command": "docplatform",
      "args": ["mcp", "--workspace", "my-docs", "--api-key", "dp_live_abc123"]
    }
  }
}
```

#### Claude Code

```bash
claude mcp add docplatform -- docplatform mcp --workspace my-docs --api-key dp_live_abc123
```

#### Cursor

Add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "docplatform": {
      "command": "docplatform",
      "args": ["mcp", "--workspace", "my-docs", "--api-key", "dp_live_abc123"]
    }
  }
}
```

#### VS Code (GitHub Copilot)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "docplatform": {
      "command": "docplatform",
      "args": ["mcp", "--workspace", "my-docs", "--api-key", "dp_live_abc123"]
    }
  }
}
```

#### Remote HTTP transport

For cloud-hosted DocPlatform or multi-workspace access, start the HTTP server:

```bash
docplatform mcp-server --addr :8081
```

Then configure your MCP client to connect via Streamable HTTP at `http://your-server:8081/mcp` with a Bearer token (`dp_live_...`).

---

## Available tools (24)

The MCP server exposes 24 tools across 9 categories.

### Content (6 tools)

| Tool | Description | Key parameters |
|---|---|---|
| `docplatform_list_pages` | List all pages in the workspace with paths and titles | — |
| `docplatform_read_page` | Read a page's full content including frontmatter, body, and metadata | `path` |
| `docplatform_write_page` | Create or update a page (smart upsert — creates if new, updates if exists) | `path`, `title`, `body`, `description`, `publish` |
| `docplatform_update_page` | Update an existing page with optimistic concurrency control | `path`, `body`, `last_known_hash` |
| `docplatform_delete_page` | Soft-delete a page by path | `path` |
| `docplatform_move_page` | Move/rename a page — wikilinks in other pages are updated automatically | `path`, `new_path` |

#### How `write_page` works (smart upsert)

The `write_page` tool provides a single "just write" operation for AI agent convenience:

1. **Page doesn't exist** → creates it automatically
2. **Page exists** → reads the current content hash, then updates with optimistic locking

AI agents never need to check if a page exists before writing. If you need explicit concurrency control, use `update_page` instead (which requires `last_known_hash` and fails on conflict).

### Discovery (5 tools)

| Tool | Description | Key parameters |
|---|---|---|
| `docplatform_search` | Full-text search across all pages | `query`, `limit` |
| `docplatform_get_context` | RAG context bundle: page content + parent + siblings + linked pages + workspace metadata | `path` |
| `docplatform_list_workspaces` | List all workspaces accessible to the authenticated user | — |
| `docplatform_get_tree` | Get the full hierarchical page tree with IDs, paths, and titles | — |
| `docplatform_get_manifest` | Complete workspace manifest: all pages with titles, descriptions, tags, status, word counts, and cross-page link relationships | — |

The `get_context` tool is designed for RAG workflows — it returns everything an AI needs to understand a page in context, including its parent, siblings, wikilink targets, and workspace metadata, in a single call.

The `get_manifest` tool gives AI agents a complete overview of the workspace structure at a glance, including link relationships (`links_to` / `linked_from`).

### Quality (2 tools)

| Tool | Description |
|---|---|
| `docplatform_validate_links` | Scan all pages for broken wikilinks. Returns source page, target, and line number for each broken link |
| `docplatform_quality_scan` | Run a quality scan returning a score (0–100), issue counts, and detailed findings: missing titles, empty pages, broken links, stale content, and readability analysis |

### Settings (2 tools)

| Tool | Description | Key parameters |
|---|---|---|
| `docplatform_get_theme` | Get the current published site theme | — |
| `docplatform_update_theme` | Update the published site theme | `theme` (default, dark, forest, rose, amber, minimal, corporate) |

### Management (2 tools)

| Tool | Description | Key parameters |
|---|---|---|
| `docplatform_create_workspace` | Create a new documentation workspace. The authenticated user becomes workspace admin | `name`, `slug`, `description` |
| `docplatform_get_workspace` | Get workspace details including your role, member count, page count, git sync status, and publish settings | `workspace_id` |

### Versioning (2 tools)

| Tool | Description | Key parameters |
|---|---|---|
| `docplatform_list_versions` | List all documentation versions (e.g., v1.0, v2.0) | — |
| `docplatform_create_version` | Create a new documentation version for side-by-side releases | `name`, `slug`, `base_path`, `set_default` |

### Export (1 tool)

| Tool | Description | Key parameters |
|---|---|---|
| `docplatform_export` | Export the workspace as a static site. Returns a summary by default; use `format=zip_base64` for small sites (≤50 pages) | `format` |

### AI writing (1 tool)

| Tool | Description | Key parameters |
|---|---|---|
| `docplatform_writing_assist` | AI-powered text improvement: improve, shorten/simplify, expand, fix_grammar, summarize, translate | `text`, `operation`, `context`, `language` |

Requires an AI provider configured on the server (Anthropic or OpenAI).

### Activity (1 tool)

| Tool | Description | Key parameters |
|---|---|---|
| `docplatform_get_activity` | Recent workspace activity (page edits, member joins, syncs) in reverse chronological order | `limit`, `action` |

### Comments (2 tools)

| Tool | Description | Key parameters |
|---|---|---|
| `docplatform_list_comments` | List threaded comments on a page with author, body, anchors, and resolution status | `page`, `limit` |
| `docplatform_add_comment` | Add a comment to a page. Supports @mentions and threaded replies | `page`, `body`, `parent_id` |

---

## Authentication

### API key scopes

API keys support three scopes:

| Scope | Allows |
|---|---|
| `read` | list_pages, read_page, search, get_context, get_tree, get_manifest, list_workspaces, get_workspace, list_versions, get_theme, validate_links, quality_scan, export, get_activity, list_comments |
| `write` | write_page, update_page, move_page, create_workspace, create_version, update_theme, writing_assist, add_comment |
| `delete` | delete_page |

By default, new API keys have all three scopes. You can restrict scope when creating the key.

### Key format

API keys use the `dp_live_` prefix:

```
dp_live_a1b2c3d4e5f6...
```

Keys are hashed with HMAC before storage — the raw key is shown only once at creation.

### Environment variable

Instead of passing `--api-key` on the command line, set:

```bash
export DOCPLATFORM_API_KEY=dp_live_abc123
```

---

## Security

- **Hashed storage**: API keys are never stored in plaintext. Only the HMAC hash is persisted.
- **Rate limited**: Each key is rate-limited based on the organization's plan.
- **Workspace-scoped**: Keys can be scoped to a specific workspace (recommended) or org-wide.
- **Revocable**: Delete a key immediately from Workspace Settings → API Keys.
- **Rotatable**: Rotate a key without changing its ID or scopes via `POST /api/v1/api-keys/:id/rotate`.

### Rate limits (MCP)

| Plan | Requests/min | Write ops/min | Concurrent |
|---|---|---|---|
| Community | 30 | 10 | 2 |
| Team | 120 | 60 | 5 |
| Business | 300 | 150 | 10 |

Rate limit headers are included on HTTP transport responses:

```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1712847600
```

---

## Troubleshooting

### "invalid API key"

- Verify the key starts with `dp_live_`
- Regenerate the key from Workspace Settings — the raw key is shown only once
- Check that the key hasn't been revoked or expired

### MCP not connecting

- Quit your AI tool completely and restart — MCP connections are established at launch
- Verify the `docplatform` binary is in your `PATH`
- Check that the DocPlatform server is running (`docplatform serve`)

### "workspace not found"

- Use the workspace **slug** (not the display name or ULID)
- Verify the workspace exists: `docplatform mcp --workspace <slug> --api-key <key>` should start without error

### Permission denied

- Check the key's scopes match the operation (e.g., `write` scope needed for `write_page`)
- Verify the key is scoped to the correct workspace

### HTTP transport issues

- Default listen address is `:8081` — check firewall rules
- For CORS issues, pass `--cors-origins https://your-domain.com`
- Verify the Bearer token is sent in the `Authorization` header

### Tool returns "service not available"

Some tools depend on optional services:

| Tool | Requires |
|---|---|
| `writing_assist` | AI provider configured (`AI_PROVIDER` + `AI_API_KEY`) |
| `quality_scan` | Quality scanner (enabled by default) |
| `export` | Published site configured for the workspace |
| `get_manifest` | Manifest service (enabled by default) |
| `search` | Search engine (Bleve, enabled by default) |
