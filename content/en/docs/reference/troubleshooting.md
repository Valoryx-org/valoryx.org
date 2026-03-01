---
title: Troubleshooting
description: Common issues and solutions for DocPlatform — server startup, git sync, authentication, search, and data recovery.
weight: 3
---

# Troubleshooting

This guide covers common issues and their solutions. For diagnostic information, always start with:

```bash
docplatform doctor
```

## Server startup

### Server fails to start: "address already in use"

**Cause:** Another process is using the configured port.

**Solution:**

```bash
# Find what's using port 3000
lsof -i :3000  # macOS/Linux
ss -tlnp | grep 3000  # Linux

# Option 1: Stop the other process
# Option 2: Use a different port
docplatform serve --port 8080
```

### Server fails to start: "permission denied"

**Cause:** The process doesn't have read/write access to the data directory.

**Solution:**

```bash
# Check ownership
ls -la .docplatform/

# Fix ownership (if running as docplatform user)
sudo chown -R docplatform:docplatform .docplatform/

# Fix permissions
chmod 700 .docplatform/
```

### Server fails to start: "database is locked"

**Cause:** Another DocPlatform process is running, or a previous process didn't shut down cleanly.

**Solution:**

```bash
# Check for other docplatform processes
ps aux | grep docplatform

# If a process is stuck, kill it
kill -SIGTERM <pid>

# If the lock file persists after no processes are running
# SQLite WAL mode handles this automatically on restart
docplatform serve
```

## Git sync

### "Permission denied (publickey)" during git sync

**Cause:** The SSH key is not configured or doesn't have access to the repository.

**Solution:**

1. Verify the key exists:
   ```bash
   ls -la $GIT_SSH_KEY_PATH
   ```

2. Verify the key has been added to the repository's deploy keys:
   ```bash
   ssh -T -i $GIT_SSH_KEY_PATH git@github.com
   ```

3. Ensure write access is enabled on the deploy key (required for pushing)

### Git sync shows "no changes" but files were updated

**Cause:** Changes were made to files outside the `docs/` directory, which DocPlatform doesn't index.

**Solution:** Ensure your Markdown files are in the workspace's `docs/` directory. Files in other directories are preserved in git but not tracked by DocPlatform.

### Conflict: HTTP 409 on save

**Cause:** The page was modified by another user or via git push between your load and save.

**Solution:**

1. The web UI shows a conflict banner with both versions
2. Click **Download both** to get both files
3. Manually merge the changes
4. Save the merged version

**Prevention:**

- Enable webhooks for faster sync (reduce conflict window)
- Use presence indicators to see who's editing what
- Assign page ownership to avoid simultaneous edits

### Git push fails: "remote rejected"

**Cause:** The deploy key doesn't have write access, or branch protection rules prevent direct pushes.

**Solution:**

1. Verify the deploy key has write access in your repository settings
2. Check branch protection rules — DocPlatform pushes directly to the configured branch
3. If branch protection is required, configure DocPlatform to push to a non-protected branch

## Authentication

### "401 Unauthorized" on every request

**Cause:** JWT access token has expired (15-minute lifetime by default).

**Solution:** The web editor handles token refresh automatically. If using the API directly, call the refresh endpoint:

```bash
curl -X POST http://localhost:3000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

### Can't log in after JWT key rotation

**Cause:** All tokens were invalidated when the JWT key was deleted and regenerated.

**Solution:** This is expected behavior. All users must log in again after key rotation. Clear your browser cookies/storage and log in with your password.

### OIDC sign-in redirects to an error page

**Cause:** The OAuth callback URL doesn't match what's configured in Google/GitHub.

**Solution:**

1. Check the callback URL in your OAuth provider settings
2. It should be: `https://your-domain.com/api/v1/auth/callback/google` (or `/github`)
3. Ensure the `OIDC_*_CLIENT_ID` and `OIDC_*_CLIENT_SECRET` environment variables are set correctly
4. Restart the server after changing OIDC environment variables

### First user is not SuperAdmin

**Cause:** The database already contained user records from a previous installation.

**Solution:**

```bash
# WARNING: This deletes all data
docplatform serve  # stop first
rm .docplatform/data.db
docplatform serve
# Register your admin account
```

Only do this on a fresh installation. For existing installations, use the database to update user roles directly (advanced).

## Search

### Search returns no results

**Cause:** The search index may be empty or out of sync.

**Solution:**

```bash
# Check search health
docplatform doctor

# If the index is out of sync, rebuild
docplatform rebuild
```

### Search results are stale (don't reflect recent edits)

**Cause:** The async indexing job hasn't processed yet (typically < 1 second delay).

