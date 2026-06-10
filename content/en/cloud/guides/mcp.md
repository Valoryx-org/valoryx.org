---
title: AI & MCP Integration
description: Connect Claude, Cursor, and other AI tools to read and write your documentation.
weight: 5
---

Valoryx Cloud includes a built-in MCP (Model Context Protocol) server that lets AI assistants interact with your documentation directly.

## What is MCP?

MCP is a standard protocol that lets AI tools connect to external services. Think of it as giving Claude or Cursor a way to "see" your docs and make changes — with your permission.

## What AI can do with your docs

- **Read** pages to answer questions about your documentation
- **Search** across all pages to find relevant content
- **Create** new pages based on your instructions
- **Edit** existing pages (rewrite, improve, translate)
- **Analyze** your docs for gaps, inconsistencies, or outdated content

## Setting up

> **Status:** the hosted MCP endpoint for Valoryx Cloud is **not yet enabled** — remote AI tools cannot connect to `app.valoryx.dev` yet. This page will be updated the moment it goes live. On a **self-hosted** instance, MCP works today — follow the steps below on the machine running DocPlatform.

### Self-hosted: Claude Desktop

1. Go to **Workspace Settings** → **API Keys**
2. Create an API key — it starts with `dp_live_` and is shown only once
3. In `claude_desktop_config.json`, add:

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

4. Restart Claude Desktop
5. Ask Claude: *"What's in my documentation?"*

### In Cursor

Same configuration — add the same `docplatform` entry to `.cursor/mcp.json` in your project.

## Available MCP tools

The MCP server provides 26 tools:

| Tool | What it does |
|---|---|
| `list_pages` | List all pages in a workspace |
| `read_page` | Read a specific page's content |
| `write_page` | Create a page, or update it if it already exists |
| `update_page` | Update an existing page |
| `delete_page` | Delete a page |
| `search` | Full-text search across all pages |
| `list_workspaces` | List available workspaces |
| *...and more* | Comments, metadata, tree structure |

## Security

- API keys are hashed (never stored in plain text)
- You control the scope per key: `read`, `write`, and `delete`
- Revoke keys at any time from Workspace Settings
- Authorization failures are logged, and every content change is tracked in page history
