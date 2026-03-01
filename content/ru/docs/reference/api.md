---
title: Справочник REST API
description: Полный справочник REST API DocPlatform — аутентификация, управление контентом, workspaces, поиск и административные endpoints.
weight: 1
---

# Справочник REST API

DocPlatform предоставляет RESTful JSON API по адресу `/api/v1/`. Все endpoints требуют аутентификации, если не указано иное.

## Базовый URL

```
http://localhost:3000/api/v1
```

## Аутентификация

Большинство endpoints требуют JWT access token в заголовке `Authorization`:

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

Получите токены через endpoints входа или OIDC.

### Жизненный цикл токенов

| Токен | Срок жизни | Назначение |
|---|---|---|
| Access token | 15 минут | Аутентификация API |
| Refresh token | 30 дней | Получение новых access token |

---

## Endpoints аутентификации

### Регистрация

```
POST /api/v1/auth/register
```

Создание новой учетной записи. Первый пользователь становится SuperAdmin.

**Запрос:**

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Ответ:** `201 Created`

```json
{
  "user": {
    "id": "01HJK...",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "role": "superadmin"
  },
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

### Вход

```
POST /api/v1/auth/login
```

Аутентификация с email и паролем.

**Запрос:**

```json
{
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Ответ:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

**Ошибки:**

| Код | Описание |
|---|---|
| `401` | Неверные учетные данные |
| `429` | Слишком много попыток входа (ограничение частоты) |

### Обновление токена

```
POST /api/v1/auth/refresh
```

Обмен refresh token на новый access token. Refresh token ротируется (старый инвалидируется).

**Запрос:**

```json
{
  "refresh_token": "eyJhbG..."
}
```

**Ответ:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

### Запрос сброса пароля

```
POST /api/v1/auth/password-reset
```

Запрос токена сброса пароля. При настроенном SMTP отправляется email. Без SMTP токен логируется в stdout.

**Запрос:**

```json
{
  "email": "jane@example.com"
}
```

**Ответ:** `200 OK` (всегда, независимо от существования email — предотвращает перебор)

### Подтверждение сброса пароля

```
POST /api/v1/auth/password-reset/confirm
```

Установка нового пароля с использованием токена сброса.

**Запрос:**

```json
{
  "token": "reset-token-here",
  "new_password": "new-secure-password"
}
```

**Ответ:** `200 OK`

---

## Endpoints контента

Все endpoints контента привязаны к workspace.

### Список страниц

```
GET /api/v1/workspaces/{workspace_id}/pages
```

Возвращает все страницы, которые текущий пользователь имеет право просматривать.

**Параметры запроса:**

| Параметр | Тип | Описание |
|---|---|---|
| `parent_id` | string | Фильтр по родительской странице (для древовидной навигации) |
| `tag` | string | Фильтр по тегу |
| `published` | boolean | Фильтр по статусу публикации |
| `limit` | int | Максимум результатов (по умолчанию: 100) |
| `offset` | int | Смещение пагинации |

**Ответ:** `200 OK`

```json
{
  "pages": [
    {
      "id": "01HJK...",
      "title": "Getting Started",
      "slug": "getting-started",
      "description": "Install and configure DocPlatform.",
      "path": "getting-started.md",
      "tags": ["guide"],
      "published": true,
      "access": "public",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-16T14:30:00Z",
      "author_id": "01HJK..."
    }
  ],
  "total": 42,
  "limit": 100,
  "offset": 0
}
```

### Получение страницы

```
GET /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Ответ:** `200 OK`

```json
{
  "id": "01HJK...",
  "title": "Getting Started",
  "slug": "getting-started",
  "description": "Install and configure DocPlatform.",
  "path": "getting-started.md",
  "content": "# Getting Started\n\nThis guide walks you through...",
  "content_hash": "sha256:abc123...",
  "tags": ["guide"],
  "published": true,
  "access": "public",
  "parent_id": null,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-16T14:30:00Z",
  "author_id": "01HJK..."
}
```

**Ошибки:**

| Код | Описание |
|---|---|
| `403` | Недостаточно прав |
| `404` | Страница не найдена |

### Создание страницы

```
POST /api/v1/workspaces/{workspace_id}/pages
```

**Запрос:**

```json
{
  "title": "New Page",
  "slug": "new-page",
  "content": "# New Page\n\nContent here...",
  "description": "Description for search and SEO.",
  "tags": ["guide"],
  "published": false,
  "parent_id": null
}
```

**Ответ:** `201 Created` — возвращает полный объект страницы.

### Обновление страницы

```
PUT /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Запрос:**

```json
{
  "title": "Updated Title",
  "content": "# Updated Title\n\nUpdated content...",
  "content_hash": "sha256:abc123..."
}
```

Поле `content_hash` обеспечивает оптимистичную конкурентность. Если хеш не совпадает с текущей версией, сервер возвращает `409 Conflict`.

**Ответ:** `200 OK` — возвращает обновленный объект страницы.

**Ошибки:**

| Код | Описание |
|---|---|
| `409` | Несовпадение хеша контента (обнаружено одновременное редактирование) |

### Удаление страницы

```
DELETE /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Ответ:** `204 No Content`

---

## Endpoints workspaces

### Список workspaces

```
GET /api/v1/workspaces
```

Возвращает workspaces, в которых текущий пользователь является участником.

### Создание workspace

```
POST /api/v1/workspaces
```

Требует роль SuperAdmin.

**Запрос:**

```json
{
  "name": "API Docs",
  "slug": "api-docs",
  "git_remote": "git@github.com:org/api-docs.git",
  "git_branch": "main"
}
```

### Участники workspace

```
GET /api/v1/workspaces/{workspace_id}/members
POST /api/v1/workspaces/{workspace_id}/invitations
DELETE /api/v1/workspaces/{workspace_id}/members/{user_id}
PUT /api/v1/workspaces/{workspace_id}/members/{user_id}/role
```

---

## Поиск

```
GET /api/v1/workspaces/{workspace_id}/search?q={query}
```

**Параметры запроса:**

| Параметр | Тип | Описание |
|---|---|---|
| `q` | string | Поисковый запрос (обязательный) |
| `tag` | string | Фильтр по тегу |
| `limit` | int | Максимум результатов (по умолчанию: 20) |

**Ответ:** `200 OK`

```json
{
  "results": [
    {
      "page_id": "01HJK...",
      "title": "Git Integration",
      "description": "Bidirectional git sync...",
      "path": "guides/git-integration.md",
      "score": 0.95,
      "highlights": [
        "...bidirectional <mark>git sync</mark> lets your team..."
      ]
    }
  ],
  "total": 5,
  "query": "git sync",
  "took_ms": 12
}
```

Результаты фильтруются по правам доступа — пользователи видят только те страницы, к которым имеют доступ.

---

## Синхронизация git

### Запуск синхронизации

```
POST /api/v1/workspaces/{workspace_id}/sync
```

Ручной запуск git pull + реконсиляция. Требует роль Admin.

**Ответ:** `200 OK`

```json
{
  "status": "completed",
  "changes": {
    "added": 2,
    "updated": 1,
    "deleted": 0
  }
}
```

### Webhook endpoints

```
POST /api/v1/webhooks/github
POST /api/v1/webhooks/gitlab
POST /api/v1/webhooks/bitbucket
```

Эти endpoints принимают payload push-событий от хостинг-провайдеров git. Заголовок аутентификации не требуется — проверка выполняется с использованием общего секрета `GIT_WEBHOOK_SECRET`.

---

## Состояние

Эти endpoints не требуют аутентификации.

```
GET /health    → 200 OK { "status": "ok" }
GET /ready     → 200 OK { "status": "ready", "db": "ok", "search": "ok" }
```

---

## Формат ошибок

Все ответы с ошибками используют единый формат:

```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Content hash mismatch. The page was modified by another user.",
    "details": {
      "current_hash": "sha256:def456...",
      "provided_hash": "sha256:abc123..."
    }
  }
}
```

### Общие коды ошибок

| HTTP | Код | Описание |
|---|---|---|
| `400` | `BAD_REQUEST` | Некорректное тело запроса или параметры |
| `401` | `UNAUTHORIZED` | Отсутствует или недействительна аутентификация |
| `403` | `FORBIDDEN` | Недостаточно прав |
| `404` | `NOT_FOUND` | Ресурс не найден |
| `409` | `CONFLICT` | Обнаружена одновременная модификация |
| `429` | `RATE_LIMITED` | Слишком много запросов |
| `500` | `INTERNAL_ERROR` | Ошибка сервера (проверьте логи) |

## Пагинация

Endpoints списков контента используют **пагинацию на основе курсоров** с ULID для стабильных результатов даже при добавлении или удалении контента.

**Параметры запроса:**

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `cursor` | string | — | ULID последнего элемента предыдущей страницы. Пропустите для первой страницы. |
| `limit` | int | 20 | Количество результатов на страницу (максимум: 100) |

**Метаданные ответа:**

```json
{
  "data": [...],
  "next_cursor": "01HJK...",
  "has_more": true
}
```

Передайте `next_cursor` как параметр `cursor` в следующем запросе. Когда `has_more` равно `false`, вы достигли конца.

---

## Загрузка ресурсов

```
POST /api/v1/workspaces/{workspace_id}/assets
```

Загрузка изображений и файлов в workspace. Ресурсы хранятся в директории `assets/` workspace и коммитятся в git, если синхронизация включена.

**Запрос:** `multipart/form-data` с полем `file`.

**Ограничения:**

| Ограничение | Значение |
|---|---|
| Максимальный размер файла | 10 МБ |
| Допустимые типы | PNG, JPG, GIF, SVG, WebP, PDF |

**Ответ:** `201 Created`

```json
{
  "path": "assets/screenshot-2025-01-15.png",
  "url": "/api/v1/workspaces/{workspace_id}/assets/screenshot-2025-01-15.png",
  "size": 245760,
  "content_type": "image/png"
}
```

---

## Разрешение конфликтов

### Список конфликтов

```
GET /api/v1/workspaces/{workspace_id}/conflicts
```

**Ответ:** `200 OK`

```json
{
  "workspace_id": "01HJK...",
  "sync_status": "conflict",
  "conflicts": [
    {
      "path": "guides/editor.md",
      "ours_hash": "abc123...",
      "theirs_hash": "def456...",
      "page_id": "01HJK...",
      "timestamp": "20250115T103045Z"
    }
  ]
}
```

### Скачивание версии конфликта

```
GET /api/v1/conflicts/{page_id}/{timestamp}/{version}
```

Параметр `version` может быть `ours` (локальная) или `theirs` (удаленная).

**Ответ:** `200 OK` с `Content-Type: text/markdown` — содержимое файла.

### Разрешение конфликта

```
POST /api/v1/conflicts/{page_id}/{timestamp}/resolve
```

Удаляет артефакты конфликта после ручного разрешения.

**Ответ:** `200 OK`

```json
{
  "message": "Conflict resolved",
  "page_id": "01HJK..."
}
```

---

## WebSocket

### Получение ticket для подключения

```
POST /api/v1/auth/ws-ticket
```

WebSocket-подключения используют паттерн одноразового ticket, чтобы избежать раскрытия JWT-токенов в URL.

**Ответ:** `200 OK`

```json
{
  "ticket": "random-ticket-value",
  "expires_in": 30
}
```

Ticket действителен **30 секунд** и может быть использован только один раз. Подключение через:

```
ws://localhost:3000/ws?ticket={ticket}
```

### Серверные события

| Тип события | Payload | Когда |
|---|---|---|
| `page-created` | `{workspace_id, path, actor}` | Создана новая страница |
| `page-updated` | `{workspace_id, path, actor}` | Страница изменена |
| `page-deleted` | `{workspace_id, path, actor}` | Страница удалена |
| `presence-join` | `{workspace_id, user_id}` | Пользователь подключился |
| `presence-leave` | `{workspace_id, user_id}` | Пользователь отключился (тайм-аут 90 с) |
| `sync-status` | `{workspace_id, status}` | Изменение статуса синхронизации git |
| `conflict-detected` | `{workspace_id, path}` | Обнаружен конфликт слияния git |
| `bulk-sync` | `{workspace_id, changed_count, paths[]}` | Синхронизировано несколько файлов (>20 файлов) |

### Клиентские сообщения

```json
{"type": "subscribe", "workspace_id": "01HJK..."}
{"type": "unsubscribe", "workspace_id": "01HJK..."}
```

---

## Заголовки безопасности

DocPlatform устанавливает следующие заголовки на все ответы:

| Заголовок | Значение |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| `X-Request-ID` | ULID (уникальный для каждого запроса, включается в ответы об ошибках и логи) |

Опубликованная документация дополнительно устанавливает:

| Заголовок | Значение |
|---|---|
| `Cache-Control` | `public, max-age=300` |
| `ETag` | Хеш контента отрендеренной страницы |

---

## Ограничение частоты запросов

| Категория endpoints | Community Edition |
|---|---|
| Операции чтения | 100 / минуту на пользователя |
| Операции записи | 20 / минуту на пользователя |
| Поиск | 30 / минуту на пользователя |
| Аутентификация (login, register, reset) | 5 / минуту на IP |
| Git webhooks | 10 / минуту на workspace |
| Опубликованная документация (публичная) | 1 000 / минуту на IP |

Ответы с превышением лимита включают заголовки `Retry-After` (в секундах) и `X-RateLimit-Reset` (Unix timestamp).
