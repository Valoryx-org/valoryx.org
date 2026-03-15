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

Restart the server. AI features appear in the editor toolbar and are accessible via the API.

### Supported providers

| Provider | Variable | Default model |
|---|---|---|
| **Anthropic** (Claude) | `AI_PROVIDER=anthropic` | Claude Sonnet 4.5 (claude-sonnet-4-5-20250514) |
| **OpenAI** | `AI_PROVIDER=openai` | GPT-4o |

Override the model with `AI_MODEL` (e.g., `claude-opus-4-6`, `gpt-4-turbo`).

### Check AI status

```
GET /api/v1/ai/status
```

Returns whether AI is enabled and which provider is configured.

## Writing assist

Select text in the editor and use the AI toolbar to transform it:

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
  "workspace_id": "01HJK...",
  "operation": "improve",
  "content": "This is the text to improve."
}
```

**Operations:** `improve`, `simplify`, `expand`, `summarize`, `fix_grammar`, `translate`

**Response:**

```json
{
  "result": "Here is the improved text with better clarity and flow."
}
```

## Doc chat

Ask questions about your workspace documentation and get context-aware answers.

### In the editor

Click the **Chat** button in the sidebar to open the doc chat panel. Ask questions like:

- "How do I configure git sync?"
- "What authentication methods are supported?"
- "Summarize the deployment guide"

The AI searches your workspace content and provides answers grounded in your actual documentation.

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

DocPlatform includes a built-in Model Context Protocol (MCP) server, allowing AI agents like Claude Code or Claude Desktop to read and search your documentation directly.

### Setup

```bash
docplatform mcp --workspace my-docs --api-key dp_live_abc123
```

The MCP server runs on stdio, making it compatible with any MCP client.

### Claude Desktop integration

Add to your `claude_desktop_config.json`:

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

### Claude Code integration

```bash
claude mcp add docplatform -- docplatform mcp --workspace my-docs --api-key dp_live_abc123
```

### Cursor integration

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

### Available MCP tools (20)

The MCP server exposes 20 tools organized into four categories:

#### Read & navigate

| Tool | Description |
|---|---|
| `docplatform_get_page` | Fetch a single page by path — returns Markdown content, frontmatter, and metadata |
| `docplatform_list_pages` | List all pages in the workspace with title, path, and status |
| `docplatform_get_page_tree` | Hierarchical page tree showing parent-child relationships |
| `docplatform_get_page_metadata` | Frontmatter, tags, status, word count, and timestamps |
| `docplatform_get_page_links` | Outbound and inbound wikilinks for a page |
| `docplatform_get_page_history` | Revision history for a page |
| `docplatform_get_workspace_config` | Workspace settings and configuration |

#### Search & discover

| Tool | Description |
|---|---|
| `docplatform_search` | Full-text search with scored results and highlighted snippets |
| `docplatform_search_by_tag` | Find pages by tag (exact match or partial) |
| `docplatform_search_by_date` | Find pages modified within a date range |

#### Write & organize

| Tool | Description |
|---|---|
| `docplatform_write_page` | Create or update a page (smart upsert — creates if new, updates with hash check if exists) |
| `docplatform_update_page` | Update page content with optimistic concurrency (requires lastKnownHash) |
| `docplatform_move_page` | Move/rename a page — updates all wikilinks automatically |
| `docplatform_delete_page` | Delete a page by path |
| `docplatform_update_frontmatter` | Update page frontmatter fields without changing body content |
| `docplatform_batch_update` | Update multiple pages in a single transaction |

#### How `write_page` works (smart upsert)

The `write_page` tool provides a single "just write" operation for AI agent convenience, while the underlying HTTP API enforces strict create/update separation:

1. **Page doesn't exist** → creates it via `POST` (new page with auto-generated ID)
2. **Page already exists** → reads the current content hash, then updates via `PUT` with optimistic locking

This means AI agents never need to check if a page exists before writing — the tool handles it automatically. Under the hood:

```
write_page("guides/deploy", title="Deploy Guide", body="# Deploy...")
    │
    ├─ Page doesn't exist → CreatePage() → 201 Created
    │
    └─ Page exists (hash: sha256:abc...)
         → UpdatePage(lastKnownHash="sha256:abc...") → 200 OK
```

If you need explicit control, use `update_page` (which requires `lastKnownHash` and fails if the page was modified since you last read it) or check existence first with `read_page`.

**Important:** The HTTP API (`POST /api/v1/content/:workspace/:path`) is strict — it returns `409 Conflict` if the page already exists. The MCP tool abstracts this complexity.

#### Maintain

| Tool | Description |
|---|---|
| `docplatform_quality_check` | Run readability scoring, dead link detection, and completeness checks |
| `docplatform_workspace_stats` | Page count, word count, tag distribution, and health summary |
| `docplatform_validate_links` | Check all internal links and wikilinks for broken references |
| `docplatform_export_workspace` | Export workspace content as a ZIP archive |

All access is authenticated via the API key and scoped to the specified workspace.

## Feature gating

AI features are available on all plans during the beta period. In future releases, advanced AI features (doc chat, custom models) may be restricted to paid plans.

## Privacy

- Your documentation content is sent to the configured AI provider for processing
- No content is stored by DocPlatform beyond the API request lifecycle
- AI providers may have their own data retention policies — review your provider's terms
- AI features are entirely optional and disabled by default
