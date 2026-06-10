---
title: AI Features
description: Use AI writing assist, doc chat, and MCP server integration to accelerate documentation workflows.
weight: 7
---

# AI Features

DocPlatform includes built-in AI capabilities powered by Claude (Anthropic) or OpenAI. These features help you write, improve, and explore your documentation faster.

## Setup

Enable AI features by setting your provider and API key:

```bash
# .env
AI_PROVIDER=anthropic     # or "openai"
AI_API_KEY=sk-ant-...     # your API key
AI_MODEL=                 # optional — uses provider default if empty
```

Restart the server. AI features become available through the REST API and the MCP server's `docplatform_writing_assist` tool.

### Supported providers

| Provider | Variable | Model |
|---|---|---|
| **Anthropic** (Claude) | `AI_PROVIDER=anthropic` (default) | Provider default, or set `AI_MODEL` |
| **OpenAI** | `AI_PROVIDER=openai` | Provider default, or set `AI_MODEL` |

Override the model with `AI_MODEL` (e.g., `claude-sonnet-4-6`, `gpt-4o`).

### Check AI status

```
GET /api/v1/ai/status
```

Returns whether AI is enabled and which provider is configured.

## Writing assist

Transform text with six operations, via the REST API or the `docplatform_writing_assist` MCP tool (there is no AI toolbar in the editor today):

| Operation | Description |
|---|---|
| **Improve** | Enhance clarity, grammar, and readability |
| **Simplify** | Simplify language while preserving meaning |
| **Expand** | Elaborate on the selected text with more detail |
| **Summarize** | Condense the text into a brief summary |
| **Fix grammar** | Correct grammar and spelling errors |
| **Translate** | Translate content to a target language |

### API usage

```
POST /api/v1/ai/writing-assist
```

```json
{
  "action": "improve",
  "content": "This is the text to improve.",
  "language": "de"
}
```

**Actions:** `improve`, `simplify`, `expand`, `summarize`, `fix_grammar`, `translate` (only `translate` uses `language`). Unknown actions are rejected with a validation error.

**Response:**

```json
{
  "result": "Here is the improved text with better clarity and flow."
}
```

## Doc chat

Ask questions about your workspace documentation and get context-aware answers. Doc chat is an **API capability** — there is no chat panel in the editor UI today. Use it from your own integrations, or point an AI agent at the [MCP server](mcp.md) for an interactive equivalent (`docplatform_search` + `docplatform_get_context`).

### API usage

```
POST /api/v1/ai/chat
```

```json
{
  "workspace_id": "01HJK...",
  "messages": [
    { "role": "user", "content": "How do I configure git sync?" }
  ]
}
```

Supports multi-turn conversations — include previous messages in the `messages` array for context.

## MCP server

DocPlatform includes a built-in Model Context Protocol (MCP) server with **26 tools**, allowing AI agents like Claude Code, Claude Desktop, or Cursor to read, write, search, and manage your documentation directly.

### Quick setup

```bash
docplatform mcp --workspace my-docs --api-key dp_live_abc123
```

### Client configuration

**Claude Desktop** — add to `claude_desktop_config.json`:

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

**Claude Code:**

```bash
claude mcp add docplatform -- docplatform mcp --workspace my-docs --api-key dp_live_abc123
```

**Cursor** — add to `.cursor/mcp.json`:

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

### Tool categories

The 26 MCP tools cover content CRUD (6), discovery & RAG (5), quality (2), settings (2), workspace management (3), versioning (2), export (1), AI writing (1), activity (1), comments (2), and sync conflict resolution (1, conditional).

Key highlights:

- **`write_page`** — smart upsert that creates or updates automatically, so AI agents never need to check if a page exists first
- **`get_context`** — RAG-optimized bundle returning a page with its parent, siblings, wikilink targets, and workspace metadata in a single call
- **`get_manifest`** — complete workspace overview with cross-page link relationships for AI agents to understand structure at a glance
- **`quality_scan`** — automated quality scoring (0–100) with detailed findings

See the [MCP Server guide](mcp.md) for the complete tool reference, authentication details, rate limits, and troubleshooting.

## Feature gating

AI features are available on all plans during the beta period. In future releases, advanced AI features (doc chat, custom models) may be restricted to paid plans.

## Privacy

- Your documentation content is sent to the configured AI provider for processing
- No content is stored by DocPlatform beyond the API request lifecycle
- AI providers may have their own data retention policies — review your provider's terms
- AI features are entirely optional and disabled by default
