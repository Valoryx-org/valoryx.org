---
title: Настройки workspace
description: Настройка параметров на уровне workspace — git remote, тема, порядок навигации, значения публикации по умолчанию и другое.
weight: 4
---

# Настройки workspace

Каждый workspace имеет собственный файл конфигурации по адресу `.docplatform/workspaces/{workspace-id}/.docplatform/config.yaml`. Редактируйте этот файл напрямую или используйте веб-интерфейс (**Settings** -> **Workspace**).

## Полный справочник конфигурации

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

## Справочник настроек

### Идентификация

| Ключ | Тип | Описание |
|---|---|---|
| `workspace_id` | string | ULID, автоматически генерируемый при создании. Не изменяйте. |
| `name` | string | Отображаемое имя в интерфейсе и заголовке опубликованного сайта |
| `slug` | string | Сегмент URL для опубликованной документации: `/p/{slug}/`. Изменение приведет к поломке существующих URL. |
| `description` | string | Опциональное описание для внутреннего использования |

### Git

| Ключ | Тип | По умолчанию | Описание |
|---|---|---|---|
| `git_remote` | string | — | URL удаленного репозитория (SSH или HTTPS) |
| `git_branch` | string | `main` | Ветка для синхронизации |
| `git_auto_commit` | bool | `true` | Auto-commit сохранений из веб-редактора |
| `sync_interval` | int | `300` | Секунды между опросами удаленного репозитория. Установите `0` для отключения polling (только webhook). |

### Тема

| Ключ | Тип | По умолчанию | Описание |
|---|---|---|---|
| `theme.mode` | string | `auto` | Цветовая схема для опубликованной документации: `light`, `dark`, `auto` |
| `theme.accent` | string | `blue` | Цвет акцента для ссылок, кнопок и выделений в опубликованной документации |

### Публикация

| Ключ | Тип | По умолчанию | Описание |
|---|---|---|---|
| `publishing.default_published` | bool | `false` | Публиковать ли новые страницы по умолчанию |
| `publishing.require_explicit_unpublish` | bool | `false` | Если true, страницы должны быть явно сняты с публикации (предотвращает случайное исключение) |

### Права доступа

| Ключ | Тип | По умолчанию | Описание |
|---|---|---|---|
| `permissions.default_role` | string | `viewer` | Роль, назначаемая пользователям, принимающим приглашение в workspace |

### Навигация

Массив `navigation` управляет порядком боковой панели в опубликованной документации. Без него страницы сортируются по алфавиту.

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

- Каждый элемент должен иметь `title`
- Элементы с `path` являются ссылками на страницы
- Элементы без `path`, но с `children` являются заголовками секций
- Глубина вложенности не ограничена
- Страницы, не указанные в `navigation`, по-прежнему существуют, но не отображаются в боковой панели

## Редактирование настроек

### Через веб-интерфейс

1. Откройте workspace в веб-редакторе
2. Нажмите **Settings** (значок шестеренки)
3. Измените настройки через интерфейс формы
4. Изменения сохраняются автоматически

### Через файл конфигурации

Редактируйте YAML-файл напрямую:

```bash
# Find your workspace config
ls .docplatform/workspaces/*/. docplatform/config.yaml

# Edit
nano .docplatform/workspaces/01KJJ.../. docplatform/config.yaml
```

Перезапустите сервер для применения изменений или запустите перезагрузку через API:

```bash
curl -X POST http://localhost:3000/api/v1/admin/reload \
  -H "Authorization: Bearer {token}"
```

### Через git

Если файл конфигурации workspace отслеживается в git, пушьте изменения из IDE, и они будут подтянуты при следующем цикле синхронизации. Это удобно для управления конфигурацией документации как кодом.

## Несколько workspaces

DocPlatform поддерживает несколько workspaces на одном экземпляре. Каждый workspace полностью изолирован:

- Отдельные директории контента
- Отдельные git-репозитории
- Отдельные списки участников и роли
- Отдельные поисковые индексы
- Отдельные опубликованные сайты (разные slugs)

Создайте дополнительные workspaces через CLI:

```bash
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git
```

Или через переключатель workspace в веб-интерфейсе.
