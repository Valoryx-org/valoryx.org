---
title: Git Integration
description: Bidirectional git sync — edit in the browser or push from your IDE, everything stays in sync.
weight: 3
---

# Git Integration

DocPlatform's bidirectional git sync lets your team work however they prefer. Technical writers use the web editor. Developers push from their IDE. Everyone sees the same content.

## How it works

```
        ┌─────────────┐
        │ Web Editor   │
        │ (browser)    │
        └──────┬───────┘
               │ save
               ▼
        ┌─────────────┐          ┌──────────────┐
        │ Content     │  commit  │ Local Git    │  push    ┌──────────────┐
        │ Ledger      │ ───────► │ Repository   │ ───────► │ Remote Repo  │
        │             │          │ (.git)       │          │ (GitHub etc) │
        └─────────────┘          └──────┬───────┘          └──────┬───────┘
               ▲                        │                         │
               │ reconcile              │ pull                    │
               │                 ┌──────▼───────┐                 │
               └──────────────── │ Sync Engine  │ ◄───────────────┘
                                 │ (polling /   │   webhook / poll
                                 │  webhook)    │
                                 └──────────────┘
```

### Web → Git (outbound)

1. You save a page in the web editor
2. Content Ledger writes the `.md` file to disk
3. Git engine auto-commits as you: `Update {page-path} via web editor`
4. Commits are pushed to the remote repository

### Git → Web (inbound)

1. Someone pushes a commit to the remote (from IDE, CI, etc.)
2. Sync engine detects the change (polling or webhook)
3. Changes are pulled to the local repository
4. Content Ledger reconciles: filesystem → database → search index
5. WebSocket broadcasts the update to connected browsers

### How reconciliation works

When DocPlatform pulls new commits from the remote, it runs a full reconciliation to sync the filesystem with the database:

```
For each .md file on disk:
  1. Parse frontmatter (extract id, title, tags, etc.)
  2. Match to existing DB page using three-tier lookup:
     ├─ Tier 1: Frontmatter ID (strongest — handles moved/renamed files)
     ├─ Tier 2: File path match (normal case — same path, same page)
     └─ Tier 3: Content hash match on recently deleted pages (ghost recovery)
  3. Compute content hash and frontmatter hash
  4. If no match found → CREATE new DB record (assign new ULID)
  5. If match found but hashes differ → UPDATE DB record
  6. If match found and hashes match → SKIP (no change)
  7. If file has no `id:` in frontmatter → inject one and rewrite the file

For each DB page with no matching file on disk:
  → Soft-delete (set deleted_at timestamp, page recoverable for 24h)

Important: the reconciler uses the ledger's internal upsert — it does NOT
go through the HTTP API. This is by design: the filesystem is the source
of truth during sync, and the API's create-only (409) semantics don't
apply to reconciliation.
```

