---
title: CLI Reference
description: Complete reference for all DocPlatform CLI commands — serve, status, open, stop, init, rebuild, doctor, export, preview, mcp, and version.
weight: 2
---

# CLI Reference

DocPlatform provides 13 CLI commands for server management, workspace initialization, diagnostics, publishing, and AI integration.

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

Illustrative example (log line count and exact fields vary by release and configuration — the general shape holds: a migration/startup log line per subsystem, then the ready banner):

```
INFO  Server starting            port=3000 version=<version>
INFO  Database initialized       path=<your-data-dir>/data.db wal=true
INFO  Migrations applied         count=1
INFO  Search index ready         documents=42
INFO  Workspace loaded           name="Docs" slug=docs git_remote=git@github.com:...
INFO  Listening on               http://0.0.0.0:3000
```

`<your-data-dir>` is an OS-standard per-user location by default, not `.docplatform/` — see [Getting Started](../getting-started/index.md#architecture-at-a-glance) or run `docplatform doctor` to see the resolved path.

---

## `docplatform status`

Report whether a DocPlatform instance is running on this data directory. Read-only — nothing is created, modified, or deleted.

```bash
docplatform status [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--data-dir` | No | — | Data directory (overrides `DATA_DIR` env var; highest precedence) |
| `--json` | No | `false` | Machine-readable JSON output |

### Behavior

Resolves the data directory (same rule as every other command), then checks whether an instance holds its single-writer lock. If one does, it confirms the instance's identity via `/api/health` before reporting details — a lock being held is not by itself proof of *which* process holds it, so an unconfirmed instance (starting up or shutting down) is reported honestly rather than guessed at.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | An instance is running (and its identity is confirmed) |
| `3` | Nothing is running on this data directory |

### Example

```bash
docplatform status
docplatform status --json
```

### Output

```
DocPlatform is running — http://localhost:3000 (pid 12345, version <version>, instance <id>)
```

Or, when nothing is running:

```
DocPlatform is not running (data dir: /home/you/.local/share/docplatform)
```

---

## `docplatform open`

Open the running DocPlatform instance in your browser — the command to reach for after you've closed the terminal or came back the next day and don't remember the URL.

```bash
docplatform open [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--data-dir` | No | — | Data directory (overrides `DATA_DIR` env var; highest precedence) |
| `--no-browser` | No | `false` | Print the URL instead of opening a browser |

### Behavior

Same identity-confirmed detection as `status`. If confirmed, opens your default browser to the running instance's URL (or prints it with `--no-browser`). If nothing is running, it exits 3 and points you at `docplatform serve` instead of opening anything.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | An instance is running and confirmed; the URL was opened (or printed) |
| `1` | An instance holds the data directory but its identity could not be confirmed (starting up or shutting down) — retry shortly |
| `3` | Nothing is running on this data directory |

### Example

```bash
docplatform open
docplatform open --no-browser
```

---

## `docplatform stop`

Stop the running DocPlatform instance gracefully — the command-line equivalent of closing the console window, but clean: it waits for in-flight requests, git syncs, and search-index writes to finish first.

```bash
docplatform stop [flags]
```

### Flags

| Flag | Required | Default | Description |
|---|---|---|---|
| `--data-dir` | No | — | Data directory (overrides `DATA_DIR` env var; highest precedence) |
| `--force` | No | `false` | Kill the instance if it does not stop gracefully in time (the target process is verified before being killed) |

### Behavior

Requests a graceful shutdown and waits up to 30 seconds for it to complete. `--force` does not skip the graceful attempt or shorten the wait — it only decides whether to escalate to a forceful kill *after* the full grace period has already been given, and only against a process that has been positively verified as the instance holding this data directory's lock. Restart is `docplatform stop && docplatform serve`.

**How the graceful request reaches the server:** `serve` opens a small internal shutdown-control endpoint bound **only to `127.0.0.1`, on an ephemeral port** — this is hardcoded and not operator-configurable, so the endpoint is unreachable from the network by construction, even if `serve` itself is bound to all interfaces. `stop` authenticates to it with a per-boot token read from the local data directory. If that endpoint is unavailable, `stop` falls back to sending the process a `SIGTERM` directly. Either way, only someone with local access to this machine and this data directory can request a shutdown.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Stopped (or nothing was running) |
| `1` | Did not stop within the grace period, identity could not be confirmed, or the instance could not be signaled safely — see the printed message; often just retry, or add `--force` |

### Example

```bash
docplatform stop
docplatform stop --force
```

### Output

```
shutdown requested — waiting up to 30s for the instance to exit
stopped
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
| `--data-dir` | No | — | Data directory (overrides `DATA_DIR` env var; highest precedence) |

The data directory is resolved the same way for every command: an explicit `--data-dir` flag or `DATA_DIR` env var wins; otherwise an existing `./.docplatform` from a pre-v0.15 install is used in place; otherwise it defaults to an OS-standard per-user location. Run `docplatform doctor` to see the resolved path and which rule chose it.

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

Illustrative example (`<your-data-dir>` is the resolved path described above, not `.docplatform` by default):

```
INFO  Data directory created     path=<your-data-dir>
INFO  Database initialized       path=<your-data-dir>/data.db
INFO  JWT key generated          path=<your-data-dir>/jwt-private.pem
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
| 9 | **wikilinks** | Wikilinks pointing to non-existent pages |
| 10 | **backups** | Backup directory present and recent backups exist |

### Exit codes

| Code | Meaning |
|---|---|
| `0` | All checks passed — including when some only produced a warning |
| `1` | One or more checks actually **failed** (a warning alone does not affect the exit code) |

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
DocPlatform Doctor v<version>
================================
[OK]   config: loaded (data_dir=<your-data-dir>, port=3000)
[OK]   data_dir: <your-data-dir> exists
       - resolved via default (OS per-user data directory) rule
[OK]   database: <your-data-dir>/data.db reachable, migrations current
[OK]   analytics_db: <your-data-dir>/analytics.db reachable
[OK]   git: binary found
[OK]   workspace_dirs: 2 git-enabled, all directories present
[OK]   sync_state: no stuck workspaces
[OK]   fs_db_consistency: 42 pages indexed, 42 in DB (consistent)
[WARN] wikilinks: 2 broken wikilink(s) found
[OK]   backups: 3 backup(s), most recent: 2026-08-18
================================
Duration: 8ms
Result: all checks passed, 1 warning(s)
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
docplatform <version> (commit: <sha>, built: <date>)
```

The version information is embedded at build time via linker flags and will match whichever release you have installed. Useful for verifying which release is deployed and for support requests.
