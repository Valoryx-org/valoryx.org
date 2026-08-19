---
title: Binary Deployment
description: Deploy DocPlatform as a standalone binary on any Linux or macOS server.
weight: 1
---

# Binary Deployment

The simplest deployment method — download a single binary, run it on your server. No runtime dependencies, no containers, no orchestrator.

## Download

Get the latest release for your platform:

```bash
# Recommended (auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh

# Or download a specific platform binary manually
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Or download a specific version
curl -sLO https://github.com/Valoryx-org/releases/releases/download/v0.10.0/docplatform-linux-amd64
```

Available platforms:

| OS | Architecture | Binary |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |
| Windows | amd64 | `docplatform-windows-amd64.exe` |

Archives (with version):

| OS | Architecture | Archive |
|---|---|---|
| Linux | amd64 | `docplatform_0.10.0_linux_amd64.tar.gz` |
| Linux | arm64 | `docplatform_0.10.0_linux_arm64.tar.gz` |
| macOS | amd64 (Intel) | `docplatform_0.10.0_darwin_amd64.tar.gz` |
| macOS | arm64 (Apple Silicon) | `docplatform_0.10.0_darwin_arm64.tar.gz` |
| Windows | amd64 | `docplatform_0.10.0_windows_amd64.zip` |

### Verify the download

Each release includes a SHA-256 checksums file:

```bash
curl -sL https://github.com/Valoryx-org/releases/releases/latest/download/checksums.txt -o checksums.txt
sha256sum -c checksums.txt --ignore-missing
```

## Install

Move the binary to a standard location:

```bash
sudo mv docplatform /usr/local/bin/
sudo chmod +x /usr/local/bin/docplatform
```

Verify:

```bash
docplatform version
# docplatform <version> (commit: <sha>, built: <date>)
```

## Initialize

```bash
# Create a data directory
sudo mkdir -p /var/lib/docplatform
cd /var/lib/docplatform

# Initialize workspace
docplatform init \
  --workspace-name "Docs" \
  --slug docs
```

To connect a git repository at initialization:

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

> `docplatform init` is optional — the server initializes its database on first run, and registering through the web UI creates a starter workspace. CLI-created workspaces belong to a server-level default organization, not to web accounts (see [Your First Workspace](../getting-started/first-workspace.md)); for most deployments, create workspaces through the web UI after registering.

## Configure

Create an environment file:

```bash
sudo nano /etc/docplatform/.env
```

```bash
# /etc/docplatform/.env
PORT=3000
DATA_DIR=/var/lib/docplatform
GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
BACKUP_RETENTION_DAYS=30  # default is 7

# Optional: SMTP for emails
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_FROM=docs@example.com
# SMTP_USERNAME=docs@example.com
# SMTP_PASSWORD=your-app-password

# Optional: OIDC
# OIDC_GOOGLE_CLIENT_ID=...
# OIDC_GOOGLE_CLIENT_SECRET=...
```

## Run as a systemd service

Create a systemd unit file for automatic startup and restart:

```bash
sudo nano /etc/systemd/system/docplatform.service
```

```ini
[Unit]
Description=DocPlatform Documentation Server
After=network.target

[Service]
Type=simple
User=docplatform
Group=docplatform
WorkingDirectory=/var/lib/docplatform
EnvironmentFile=/etc/docplatform/.env
ExecStart=/usr/local/bin/docplatform serve
Restart=on-failure
RestartSec=5

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/docplatform

# Graceful shutdown
KillSignal=SIGTERM
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
```

Create the service user:

```bash
sudo useradd -r -s /sbin/nologin -d /var/lib/docplatform docplatform
sudo chown -R docplatform:docplatform /var/lib/docplatform
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable docplatform
sudo systemctl start docplatform
```

Check status:

```bash
sudo systemctl status docplatform
sudo journalctl -u docplatform -f  # Follow logs
```

## Reverse proxy

For production, place DocPlatform behind a reverse proxy for TLS termination, custom domains, and HTTP/2.

### Caddy (recommended — automatic TLS)

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy automatically provisions and renews Let's Encrypt certificates.

### nginx

```nginx
server {
    listen 443 ssl http2;
    server_name docs.yourcompany.com;

    ssl_certificate /etc/letsencrypt/live/docs.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docs.yourcompany.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

DocPlatform listens on all interfaces on `PORT` (there is no listen-address setting). When running behind a reverse proxy, use your firewall to block external access to port 3000 so only the proxy can reach it.

## Upgrades

**Stop the instance before replacing the binary** — overwriting a running binary fails on Linux with "Text file busy". Database migrations run automatically on the next startup, so upgrading is always stop → replace → start; check [the changelog](../reference/zz-changelog.md) for what's new (and any breaking changes) before you upgrade.

### Under systemd

```bash
# 1. Stop
sudo systemctl stop docplatform

# 2. Download the new version
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# 3. Start
sudo systemctl start docplatform
```

Keep `BACKUP_ENABLED=true` (the default) so daily backups are available if you need to roll back.

### Manual / desktop (no systemd)

If you're running DocPlatform directly rather than as a systemd service — a desktop install, or a manually-launched server — use the built-in `stop`/`serve` pair instead of finding and killing the process yourself:

```bash
# 1. Stop the running instance gracefully
docplatform stop

# 2. Replace the binary (same download step as above, adjusted for your platform —
#    see Installation for macOS/Windows). Overwrite in place, or move the new
#    binary over the old path.
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# 3. Start it again the same way you normally do
docplatform serve
```

`docplatform stop` waits for a graceful shutdown before returning, so step 2 is always safe to run immediately after it — see the [CLI reference](../reference/cli.md#docplatform-stop). If you later switch to a package manager (brew/scoop/winget), note that launching the binary from a different location resolves a *different* default data directory — set `DATA_DIR` explicitly if you want the packaged install to keep using your existing data; `docplatform doctor` tells you exactly where your current data lives.

## Rollback

If an upgrade causes issues:

1. Stop the service: `sudo systemctl stop docplatform`
2. Replace the binary with the previous version
3. Restore the database from backup: `cp /var/lib/docplatform/backups/{latest}.db /var/lib/docplatform/data.db`
4. Start the service: `sudo systemctl start docplatform`
