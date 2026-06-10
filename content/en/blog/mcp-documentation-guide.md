---
title: "MCP for Documentation: A Technical Guide"
description: "How Model Context Protocol connects AI assistants to your documentation. Configure Claude Desktop, use 26 built-in tools, and automate doc maintenance."
date: "2026-03-16"
author: "Valoryx Team"
tags: ["mcp", "ai", "documentation", "tutorial"]
---

Model Context Protocol (MCP) is an open standard that lets AI assistants interact with external tools and data sources through a structured interface. Instead of copying text into a chat window and hoping the model understands the context, MCP gives the assistant direct, typed access to your systems — read files, run searches, create content, all through well-defined tool calls.

For documentation teams, this changes the workflow fundamentally. Your AI assistant stops being a text generator that works from stale context and becomes a participant that reads your actual docs, searches across your knowledge base, and makes edits you can review before they go live.

Valoryx ships a built-in MCP server with 26 tools. No plugins to install, no separate service to run — if you have a running instance, the MCP server is already there. All you need is an API key.

## What MCP Actually Does

MCP defines a protocol for tool discovery and invocation. An AI client (like Claude Desktop) connects to an MCP server, asks what tools are available, and calls them with structured parameters. The server executes the operation and returns structured results.

This is different from "AI features" bolted onto a product. There's no proprietary integration. Any MCP-compatible client works. The [MCP specification](https://modelcontextprotocol.io) is open, and multiple AI assistants already support it.

The practical result: you can ask Claude "find all pages that mention authentication" and it will actually search your documentation instance, not hallucinate page titles from training data.

## The 26 Built-In Tools

Every tool is namespaced `docplatform_*` so it never collides with other MCP servers in your client. The full parameter-level reference lives on the [MCP page](/mcp/); here is the complete registry by category:

### Content
Create, read, and reorganize pages. Every write goes through the same content service as the web editor, so changes are tracked and sync-safe.

- **docplatform_list_pages** — list the pages in the connected workspace.
- **docplatform_read_page** — read a page's markdown content and metadata.
- **docplatform_write_page** — write a page: creates it if it doesn't exist, updates it if it does. The single "just write it" operation for AI agents.
- **docplatform_update_page** — update an existing page (fails rather than creates — useful when the page must already exist).
- **docplatform_delete_page** — delete a page.
- **docplatform_move_page** — move a page to a new path in the tree.

### Discovery & context
- **docplatform_search** — full-text search across the workspace, with fuzzy matching and relevance-ranked results — the same Bleve engine that drives the web UI.
- **docplatform_get_context** — the RAG workhorse: returns a page together with its parent, siblings, and the targets of its wikilinks in one call, so the assistant gets surrounding context without five round-trips.
- **docplatform_get_tree** — the full navigation tree of a workspace. Useful for understanding doc structure before making changes.
- **docplatform_list_workspaces** — list the workspaces the API key can reach.
- **docplatform_get_manifest** — a machine-readable manifest of the workspace.

### Quality
- **docplatform_validate_links** — find broken internal links and wikilinks.
- **docplatform_quality_scan** — scan content for quality issues.

### Versioning
- **docplatform_list_versions** / **docplatform_create_version** — list and create named version snapshots.

### Comments & activity
- **docplatform_list_comments** / **docplatform_add_comment** — read and join page discussions.
- **docplatform_get_activity** — the recent activity feed: who changed what, and when.

### Workspace management
- **docplatform_create_workspace** / **docplatform_get_workspace** — create and inspect workspaces.
- **docplatform_publish_workspace** — publish a workspace as a public site.

### Themes, export, AI, and git sync
- **docplatform_get_theme** / **docplatform_update_theme** — read and change the workspace theme.
- **docplatform_export** — export workspace content.
- **docplatform_writing_assist** — server-side writing assistance (improve, simplify, expand, summarize, fix grammar, translate) when an AI provider is configured.
- **docplatform_resolve_sync_conflict** — resolve a git-sync conflict by choosing a side or supplying merged content.

