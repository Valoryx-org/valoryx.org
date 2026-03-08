---
title: Довідник REST API
description: Повний довідник REST API DocPlatform — автентифікація, управління контентом, робочі простори, пошук та адміністративні ендпоінти.
weight: 1
---

# Довідник REST API

DocPlatform надає RESTful JSON API за адресою `/api/v1/`. Усі ендпоінти вимагають автентифікації, якщо не вказано інше.

## Базова URL

```
http://localhost:3000/api/v1
```

## Автентифікація

Більшість ендпоінтів вимагають JWT токен доступу в заголовку `Authorization`:

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

Отримайте токени через ендпоінти login або OIDC.

### Життєвий цикл токенів

| Токен | Час життя | Призначення |
|---|---|---|
| Токен доступу | 15 хвилин | Автентифікація API |
| Токен оновлення | 30 днів | Отримання нових токенів доступу |

---

## Ендпоінти автентифікації

### Реєстрація

```
POST /api/v1/auth/register
```

Створення нового облікового запису. Перший користувач стає SuperAdmin.

**Запит:**

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Відповідь:** `201 Created`

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

### Вхід

```
POST /api/v1/auth/login
```

Автентифікація за допомогою email та пароля.

**Запит:**

```json
{
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Відповідь:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

**Помилки:**

| Код | Опис |
|---|---|
| `401` | Невірні облікові дані |
| `429` | Забагато спроб входу (обмеження частоти) |

### Оновлення токена

```
POST /api/v1/auth/refresh
```

Обмін токена оновлення на новий токен доступу. Токен оновлення ротується (старий інвалідується).

**Запит:**

```json
{
  "refresh_token": "eyJhbG..."
}
```

**Відповідь:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

### Запит на скидання пароля

```
POST /api/v1/auth/password-reset
```

Запит токена скидання пароля. З налаштованим SMTP надсилається email. Без SMTP токен виводиться в stdout.

**Запит:**

```json
{
  "email": "jane@example.com"
}
```

**Відповідь:** `200 OK` (завжди, незалежно від існування email — запобігає перерахуванню)

### Підтвердження скидання пароля

```
POST /api/v1/auth/password-reset/confirm
```

Встановлення нового пароля за допомогою токена скидання.

**Запит:**

```json
{
  "token": "reset-token-here",
  "new_password": "new-secure-password"
}
```

**Відповідь:** `200 OK`

---

## Ендпоінти контенту

Усі ендпоінти контенту прив'язані до робочого простору.

### Список сторінок

```
GET /api/v1/workspaces/{workspace_id}/pages
```

Повертає всі сторінки, які поточний користувач має право переглядати.

**Параметри запиту:**

| Параметр | Тип | Опис |
|---|---|---|
| `parent_id` | string | Фільтр за батьківською сторінкою (для деревоподібної навігації) |
| `tag` | string | Фільтр за тегом |
| `published` | boolean | Фільтр за статусом публікації |
| `limit` | int | Максимум результатів (за замовчуванням: 100) |
| `offset` | int | Зсув для пагінації |

**Відповідь:** `200 OK`

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
      "created_at": "2026-03-08T10:00:00Z",
      "updated_at": "2025-01-16T14:30:00Z",
      "author_id": "01HJK..."
    }
  ],
  "total": 42,
  "limit": 100,
  "offset": 0
}
```

### Отримання сторінки

```
GET /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Відповідь:** `200 OK`

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
  "created_at": "2026-03-08T10:00:00Z",
  "updated_at": "2025-01-16T14:30:00Z",
  "author_id": "01HJK..."
}
```

**Помилки:**

| Код | Опис |
|---|---|
| `403` | Недостатньо прав |
| `404` | Сторінку не знайдено |

### Створення сторінки

```
POST /api/v1/workspaces/{workspace_id}/pages
```

**Запит:**

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

**Відповідь:** `201 Created` — повертає повний об'єкт сторінки.

### Оновлення сторінки