**Solution:** Wait a moment and retry. If the issue persists:

1. Check server logs for indexing errors
2. Run `docplatform rebuild` to force a full re-index

### Search is slow

**Cause:** Very large workspaces (1000+ pages) with complex queries.

**Solution:**

- Use more specific search terms
- Use tag filters to narrow the scope
- Future releases will support Meilisearch for high-performance search

## Data recovery

### Deleted a page accidentally

**Option 1: Git history** (if git sync is enabled)

```bash
cd .docplatform/workspaces/{id}/docs/
git log --all -- path/to/deleted-page.md
git checkout <commit-hash> -- path/to/deleted-page.md
```

Then run `docplatform rebuild` to re-index.

**Option 2: Database backup**

```bash
# List backups
ls .docplatform/backups/

# Restore from backup (stops the server first)
cp .docplatform/backups/{latest}.db .docplatform/data.db
docplatform serve
```

### Database is corrupted

**Solution:**

1. Stop the server
2. Check for a recent backup:
   ```bash
   ls -la .docplatform/backups/
   ```
3. Restore from backup:
   ```bash
   cp .docplatform/backups/{latest}.db .docplatform/data.db
   ```
4. If no backup is available, rebuild from the filesystem:
   ```bash
   rm .docplatform/data.db
   docplatform rebuild
   ```
5. Start the server

The filesystem (`.md` files) is the source of truth. Even if the database is lost, `rebuild` recreates it from your files.

### Lost the JWT key

**Cause:** The `jwt-key.pem` file was deleted.

**Impact:** All user sessions are invalidated. Users must log in again.

**Solution:** Start the server — a new key is generated automatically. No data is lost, but all users need to re-authenticate.

## Frontmatter errors

### Page becomes inaccessible after frontmatter edit

**Cause:** Invalid YAML in the frontmatter block. DocPlatform uses **strict mode** by default — if frontmatter parsing fails, the page is restricted to WorkspaceAdmin access only to prevent a YAML typo from accidentally making a private page public.

**Symptoms:**

- Page disappears from search results
- Page excluded from published docs
- Non-admin users get 403 Forbidden
- Admin sees a warning banner on the page

**Solution:**

1. Sign in as a WorkspaceAdmin or SuperAdmin
2. Open the affected page in the web editor
3. Switch to raw Markdown mode (`</>` toggle)
4. Fix the YAML frontmatter (common issues: missing quotes around values with colons, incorrect indentation, unclosed brackets)
5. Save — the page is re-indexed and access restored

**If you can't access the web editor**, fix the file directly on disk:

```bash
# Edit the Markdown file
nano .docplatform/workspaces/{id}/docs/{path-to-page}.md

# Rebuild to re-index
docplatform rebuild
```

### Understanding frontmatter error modes

| Mode | Behavior on invalid YAML | When to use |
|---|---|---|
| **Strict** (default) | Page restricted to WorkspaceAdmin only, excluded from search and published docs | Production — prevents accidental exposure |
| **Lenient** | Keep last-known-good frontmatter from database, show warning | Development — less disruption during editing |

Strict mode ensures a YAML typo never accidentally makes a restricted page public. This is a deliberate safety design.

## Disk space

### "Low disk space" warning from doctor

**Cause:** DocPlatform warns when free disk space drops below 1 GB.

**Impact:** SQLite requires free disk space for WAL (write-ahead log) operations. If the disk fills completely, writes fail and data may be corrupted.

**Solution:**

1. Check disk usage: `df -h`
2. Clean up old backups: reduce `BACKUP_RETENTION_DAYS` or manually delete old files in `{DATA_DIR}/backups/`
3. Move the data directory to a larger disk: update `DATA_DIR` and move the directory
4. If using Docker, increase the volume size

## Performance

### High memory usage

**Expected:** < 80 MB idle, < 200 MB under load.

If memory usage exceeds 200 MB:

1. Check the number of active WebSocket connections
2. Check workspace count and total page count
3. Large git repositories (>5,000 files) use more memory — the hybrid engine auto-switches to native git CLI when go-git exceeds 512 MB RSS

### Slow page renders

**Expected:** < 50ms p99.

If page renders are slow:

1. Check disk I/O — SQLite performance depends on disk speed
2. Use an SSD for the data directory
3. Check if the database file is on a network filesystem (NFS/CIFS) — move to local disk

## Getting help

If you can't resolve an issue:

1. Run `docplatform doctor --bundle` to generate a diagnostic bundle
2. Check the server logs for error messages
3. Open an issue on GitHub with the diagnostic bundle and relevant log entries

The diagnostic bundle **does not** contain your content, passwords, or API tokens — only structural metadata and configuration (with secrets redacted).