## Configuring Claude Desktop

The MCP server speaks stdio through the `docplatform` binary itself — no wrapper packages. Add an entry to your configuration file (on macOS, `~/Library/Application Support/Claude/claude_desktop_config.json`; on Windows, `%APPDATA%\Claude\claude_desktop_config.json`):

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

Create the API key in **Workspace Settings → API Keys**. It starts with `dp_live_` and is shown only once. Keys carry scopes (`read`, `write`, `delete` — `admin` is opt-in), and every MCP call is also checked against the acting user's workspace role, so an Editor's key can't do admin operations no matter what scopes it claims.

For remote or cloud instances there is also a Streamable HTTP transport (`/mcp` endpoint) — see the [MCP page](/mcp/) for the transport matrix and per-client setup (Claude Code, Cursor, VS Code).

## Practical Examples

Once connected, here are concrete things you can do:

### Audit for Consistency

```
"Search all pages for references to our old API endpoint
api.example.com/v1 and list them"
```

This calls `docplatform_search` with the old endpoint string. You get a list of every page that still references the deprecated URL. No manual grep through a docs repo required.

### Draft and Update Content

```
"Read the current authentication guide, then update it to include
the new passkey login flow. Keep the existing structure."
```

The assistant calls `docplatform_read_page` to read the current content, drafts the update, and calls `docplatform_update_page` to apply it. If [git sync](/docs/guides/git-integration/) is configured, the edit appears as a commit in your repository, attributed to the acting user.

### Review Recent Changes

```
"Show me everything that changed this week in this workspace"
```

Calls `docplatform_get_activity`. Returns what changed, who changed it, and when. Useful for weekly documentation reviews without logging into the web UI.

### Check Quality Before a Release

```
"Validate all internal links in this workspace and list anything broken"
```

Calls `docplatform_validate_links` and returns the broken targets with their source pages — the kind of sweep that's tedious by hand and instant with structured access.

## What This Means for Doc Maintenance

The traditional documentation maintenance workflow is: someone notices docs are wrong, files a ticket, someone else eventually updates the page. The gap between "noticed" and "fixed" is usually weeks.

With MCP, the workflow becomes: ask the AI to audit a section, review the findings, approve the changes. The gap shrinks to minutes. Not because AI writes better documentation — it doesn't, not reliably — but because the bottleneck was always finding what's wrong and making the edit, not composing the text.

This works especially well for mechanical updates: URL changes, terminology renames, version number bumps, deprecation notices. The kind of changes that are tedious for humans and straightforward for an AI with structured access to the content.

For more on using MCP to keep docs current, see [How to Keep Documentation Up to Date](/blog/keep-docs-up-to-date/).

## Limitations Worth Knowing

MCP tools operate on individual pages. There's no "rewrite the entire docs site" tool — by design. Large-scale restructuring still needs human judgment about information architecture.

The write tools create real changes. If you hand the assistant a key with `write` and `delete` scopes, it can modify and remove pages. Start read-only: create a key with only the `read` scope for audit workflows, and grant write scopes once you trust the review loop. Scopes are enforced server-side, alongside the acting user's workspace role.

Search quality depends on your content. If your docs use inconsistent terminology, the AI will find inconsistent results. MCP makes the search fast, but it doesn't fix the underlying content problems.

## Getting Started

1. [Install Valoryx](/install/) — single binary, no dependencies, running in under 2 minutes
2. Create an API key in **Workspace Settings → API Keys**
3. Add the MCP server config to Claude Desktop
4. Start with a read-only workflow: search and audit before you enable writes

The [MCP documentation](/mcp/) covers the full reference for all 26 tools, including parameter types and response schemas.

Documentation maintenance doesn't have to be a manual process. With a structured protocol between your AI assistant and your docs platform, the tedious parts — finding stale content, checking consistency, making mechanical updates — become something you can delegate with confidence.
