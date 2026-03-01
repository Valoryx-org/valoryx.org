---
title: Развертывание бинарного файла
description: Развертывание DocPlatform как автономного бинарного файла на любом сервере Linux или macOS.
weight: 1
---

# Развертывание бинарного файла

Простейший способ развертывания — скачайте единый бинарный файл и запустите на сервере. Без runtime-зависимостей, контейнеров и оркестратора.

## Скачивание

Получите последний релиз для вашей платформы:

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

Доступные платформы:

| ОС | Архитектура | Бинарный файл |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |

Архивы (с версией):

| ОС | Архитектура | Архив |
|---|---|---|
| Linux | amd64 | `docplatform_0.5.0_linux_amd64.tar.gz` |
| Linux | arm64 | `docplatform_0.5.0_linux_arm64.tar.gz` |
| macOS | amd64 (Intel) | `docplatform_0.5.0_darwin_amd64.tar.gz` |
| macOS | arm64 (Apple Silicon) | `docplatform_0.5.0_darwin_arm64.tar.gz` |
| Windows | amd64 | `docplatform_0.5.0_windows_amd64.zip` |

### Проверка загрузки

Каждый релиз включает файл с контрольными суммами SHA-256:

```bash
curl -sL https://github.com/Valoryx-org/releases/releases/latest/download/checksums.txt -o checksums.txt
sha256sum -c checksums.txt --ignore-missing
```

## Установка

Переместите бинарный файл в стандартное расположение:

```bash
sudo mv docplatform /usr/local/bin/
sudo chmod +x /usr/local/bin/docplatform
```

Проверка:

```bash
docplatform version
# docplatform v0.5.0 (commit: abc1234, built: 2025-01-15T10:00:00Z)
```

## Инициализация

```bash
# Create a data directory
sudo mkdir -p /var/lib/docplatform
cd /var/lib/docplatform

# Initialize workspace
docplatform init \
  --workspace-name "Docs" \
  --slug docs
```

Для подключения git-репозитория при инициализации:

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

## Настройка

Создайте файл окружения:

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

## Запуск как сервис systemd

Создайте файл юнита systemd для автоматического запуска и перезапуска:

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

Создайте сервисного пользователя:

```bash
sudo useradd -r -s /sbin/nologin -d /var/lib/docplatform docplatform
sudo chown -R docplatform:docplatform /var/lib/docplatform
```

Включите и запустите:

```bash
sudo systemctl daemon-reload
sudo systemctl enable docplatform
sudo systemctl start docplatform
```

Проверьте статус:

```bash
sudo systemctl status docplatform
sudo journalctl -u docplatform -f  # Follow logs
```

## Reverse proxy

Для production-среды разместите DocPlatform за reverse proxy для TLS-терминации, пользовательских доменов и HTTP/2.

### Caddy (рекомендуется — автоматический TLS)

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy автоматически получает и обновляет сертификаты Let's Encrypt.

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

При использовании reverse proxy установите `HOST=127.0.0.1`, чтобы DocPlatform слушал только на localhost.

## Обновления

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

Миграции базы данных выполняются автоматически при запуске. Резервные копии создаются перед миграцией, если `BACKUP_ENABLED=true`.

## Откат

Если обновление вызвало проблемы:

1. Остановите сервис: `sudo systemctl stop docplatform`
2. Замените бинарный файл на предыдущую версию
3. Восстановите базу данных из резервной копии: `cp /var/lib/docplatform/backups/{latest}.db /var/lib/docplatform/data.db`
4. Запустите сервис: `sudo systemctl start docplatform`