The three-tier matching ensures that:
- **Renamed files** are detected (tier 1 — frontmatter ID stays the same)
- **Normal edits** are fast (tier 2 — path hasn't changed)
- **Deleted-then-recreated files** are recovered (tier 3 — content hash matches a recently deleted page)

### What happens when the workspace directory is missing

If the workspace `docs/` directory is missing or empty when a sync runs (e.g., due to a failed clone, a misconfigured path, or a filesystem error), the reconciler **refuses to delete** any pages and returns an error instead of proceeding. Without this safety check, the reconciler would see zero files on disk and soft-delete every page in the database — a catastrophic outcome for a corrupted or misconfigured workspace. The sync logs the error as `reconcile: workspace directory missing or empty, aborting` and the workspace's sync status reports the error.

## Setup

### Connect a remote repository

**During initialization:**

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

**After creation** — connect from the web UI (**Settings** → **Git**): validate a GitHub personal access token, pick the repository and branch. The token is encrypted at rest (AES-256-GCM; requires `GIT_ENCRYPTION_KEY`). Git settings are stored in the workspace database record and can also be updated via the API:

```bash
curl -X PATCH http://localhost:3000/api/v1/workspaces/{id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "git_remote": "git@github.com:your-org/docs.git",
    "git_branch": "main",
    "git_auto_commit": true,
    "sync_interval": 300
  }'
```

No restart is required — changes take effect on the next sync cycle.

> **Provider support:** the guided web-UI connection flow supports **GitHub personal access tokens** — GitHub is the only provider registered today. For GitLab, Bitbucket, or any other git host, configure a raw `git_remote` URL (SSH or HTTPS with token) instead.

### Authentication

#### SSH (recommended)

Generate a deploy key and add it to your repository:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""
```

Set the environment variable:

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

Add the public key (`~/.ssh/docplatform_deploy_key.pub`) to your repository's deploy keys. **Enable write access** if you want DocPlatform to push commits.

#### HTTPS with token

For HTTPS repositories, embed the token in the URL:

```yaml
git_remote: https://x-access-token:ghp_xxxxxxxxxxxx@github.com/your-org/docs.git
```

Or use a Git credential helper configured on the host.

## Sync behavior

### Auto-commit

When `git_auto_commit: true` (default) and a git remote is configured, every save in the web editor produces a git commit.

Commit message format:

```
Update guides/getting-started.md via web editor
```

(`Create` / `Delete` / `Move` for those operations.) The commit **author is the acting user** — their name and email from their DocPlatform account — so `git blame` reflects who actually made each change. Automatic conflict-merge commits are authored as `sync@valoryx.dev`.

Set `git_auto_commit: false` to disable auto-commit. In this mode, the web editor writes to the filesystem but does not create git commits — useful if you want to commit manually or on a schedule.

### Polling

DocPlatform polls the remote repository at the configured interval (default: 300 seconds / 5 minutes). Adjust with:

```yaml
sync_interval: 60  # check every minute
```

Lower intervals mean faster sync but more network traffic.

### Webhooks

For instant sync, configure a webhook in your repository.

DocPlatform generates a **per-workspace webhook secret** automatically (find it in **Settings** → **Git**). The single endpoint accepts GitHub (`X-Hub-Signature-256`), GitLab (`X-Gitlab-Token`), and Bitbucket (`X-Hub-Signature`) signature schemes. Pushes to branches other than the workspace's configured branch are ignored.

**GitHub:**

1. Go to **Settings** → **Webhooks** → **Add webhook**
2. Payload URL: `https://your-domain.com/api/git/webhook/{workspace-id}`
3. Content type: `application/json`
4. Secret: paste the workspace's webhook secret
5. Events: Select **Push events**

**GitLab:**

1. Go to **Settings** → **Webhooks**
2. URL: `https://your-domain.com/api/git/webhook/{workspace-id}`
3. Secret token: paste the workspace's webhook secret
4. Trigger: **Push events**

**Bitbucket:**

1. Go to **Repository settings** → **Webhooks** → **Add webhook**
2. URL: `https://your-domain.com/api/git/webhook/{workspace-id}`
3. Secret: paste the workspace's webhook secret
4. Triggers: **Repository push**

### Manual sync

Trigger a sync from the web UI (**Settings** → **Git** → **Sync Now**) or via API:

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{id}/sync \
  -H "Authorization: Bearer {token}"
```

## Conflict resolution

Conflicts occur when the same file is modified both in the web editor and via git push between sync intervals.

### How conflicts are detected

DocPlatform tracks content hashes (SHA-256) for every page. When pulling remote changes, it compares the incoming hash against the local hash. If both differ from the common ancestor, a conflict is declared.

### What happens on conflict

1. The save or sync operation returns **HTTP 409 Conflict**
2. All three versions (ours, theirs, base) are preserved in the conflict directory
3. The web UI displays a conflict banner with a three-way merge view:
   - **Ours** — the local version (web editor)
   - **Theirs** — the remote version (git push)
   - **Base** — the common ancestor before divergence
4. The user resolves by choosing or merging content from the three versions

For the workspace manifests `redirects.yaml`, `workspace.yaml`, and `publish.yaml` (under `.docplatform/`), DocPlatform attempts an automatic three-way merge first. Markdown pages and `nav.yaml` are **never** auto-merged — they always go to a human.

### Preventing conflicts

- **Use webhooks** instead of polling — faster sync means smaller conflict windows
- **Assign page ownership** — one writer per page reduces collision risk
- **Use the web editor for content**, IDE for code — natural separation
- **Short sync intervals** — `sync_interval: 30` in high-collaboration environments

## Batch sync

Whenever a remote push contains multiple changed files, DocPlatform uses batch mode:

1. Fetches all changed files in a single diff
2. Processes the changes as one reconciliation pass
3. Emits a `bulk-sync` WebSocket event with the total changed count

This prevents notification storms and database overhead when large changes are pushed (e.g., initial repository import or bulk restructuring).

## Conflict storage

When a conflict is detected, both versions are stored on disk:

```
{DATA_DIR}/conflicts/
└── {page-id}/
    └── 20250115T103045Z/
        ├── ours.md      # Local version (web editor)
        ├── theirs.md    # Remote version (git push)
        └── base.md      # Common ancestor version
```

Conflicts persist until explicitly resolved via the web UI or API. The `docplatform doctor` command reports unresolved conflicts.

## Git engine details

DocPlatform uses a **hybrid git engine** that routes each operation to the best backend automatically: a pure-Go engine (go-git) for everyday operations, switching to the native `git` CLI for large repositories (file-count and memory thresholds). Operations on the same workspace are serialized; different workspaces sync in parallel.

## Working with existing repositories

DocPlatform works with existing documentation repositories. When you connect a repo:

1. The repo is cloned (or pulled if it already exists locally)
2. All `.md` files in the repository are indexed
3. Frontmatter is parsed and page metadata is stored in SQLite
4. The search index is built incrementally

Non-Markdown files are not indexed or displayed in the editor, but they remain in the git repository untouched.

### Importing from other platforms

DocPlatform works with any Markdown content. Here's how to migrate from common platforms:

| Source | Export method | Notes |
|---|---|---|
| **Docusaurus** | Direct copy | Already `.md`-based — copy your docs directory as-is, add frontmatter if missing |
| **GitBook** | JSON export → convert | Export via GitBook API, convert to Markdown |
| **Notion** | Markdown export | Export workspace as Markdown, restructure into a folder hierarchy |
| **Confluence** | HTML export → convert | Export spaces as HTML, convert to Markdown with pandoc or similar |
| **Wiki.js** | Database export | Export pages as Markdown from the admin panel |

**General migration steps:**

1. Export your content as Markdown files
2. Place them in a git repository
3. Add YAML frontmatter (at minimum, `title`) to each file
4. Connect the repository to DocPlatform
5. Run `docplatform rebuild --workspace {id}` to force a full reconciliation

DocPlatform's reconciler automatically discovers all `.md` files, parses their frontmatter, assigns ULIDs to pages missing an `id` field, and builds the search index.
