---
title: CLI Reference
description: Complete reference for all DocPlatform CLI commands — serve, init, rebuild, doctor, export, preview, mcp, and version.
weight: 2
---

# CLI Reference

DocPlatform provides 10 CLI commands for server management, workspace initialization, diagnostics, publishing, and AI integration.

## Global options

These options apply to all commands:

| Flag | Description |
|---|---|
| `--help`, `-h` | Show help for any command |
| `--version`, `-v` | Print version information |

## `docplatform serve`

Start the HTTP server.

```bash
docplatform serve [flags]
```

### Flags

| Flag | Default | Description |
|---|---|---|
| `--port` | `3000` | HTTP listen port (overrides `PORT` env var) |

### Behavior

- Reads configuration from environment variables (there is no config file)
- Initializes SQLite database with WAL mode
- Runs pending database migrations
- Builds or opens the Bleve search index
- Starts the git sync engine for all configured workspaces
- Starts the backup scheduler (if enabled)
- Serves the web editor and API on the configured port

### Startup sequence

When `docplatform serve` runs, the following happens in order:

1. Load config from environment variables (+ defaults)
2. Open SQLite database (WAL mode) and run pending migrations
3. Initialize services: Content Ledger, Git Engine, Search Engine, Permission Service, Auth Service (RS256 JWT, Argon2id, WebAuthn), WebSocket Hub, License Service, Analytics Collector, AI Service (if configured)
4. Start background goroutines: WebSocket hub, git sync polling, backup scheduler, job worker, analytics collector, telemetry (if enabled)
5. Begin listening on the configured port

Read requests are served immediately. If workspaces have existing content, reconciliation runs in the background without blocking.

### Signals

| Signal | Effect |
|---|---|
| `SIGTERM` | Graceful shutdown — stop accepting requests, finish in-flight operations, flush database |
| `SIGINT` | Same as SIGTERM (Ctrl+C) |

**Shutdown sequence** (15-second deadline):

1. Cancel application context (signals all goroutines to stop)
2. Stop WebSocket hub (close all client connections)
3. Stop git sync manager (finish in-flight sync operations)
4. Drain durable job worker (finish in-flight async jobs)
5. Close search engine (flush Bleve index to disk)
6. Drain git worker pool (wait for in-flight git operations)
7. Shutdown HTTP server (10-second timeout for in-flight requests)

If shutdown exceeds 15 seconds, the process exits forcefully.

### Example

```bash
# Start on default port
docplatform serve

# Start on custom port
docplatform serve --port 8080
```

### Output

```
INFO  Server starting            port=3000 version=v0.10.0
INFO  Database initialized       path=.docplatform/data.db wal=true
INFO  Migrations applied         count=1
INFO  Search index ready         documents=42
INFO  Workspace loaded           name="Docs" slug=docs git_remote=git@github.com:...
INFO  Backup scheduler started   retention_days=7
INFO  Listening on               http://0.0.0.0:3000
```

---

## `docplatform init`

Initialize a new workspace.

```bash
docplatform init [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--workspace-name` | Yes | — | Display name for the workspace |
| `--slug` | Yes | — | URL-safe identifier (used in published docs URL) |
| `--git-url` | No | — | Remote git repository URL (SSH or HTTPS) |
| `--branch` | No | `main` | Git branch to sync |

The data directory comes from the `DATA_DIR` environment variable (default `.docplatform`) — this applies to every command; there is no `--data-dir` flag.

> CLI-created workspaces attach to a server-level default organization, not to a web account's organization. See [Your First Workspace](../getting-started/first-workspace.md).

### Behavior

1. Creates the data directory structure (`{DATA_DIR}/`)
2. Initializes the SQLite database (if not already present)
3. Generates an RS256 JWT signing key (if not already present)
4. Creates the workspace directory (`{DATA_DIR}/workspaces/{ulid}/`)
5. If `--git-url` is provided, clones the repository
6. Creates the workspace config file
7. Indexes any existing `.md` files

### Example

