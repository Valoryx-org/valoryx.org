---
title: "MCP for Documentation: A Technical Guide"
description: "How Model Context Protocol connects AI assistants to your documentation. Configure Claude Desktop, use 13 built-in tools, and automate doc maintenance."
date: "2026-03-16"
author: "Valoryx Team"
tags: ["mcp", "ai", "documentation", "tutorial"]
---

Model Context Protocol (MCP) is an open standard that lets AI assistants interact with external tools and data sources through a structured interface. Instead of copying text into a chat window and hoping the model understands the context, MCP gives the assistant direct, typed access to your systems — read files, run searches, create content, all through well-defined tool calls.

For documentation teams, this changes the workflow fundamentally. Your AI assistant stops being a text generator that works from stale context and becomes a participant that reads your actual docs, searches across your knowledge base, and makes edits you can review before they go live.

Valoryx ships a built-in MCP server with 13 tools. No plugins to install, no API keys to configure. If you have a running instance, the MCP server is already there.

## What MCP Actually Does

MCP defines a protocol for tool discovery and invocation. An AI client (like Claude Desktop) connects to an MCP server, asks what tools are available, and calls them with structured parameters. The server executes the operation and returns structured results.

This is different from "AI features" bolted onto a product. There's no proprietary integration. Any MCP-compatible client works. The [MCP specification](https://modelcontextprotocol.io) is open, and multiple AI assistants already support it.

The practical result: you can ask Claude "find all pages that mention authentication" and it will actually search your documentation instance, not hallucinate page titles from training data.

## The 13 Built-In Tools

Valoryx's MCP tools fall into four categories:

### Read Tools
These retrieve content without modifying anything.

- **get_page** — Fetch a single page by ID or path. Returns title, markdown content, metadata, and last-modified timestamp.
- **get_workspace** — List all workspaces with their page counts and settings.
- **get_page_tree** — Return the full navigation tree for a workspace. Useful for understanding doc structure before making changes.

### Search Tools
Full-text search powered by the same Bleve engine that drives the web UI.

- **search_pages** — Search across all pages in a workspace. Supports phrase queries, field-specific searches, and boolean operators.
- **search_by_tag** — Find pages with specific tags. Useful for auditing: "show me everything tagged `deprecated`."
- **search_recent** — Find pages modified in the last N days. Good for reviewing recent changes.

### Write Tools
These create or modify content. Every write operation creates a ledger entry, so changes are tracked and sync-safe.

- **create_page** — Create a new page with title, content, parent path, and tags.
- **update_page** — Replace the content of an existing page. The previous version is preserved in history.
- **move_page** — Change a page's position in the navigation tree.
- **delete_page** — Soft-delete a page (recoverable from the admin panel).

### Admin Tools
Workspace and user management operations.

- **list_users** — Get all users with their roles. Useful for auditing access.
- **get_activity_log** — Retrieve recent activity (edits, logins, permission changes).
- **get_sync_status** — Check the git sync state for a workspace — last sync time, pending changes, any conflicts.

## Configuring Claude Desktop

To connect Claude Desktop to your Valoryx instance, add an MCP server entry to your configuration file. On macOS, this lives at `~/Library/Application Support/Claude/claude_desktop_config.json`. On Windows, it's `%APPDATA%\Claude\claude_desktop_config.json`.

```json
{
  "mcpServers": {
    "valoryx-docs": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-client",
        "--server-url",
        "https://docs.yourcompany.com/api/mcp"
      ],
      "env": {
        "MCP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Generate an API key from the Valoryx admin panel under **Settings > API Keys**. The key inherits the permissions of the user who created it, so use a dedicated service account with appropriate RBAC role if you want to limit what the AI can do.

For the Community Edition running locally, the URL is typically `http://localhost:3000/api/mcp`.

## Practical Examples

Once connected, here are concrete things you can do:

### Find Stale Content

```
"Find all pages in the Engineering workspace that haven't been 
updated in the last 90 days"
```

The assistant calls `search_recent` with a 90-day window, inverts the result against `get_page_tree`, and returns a list of potentially stale pages. You get page paths, last-modified dates, and last editors — enough to assign review tasks.

### Audit for Consistency

```
"Search all pages for references to our old API endpoint 
api.example.com/v1 and list them"
```

This calls `search_pages` with the old endpoint string. You get a list of every page that still references the deprecated URL, with surrounding context. No manual grep through a docs repo required.

### Draft and Update Content

```
"Read the current authentication guide, then update it to include 
the new passkey login flow. Keep the existing structure."
```

The assistant calls `get_page` to read the current content, drafts the update, and calls `update_page` to apply it. The previous version stays in history. If [git sync](/docs/guides/git-integration/) is configured, the edit appears as a commit in your repository.

### Review Recent Changes

```
"Show me everything that changed in the last week across 
all workspaces"
```

Calls `search_recent` with a 7-day window. Returns a summary of what changed, who changed it, and when. Useful for weekly documentation reviews without logging into the web UI.

## What This Means for Doc Maintenance

The traditional documentation maintenance workflow is: someone notices docs are wrong, files a ticket, someone else eventually updates the page. The gap between "noticed" and "fixed" is usually weeks.

With MCP, the workflow becomes: ask the AI to audit a section, review the findings, approve the changes. The gap shrinks to minutes. Not because AI writes better documentation — it doesn't, not reliably — but because the bottleneck was always finding what's wrong and making the edit, not composing the text.

This works especially well for mechanical updates: URL changes, terminology renames, version number bumps, deprecation notices. The kind of changes that are tedious for humans and straightforward for an AI with structured access to the content.

For more on using MCP to keep docs current, see [How to Keep Documentation Up to Date](/blog/keep-docs-up-to-date/).

## Limitations Worth Knowing

MCP tools operate on individual pages. There's no "rewrite the entire docs site" tool — by design. Large-scale restructuring still needs human judgment about information architecture.

The write tools create real changes. If you configure Claude Desktop with an admin-level API key, the AI can delete pages. Use RBAC to scope the API key's permissions appropriately. An "Editor" role can read and write content but can't delete workspaces or manage users.

Search quality depends on your content. If your docs use inconsistent terminology, the AI will find inconsistent results. MCP makes the search fast, but it doesn't fix the underlying content problems.

## Getting Started

1. [Install Valoryx](/install/) — single binary, no dependencies, running in under 2 minutes
2. Generate an API key from the admin panel
3. Add the MCP server config to Claude Desktop
4. Start with a read-only workflow: search and audit before you enable writes

The [MCP documentation](/mcp/) covers the full API reference for all 13 tools, including parameter types and response schemas.

Documentation maintenance doesn't have to be a manual process. With a structured protocol between your AI assistant and your docs platform, the tedious parts — finding stale content, checking consistency, making mechanical updates — become something you can delegate with confidence.
