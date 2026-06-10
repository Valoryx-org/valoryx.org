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
- **Tags** (keyword field, boosted)
- **Page path**

### Matching behavior

Queries are plain keywords — there is no special operator syntax:

| Behavior | Example | Description |
|---|---|---|
| Keywords | `git sync` | Matches pages containing the terms across title, description, and body |
| Fuzzy matching | `gti snyc` | Typos within a small edit distance still match (title tolerates more than body) |
| Highlighting | — | Results include highlighted snippets showing where the match occurred |

## Permission filtering

Search is workspace-scoped: every query is constrained to the workspace it's issued against at the search-engine level, and the search endpoint requires read access to that workspace. There is no cross-workspace search.

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
docplatform rebuild --workspace {workspace-id} --search
```

This re-indexes the workspace's pages from the filesystem (the `--search` flag includes the search index in the rebuild).

### Index health

Check overall instance health (FS/DB consistency, broken wikilinks, backups, and more) with the doctor command:

```bash
docplatform doctor
```

If search results look stale or incomplete, rebuild the index with `docplatform rebuild --workspace {id} --search`.

## Search in published docs

Published documentation sites do **not** currently include a visitor-facing search interface — search is available to authenticated workspace members in the editor. For AI agents and crawlers, published sites expose `llms.txt` / `llms-full.txt` and `sitemap.xml` for content discovery instead.

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
| `tags` | Boosted (2.0x) | Keyword field — exact tag matches |
| `body` | Normal (1.0x) | Full page content |
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
