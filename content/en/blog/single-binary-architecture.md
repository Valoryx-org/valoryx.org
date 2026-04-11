---
title: "Why We Ship a Single Go Binary"
description: "DocPlatform is one binary with zero dependencies. No Docker, no Postgres, no Redis. Here's the architecture behind a 30-second install."
date: "2026-03-30"
author: "Valoryx Team"
tags: ["architecture", "golang", "self-hosted", "documentation"]
---

Most documentation platforms ship as a stack. You get a Node.js application, a PostgreSQL database, a Redis cache, an Elasticsearch cluster for search, and an Nginx reverse proxy to tie it all together. Five services, five things that can break, five things to monitor, patch, and upgrade.

DocPlatform ships as one file. Download it, run it, done.

This isn't a marketing trick. It's an architecture decision we made on day one, and every design choice since then flows from it. Here's why.

## The Typical Documentation Stack

Let's look at what you actually deploy when you set up a modern documentation platform:

```
┌─────────────┐
│   Nginx     │  ← reverse proxy, TLS termination
├─────────────┤
│   Node.js   │  ← application server
├─────────────┤
│  PostgreSQL │  ← content storage
├─────────────┤
│    Redis    │  ← session cache, job queue
├─────────────┤
│Elasticsearch│  ← full-text search
└─────────────┘
```

That's five processes, each with its own configuration files, version requirements, and failure modes. Docker Compose helps manage the orchestration, but it doesn't reduce the surface area. You still need to:

- Monitor each service for crashes and resource usage
- Run database migrations on upgrades
- Tune Elasticsearch heap sizes and index settings
- Handle Redis eviction policies when memory fills up
- Rotate Nginx logs and renew TLS certificates

For a Fortune 500 company with a platform team, this is routine. For a 10-person startup that just wants internal docs, it's overhead that never ends.

## What One Binary Looks Like

Here's the DocPlatform deployment:

```
┌──────────────────────────┐
│      docplatform          │  ← single Go binary
│  ┌────────┐ ┌──────────┐ │
│  │ SQLite │ │  Bleve   │ │
│  │  (DB)  │ │ (search) │ │
│  └────────┘ └──────────┘ │
└──────────────────────────┘
```

One binary. One data directory. SQLite handles content storage, sessions, and configuration. [Bleve](https://blevesearch.com/) handles full-text search. Both are embedded libraries compiled directly into the binary — no external processes, no network calls between services.

Installation takes 30 seconds:

```bash
curl -fsSL https://get.valoryx.org | sh
docplatform serve
```

That's it. No `docker-compose up`, no database initialization, no environment variables for connection strings. The binary creates its data directory on first run and starts serving on port 3000.

For more installation options, see the [install guide](/install/).

## Why Go Makes This Possible

We chose Go specifically because it enables this architecture. Three properties matter:

### Static Compilation

Go compiles to a single statically-linked binary. No runtime dependencies, no shared libraries, no JVM, no `node_modules`. The binary runs on a bare Linux server with nothing else installed.

```bash
# Cross-compile for Linux from any OS
GOOS=linux GOARCH=amd64 go build -o docplatform ./cmd/server/
```

That one command produces a binary you can `scp` to a server and run. Compare this with deploying a Node.js application, where you need to install Node, run `npm install`, hope the native dependencies compile correctly on the target architecture, and configure a process manager.

### Goroutines for Concurrency

A documentation platform needs to handle concurrent requests (page views, search queries, editor saves), run background jobs (git sync, search indexing), and manage WebSocket connections (real-time collaboration) — all simultaneously.

Go's goroutines make this cheap. Each WebSocket connection gets its own goroutine, costing roughly 2KB of memory. A Node.js server handling the same connections needs to manage them on a single event loop, or offload to worker threads with shared-memory complexity.

The git sync engine, which polls and reconciles changes between the web editor and git repositories, runs as a set of goroutines within the same process. No separate worker service, no job queue, no Redis.

### Embedded Databases

Both SQLite and Bleve are written in C and Go respectively, and both compile directly into the binary via `cgo` (SQLite) and pure Go (Bleve). This means:

- No database server to install, configure, or monitor
- No network latency between the application and its data
- Backups are file copies — `cp data.db data.db.bak`
- Upgrades preserve data automatically — the new binary reads the old data files

SQLite handles [billions of rows](https://www.sqlite.org/whentouse.html) in production at companies far larger than ours. For a documentation platform serving hundreds of concurrent users, it's more than enough.

## The Operational Advantage

The single-binary approach pays dividends in operations:

**Upgrades** are replacing one file. Stop the old binary, copy the new one, start it. No database migrations to worry about — the application handles schema changes on startup.

**Backups** are copying two files: the SQLite database and the Bleve index. Or just the database — the search index can be rebuilt from content.

**Monitoring** is watching one process. If it's running, everything is running. If it crashes, restart it. There's no partial failure where the database is up but search is down.

**Resource usage** is predictable. One process, one memory footprint. No surprise memory spikes from Elasticsearch's JVM heap or Redis accumulating keys.

**Security surface** is minimal. One binary, one listening port. No inter-service communication to secure, no Redis exposed on a network port, no Elasticsearch cluster with its own authentication layer. See our [security documentation](/security/) for the full model.

## Trade-offs We Accept

This architecture has limits, and we're honest about them:

**Vertical scaling only.** SQLite runs on one machine. You can't distribute the database across a cluster. For most documentation use cases — even large ones with thousands of pages — a single modern server handles the load easily. But if you need horizontal scaling across data centers, this isn't the right architecture.

**Single-writer for SQLite.** SQLite supports concurrent readers but serializes writes. In practice, documentation platforms are read-heavy (many page views, few edits), so this is rarely a bottleneck. But a team of 200 people all saving pages simultaneously would see some write contention.

**No component swapping.** You can't replace Bleve with Elasticsearch if you want more advanced search features. The search engine is embedded, not pluggable. We think the trade-off is worth it — Bleve supports stemming, fuzzy matching, and field boosting, which covers what documentation search needs.

## Deployment Examples

The single binary runs anywhere a Linux/macOS/Windows process can run:

**Bare metal or VM:**
```bash
# Download, run, done
curl -fsSL https://get.valoryx.org | sh
docplatform serve --port 3000
```

**Systemd service:**
```ini
[Unit]
Description=DocPlatform
After=network.target

[Service]
ExecStart=/opt/docplatform/bin/docplatform serve
WorkingDirectory=/opt/docplatform
Restart=always

[Install]
WantedBy=multi-user.target
```

**Docker (if you want it):**
```dockerfile
FROM scratch
COPY docplatform /docplatform
ENTRYPOINT ["/docplatform", "serve"]
```

Note the `FROM scratch` — since the binary has no dependencies, the Docker image contains literally nothing except the binary itself. The image is under 30MB.

For detailed deployment options, see the [binary deployment guide](/docs/deployment/binary/).

## What This Means for Your Team

Every additional service in your stack is a service someone has to understand, monitor, and fix at 2 AM when it breaks. Documentation infrastructure should fade into the background — it should be something you set up once and forget about.

A single binary that embeds everything it needs is the closest we've found to that ideal. No containers to orchestrate, no databases to tune, no search clusters to monitor. Just one file that runs your docs.

[Install DocPlatform](/install/) in 30 seconds and see for yourself. The Community Edition is free — unlimited users, unlimited pages, no time limit.
