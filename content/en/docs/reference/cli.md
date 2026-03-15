---
title: CLI Reference
description: Complete reference for all DocPlatform CLI commands — serve, init, rebuild, doctor, export, preview, mcp, and version.
weight: 2
---

# CLI Reference

DocPlatform provides 9 CLI commands for server management, workspace initialization, diagnostics, publishing, and AI integration.

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

- Loads environment variables from `.env` file (if present)
- Initializes SQLite database with WAL mode
- Runs pending database migrations
- Loads custom RBAC permission policies into memory
- Builds or opens the Bleve search index
- Starts the git sync engine for all configured workspaces
- Starts the backup scheduler (if enabled)
- Serves the web editor and API on the configured port

### Startup sequence

When `docplatform serve` runs, the following happens in order:

1. Load config (environment variables + `.env` file + defaults)
2. Open SQLite database (WAL mode) and run pending migrations
3. Seed default organization if this is a first run
4. Initialize services: Content Ledger, Git Engine (worker pool of 4), Search Engine, Permission Service, Auth Service (RS256 JWT, Argon2id, WebAuthn), WebSocket Hub, Billing/License Service (Stripe), Analytics Collector, AI Service
5. Start background goroutines: WebSocket hub, git sync polling, backup scheduler, durable job worker, analytics collector, telemetry (if enabled)
6. Begin listening on the configured host:port

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
INFO  Server starting            port=3000 version=v0.5.2
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
| `--data-dir` | No | `.docplatform` | Data directory path |

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
| `--workspace` | Yes | — | ULID of the workspace to rebuild (required). |
| `--search` | No | `false` | Also drop and rebuild the Bleve search index |
| `--data-dir` | No | `.docplatform` | Data directory path |

### Behavior

1. Creates a backup of the current database
2. Drops the `pages` table
3. Scans the filesystem for all `.md` files in workspace `docs/` directories
4. Parses frontmatter and content for each file
5. Inserts page records into the database
6. Rebuilds the Bleve search index
7. Reports reconciliation results

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
INFO  Backup created             path=.docplatform/backups/pre-rebuild-20250115.db
INFO  Rebuilding workspace       id=01KJJ10NTF... name="API Docs"
INFO  Scanning filesystem        path=.docplatform/workspaces/01KJJ.../docs/
INFO  Pages found                count=42
INFO  Database rebuilt            inserted=42 updated=0 orphaned=3
INFO  Search index rebuilt        documents=42
INFO  Ghost recovery             matched=2 unmatched=1
INFO  Rebuild complete
```

**Ghost recovery:** When orphaned database records (no matching file) are found, DocPlatform attempts to match them to unindexed files by content hash. This recovers pages that were moved or renamed outside of DocPlatform.

---

## `docplatform doctor`

Run 9 diagnostic checks on the platform health.

```bash
docplatform doctor [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--bundle` | No | `false` | Create a ZIP file containing diagnostic output for support |
| `--data-dir` | No | `.docplatform` | Data directory path |

### Checks

| # | Check | Description |
|---|---|---|
| 1 | **Database connection** | SQLite file exists, is readable, WAL mode enabled |
| 2 | **Schema version** | Migrations are up to date |
| 3 | **FS/DB consistency** | Every file in `docs/` has a database record, and vice versa |
| 4 | **Orphaned files** | Files on disk without a database record |
| 5 | **Orphaned records** | Database records without a file on disk |
| 6 | **Search index health** | Bleve index document count matches page count |
| 7 | **Broken internal links** | Markdown links pointing to non-existent pages |
| 8 | **Frontmatter validity** | All pages have valid YAML frontmatter with a title |
| 9 | **Git remote connectivity** | If git is configured, can the remote be reached? |

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

✓ Database connection          OK (WAL mode, 42 pages, 3 users)
✓ Schema version               OK (v1, up to date)
✓ FS/DB consistency            OK (42 files, 42 records)
✓ Orphaned files               OK (0 found)
✓ Orphaned records             OK (0 found)
✓ Search index health          OK (42 indexed, 42 expected)
⚠ Broken internal links        WARNING (2 broken links found)
  → guides/editor.md:15 → "old-page.md" (file not found)
  → api/endpoints.md:42 → "deprecated.md" (file not found)
✓ Frontmatter validity         OK (42/42 valid)
✓ Git remote connectivity      OK (git@github.com:your-org/docs.git)

Result: 8/9 passed, 1 warning
```

### Bundle mode

```bash
docplatform doctor --bundle
# Creates: docplatform-doctor-20250115.zip
```

The bundle is saved to `{DATA_DIR}/diagnostics/docplatform-diagnostics-{timestamp}.zip` and contains:

- `report.json` — structured diagnostic results
- Schema information (table definitions, no row data)
- File listing (paths and sizes, no content)
- System info (OS, architecture, Go version)
- Last 1,000 lines of error logs
- Server version and configuration (with secrets redacted)

The bundle **never** includes page content, passwords, tokens, or private keys.

---

## `docplatform export`

Export a workspace's published documentation as a static HTML ZIP file.

```bash
docplatform export [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--workspace` | Yes | — | Workspace ID (ULID) to export |
| `--output` | No | `{workspace}-export.zip` | Output ZIP file path |
| `--data-dir` | No | `.docplatform` | Data directory path |

### Behavior

1. Opens the database and loads workspace configuration
2. Renders all published pages to HTML (same rendering pipeline as `/p/` routes)
3. Generates `sitemap.xml` and `robots.txt`
4. Packages everything into a self-contained ZIP file

### Example

```bash
docplatform export --workspace my-docs --output ./dist/my-docs.zip
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
| `--workspace` | Yes | — | Workspace ID (ULID) to preview |
| `--port` | No | `4000` | HTTP listen port |
| `--data-dir` | No | `.docplatform` | Data directory path |

### Behavior

Starts a lightweight Fiber HTTP server that renders published pages in real-time. Useful for reviewing changes before deploying to production.

### Example

```bash
docplatform preview --workspace my-docs --port 4000
```

Open [http://localhost:4000](http://localhost:4000) to view the published docs.

---

## `docplatform mcp`

Start a Model Context Protocol (MCP) server for AI agent integration.

```bash
docplatform mcp [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--workspace` | Yes | — | Workspace ID (ULID) to expose |
| `--api-key` | Yes | — | API key for authentication (or set `DOCPLATFORM_API_KEY` env var) |
| `--data-dir` | No | `.docplatform` | Data directory path |

### Behavior

Starts an MCP server on stdio, exposing workspace content to AI agents (Claude Code, Claude Desktop, etc.). The server is scoped to a single workspace and authenticated via API key.

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

---

## `docplatform version`

Print version, commit hash, and build date.

```bash
docplatform version
```

### Output

```
docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
```

The version information is embedded at build time via linker flags. Useful for verifying which release is deployed and for support requests.