```bash
# Local workspace (no git)
docplatform init \
  --workspace-name "Internal Wiki" \
  --slug wiki

# With git
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git \
  --branch main
```

### Output

```
INFO  Data directory created     path=.docplatform
INFO  Database initialized       path=.docplatform/data.db
INFO  JWT key generated          path=.docplatform/jwt-private.pem
INFO  Workspace created          id=01KJJ10NTF... name="API Docs" slug=api-docs
INFO  Repository cloned          url=git@github.com:your-org/api-docs.git branch=main
INFO  Pages indexed              count=15
INFO  Ready. Run 'docplatform serve' to start.
```

---

## `docplatform rebuild`

Rebuild the database and search index from the filesystem. Use when the database is out of sync with the actual files on disk.

```bash
docplatform rebuild [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--workspace`, `-w` | Yes | — | ULID of the workspace to rebuild (required). |
| `--search` | No | `false` | Also rebuild the Bleve search index |

### Behavior

1. Scans the filesystem for all `.md` files in the workspace directory
2. Parses frontmatter and content for each file
3. Reconciles page records in the database (three-tier matching: frontmatter ID → path → content hash)
4. Rebuilds the search index when `--search` is passed
5. Reports reconciliation results

### When to use

- After manually adding, moving, or deleting `.md` files outside of DocPlatform
- After a crash that may have left the database inconsistent
- After restoring files from a git backup
- When `docplatform doctor` reports FS/DB mismatches

### Example

```bash
# Rebuild a specific workspace
docplatform rebuild --workspace 01KJJ10NTF31Z1QJTG4ZRQZ2Z2
```

### Output

```
INFO  Rebuilding workspace       id=01KJJ10NTF... name="API Docs"
INFO  Pages found                count=42
INFO  Database rebuilt           inserted=42 updated=0 orphaned=3
INFO  Search index rebuilt       documents=42
INFO  Rebuild complete
```

**Ghost recovery:** When orphaned database records (no matching file) are found, DocPlatform attempts to match them to unindexed files by content hash. This recovers pages that were moved or renamed outside of DocPlatform.

---

## `docplatform doctor`

Run 10 diagnostic checks on the platform health.

```bash
docplatform doctor [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--bundle` | No | `false` | Create a ZIP file containing diagnostic output for support |

### Checks

| # | Check | Description |
|---|---|---|
| 1 | **config** | Configuration loads and validates |
| 2 | **data_dir** | The data directory exists and is a directory |
| 3 | **database** | Main database reachable, migrations current |
| 4 | **analytics_db** | Analytics database reachable |
| 5 | **git** | Native `git` binary available in PATH (warning if missing) |
| 6 | **workspace_dirs** | Every workspace has its content directory on disk |
| 7 | **sync_state** | Git sync state is consistent |
| 8 | **fs_db_consistency** | Files on disk match database page records |
| 9 | **broken_wikilinks** | Wikilinks pointing to non-existent pages |
| 10 | **backups** | Backup directory present and recent backups exist |

### Exit codes

| Code | Meaning |
|---|---|
| `0` | All checks passed (healthy) |
| `1` | One or more checks failed or had warnings |

Use the exit code in scripts and monitoring:

```bash
docplatform doctor || echo "Health check failed"
```

### Example

```bash
docplatform doctor
```

### Output

```
DocPlatform Health Check
========================

✓ config                OK
✓ data_dir              OK (.docplatform exists)
✓ database              OK (migrations current)
✓ analytics_db          OK
✓ git                   OK (binary found)
✓ workspace_dirs        OK
✓ sync_state            OK
✓ fs_db_consistency     OK (42 files, 42 records)
⚠ broken_wikilinks      WARNING (2 broken links found)
✓ backups               OK

Result: 9/10 passed, 1 warning
```

### Bundle mode

```bash
docplatform doctor --bundle
```

The bundle is saved to `{DATA_DIR}/diagnostics-{timestamp}.zip` and contains sanitized system information and the structured check results for support requests. It never includes page content, passwords, tokens, or private keys.

