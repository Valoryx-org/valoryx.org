---
title: Розгортання бінарного файлу
description: Розгорніть DocPlatform як автономний бінарний файл на будь-якому Linux або macOS сервері.
weight: 1
---

# Розгортання бінарного файлу

Найпростіший метод розгортання — завантажте один бінарний файл, запустіть його на сервері. Без залежностей часу виконання, без контейнерів, без оркестратора.

## Завантаження

Отримайте останній реліз для вашої платформи:

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

Доступні платформи:

| ОС | Архітектура | Бінарний файл |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |
| Windows | amd64 | `docplatform-windows-amd64.exe` |

Архіви (з версією):

| ОС | Архітектура | Архів |
|---|---|---|
| Linux | amd64 | `docplatform_0.5.2_linux_amd64.tar.gz` |
| Linux | arm64 | `docplatform_0.5.2_linux_arm64.tar.gz` |
| macOS | amd64 (Intel) | `docplatform_0.5.2_darwin_amd64.tar.gz` |
| macOS | arm64 (Apple Silicon) | `docplatform_0.5.2_darwin_arm64.tar.gz` |
| Windows | amd64 | `docplatform_0.5.2_windows_amd64.zip` |

### Перевірка завантаження

Кожен реліз включає файл контрольних сум SHA-256:

```bash
curl -sL https://github.com/Valoryx-org/releases/releases/latest/download/checksums.txt -o checksums.txt
sha256sum -c checksums.txt --ignore-missing
```

## Встановлення

Перемістіть бінарний файл до стандартного розташування:

```bash
sudo mv docplatform /usr/local/bin/
sudo chmod +x /usr/local/bin/docplatform
```

Перевірте:

```bash
docplatform version
# docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
```

## Ініціалізація

```bash
# Create a data directory
sudo mkdir -p /var/lib/docplatform
cd /var/lib/docplatform

# Initialize workspace
docplatform init \
  --workspace-name "Docs" \
  --slug docs
```

Для підключення git репозиторію при ініціалізації:

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

## Налаштування

Створіть файл середовища:

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

## Запуск як systemd сервіс

Створіть файл юніта systemd для автоматичного запуску та перезапуску:

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

Створіть користувача сервісу:

```bash
sudo useradd -r -s /sbin/nologin -d /var/lib/docplatform docplatform
sudo chown -R docplatform:docplatform /var/lib/docplatform
```

Увімкніть та запустіть:

```bash
sudo systemctl daemon-reload
sudo systemctl enable docplatform
sudo systemctl start docplatform
```

Перевірте стан:

```bash
sudo systemctl status docplatform
sudo journalctl -u docplatform -f  # Follow logs
```

## Зворотний проксі

Для виробництва розмістіть DocPlatform за зворотним проксі для TLS термінації, власних доменів та HTTP/2.

### Caddy (рекомендовано — автоматичний TLS)

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy автоматично отримує та оновлює сертифікати Let's Encrypt.

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

При використанні зворотного проксі встановіть `HOST=127.0.0.1`, щоб DocPlatform прослуховував лише localhost.

## Оновлення

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

Міграції бази даних виконуються автоматично при старті. Резервні копії створюються перед міграцією, якщо `BACKUP_ENABLED=true`.

## Відкат

Якщо оновлення спричиняє проблеми:

1. Зупиніть сервіс: `sudo systemctl stop docplatform`
2. Замініть бінарний файл попередньою версією
3. Відновіть базу даних із резервної копії: `cp /var/lib/docplatform/backups/{latest}.db /var/lib/docplatform/data.db`
4. Запустіть сервіс: `sudo systemctl start docplatform`
