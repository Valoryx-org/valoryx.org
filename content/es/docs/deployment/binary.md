---
title: Despliegue con binario
description: Despliegue DocPlatform como un binario independiente en cualquier servidor Linux o macOS.
weight: 1
---

# Despliegue con binario

El método de despliegue más simple — descargue un único binario, ejecútelo en su servidor. Sin dependencias de runtime, sin contenedores, sin orquestador.

## Descarga

Obtenga la última versión para su plataforma:

```bash
# Recommended (auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh

# Or download a specific platform binary manually
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Or download a specific version
curl -sLO https://github.com/Valoryx-org/releases/releases/download/v0.5.0/docplatform-linux-amd64
```

Plataformas disponibles:

| SO | Arquitectura | Binario |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |

Archivos (con versión):

| SO | Arquitectura | Archivo |
|---|---|---|
| Linux | amd64 | `docplatform_0.5.0_linux_amd64.tar.gz` |
| Linux | arm64 | `docplatform_0.5.0_linux_arm64.tar.gz` |
| macOS | amd64 (Intel) | `docplatform_0.5.0_darwin_amd64.tar.gz` |
| macOS | arm64 (Apple Silicon) | `docplatform_0.5.0_darwin_arm64.tar.gz` |
| Windows | amd64 | `docplatform_0.5.0_windows_amd64.zip` |

### Verificar la descarga

Cada versión incluye un archivo de sumas de verificación SHA-256:

```bash
curl -sL https://github.com/Valoryx-org/releases/releases/latest/download/checksums.txt -o checksums.txt
sha256sum -c checksums.txt --ignore-missing
```

## Instalar

Mueva el binario a una ubicación estándar:

```bash
sudo mv docplatform /usr/local/bin/
sudo chmod +x /usr/local/bin/docplatform
```

Verifique:

```bash
docplatform version
# docplatform v0.5.0 (commit: abc1234, built: 2025-01-15T10:00:00Z)
```

## Inicializar

```bash
# Create a data directory
sudo mkdir -p /var/lib/docplatform
cd /var/lib/docplatform

# Initialize workspace
docplatform init \
  --workspace-name "Docs" \
  --slug docs
```

Para conectar un repositorio git en la inicialización:

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

## Configurar

Cree un archivo de entorno:

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

## Ejecutar como servicio systemd

Cree un archivo de unidad systemd para inicio automático y reinicio:

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

Cree el usuario del servicio:

```bash
sudo useradd -r -s /sbin/nologin -d /var/lib/docplatform docplatform
sudo chown -R docplatform:docplatform /var/lib/docplatform
```

Habilite e inicie:

```bash
sudo systemctl daemon-reload
sudo systemctl enable docplatform
sudo systemctl start docplatform
```

Verifique el estado:

```bash
sudo systemctl status docplatform
sudo journalctl -u docplatform -f  # Follow logs
```

## Reverse proxy

Para producción, coloque DocPlatform detrás de un reverse proxy para terminación TLS, dominios personalizados y HTTP/2.

### Caddy (recomendado — TLS automático)

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy aprovisiona y renueva certificados Let's Encrypt automáticamente.

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

Cuando use un reverse proxy, establezca `HOST=127.0.0.1` para que DocPlatform solo escuche en localhost.

## Actualizaciones

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

Las migraciones de base de datos se ejecutan automáticamente al iniciar. Las copias de seguridad se crean antes de la migración si `BACKUP_ENABLED=true`.

## Reversión

Si una actualización causa problemas:

1. Detenga el servicio: `sudo systemctl stop docplatform`
2. Reemplace el binario con la versión anterior
3. Restaure la base de datos desde una copia de seguridad: `cp /var/lib/docplatform/backups/{latest}.db /var/lib/docplatform/data.db`
4. Inicie el servicio: `sudo systemctl start docplatform`
