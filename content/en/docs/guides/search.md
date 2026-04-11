---
title: Search
description: Instant full-text search across all your documentation with permission-filtered results.
weight: 6
---

# Search

DocPlatform includes an embedded full-text search engine (Bleve) that indexes all content automatically. No external service to configure — search works out of the box.

## Using search

### Cmd+K dialog

Press `Cmd+K` (macOS) or `Ctrl+K` (Windows/Linux) anywhere in the web editor to open the search dialog.

```
┌──────────────────────────────────────────┐
│  🔍  Search documentation...             │
├──────────────────────────────────────────┤
│                                          │
│  📄 Getting Started                      │
│     Install and configure DocPlatform... │
│                                          │
│  📄 API Authentication                   │
│     JWT tokens, OAuth2, and session...   │
│                                          │
│  📄 Docker Deployment                    │
│     Run DocPlatform as a container...    │
│                                          │
│  ↑↓ Navigate   ↵ Open   Esc Close       │
└──────────────────────────────────────────┘
```

### What's indexed

The search engine indexes:

- **Page title** (boosted weight for ranking)
- **Page description** (boosted weight)
- **Full page content** (body text, code blocks, lists, etc.)
- **Tags** (exact match boosting)
- **Frontmatter metadata**

### Search syntax

| Syntax | Example | Description |
|---|---|---|
| Keywords | `git sync` | Pages containing both "git" and "sync" |
| Exact phrase | `"bidirectional sync"` | Pages with the exact phrase |
| Prefix | `auth*` | Pages with words starting with "auth" |
| Tag filter | `tag:api` | Pages tagged with "api" |

## Permission filtering

Search results are automatically filtered based on the current user's permissions:

- **Workspace-scoped filtering** — results are limited to workspaces the user belongs to. This filtering happens at the search engine level.
- **Page-level access** — pages with `access` rules are filtered post-query based on the user's role. A Viewer cannot find restricted admin-only pages through search, even if the content matches their query.

## Indexing

### Automatic indexing

Content is indexed incrementally via an async job queue:

1. A page is created or updated (via editor or git sync)
2. Content Ledger emits an event
3. A search indexing job is queued
4. The Bleve indexer processes the job and updates the index

There's a brief delay (typically under 1 second) between saving a page and the updated content appearing in search results.

### Rebuild the search index

If the search index gets out of sync (rare — usually after a crash or manual file manipulation), rebuild it:

```bash
docplatform rebuild
```

This drops the existing search index and re-indexes all pages from the filesystem. The process runs in the background — the server remains available during rebuild.

### Index health

Check search index health with the doctor command:

```bash
docplatform doctor
```

The doctor reports:

- Number of indexed documents vs. database page count
- Orphaned index entries (indexed but no matching page)
- Missing index entries (page exists but not indexed)
- Index file size and last update timestamp

## Search in published docs

Published documentation sites include a search interface for visitors. The search input appears in the site header and uses the same Bleve engine.

Public site search is scoped to published pages only — unpublished or restricted content never appears in public search results.

## Search engine internals

For users who want to understand how search works under the hood:

### Analyzer

Bleve uses the **English analyzer** by default, which includes:

- **Tokenization** — splits text on whitespace and punctuation
- **Lowercasing** — case-insensitive matching
- **Stop word removal** — filters common words (the, is, at, etc.)
- **Stemming** — matches word variants (running → run, documented → document)

### Field boosting

Not all fields are weighted equally in relevance scoring:

| Field | Weight | Description |
|---|---|---|
| `title` | High (3.0x) | Page title (most relevant signal) |
| `description` | Medium (1.5x) | Page description / summary |
| `tags` | Exact match | Keyword field — exact tag matches boosted |
| `body` | Normal | Full page content |
| `path` | Keyword | File path — exact match only |

This means a query matching a page's title ranks higher than the same query matching deep in the body text.

### Storage

The Bleve index is stored at `{DATA_DIR}/search-index/` using the Bleve scorch storage engine (backed by bbolt). The index is separate from the SQLite database and can be safely deleted and rebuilt with `docplatform rebuild`.

## Performance

| Metric | Value |
|---|---|
| **Query latency** | < 8ms (p99) |
| **Index size** | ~1 KB per page (approximate) |
| **Max tested corpus** | 1,000 pages |
| **Concurrent queries** | Supported (thread-safe) |
| **Indexing latency** | < 1 second after save (async) |

Search performance scales linearly with content volume. For workspaces exceeding 10,000 pages, a future release will offer optional Meilisearch integration.
