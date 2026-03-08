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
curl -sLO https://github.com/Valoryx-org/releases/releases/download/v0.5.2/docplatform-linux-amd64
```

Available platforms:

| OS | Architecture | Binary |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |

Archives (with version):

| OS | Architecture | Archive |
|---|---|---|
| Linux | amd64 | `docplatform_0.5.2_linux_amd64.tar.gz` |
| Linux | arm64 | `docplatform_0.5.2_linux_arm64.tar.gz` |
| macOS | amd64 (Intel) | `docplatform_0.5.2_darwin_amd64.tar.gz` |
| macOS | arm64 (Apple Silicon) | `docplatform_0.5.2_darwin_arm64.tar.gz` |
| Windows | amd64 | `docplatform_0.5.2_windows_amd64.zip` |

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
# docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
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
BACKUP_RETENTION_DAYS=30

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
TimeoutStopSec=30

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

When using a reverse proxy, set `HOST=127.0.0.1` so DocPlatform only listens on localhost.

## Upgrades

```bash
# Download new version (recommended)
curl -fsSL https://valoryx.org/install.sh | sh

# Or download manually
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Restart
sudo systemctl restart docplatform
```

Database migrations run automatically on startup. Backups are created before migration if `BACKUP_ENABLED=true`.

## Rollback

If an upgrade causes issues:

1. Stop the service: `sudo systemctl stop docplatform`
2. Replace the binary with the previous version
3. Restore the database from backup: `cp /var/lib/docplatform/backups/{latest}.db /var/lib/docplatform/data.db`
4. Start the service: `sudo systemctl start docplatform`
