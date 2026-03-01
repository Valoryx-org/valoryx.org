---
title: Встановлення
description: Встановіть DocPlatform за допомогою готового бінарного файлу, Docker або зі сирцевого коду.
weight: 2
---

# Встановлення

DocPlatform постачається як єдиний бінарний файл без залежностей часу виконання. Оберіть спосіб встановлення, який відповідає вашому робочому процесу.

## Варіант 1: Готовий бінарний файл (рекомендовано)

Завантажте останній реліз для вашої платформи.

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

**Очікуваний результат:**

```
docplatform v0.5.0 (commit: abc1234, built: 2025-01-15T10:00:00Z)
```

### Ручне завантаження

Якщо ви бажаєте завантажити вручну, відвідайте сторінку [GitHub Releases](https://github.com/Valoryx-org/releases/releases). Бінарні файли доступні для:

| Платформа | Архітектура | Файл |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |

Кожен реліз містить контрольні суми SHA-256 для перевірки.

## Варіант 2: Docker

Запустіть DocPlatform як контейнер із постійними даними, що зберігаються у томі.

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Контейнер автоматично ініціалізується при першому запуску. Відкрийте [http://localhost:3000](http://localhost:3000), щоб розпочати.

### Docker Compose

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

Для виробничих Docker-розгортань див. [посібник з розгортання Docker](../deployment/docker.md).

## Варіант 3: Збірка зі сирцевого коду

Зберіть зі сирцевого коду, якщо хочете зробити внесок або запустити версію для розробки.

**Передумови:**

- Go 1.24+
- Node.js 20+ та pnpm (для збірки фронтенду)
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

### Режим розробки

Для гарячого перезавантаження під час розробки:

```bash
make dev
```

Це запускає Go сервер із живим перезавантаженням та Next.js dev сервер із HMR.

## Наступні кроки

Після встановлення DocPlatform перейдіть до:

1. **[Швидкий старт](quickstart.md)** — ініціалізуйте робочий простір та запустіть сервер двома командами
2. **[Ваш перший робочий простір](first-workspace.md)** — налаштуйте синхронізацію git, запросіть користувачів та налаштуйте параметри

## Видалення

### Бінарний файл

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
