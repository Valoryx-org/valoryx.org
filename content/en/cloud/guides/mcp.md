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

### In Claude Desktop

1. Go to **Workspace Settings** → **API Keys**
2. Create an API key (Read & Write or Read Only)
3. In Claude Desktop settings, add this MCP server:

```json
{
  "mcpServers": {
    "valoryx-docs": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-remote", "https://app.valoryx.dev/api/v1/mcp"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

4. Restart Claude Desktop
5. Ask Claude: *"What's in my documentation?"*

### In Cursor

Same configuration — add the MCP server in Cursor's settings and use the same API key.

## Available MCP tools

The MCP server provides 26 tools:

| Tool | What it does |
|---|---|
| `list_pages` | List all pages in a workspace |
| `read_page` | Read a specific page's content |
| `create_page` | Create a new page |
| `update_page` | Update an existing page |
| `delete_page` | Delete a page |
| `search` | Full-text search across all pages |
| `list_workspaces` | List available workspaces |
| *...and more* | Comments, metadata, tree structure |

## Security

- API keys are hashed (never stored in plain text)
- You control the scope: Read Only or Read & Write
- Revoke keys at any time from Workspace Settings
- All MCP requests are logged in the audit trail
