---
title: Docker Deployment
description: Deploy DocPlatform as a Docker container with persistent volumes and environment configuration.
weight: 2
---

# Docker Deployment

DocPlatform ships as a multi-architecture Docker image (amd64/arm64) built on Alpine Linux.

## Quick start

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Open [http://localhost:3000](http://localhost:3000) and register your admin account.

## Docker Compose

For easier management, use Docker Compose:

```yaml
# docker-compose.yml
services:
  docplatform:
    image: ghcr.io/valoryx-org/docplatform:latest
    container_name: docplatform
    ports:
      - "3000:3000"
    volumes:
      - docplatform-data:/data
      - ./deploy_key:/etc/docplatform/deploy_key:ro
    environment:
      - DATA_DIR=/data
      - PORT=3000
      - GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
      - BACKUP_RETENTION_DAYS=30
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  docplatform-data:
```

```bash
docker compose up -d
```

## Image details

| Property | Value |
|---|---|
| **Registry** | `ghcr.io/valoryx-org/docplatform` |
| **Base image** | Alpine Linux 3.19 |
| **Architectures** | `linux/amd64`, `linux/arm64` |
| **Size** | ~120 MB compressed |
| **User** | Non-root (`docplatform`, UID 1000) |
| **Exposed port** | 3000 |
| **Data directory** | `/data` |

### Tags

| Tag | Description |
|---|---|
| `latest` | Most recent stable release |
| `v0.5.0` | Specific version |
| `v0.5` | Latest patch for v0.5.x |

## Volumes

Mount a persistent volume at `/data` to preserve data across container restarts:

```bash
-v docplatform-data:/data
```

The `/data` directory contains:

```
/data/
├── data.db              # SQLite database
├── jwt-key.pem          # Auto-generated RS256 signing key
├── backups/             # Daily backup files
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Markdown files
        ├── .git/        # Git repository (if connected)
        └── .docplatform/
            └── config.yaml
```

**Do not skip the volume mount.** Without it, all data is lost when the container is removed.

## Environment variables

Pass configuration via `-e` flags, `--env-file`, or Docker Compose `environment`:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  -e DATA_DIR=/data \
  -e SMTP_HOST=smtp.example.com \
  -e SMTP_PORT=587 \
  -e SMTP_FROM=docs@example.com \
  -e SMTP_USERNAME=docs@example.com \
  -e SMTP_PASSWORD=app-password \
  -e OIDC_GOOGLE_CLIENT_ID=your-client-id \
  -e OIDC_GOOGLE_CLIENT_SECRET=your-client-secret \
  ghcr.io/valoryx-org/docplatform:latest
```

Or use an env file:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

See [Environment Variables](../configuration/environment.md) for the complete reference.

## SSH key for git sync

Mount your deploy key as a read-only volume:

```bash
-v /path/to/deploy_key:/etc/docplatform/deploy_key:ro
-e GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
```

Ensure the key file has correct permissions on the host:

```bash
chmod 600 /path/to/deploy_key
```

## Health checks

DocPlatform exposes health endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Basic liveness check (server is running) |
| `GET /ready` | Readiness check (database and search are initialized) |

Use these for Docker healthchecks, load balancer probes, or orchestrator liveness/readiness probes.

## With a reverse proxy

### Caddy + Docker Compose

```yaml
services:
  docplatform:
    image: ghcr.io/valoryx-org/docplatform:latest
    volumes:
      - docplatform-data:/data
    environment:
      - DATA_DIR=/data
      - HOST=0.0.0.0
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config
    restart: unless-stopped

volumes:
  docplatform-data:
  caddy-data:
  caddy-config:
```

```
# Caddyfile
docs.yourcompany.com {
    reverse_proxy docplatform:3000
}
```

Caddy handles TLS automatically via Let's Encrypt.

## Upgrades

```bash
# Pull the latest image
docker pull ghcr.io/valoryx-org/docplatform:latest

# Recreate the container
docker compose up -d
```

Or with plain Docker:

```bash
docker pull ghcr.io/valoryx-org/docplatform:latest
docker stop docplatform
docker rm docplatform
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Data in the volume persists across container recreations.

## Build from source

Build your own image from the Dockerfile:

```bash
cd Phase05/src
docker build -t docplatform:custom .
```

The Dockerfile uses a multi-stage build:

1. **Build stage** — Go compilation with CGO disabled
2. **Frontend stage** — Next.js static export
3. **Runtime stage** — Alpine Linux with the compiled binary and static assets

## Logs

```bash
# Follow container logs
docker logs -f docplatform

# Last 100 lines
docker logs --tail 100 docplatform
```

Logs are JSON-structured with request IDs for observability.

## Backup and restore

### Manual backup

```bash
# Copy the database from the container
docker cp docplatform:/data/data.db ./backup-$(date +%Y%m%d).db
```

### Automated backups

Daily backups run automatically inside the container (enabled by default). They're stored in `/data/backups/` and included in the volume.

### Restore

```bash
docker stop docplatform
docker cp ./backup-20250115.db docplatform:/data/data.db
docker start docplatform
```