```
PUT /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Запит:**

```json
{
  "title": "Updated Title",
  "content": "# Updated Title\n\nUpdated content...",
  "content_hash": "sha256:abc123..."
}
```

Поле `content_hash` забезпечує оптимістичне управління паралельністю. Якщо хеш не збігається з поточною версією, сервер повертає `409 Conflict`.

**Відповідь:** `200 OK` — повертає оновлений об'єкт сторінки.

**Помилки:**

| Код | Опис |
|---|---|
| `409` | Невідповідність хешу контенту (виявлено одночасне редагування) |

### Видалення сторінки

```
DELETE /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Відповідь:** `204 No Content`

---

## Ендпоінти робочих просторів

### Список робочих просторів

```
GET /api/v1/workspaces
```

Повертає робочі простори, учасником яких є поточний користувач.

### Створення робочого простору

```
POST /api/v1/workspaces
```

Потребує роль SuperAdmin.

**Запит:**

```json
{
  "name": "API Docs",
  "slug": "api-docs",
  "git_remote": "git@github.com:org/api-docs.git",
  "git_branch": "main"
}
```

### Учасники робочого простору

```
GET /api/v1/workspaces/{workspace_id}/members
POST /api/v1/workspaces/{workspace_id}/invitations
DELETE /api/v1/workspaces/{workspace_id}/members/{user_id}
PUT /api/v1/workspaces/{workspace_id}/members/{user_id}/role
```

---

## Пошук

```
GET /api/v1/workspaces/{workspace_id}/search?q={query}
```

**Параметри запиту:**

