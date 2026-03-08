---
title: Déploiement binaire
description: Déployez DocPlatform en tant que binaire autonome sur n'importe quel serveur Linux ou macOS.
weight: 1
---

# Déploiement binaire

La méthode de déploiement la plus simple — téléchargez un binaire unique, exécutez-le sur votre serveur. Pas de dépendances d'exécution, pas de conteneurs, pas d'orchestrateur.

## Téléchargement

Obtenez la dernière version pour votre plateforme :

```bash
# Recommandé (détection automatique de la plateforme)
curl -fsSL https://valoryx.org/install.sh | sh

# Ou téléchargement manuel d'un binaire spécifique à la plateforme
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Ou téléchargement d'une version spécifique
curl -sLO https://github.com/Valoryx-org/releases/releases/download/v0.5.2/docplatform-linux-amd64
```

Plateformes disponibles :

| OS | Architecture | Binaire |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |
| Windows | amd64 | `docplatform-windows-amd64.exe` |

Archives (avec version) :

| OS | Architecture | Archive |
|---|---|---|
| Linux | amd64 | `docplatform_0.5.2_linux_amd64.tar.gz` |
| Linux | arm64 | `docplatform_0.5.2_linux_arm64.tar.gz` |
| macOS | amd64 (Intel) | `docplatform_0.5.2_darwin_amd64.tar.gz` |
| macOS | arm64 (Apple Silicon) | `docplatform_0.5.2_darwin_arm64.tar.gz` |
| Windows | amd64 | `docplatform_0.5.2_windows_amd64.zip` |

### Vérifier le téléchargement

Chaque version inclut un fichier de sommes de contrôle SHA-256 :

```bash
curl -sL https://github.com/Valoryx-org/releases/releases/latest/download/checksums.txt -o checksums.txt
sha256sum -c checksums.txt --ignore-missing
```

## Installation

Déplacez le binaire vers un emplacement standard :

```bash
sudo mv docplatform /usr/local/bin/
sudo chmod +x /usr/local/bin/docplatform
```

Vérification :

```bash
docplatform version
# docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
```

## Initialisation

```bash
# Créer un répertoire de données
sudo mkdir -p /var/lib/docplatform
cd /var/lib/docplatform

# Initialiser l'espace de travail
docplatform init \
  --workspace-name "Docs" \
  --slug docs
```

Pour connecter un dépôt git lors de l'initialisation :

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

## Configuration

Créez un fichier d'environnement :

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

## Exécuter en tant que service systemd

Créez un fichier d'unité systemd pour le démarrage automatique et le redémarrage :

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

Créez l'utilisateur de service :

```bash
sudo useradd -r -s /sbin/nologin -d /var/lib/docplatform docplatform
sudo chown -R docplatform:docplatform /var/lib/docplatform
```

Activez et démarrez :

```bash
sudo systemctl daemon-reload
sudo systemctl enable docplatform
sudo systemctl start docplatform
```

Vérifiez le statut :

```bash
sudo systemctl status docplatform
sudo journalctl -u docplatform -f  # Follow logs
```

## Reverse proxy

En production, placez DocPlatform derrière un reverse proxy pour la terminaison TLS, les domaines personnalisés et HTTP/2.

### Caddy (recommandé — TLS automatique)

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy provisionne et renouvelle automatiquement les certificats Let's Encrypt.

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

Lorsque vous utilisez un reverse proxy, définissez `HOST=127.0.0.1` pour que DocPlatform n'écoute que sur localhost.

## Mises à jour

```bash
# Télécharger la nouvelle version (recommandé)
curl -fsSL https://valoryx.org/install.sh | sh

# Ou téléchargement manuel
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Redémarrer
sudo systemctl restart docplatform
```

Les migrations de base de données s'exécutent automatiquement au démarrage. Des sauvegardes sont créées avant la migration si `BACKUP_ENABLED=true`.

## Retour en arrière

Si une mise à jour cause des problèmes :

1. Arrêtez le service : `sudo systemctl stop docplatform`
2. Remplacez le binaire par la version précédente
3. Restaurez la base de données depuis la sauvegarde : `cp /var/lib/docplatform/backups/{latest}.db /var/lib/docplatform/data.db`
4. Démarrez le service : `sudo systemctl start docplatform`
