---
title: Ваш перший робочий простір
description: Створіть та налаштуйте робочий простір документації — підключіть git, налаштуйте структуру контенту та запросіть команду.
weight: 3
---

# Ваш перший робочий простір

Робочий простір — це контейнер верхнього рівня для проєкту документації. Кожен робочий простір відповідає директорії Markdown файлів та опціонально синхронізується з git репозиторієм.

## Концепції робочого простору

| Концепція | Опис |
|---|---|
| **Робочий простір** | Проєкт документації, що містить сторінки, учасників та налаштування |
| **Сторінка** | Markdown файл із YAML frontmatter (назва, опис, теги, доступ) |
| **Slug** | URL-безпечний ідентифікатор вашого робочого простору (наприклад, `my-docs` → `/p/my-docs/`) |
| **Учасник** | Користувач із роллю в робочому просторі (від Viewer до WorkspaceAdmin) |

## Створення робочого простору

### Через CLI

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs
```

### Через веб-інтерфейс

1. Увійдіть як SuperAdmin або WorkspaceAdmin
2. Відкрийте перемикач робочих просторів (випадаючий список зверху зліва)
3. Натисніть **Create Workspace**
4. Введіть назву та slug
5. Опціонально налаштуйте віддалений git репозиторій

## Підключення git репозиторію

Двонаправлена синхронізація підтримує файли робочого простору та віддалений git репозиторій в актуальному стані.

### Під час ініціалізації

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs \
  --git-url git@github.com:your-org/eng-docs.git \
  --branch main
```

### Після створення

Оновіть конфігурацію робочого простору за адресою `.docplatform/workspaces/{id}/.docplatform/config.yaml`:

```yaml
git_remote: git@github.com:your-org/eng-docs.git
git_branch: main
git_auto_commit: true
sync_interval: 300  # seconds
```

Потім перезапустіть сервер або запустіть ручну синхронізацію з веб-інтерфейсу.

### Налаштування SSH ключа

Для приватних репозиторіїв DocPlatform використовує виділений SSH deploy key:

```bash
# Generate a deploy key (no passphrase)
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""

# Add the public key to your repository's deploy keys
cat ~/.ssh/docplatform_deploy_key.pub
# → Copy this to GitHub/GitLab Settings → Deploy Keys (enable write access)
```

Встановіть змінну середовища:

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

### Як працює синхронізація

```
┌─────────────┐     auto-commit + push      ┌──────────────┐
│ Web Editor   │ ──────────────────────────► │ Remote Repo  │
│ (browser)    │                             │ (GitHub, etc)│
│              │ ◄────────────────────────── │              │
└─────────────┘     polling / webhook        └──────────────┘
```

**Веб → Git:** Коли ви зберігаєте в редакторі, DocPlatform записує `.md` файл, автоматично фіксує з описовим повідомленням та відправляє на віддалений сервер.

**Git → Веб:** DocPlatform опитує віддалений сервер (за замовчуванням: кожні 5 хвилин) або слухає webhook. Нові коміти витягуються, і веб-інтерфейс оновлюється в реальному часі через WebSocket.

**Конфлікти:** Якщо обидві сторони змінюють той самий файл між синхронізаціями, DocPlatform виявляє колізію за допомогою хешів контенту, повертає HTTP 409 та робить обидві версії доступними для завантаження, щоб ви могли вирішити конфлікт вручну.

## Організація контенту

### Ієрархія сторінок

Сторінки можуть бути вкладені на будь-яку глибину. Структура файлів у `docs/` безпосередньо відповідає структурі URL:

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

Кожна сторінка починається з YAML frontmatter:

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

Поле `title` є обов'язковим. Усі інші поля є опціональними та мають розумні значення за замовчуванням.

## Запрошення команди

### Через веб-інтерфейс

1. Відкрийте **Workspace Settings** → **Members**
2. Натисніть **Invite**
3. Введіть електронну адресу особи
4. Оберіть роль (Viewer, Commenter, Editor, Admin)
5. Натисніть **Send Invitation**

Якщо SMTP налаштовано, запрошення надсилається електронною поштою. В іншому випадку відображається посилання-запрошення, яке можна скопіювати.

### Ролі

| Роль | Перегляд | Коментування | Редагування | Управління учасниками | Управління робочим простором |
|---|---|---|---|---|---|
| **Viewer** | Так | | | | |
| **Commenter** | Так | Так | | | |
| **Editor** | Так | Так | Так | | |
| **Admin** | Так | Так | Так | Так | |
| **WorkspaceAdmin** | Так | Так | Так | Так | Так |
| **SuperAdmin** | Повний доступ до платформи в усіх робочих просторах |

Для детальної конфігурації прав доступу див. [Ролі та права доступу](../configuration/permissions.md).

## Налаштування робочого простору

Доступ до налаштувань робочого простору через веб-інтерфейс (значок **Settings** шестеренки) або шляхом безпосереднього редагування конфігураційного файлу.

Основні налаштування:

| Параметр | Опис | За замовчуванням |
|---|---|---|
| `name` | Відображувана назва робочого простору | — |
| `slug` | URL slug для опублікованої документації | — |
| `git_remote` | URL віддаленого git репозиторію | (немає) |
| `git_branch` | Гілка для синхронізації | `main` |
| `git_auto_commit` | Автоматична фіксація збережень редактора | `true` |
| `sync_interval` | Інтервал опитування git (секунди) | `300` |
| `theme.mode` | Кольорова схема: `light`, `dark`, `auto` | `auto` |
| `theme.accent` | Акцентний колір | `blue` |
| `permissions.default_role` | Роль для нових учасників | `viewer` |

Для повного довідника конфігурації див. [Налаштування робочого простору](../configuration/workspace-config.md).

## Що далі

Ваш робочий простір готовий. Ось куди рухатися далі:

| Мета | Посібник |
|---|---|
| Вивчити веб-редактор | [Веб-редактор](../guides/editor.md) |
| Налаштувати опубліковану документацію | [Публікація](../guides/publishing.md) |
| Налаштувати автентифікацію | [Автентифікація](../configuration/authentication.md) |
| Розгорнути у виробництво | [Контрольний список для виробництва](../deployment/production.md) |