| Параметр | Тип | Опис |
|---|---|---|
| `q` | string | Пошуковий запит (обов'язковий) |
| `tag` | string | Фільтр за тегом |
| `limit` | int | Максимум результатів (за замовчуванням: 20) |

**Відповідь:** `200 OK`

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

Результати фільтруються за правами доступу — користувачі бачать лише сторінки, до яких мають доступ.

---

## Синхронізація Git

### Запуск синхронізації

```
POST /api/v1/workspaces/{workspace_id}/sync
```

Ручний запуск git pull + реконсиляції. Потребує роль Admin.

**Відповідь:** `200 OK`

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

### Ендпоінти webhook

```
POST /api/v1/webhooks/github
POST /api/v1/webhooks/gitlab
POST /api/v1/webhooks/bitbucket
```

Ці ендпоінти отримують payload push подій від провайдерів git хостингу. Заголовок автентифікації не потрібен — вони перевіряються за допомогою спільного секрету `GIT_WEBHOOK_SECRET`.

---

## Стан

Ці ендпоінти не вимагають автентифікації.

```
GET /health    → 200 OK { "status": "ok" }
GET /ready     → 200 OK { "status": "ready", "db": "ok", "search": "ok" }
```

---

## Формат помилок

Усі відповіді з помилками використовують єдиний формат:

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

### Поширені коди помилок

| HTTP | Код | Опис |
|---|---|---|
| `400` | `BAD_REQUEST` | Невірне тіло запиту або параметри |
| `401` | `UNAUTHORIZED` | Відсутня або невірна автентифікація |
| `403` | `FORBIDDEN` | Недостатньо прав |
| `404` | `NOT_FOUND` | Ресурс не знайдено |
| `409` | `CONFLICT` | Виявлено одночасну модифікацію |
| `429` | `RATE_LIMITED` | Забагато запитів |
| `500` | `INTERNAL_ERROR` | Помилка сервера (перевірте логи) |

## Пагінація

Ендпоінти списків контенту використовують **пагінацію на основі курсора** з ULID для стабільних результатів навіть при додаванні або видаленні контенту.

**Параметри запиту:**

| Параметр | Тип | За замовчуванням | Опис |
|---|---|---|---|
| `cursor` | string | — | ULID останнього елемента з попередньої сторінки. Опустіть для першої сторінки. |
| `limit` | int | 20 | Кількість результатів на сторінку (максимум: 100) |

**Метадані відповіді:**

```json
{
  "data": [...],
  "next_cursor": "01HJK...",
  "has_more": true
}
```

Передайте `next_cursor` як параметр `cursor` у наступному запиті. Коли `has_more` дорівнює `false`, ви досягли кінця.

---

## Завантаження ресурсів

```
POST /api/v1/workspaces/{workspace_id}/assets
```

Завантаження зображень та файлів у робочий простір. Ресурси зберігаються в директорії `assets/` робочого простору та фіксуються в git, якщо синхронізація увімкнена.

**Запит:** `multipart/form-data` з полем `file`.

**Обмеження:**

| Обмеження | Значення |
|---|---|
| Максимальний розмір файлу | 10 МБ |
| Прийнятні типи | PNG, JPG, GIF, SVG, WebP, PDF |

**Відповідь:** `201 Created`

```json
{
  "path": "assets/screenshot-2025-01-15.png",
  "url": "/api/v1/workspaces/{workspace_id}/assets/screenshot-2025-01-15.png",
  "size": 245760,
  "content_type": "image/png"
}
```

---

## Вирішення конфліктів

### Список конфліктів

```
GET /api/v1/workspaces/{workspace_id}/conflicts
```

**Відповідь:** `200 OK`

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

### Завантаження версії конфлікту

```
GET /api/v1/conflicts/{page_id}/{timestamp}/{version}
```

Параметр `version` — це або `ours` (локальна), або `theirs` (віддалена).

**Відповідь:** `200 OK` з `Content-Type: text/markdown` — необроблений вміст файлу.

### Вирішення конфлікту

```
POST /api/v1/conflicts/{page_id}/{timestamp}/resolve
```

Видаляє артефакти конфлікту після ручного вирішення.

**Відповідь:** `200 OK`

```json
{
  "message": "Conflict resolved",
  "page_id": "01HJK..."
}
```

---

## WebSocket

### Отримання ticket для підключення

```
POST /api/v1/auth/ws-ticket
```

WebSocket з'єднання використовують шаблон одноразового ticket, щоб уникнути розкриття JWT токенів у URL.

**Відповідь:** `200 OK`

```json
{
  "ticket": "random-ticket-value",
  "expires_in": 30
}
```

Ticket дійсний **30 секунд** та може бути використаний лише один раз. Підключення через:

```
ws://localhost:3000/ws?ticket={ticket}
```

### Серверні події

| Тип події | Payload | Коли |
|---|---|---|
| `page-created` | `{workspace_id, path, actor}` | Створено нову сторінку |
| `page-updated` | `{workspace_id, path, actor}` | Сторінку змінено |
| `page-deleted` | `{workspace_id, path, actor}` | Сторінку видалено |
| `presence-join` | `{workspace_id, user_id}` | Користувач підключився |
| `presence-leave` | `{workspace_id, user_id}` | Користувач відключився (таймаут 90 с) |
| `sync-status` | `{workspace_id, status}` | Зміна статусу синхронізації git |
| `conflict-detected` | `{workspace_id, path}` | Виявлено конфлікт злиття git |
| `bulk-sync` | `{workspace_id, changed_count, paths[]}` | Синхронізовано кілька файлів (>20 файлів) |

### Клієнтські повідомлення

```json
{"type": "subscribe", "workspace_id": "01HJK..."}
{"type": "unsubscribe", "workspace_id": "01HJK..."}
```

---

## Заголовки безпеки

DocPlatform встановлює наступні заголовки на всі відповіді:

| Заголовок | Значення |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| `X-Request-ID` | ULID (унікальний для кожного запиту, включається у відповіді з помилками та логи) |

Опублікована документація додатково встановлює:

| Заголовок | Значення |
|---|---|
| `Cache-Control` | `public, max-age=300` |
| `ETag` | Хеш контенту відрендереної сторінки |

---

## Обмеження частоти

| Категорія ендпоінтів | Community Edition |
|---|---|
| Операції читання | 100 / хвилину на користувача |
| Операції запису | 20 / хвилину на користувача |
| Пошук | 30 / хвилину на користувача |
| Автентифікація (login, register, reset) | 5 / хвилину на IP |
| Git webhook | 10 / хвилину на робочий простір |
| Опублікована документація (публічна) | 1 000 / хвилину на IP |

Відповіді з обмеженням частоти включають заголовки `Retry-After` (секунди) та `X-RateLimit-Reset` (Unix timestamp).
