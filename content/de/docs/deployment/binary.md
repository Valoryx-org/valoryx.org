---
title: Binary-Deployment
description: Deployen Sie DocPlatform als eigenständige Binärdatei auf einem beliebigen Linux- oder macOS-Server.
weight: 1
---

# Binary-Deployment

Die einfachste Deployment-Methode — eine einzelne Binärdatei herunterladen und auf Ihrem Server ausführen. Keine Runtime-Abhängigkeiten, keine Container, kein Orchestrator.

## Herunterladen

Laden Sie die neueste Version für Ihre Plattform herunter:

```bash
# Empfohlen (erkennt die Plattform automatisch)
curl -fsSL https://valoryx.org/install.sh | sh

# Oder eine spezifische Plattform-Binärdatei manuell herunterladen
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Oder eine spezifische Version herunterladen
curl -sLO https://github.com/Valoryx-org/releases/releases/download/v0.5.2/docplatform-linux-amd64
```

Verfügbare Plattformen:

| Betriebssystem | Architektur | Binärdatei |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |
| Windows | amd64 | `docplatform-windows-amd64.exe` |

Archive (mit Version):

| Betriebssystem | Architektur | Archiv |
|---|---|---|
| Linux | amd64 | `docplatform_0.5.2_linux_amd64.tar.gz` |
| Linux | arm64 | `docplatform_0.5.2_linux_arm64.tar.gz` |
| macOS | amd64 (Intel) | `docplatform_0.5.2_darwin_amd64.tar.gz` |
| macOS | arm64 (Apple Silicon) | `docplatform_0.5.2_darwin_arm64.tar.gz` |
| Windows | amd64 | `docplatform_0.5.2_windows_amd64.zip` |

### Download verifizieren

Jedes Release enthält eine SHA-256-Prüfsummendatei:

```bash
curl -sL https://github.com/Valoryx-org/releases/releases/latest/download/checksums.txt -o checksums.txt
sha256sum -c checksums.txt --ignore-missing
```

## Installieren

Verschieben Sie die Binärdatei an einen Standardort:

```bash
sudo mv docplatform /usr/local/bin/
sudo chmod +x /usr/local/bin/docplatform
```

Überprüfen:

```bash
docplatform version
# docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
```

## Initialisieren

```bash
# Datenverzeichnis erstellen
sudo mkdir -p /var/lib/docplatform
cd /var/lib/docplatform

# Workspace initialisieren
docplatform init \
  --workspace-name "Docs" \
  --slug docs
```

Um ein Git-Repository bei der Initialisierung zu verbinden:

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

## Konfigurieren

Erstellen Sie eine Umgebungsdatei:

```bash
sudo nano /etc/docplatform/.env
```

```bash
# /etc/docplatform/.env
PORT=3000
DATA_DIR=/var/lib/docplatform
GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
BACKUP_RETENTION_DAYS=30

# Optional: SMTP für E-Mails
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_FROM=docs@example.com
# SMTP_USERNAME=docs@example.com
# SMTP_PASSWORD=your-app-password

# Optional: OIDC
# OIDC_GOOGLE_CLIENT_ID=...
# OIDC_GOOGLE_CLIENT_SECRET=...
```

## Als systemd-Dienst ausführen

Erstellen Sie eine systemd-Unit-Datei für automatischen Start und Neustart:

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

# Sicherheitshärtung
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/docplatform

# Kontrolliertes Herunterfahren
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

Dienstbenutzer erstellen:

```bash
sudo useradd -r -s /sbin/nologin -d /var/lib/docplatform docplatform
sudo chown -R docplatform:docplatform /var/lib/docplatform
```

Aktivieren und starten:

```bash
sudo systemctl daemon-reload
sudo systemctl enable docplatform
sudo systemctl start docplatform
```

Status prüfen:

```bash
sudo systemctl status docplatform
sudo journalctl -u docplatform -f  # Logs verfolgen
```

## Reverse Proxy

Für die Produktion stellen Sie DocPlatform hinter einen Reverse Proxy für TLS-Terminierung, eigene Domains und HTTP/2.

### Caddy (empfohlen — automatisches TLS)

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy stellt automatisch Let's-Encrypt-Zertifikate bereit und erneuert sie.

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

        # WebSocket-Unterstützung
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Bei Verwendung eines Reverse Proxy setzen Sie `HOST=127.0.0.1`, damit DocPlatform nur auf localhost lauscht.

## Upgrades

```bash
# Neue Version herunterladen (empfohlen)
curl -fsSL https://valoryx.org/install.sh | sh

# Oder manuell herunterladen
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Neustart
sudo systemctl restart docplatform
```

Datenbankmigrationen werden beim Start automatisch ausgeführt. Backups werden vor der Migration erstellt, wenn `BACKUP_ENABLED=true`.

## Rollback

Wenn ein Upgrade Probleme verursacht:

1. Dienst stoppen: `sudo systemctl stop docplatform`
2. Binärdatei durch die vorherige Version ersetzen
3. Datenbank aus Backup wiederherstellen: `cp /var/lib/docplatform/backups/{latest}.db /var/lib/docplatform/data.db`
4. Dienst starten: `sudo systemctl start docplatform`
