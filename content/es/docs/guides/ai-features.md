---
title: AI Features
description: Use AI writing assist, doc chat, and MCP server integration to accelerate documentation workflows.
weight: 999
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
| **Anthropic** (Claude) | `AI_PROVIDER=anthropic` | Claude Sonnet (latest) |
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
| **Rewrite** | Rephrase the selected text while preserving meaning |
| **Improve** | Enhance clarity, grammar, and readability |
| **Shorten** | Condense the text while keeping key information |
| **Expand** | Elaborate on the selected text with more detail |

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

**Operations:** `rewrite`, `improve`, `shorten`, `expand`

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

### What MCP exposes

The MCP server provides tools for AI agents to:

- **Read pages** — fetch any page by path
- **Search** — full-text search across workspace content
- **List pages** — browse the page tree
- **Get metadata** — frontmatter, tags, status, and relationships

All access is authenticated via the API key and respects workspace permissions.

## Feature gating

AI features are available on all plans during the beta period. In future releases, advanced AI features (doc chat, custom models) may be restricted to paid plans.

## Privacy

- Your documentation content is sent to the configured AI provider for processing
- No content is stored by DocPlatform beyond the API request lifecycle
- AI providers may have their own data retention policies — review your provider's terms
- AI features are entirely optional and disabled by default
