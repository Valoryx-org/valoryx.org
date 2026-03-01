---
title: Налаштування робочого простору
description: Налаштуйте параметри на рівні робочого простору — git remote, тему, порядок навігації, значення за замовчуванням для публікації тощо.
weight: 4
---

# Налаштування робочого простору

Кожен робочий простір має власний конфігураційний файл за адресою `.docplatform/workspaces/{workspace-id}/.docplatform/config.yaml`. Редагуйте цей файл безпосередньо або використовуйте веб-інтерфейс (**Settings** → **Workspace**).

## Повний довідник конфігурації

```yaml
# Workspace identity
workspace_id: 01KJJ10NTF31Z1QJTG4ZRQZ2Z2    # Auto-generated ULID
name: "Engineering Docs"                        # Display name
slug: eng-docs                                  # URL slug for published docs
description: "Internal engineering documentation"

# Git synchronization
git_remote: git@github.com:your-org/eng-docs.git
git_branch: main
git_auto_commit: true       # Auto-commit editor saves to git
sync_interval: 300          # Polling interval in seconds (0 = disabled)

# Theme
theme:
  mode: auto                # light, dark, auto (follows system preference)
  accent: blue              # Accent color for published site

# Publishing defaults
publishing:
  default_published: false  # New pages published by default?
  require_explicit_unpublish: false

# Permissions
permissions:
  default_role: viewer      # Role assigned to new workspace members

# Navigation (for published docs sidebar)
navigation:
  - title: "Overview"
    path: "index.md"
  - title: "Getting Started"
    path: "getting-started/index.md"
    children:
      - title: "Installation"
        path: "getting-started/installation.md"
      - title: "Configuration"
        path: "getting-started/configuration.md"
```

## Довідник параметрів

### Ідентичність

| Ключ | Тип | Опис |
|---|---|---|
| `workspace_id` | string | ULID, автоматично згенерований при створенні. Не змінюйте. |
| `name` | string | Відображувана назва в інтерфейсі та заголовку опублікованого сайту |
| `slug` | string | Сегмент URL для опублікованої документації: `/p/{slug}/`. Зміна цього значення порушить наявні URL. |
| `description` | string | Опціональний опис для внутрішнього використання |

### Git

| Ключ | Тип | За замовчуванням | Опис |
|---|---|---|---|
| `git_remote` | string | — | URL віддаленого репозиторію (SSH або HTTPS) |
| `git_branch` | string | `main` | Гілка для синхронізації |
| `git_auto_commit` | bool | `true` | Автоматична фіксація збережень із веб-редактора |
| `sync_interval` | int | `300` | Секунди між опитуваннями віддаленого репозиторію. Встановіть `0`, щоб вимкнути polling (лише webhook). |

### Тема

| Ключ | Тип | За замовчуванням | Опис |
|---|---|---|---|
| `theme.mode` | string | `auto` | Кольорова схема для опублікованої документації: `light`, `dark`, `auto` |
| `theme.accent` | string | `blue` | Акцентний колір в опублікованій документації для посилань, кнопок та виділень |

### Публікація

| Ключ | Тип | За замовчуванням | Опис |
|---|---|---|---|
| `publishing.default_published` | bool | `false` | Чи публікуються нові сторінки за замовчуванням |
| `publishing.require_explicit_unpublish` | bool | `false` | Коли true, сторінки повинні бути явно зняті з публікації (запобігає випадковому виключенню) |

### Права доступу

| Ключ | Тип | За замовчуванням | Опис |
|---|---|---|---|
| `permissions.default_role` | string | `viewer` | Роль, що призначається користувачам при прийнятті запрошення до робочого простору |

### Навігація

Масив `navigation` контролює порядок бічної панелі в опублікованій документації. Без нього сторінки впорядковуються за алфавітом.

```yaml
navigation:
  - title: "Overview"       # Display label
    path: "index.md"        # File path relative to docs/
  - title: "Guides"         # Section header (no path = non-clickable group)
    children:
      - title: "Editor"
        path: "guides/editor.md"
      - title: "Git Sync"
        path: "guides/git-integration.md"
```

**Правила:**

- Кожен запис потребує `title`
- Записи з `path` є посиланнями на сторінки
- Записи без `path`, але з `children` є заголовками секцій
- Глибина вкладення необмежена
- Сторінки, не перелічені в `navigation`, все ще існують, але не з'являються на бічній панелі

## Редагування налаштувань

### Через веб-інтерфейс

1. Відкрийте робочий простір у веб-редакторі
2. Натисніть **Settings** (значок шестеренки)
3. Змініть налаштування через інтерфейс форми
4. Зміни зберігаються автоматично

### Через конфігураційний файл

Редагуйте YAML файл безпосередньо:

```bash
# Find your workspace config
ls .docplatform/workspaces/*/. docplatform/config.yaml

# Edit
nano .docplatform/workspaces/01KJJ.../. docplatform/config.yaml
```

Перезапустіть сервер, щоб зміни набули чинності, або запустіть перезавантаження через API:

```bash
curl -X POST http://localhost:3000/api/v1/admin/reload \
  -H "Authorization: Bearer {token}"
```

### Через git

Якщо конфігураційний файл робочого простору відстежується в git, відправте зміни з IDE, і вони будуть підхоплені при наступному циклі синхронізації. Це корисно для управління конфігурацією документації як кодом.

## Кілька робочих просторів

DocPlatform підтримує кілька робочих просторів на одному екземплярі. Кожен робочий простір повністю ізольований:

- Окремі директорії контенту
- Окремі git репозиторії
- Окремі списки учасників та ролі
- Окремі пошукові індекси
- Окремі опубліковані сайти (різні slug)

Створіть додаткові робочі простори через CLI:

```bash
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git
```

Або через перемикач робочих просторів у веб-інтерфейсі.
