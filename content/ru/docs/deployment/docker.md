---
title: Развертывание Docker
description: Развертывание DocPlatform как Docker-контейнера с persistent volumes и конфигурацией окружения.
weight: 2
---

# Развертывание Docker

DocPlatform поставляется как мультиархитектурный Docker-образ (amd64/arm64) на базе Alpine Linux.

## Быстрый старт

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Откройте [http://localhost:3000](http://localhost:3000) и зарегистрируйте учетную запись администратора.

## Первый запуск

При первой загрузке DocPlatform автоматически:

1. Создает базу данных SQLite по адресу `/data/data.db`
2. Генерирует ключ подписи RS256 по адресу `/data/jwt-key.pem`
3. Инициализирует индекс полнотекстового поиска
4. Начинает слушать на порту 3000

Первый зарегистрированный пользователь становится **SuperAdmin** с полным доступом к платформе. Ручной шаг `init` не требуется — контейнер готов к использованию сразу.

```bash
# Verify the container started correctly
docker logs docplatform
# → INFO  Server starting            port=3000 version=v0.5.2
# → INFO  Database initialized       path=/data/data.db
# → INFO  Search index ready         documents=0
# → INFO  Listening on               http://0.0.0.0:3000
```

## Docker Compose

Для более удобного управления используйте Docker Compose:

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

## Детали образа

| Свойство | Значение |
|---|---|
| **Registry** | `ghcr.io/valoryx-org/docplatform` |
| **Базовый образ** | Alpine Linux 3.19 |
| **Архитектуры** | `linux/amd64`, `linux/arm64` |
| **Размер** | ~120 МБ в сжатом виде |
| **Пользователь** | Non-root (`docplatform`, UID 1000) |
| **Открытый порт** | 3000 |
| **Директория данных** | `/data` |

### Теги

| Тег | Описание |
|---|---|
| `latest` | Последний стабильный релиз |
| `v0.5.2` | Конкретная версия |
| `v0.5` | Последний патч для v0.5.x |

## Volumes

Примонтируйте persistent volume к `/data` для сохранения данных между перезапусками контейнера:

```bash
-v docplatform-data:/data
```

Директория `/data` содержит:

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

**Не пропускайте монтирование volume.** Без него все данные будут потеряны при удалении контейнера.

## Переменные окружения

Передавайте конфигурацию через флаги `-e`, `--env-file` или Docker Compose `environment`:

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

Или используйте файл env:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

Полный справочник смотрите в разделе [Переменные окружения](../configuration/environment.md).

## SSH-ключ для синхронизации git

Примонтируйте deploy key как read-only volume:

```bash
-v /path/to/deploy_key:/etc/docplatform/deploy_key:ro
-e GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
```

Убедитесь, что файл ключа имеет правильные права на хосте:

```bash
chmod 600 /path/to/deploy_key
```

## Проверки состояния

DocPlatform предоставляет endpoints для проверки состояния:

| Endpoint | Назначение |
|---|---|
| `GET /health` | Базовая проверка работоспособности (сервер работает) |
| `GET /ready` | Проверка готовности (база данных и поиск инициализированы) |

Используйте их для healthcheck Docker, проб балансировщика нагрузки или проб liveness/readiness оркестратора.

```bash
# Quick liveness check
curl -f http://localhost:3000/health
# → {"status":"ok"}

# Readiness check (database + search initialized)
curl -f http://localhost:3000/ready
# → {"status":"ok","database":"ok","search":"ok"}
```

## С reverse proxy

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

Caddy обрабатывает TLS автоматически через Let's Encrypt.

## Обновления

```bash
# Pull the latest image
docker pull ghcr.io/valoryx-org/docplatform:latest

# Recreate the container
docker compose up -d
```

Или с обычным Docker:

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

Данные в volume сохраняются при пересоздании контейнера.

## Сборка из исходного кода

Соберите собственный образ из Dockerfile:

```bash
cd Phase05/src
docker build -t docplatform:custom .
```

Dockerfile использует multi-stage сборку:

1. **Build stage** — компиляция Go с отключенным CGO
2. **Frontend stage** — статический экспорт Next.js
3. **Runtime stage** — Alpine Linux с скомпилированным бинарным файлом и статическими ресурсами

## Логи

```bash
# Follow container logs
docker logs -f docplatform

# Last 100 lines
docker logs --tail 100 docplatform
```

Логи структурированы в формате JSON с идентификаторами запросов для наблюдаемости.

## Резервное копирование и восстановление

### Ручное резервное копирование

```bash
# Copy the database from the container
docker cp docplatform:/data/data.db ./backup-$(date +%Y%m%d).db
```

### Автоматическое резервное копирование

Ежедневные резервные копии создаются автоматически внутри контейнера (включены по умолчанию). Они хранятся в `/data/backups/` и включены в volume.

### Восстановление

```bash
docker stop docplatform
docker cp ./backup-20250115.db docplatform:/data/data.db
docker start docplatform
```
