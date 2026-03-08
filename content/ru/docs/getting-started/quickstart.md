---
title: Быстрый старт
description: Запустите DocPlatform менее чем за 5 минут с полностью функциональным workspace для документации.
weight: 1
---

# Быстрый старт

От нуля до работающей платформы документации менее чем за 5 минут. Это руководство описывает самый быстрый путь — для подробных вариантов смотрите руководство по [установке](installation.md).

## Шаг 1: Установка

```bash
# Recommended (auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh
```

Или скачайте вручную:

```bash
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform
```

Или с Docker:

```bash
docker run -d --name docplatform -p 3000:3000 -v docplatform-data:/data ghcr.io/valoryx-org/docplatform:latest
```

Если используете Docker, переходите к [шагу 3](#step-3-register-your-account) — контейнер инициализируется автоматически.

## Шаг 2: Инициализация workspace

```bash
docplatform init --workspace-name "My Docs" --slug my-docs
```

Это создает:

```
.docplatform/
├── data.db              # SQLite database
├── jwt-key.pem          # Auto-generated RS256 signing key
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Your documentation lives here
        └── .docplatform/
            └── config.yaml
```

### С git (опционально)

Подключение к существующему git-репозиторию при инициализации:

```bash
docplatform init \
  --workspace-name "My Docs" \
  --slug my-docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

DocPlatform клонирует репозиторий и начинает синхронизацию. Все существующие файлы `.md` автоматически индексируются.

## Шаг 3: Запуск сервера

```bash
docplatform serve
```

```
INFO  Server starting            port=3000 version=v0.5.2
INFO  Database initialized       path=.docplatform/data.db
INFO  Search index ready         documents=0
INFO  Workspace loaded           name="My Docs" slug=my-docs
INFO  Listening on               http://localhost:3000
```

Откройте [http://localhost:3000](http://localhost:3000) в браузере.

## Шаг 4: Регистрация учетной записи

Первый зарегистрированный пользователь автоматически становится **SuperAdmin** с полным доступом к платформе.

1. Нажмите **Create Account**
2. Введите имя, email и пароль
3. Вы вошли в систему и готовы к работе

> **Примечание по безопасности:** Механизм назначения первого пользователя администратором действует только при отсутствии пользователей. После первой регистрации новые учетные записи получают роль по умолчанию, настроенную для workspace.

## Шаг 5: Создание первой страницы

1. Нажмите **New Page** в боковой панели
2. Укажите заголовок — URL-slug генерируется автоматически из заголовка
3. Начните писать в редакторе
4. Изменения автоматически сохраняются каждые несколько секунд

Страница хранится как Markdown-файл в директории `docs/` вашего workspace. Если подключен git, изменения автоматически коммитятся и пушатся.

## Шаг 6: Попробуйте

Вот несколько действий, которые можно попробовать прямо сейчас:

| Действие | Как |
|---|---|
| **Переключиться на raw Markdown** | Нажмите переключатель `</>` на панели инструментов редактора |
| **Поиск** | Нажмите `Cmd+K` (или `Ctrl+K`), чтобы открыть мгновенный поиск |
| **Создать подстраницу** | Нажмите `+` рядом с существующей страницей в боковой панели |
| **Предпросмотр опубликованного сайта** | Перейдите по адресу `http://localhost:3000/p/my-docs/` |
| **Запустить диагностику** | Выполните `docplatform doctor` в терминале |

## Что дальше

| Цель | Руководство |
|---|---|
| Подключить git-репозиторий | [Интеграция с Git](../guides/git-integration.md) |
| Пригласить команду | [Команды и совместная работа](../guides/collaboration.md) |
| Опубликовать документацию | [Публикация](../guides/publishing.md) |
| Развернуть в production | [Развертывание](../deployment/binary.md) |
| Настроить провайдеры аутентификации | [Аутентификация](../configuration/authentication.md) |
