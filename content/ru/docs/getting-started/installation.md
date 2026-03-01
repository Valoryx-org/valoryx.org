---
title: Установка
description: Установите DocPlatform с помощью готового бинарного файла, Docker или из исходного кода.
weight: 2
---

# Установка

DocPlatform поставляется как единый бинарный файл без runtime-зависимостей. Выберите способ установки, который подходит для вашего рабочего процесса.

## Вариант 1: Готовый бинарный файл (рекомендуется)

Скачайте последний релиз для вашей платформы.

### Linux / macOS

```bash
# Recommended (auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh

# Or download manually
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Verify the installation
docplatform version
```

**Ожидаемый вывод:**

```
docplatform v0.5.0 (commit: abc1234, built: 2025-01-15T10:00:00Z)
```

### Скачать вручную

Если вы предпочитаете скачать вручную, посетите страницу [GitHub Releases](https://github.com/Valoryx-org/releases/releases). Доступны бинарные файлы для:

| Платформа | Архитектура | Имя файла |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |

Каждый релиз включает контрольные суммы SHA-256 для проверки.

## Вариант 2: Docker

Запустите DocPlatform как контейнер с постоянным хранением данных в volume.

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Контейнер автоматически инициализируется при первом запуске. Откройте [http://localhost:3000](http://localhost:3000), чтобы начать работу.

### Docker Compose

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
    environment:
      - PORT=3000
      - DATA_DIR=/data
    restart: unless-stopped

volumes:
  docplatform-data:
```

```bash
docker compose up -d
```

Для промышленного развертывания Docker смотрите [руководство по развертыванию Docker](../deployment/docker.md).

## Вариант 3: Сборка из исходного кода

Соберите из исходного кода, если хотите внести свой вклад или запустить версию для разработки.

**Требования:**

- Go 1.24+
- Node.js 20+ и pnpm (для сборки фронтенда)
- Git
- Make

```bash
# Clone the repository
git clone https://github.com/Valoryx-org/docplatform.git
cd docplatform/Phase05/src

# Build the binary (compiles Go + embeds Next.js static export)
make build

# Verify
./docplatform version
```

### Режим разработки

Для горячей перезагрузки во время разработки:

```bash
make dev
```

Это запускает Go-сервер с live reload и dev-сервер Next.js с HMR.

## Следующие шаги

После установки DocPlatform перейдите к:

1. **[Быстрый старт](quickstart.md)** — инициализация workspace и запуск сервера в 2 команды
2. **[Ваш первый workspace](first-workspace.md)** — настройка синхронизации git, приглашение пользователей и кастомизация параметров

## Удаление

### Бинарный файл

```bash
# Remove the binary
sudo rm /usr/local/bin/docplatform

# Remove data (if you want a clean slate)
rm -rf .docplatform/
```

### Docker

```bash
docker stop docplatform && docker rm docplatform
docker volume rm docplatform-data  # removes all data
```