---

## `docplatform export`

Export a workspace's published documentation as a static HTML ZIP file.

```bash
docplatform export [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--workspace`, `-w` | Yes | — | Workspace ID (ULID) to export |
| `--output`, `-o` | No | `{site-slug}-export.zip` | Output ZIP file path |

### Behavior

1. Opens the database and loads workspace configuration
2. Renders all published pages to HTML (same rendering pipeline as `/p/` routes)
3. Generates `sitemap.xml` and `robots.txt`
4. Packages everything into a self-contained ZIP file

### Example

```bash
docplatform export --workspace 01KJJ10NTF31Z1QJTG4ZRQZ2Z2 --output ./dist/my-docs.zip
```

The resulting ZIP can be deployed to any static file host (Netlify, Vercel, S3, GitHub Pages, Cloudflare Pages).

---

## `docplatform preview`

Start a local preview server for published documentation.

```bash
docplatform preview [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--workspace`, `-w` | Yes | — | Workspace ID (ULID) to preview |
| `--port`, `-p` | No | `4000` | HTTP listen port |

### Behavior

Starts a lightweight Fiber HTTP server that renders published pages in real-time. Useful for reviewing changes before deploying to production.

### Example

```bash
docplatform preview --workspace my-docs --port 4000
```

Open [http://localhost:4000](http://localhost:4000) to view the published docs.

---

## `docplatform mcp`

Start a Model Context Protocol (MCP) server on stdio for AI agent integration.

```bash
docplatform mcp [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--workspace`, `-w` | Yes | — | Workspace slug to expose |
| `--api-key` | Yes | — | API key for authentication (`dp_live_...`). Also accepts `DOCPLATFORM_API_KEY` env var |

### Behavior

Starts an MCP server on stdin/stdout, scoped to a single workspace and authenticated via API key. Exposes 26 tools for content CRUD, search, quality scanning, versioning, export, and more. Compatible with any MCP client (Claude Desktop, Claude Code, Cursor, VS Code).

### Example

```bash
docplatform mcp --workspace my-docs --api-key dp_live_abc123
```

Configure in your MCP client (e.g., Claude Desktop `claude_desktop_config.json`):

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

See the [MCP Server guide](../guides/mcp.md) for complete setup instructions and the full tool reference.

---

## `docplatform mcp-server`

Start a Streamable HTTP MCP server for remote AI tool access.

```bash
docplatform mcp-server [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--addr` | No | `:8081` | Listen address (e.g., `:8081`, `0.0.0.0:9090`) |
| `--cors-origins` | No | claude.ai, cursor | Allowed CORS origins (comma-separated) |

### Behavior

Runs a Streamable HTTP MCP server authenticated via Bearer API keys. Unlike `docplatform mcp` (stdio, single workspace), the HTTP transport supports multi-workspace access — content tools accept an optional `workspace` parameter to target different workspaces. Suitable for cloud deployment behind a reverse proxy.

### Example

```bash
# Start on default port
docplatform mcp-server

# Custom port with CORS
docplatform mcp-server --addr :9090 --cors-origins https://my-app.com
```

Clients connect via HTTP and authenticate with a Bearer token:

```
POST http://your-server:8081/mcp
Authorization: Bearer dp_live_abc123
```

---

## `docplatform reset-password`

Generate a one-time password-reset link for a user — useful when email isn't configured or a user is locked out.

```bash
docplatform reset-password --email user@example.com
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--email` | Yes | — | Email address of the user |
| `--base-url` | No | `BASE_URL` env or `http://localhost:3000` | Base URL used to build the reset link |

The printed link is single-use and expires after 1 hour.

---

## `docplatform version`

Print version, commit hash, and build date.

```bash
docplatform version
```

### Output

```
docplatform v0.10.0 (commit: 5738520, built: 2026-05-16T17:52:38Z)
```

The version information is embedded at build time via linker flags. Useful for verifying which release is deployed and for support requests.
