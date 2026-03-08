---
title: Розгортання Docker
description: Розгорніть DocPlatform як Docker контейнер із постійними томами та конфігурацією через змінні середовища.
weight: 2
---

# Розгортання Docker

DocPlatform постачається як мультиархітектурний Docker образ (amd64/arm64), побудований на Alpine Linux.

## Швидкий старт

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Відкрийте [http://localhost:3000](http://localhost:3000) та зареєструйте обліковий запис адміністратора.

## Перший запуск

При першому завантаженні DocPlatform автоматично:

1. Створює базу даних SQLite за адресою `/data/data.db`
2. Генерує ключ підпису RS256 за адресою `/data/jwt-key.pem`
3. Ініціалізує повнотекстовий пошуковий індекс
4. Починає прослуховувати порт 3000

Перший зареєстрований користувач стає **SuperAdmin** із повним доступом до платформи. Ручний крок `init` не потрібен — контейнер готовий до використання відразу.

```bash
# Verify the container started correctly
docker logs docplatform
# → INFO  Server starting            port=3000 version=v0.5.2
# → INFO  Database initialized       path=/data/data.db
# → INFO  Search index ready         documents=0
# → INFO  Listening on               http://0.0.0.0:3000
```

## Docker Compose

Для зручнішого управління використовуйте Docker Compose:

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

## Деталі образу

| Властивість | Значення |
|---|---|
| **Реєстр** | `ghcr.io/valoryx-org/docplatform` |
| **Базовий образ** | Alpine Linux 3.19 |
| **Архітектури** | `linux/amd64`, `linux/arm64` |
| **Розмір** | ~120 МБ стиснутий |
| **Користувач** | Non-root (`docplatform`, UID 1000) |
| **Відкритий порт** | 3000 |
| **Директорія даних** | `/data` |

### Теги

| Тег | Опис |
|---|---|
| `latest` | Найновіший стабільний реліз |
| `v0.5.2` | Конкретна версія |
| `v0.5` | Останній патч для v0.5.x |

## Томи

Підключіть постійний том до `/data` для збереження даних між перезапусками контейнера:

```bash
-v docplatform-data:/data
```

Директорія `/data` містить:

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

**Не пропускайте підключення тому.** Без нього всі дані втрачаються при видаленні контейнера.

## Змінні середовища

Передавайте конфігурацію через прапорці `-e`, `--env-file` або секцію `environment` Docker Compose:

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

Або використовуйте файл env:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

Див. [Змінні середовища](../configuration/environment.md) для повного довідника.

## SSH ключ для синхронізації git

Підключіть deploy key як том лише для читання:

```bash
-v /path/to/deploy_key:/etc/docplatform/deploy_key:ro
-e GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
```

Переконайтесь, що файл ключа має правильні дозволи на хості:

```bash
chmod 600 /path/to/deploy_key
```

## Перевірки стану

DocPlatform надає ендпоінти перевірки стану:

| Ендпоінт | Призначення |
|---|---|
| `GET /health` | Базова перевірка активності (сервер працює) |
| `GET /ready` | Перевірка готовності (база даних та пошук ініціалізовані) |

Використовуйте їх для Docker healthcheck, проб балансувальника навантаження або проб liveness/readiness оркестратора.

```bash
# Quick liveness check
curl -f http://localhost:3000/health
# → {"status":"ok"}

# Readiness check (database + search initialized)
curl -f http://localhost:3000/ready
# → {"status":"ok","database":"ok","search":"ok"}
```

## Зі зворотним проксі

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

Caddy автоматично обробляє TLS через Let's Encrypt.

## Оновлення

```bash
# Pull the latest image
docker pull ghcr.io/valoryx-org/docplatform:latest

# Recreate the container
docker compose up -d
```

Або зі звичайним Docker:

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

Дані в томі зберігаються між пересозданнями контейнера.

## Збірка зі сирцевого коду

Зберіть власний образ з Dockerfile:

```bash
cd Phase05/src
docker build -t docplatform:custom .
```

Dockerfile використовує багатоетапну збірку:

1. **Етап збірки** — компіляція Go з вимкненим CGO
2. **Етап фронтенду** — статичний експорт Next.js
3. **Етап виконання** — Alpine Linux із скомпільованим бінарним файлом та статичними ресурсами

## Логи

```bash
# Follow container logs
docker logs -f docplatform

# Last 100 lines
docker logs --tail 100 docplatform
```

Логи структуровані у форматі JSON із ідентифікаторами запитів для спостережуваності.

## Резервне копіювання та відновлення

### Ручне резервне копіювання

```bash
# Copy the database from the container
docker cp docplatform:/data/data.db ./backup-$(date +%Y%m%d).db
```

### Автоматичне резервне копіювання

Щоденні резервні копії створюються автоматично всередині контейнера (увімкнено за замовчуванням). Вони зберігаються в `/data/backups/` та включені в том.

### Відновлення

```bash
docker stop docplatform
docker cp ./backup-20250115.db docplatform:/data/data.db
docker start docplatform
```
