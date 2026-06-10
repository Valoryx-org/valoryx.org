---
title: Production Checklist
description: Everything you need to verify before running DocPlatform in a production environment.
weight: 3
---

# Production Checklist

Use this checklist before deploying DocPlatform to a production environment. Each item links to the relevant documentation section.

## Required

These items are necessary for a secure, reliable production deployment.

### Server

- [ ] **Persistent storage configured** — Mount a volume or use a stable filesystem path for `DATA_DIR`. Loss of this directory means loss of all data.
- [ ] **Process manager in place** — Use systemd, Docker with `restart: unless-stopped`, or a container orchestrator to ensure the server restarts after crashes or reboots.
- [ ] **Port accessible** — Ensure the configured `PORT` (default: 3000) is reachable from your network or reverse proxy.
- [ ] **Sufficient resources** — Minimum 128 MB RAM, 200 MB disk. Recommended 512 MB RAM, 1 GB disk.

### Security

- [ ] **TLS enabled** — Run behind a reverse proxy (Caddy, nginx, cloud load balancer) with HTTPS. DocPlatform does not terminate TLS itself.
- [ ] **JWT key secured** — The `jwt-private.pem` file grants the ability to forge authentication tokens. Restrict filesystem permissions: `chmod 600`.
- [ ] **Production mode enabled** — Set `DOCPLATFORM_ENV=production` to turn on strict configuration validation.
- [ ] **API key pepper set** — `API_KEY_PEPPER` is required in production mode; it strengthens API-key hashing.
- [ ] **Git token encryption key set** — If you'll connect git providers with access tokens, set `GIT_ENCRYPTION_KEY` (min 16 chars) so tokens are encrypted at rest.
- [ ] **Firewall the app port** — If using a reverse proxy on the same host, block external access to port 3000 so DocPlatform is only reachable through the proxy (there is no listen-address setting).

### Backups

- [ ] **Backups enabled** — `BACKUP_ENABLED=true` (default). Verify backups are being created in `{DATA_DIR}/backups/`.
- [ ] **Backup retention set** — `BACKUP_RETENTION_DAYS` configured to your policy (default: 7 days).
- [ ] **Off-server backup** — Copy backup files to a separate location (S3, NFS, another server). On-disk backups don't protect against disk failure.

## Recommended

These items improve reliability, security, and team experience.

### Authentication

- [ ] **OIDC configured** — If your team uses Google or GitHub, enable OIDC sign-in to delegate password management. See [Authentication](../configuration/authentication.md).
- [ ] **SMTP configured** — Enable email for workspace invitations and password reset. Without SMTP, tokens print to stdout. See [Environment Variables](../configuration/environment.md).

### Git

- [ ] **SSH deploy key provisioned** — For private repositories, generate a dedicated deploy key with write access. See [Git Integration](../guides/git-integration.md).
- [ ] **Webhook configured** — For near-instant sync, set up a push webhook in your git hosting provider. Polling (default: 5 minutes) works but adds delay.
- [ ] **Git installed on host** — While go-git handles most operations, native git CLI is needed for large repositories (>1 GB).

### Monitoring

- [ ] **Health endpoint monitored** — Poll `GET /api/health` from your monitoring system (Uptime Robot, Prometheus blackbox exporter, etc.).
- [ ] **Logs collected** — DocPlatform outputs JSON-structured logs to stdout. Forward them to your log aggregator (ELK, Datadog, CloudWatch).
- [ ] **Disk usage monitored** — SQLite databases and search indexes grow with content. Alert when disk usage exceeds 80%.

### Operations

- [ ] **`docplatform doctor` run** — Execute `docplatform doctor` after initial setup to verify FS/DB consistency, search health, and broken links.
- [ ] **Update process documented** — Document how your team upgrades DocPlatform (binary replacement + restart, or Docker pull + recreate).
- [ ] **Rollback plan in place** — Keep the previous binary version and know how to restore from a database backup.

## Community Edition resource limits

Community Edition includes the following hardcoded limits:

| Resource | Limit |
|---|---|
| Users with Editor role or above | Unlimited |
| Workspaces | Unlimited |
| Viewers and Commenters | Unlimited |
| Pages per workspace | Unlimited |

Community Edition is fully unlimited — no artificial caps on editors, workspaces, or pages.

## Scaling considerations

DocPlatform Community Edition runs as a single instance with a single-writer SQLite database. This is the correct architecture for the target scale:

| Metric | Tested limit |
|---|---|
| **Pages** | 1,000 |
| **Concurrent users** | 50 |
| **Workspaces** | 10 |
| **Page render latency** | < 50ms (p99) |
| **Search latency** | < 50ms (p99) |
| **Memory usage** | < 200 MB under load |

If you need to scale beyond these limits, future editions will support multi-instance deployment, external databases, and Meilisearch.

## Security hardening

### Network

- Run behind a reverse proxy with TLS
- Use firewall rules so only the reverse proxy can reach the app port
- **WebSocket proxy** — ensure your reverse proxy supports WebSocket upgrade. Without it, real-time presence and live updates won't work. Both Caddy and nginx (with `proxy_http_version 1.1` and `Upgrade` headers) support this.

### Response headers

DocPlatform sets security headers automatically:

| Header | Value |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `Content-Security-Policy` | Set per surface (API, published sites, and the SPA each get an appropriate nonce-based policy) |

`HSTS` and `X-Frame-Options` are intentionally left to the reverse proxy — configure them there (Caddy and nginx both make this a one-liner).

### Filesystem

- Run as a dedicated non-root user (systemd: `User=docplatform`)
- Restrict data directory permissions: `chmod 700 {DATA_DIR}`
- Restrict JWT key permissions: `chmod 600 {DATA_DIR}/jwt-private.pem`

### Authentication

- Enable OIDC to reduce locally-stored credentials
- Use strong passwords (DocPlatform uses argon2id — resistant to brute force; repeated failures trigger a 15-minute lockout)
- Have users review their active sessions periodically (Profile → Sessions)

### Updates

- Subscribe to GitHub releases for security updates
- Update promptly when security patches are released
- Run `docplatform doctor` after every upgrade

## Example: minimal production setup

```bash
# 1. Install
sudo mv docplatform /usr/local/bin/

# 2. Create service user and data directory
sudo useradd -r -s /sbin/nologin docplatform
sudo mkdir -p /var/lib/docplatform
sudo chown docplatform:docplatform /var/lib/docplatform

# 3. Configure environment
sudo mkdir -p /etc/docplatform
sudo tee /etc/docplatform/.env <<EOF
PORT=3000
DATA_DIR=/var/lib/docplatform
DOCPLATFORM_ENV=production
API_KEY_PEPPER=$(openssl rand -hex 32)
BACKUP_RETENTION_DAYS=30
EOF
sudo chmod 600 /etc/docplatform/.env

# 4. Create systemd service (see Binary Deployment guide)
# 5. Set up reverse proxy with TLS (see Binary Deployment guide)

# 6. Start and verify
sudo systemctl enable --now docplatform
docplatform doctor

# 7. Register your account at https://docs.yourcompany.com
#    (registration creates your organization + starter workspace)
```
