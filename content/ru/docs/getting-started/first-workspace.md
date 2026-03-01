---
title: Ваш первый workspace
description: Создайте и настройте workspace для документации — подключите git, настройте структуру контента и пригласите команду.
weight: 3
---

# Ваш первый workspace

Workspace — это контейнер верхнего уровня для проекта документации. Каждый workspace соответствует директории с Markdown-файлами и опционально синхронизируется с git-репозиторием.

## Концепции workspace

| Концепция | Описание |
|---|---|
| **Workspace** | Проект документации, содержащий страницы, участников и настройки |
| **Page** | Markdown-файл с YAML frontmatter (заголовок, описание, теги, доступ) |
| **Slug** | URL-безопасный идентификатор workspace (например, `my-docs` -> `/p/my-docs/`) |
| **Member** | Пользователь с ролью в workspace (от Viewer до WorkspaceAdmin) |

## Создание workspace

### Через CLI

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs
```

### Через веб-интерфейс

1. Войдите как SuperAdmin или WorkspaceAdmin
2. Откройте переключатель workspace (выпадающий список вверху слева)
3. Нажмите **Create Workspace**
4. Введите имя и slug
5. Опционально настройте удаленный git-репозиторий

## Подключение git-репозитория

Двунаправленная синхронизация поддерживает файлы workspace и удаленный git-репозиторий в актуальном состоянии.

### При инициализации

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs \
  --git-url git@github.com:your-org/eng-docs.git \
  --branch main
```

### После создания

Обновите конфигурацию workspace по адресу `.docplatform/workspaces/{id}/.docplatform/config.yaml`:

```yaml
git_remote: git@github.com:your-org/eng-docs.git
git_branch: main
git_auto_commit: true
sync_interval: 300  # seconds
```

Затем перезапустите сервер или запустите ручную синхронизацию через веб-интерфейс.

### Настройка SSH-ключа

Для приватных репозиториев DocPlatform использует выделенный SSH deploy key:

```bash
# Generate a deploy key (no passphrase)
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""

# Add the public key to your repository's deploy keys
cat ~/.ssh/docplatform_deploy_key.pub
# → Copy this to GitHub/GitLab Settings → Deploy Keys (enable write access)
```

Установите переменную окружения:

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

### Как работает синхронизация

```
┌─────────────┐     auto-commit + push      ┌──────────────┐
│ Web Editor   │ ──────────────────────────► │ Remote Repo  │
│ (browser)    │                             │ (GitHub, etc)│
│              │ ◄────────────────────────── │              │
└─────────────┘     polling / webhook        └──────────────┘
```

**Web -> Git:** При сохранении в редакторе DocPlatform записывает файл `.md`, автоматически коммитит с описательным сообщением и пушит в удаленный репозиторий.

**Git -> Web:** DocPlatform опрашивает удаленный репозиторий (по умолчанию: каждые 5 минут) или слушает webhook. Новые коммиты подтягиваются, и веб-интерфейс обновляется в реальном времени через WebSocket.

**Конфликты:** Если обе стороны изменяют один и тот же файл между синхронизациями, DocPlatform обнаруживает коллизию с помощью хешей контента, возвращает HTTP 409 и делает обе версии доступными для скачивания, чтобы можно было разрешить конфликт вручную.

## Организация контента

### Иерархия страниц

Страницы могут быть вложены на любую глубину. Структура файлов в `docs/` напрямую соответствует структуре URL:

```
docs/
├── index.md                → /p/eng-docs/
├── getting-started.md      → /p/eng-docs/getting-started
├── api/
│   ├── index.md            → /p/eng-docs/api/
│   ├── authentication.md   → /p/eng-docs/api/authentication
│   └── endpoints.md        → /p/eng-docs/api/endpoints
└── guides/
    ├── deployment.md       → /p/eng-docs/guides/deployment
    └── contributing.md     → /p/eng-docs/guides/contributing
```

### Frontmatter

Каждая страница начинается с блока YAML frontmatter:

```yaml
---
title: Authentication
description: How to authenticate with the API using JWT tokens.
tags: [api, auth, jwt]
published: true
access: public        # public, workspace, restricted
allowed_roles: []     # only used when access: restricted
---
```

Поле `title` является обязательным. Все остальные поля опциональны и имеют разумные значения по умолчанию.

## Приглашение команды

### Через веб-интерфейс

1. Откройте **Workspace Settings** -> **Members**
2. Нажмите **Invite**
3. Введите email-адрес приглашаемого
4. Выберите роль (Viewer, Commenter, Editor, Admin)
5. Нажмите **Send Invitation**

Если настроен SMTP, приглашение отправляется по email. В противном случае отображается ссылка-приглашение для совместного использования.

### Роли

| Роль | Просмотр | Комментирование | Редактирование | Управление участниками | Управление workspace |
|---|---|---|---|---|---|
| **Viewer** | Да | | | | |
| **Commenter** | Да | Да | | | |
| **Editor** | Да | Да | Да | | |
| **Admin** | Да | Да | Да | Да | |
| **WorkspaceAdmin** | Да | Да | Да | Да | Да |
| **SuperAdmin** | Полный доступ ко всем workspaces |

Подробнее о настройке прав доступа смотрите в разделе [Роли и права доступа](../configuration/permissions.md).

## Настройки workspace

Управляйте настройками workspace через веб-интерфейс (значок шестеренки **Settings**) или редактируя файл конфигурации напрямую.

Основные настройки:

| Настройка | Описание | По умолчанию |
|---|---|---|
| `name` | Отображаемое имя workspace | — |
| `slug` | URL-slug для опубликованной документации | — |
| `git_remote` | URL удаленного git-репозитория | (нет) |
| `git_branch` | Ветка для синхронизации | `main` |
| `git_auto_commit` | Автоматический commit при сохранении в редакторе | `true` |
| `sync_interval` | Интервал опроса git (в секундах) | `300` |
| `theme.mode` | Цветовая схема: `light`, `dark`, `auto` | `auto` |
| `theme.accent` | Цвет акцента | `blue` |
| `permissions.default_role` | Роль для новых участников | `viewer` |

Полный справочник конфигурации смотрите в разделе [Настройки workspace](../configuration/workspace-config.md).

## Что дальше

Ваш workspace готов. Куда двигаться дальше:

| Цель | Руководство |
|---|---|
| Изучить веб-редактор | [Веб-редактор](../guides/editor.md) |
| Настроить публикацию | [Публикация](../guides/publishing.md) |
| Настроить аутентификацию | [Аутентификация](../configuration/authentication.md) |
| Развернуть в production | [Чек-лист для production](../deployment/production.md) |
