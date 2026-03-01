---
title: REST API Reference
description: Complete reference for DocPlatform's REST API — authentication, content management, workspaces, search, and admin endpoints.
weight: 1
---

# REST API Reference

DocPlatform exposes a RESTful JSON API at `/api/v1/`. All endpoints require authentication unless noted otherwise.

## Base URL

```
http://localhost:3000/api/v1
```

## Authentication

Most endpoints require a JWT access token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

Obtain tokens via the login or OIDC endpoints.

### Token lifecycle

| Token | Lifetime | Purpose |
|---|---|---|
| Access token | 15 minutes | API authentication |
| Refresh token | 30 days | Obtain new access tokens |

---

## Auth endpoints

### Register

```
POST /api/v1/auth/register
```

Create a new user account. The first user becomes SuperAdmin.

**Request:**

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Response:** `201 Created`

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

### Login

```
POST /api/v1/auth/login
```

Authenticate with email and password.

**Request:**

```json
{
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

**Errors:**

| Code | Description |
|---|---|
| `401` | Invalid credentials |
| `429` | Too many login attempts (rate limited) |

### Refresh token

```
POST /api/v1/auth/refresh
```

Exchange a refresh token for a new access token. The refresh token is rotated (old one invalidated).

**Request:**

```json
{
  "refresh_token": "eyJhbG..."
}
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

### Password reset request

```
POST /api/v1/auth/password-reset
```

Request a password reset token. With SMTP configured, an email is sent. Without SMTP, the token is logged to stdout.

**Request:**

```json
{
  "email": "jane@example.com"
}
```

**Response:** `200 OK` (always, regardless of whether the email exists — prevents enumeration)

### Password reset confirm

```
POST /api/v1/auth/password-reset/confirm
```

Set a new password using a reset token.

**Request:**

```json
{
  "token": "reset-token-here",
  "new_password": "new-secure-password"
}
```

**Response:** `200 OK`

---

## Content endpoints

All content endpoints are scoped to a workspace.

### List pages

```
GET /api/v1/workspaces/{workspace_id}/pages
```

Returns all pages the current user has permission to view.

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `parent_id` | string | Filter by parent page (for tree navigation) |
| `tag` | string | Filter by tag |
| `published` | boolean | Filter by published status |
| `limit` | int | Max results (default: 100) |
| `offset` | int | Pagination offset |

**Response:** `200 OK`

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

### Get page

```
GET /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Response:** `200 OK`

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

**Errors:**

| Code | Description |
|---|---|
| `403` | Insufficient permissions |
| `404` | Page not found |

### Create page

```
POST /api/v1/workspaces/{workspace_id}/pages
```

**Request:**

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

**Response:** `201 Created` — returns the full page object.

### Update page

```
PUT /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Request:**

```json
{
  "title": "Updated Title",
  "content": "# Updated Title\n\nUpdated content...",
  "content_hash": "sha256:abc123..."
}
```

The `content_hash` field enables optimistic concurrency. If the hash doesn't match the current version, the server returns `409 Conflict`.

**Response:** `200 OK` — returns the updated page object.

**Errors:**

| Code | Description |
|---|---|
| `409` | Content hash mismatch (concurrent edit detected) |

### Delete page

```
DELETE /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Response:** `204 No Content`

---

## Workspace endpoints

### List workspaces

```
GET /api/v1/workspaces
```

Returns workspaces the current user is a member of.

### Create workspace

```
POST /api/v1/workspaces
```

Requires SuperAdmin role.

**Request:**

```json
{
  "name": "API Docs",
  "slug": "api-docs",
  "git_remote": "git@github.com:org/api-docs.git",
  "git_branch": "main"
}
```

### Workspace members

```
GET /api/v1/workspaces/{workspace_id}/members
POST /api/v1/workspaces/{workspace_id}/invitations
DELETE /api/v1/workspaces/{workspace_id}/members/{user_id}
PUT /api/v1/workspaces/{workspace_id}/members/{user_id}/role
```

---

## Search

```
GET /api/v1/workspaces/{workspace_id}/search?q={query}
```

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `q` | string | Search query (required) |
| `tag` | string | Filter by tag |
| `limit` | int | Max results (default: 20) |

**Response:** `200 OK`

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

Results are permission-filtered — users only see pages they have access to.

---

## Git sync

### Trigger sync

```
POST /api/v1/workspaces/{workspace_id}/sync
```

Manually trigger a git pull + reconciliation. Requires Admin role.

**Response:** `200 OK`

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

These endpoints receive push event payloads from git hosting providers. No authentication header required — they validate using the `GIT_WEBHOOK_SECRET` shared secret.

---

## Health

These endpoints do not require authentication.

```
GET /health    → 200 OK { "status": "ok" }
GET /ready     → 200 OK { "status": "ready", "db": "ok", "search": "ok" }
```

---

## Error format

All error responses use a consistent format:

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

### Common error codes

| HTTP | Code | Description |
|---|---|---|
| `400` | `BAD_REQUEST` | Invalid request body or parameters |
| `401` | `UNAUTHORIZED` | Missing or invalid authentication |
| `403` | `FORBIDDEN` | Insufficient permissions |
| `404` | `NOT_FOUND` | Resource not found |
| `409` | `CONFLICT` | Concurrent modification detected |
| `429` | `RATE_LIMITED` | Too many requests |
| `500` | `INTERNAL_ERROR` | Server error (check logs) |

## Pagination

Content listing endpoints use **cursor-based pagination** with ULIDs for stable results even when content is being added or deleted.

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `cursor` | string | — | ULID of the last item from the previous page. Omit for the first page. |
| `limit` | int | 20 | Number of results per page (max: 100) |

**Response metadata:**

```json
{
  "data": [...],
  "next_cursor": "01HJK...",
  "has_more": true
}
```

Pass `next_cursor` as the `cursor` parameter in the next request. When `has_more` is `false`, you've reached the end.

---

## Asset uploads

```
POST /api/v1/workspaces/{workspace_id}/assets
```

Upload images and files to a workspace. Assets are stored in the workspace's `assets/` directory and committed to git if sync is enabled.

**Request:** `multipart/form-data` with a `file` field.

**Limits:**

| Constraint | Value |
|---|---|
| Max file size | 10 MB |
| Accepted types | PNG, JPG, GIF, SVG, WebP, PDF |

**Response:** `201 Created`

```json
{
  "path": "assets/screenshot-2025-01-15.png",
  "url": "/api/v1/workspaces/{workspace_id}/assets/screenshot-2025-01-15.png",
  "size": 245760,
  "content_type": "image/png"
}
```

---

## Conflict resolution

### List conflicts

```
GET /api/v1/workspaces/{workspace_id}/conflicts
```

**Response:** `200 OK`

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

### Download a conflict version

```
GET /api/v1/conflicts/{page_id}/{timestamp}/{version}
```

The `version` parameter is either `ours` (local) or `theirs` (remote).

**Response:** `200 OK` with `Content-Type: text/markdown` — raw file content.

### Resolve a conflict

```
POST /api/v1/conflicts/{page_id}/{timestamp}/resolve
```

Removes conflict artifacts after manual resolution.

**Response:** `200 OK`

```json
{
  "message": "Conflict resolved",
  "page_id": "01HJK..."
}
```

---

## WebSocket

### Obtain a connection ticket

```
POST /api/v1/auth/ws-ticket
```

WebSocket connections use a one-time ticket pattern to avoid exposing JWT tokens in URLs.

**Response:** `200 OK`

```json
{
  "ticket": "random-ticket-value",
  "expires_in": 30
}
```

The ticket is valid for **30 seconds** and can only be used once. Connect via:

```
ws://localhost:3000/ws?ticket={ticket}
```

### Server events

| Event type | Payload | When |
|---|---|---|
| `page-created` | `{workspace_id, path, actor}` | A new page is created |
| `page-updated` | `{workspace_id, path, actor}` | A page is modified |
| `page-deleted` | `{workspace_id, path, actor}` | A page is deleted |
| `presence-join` | `{workspace_id, user_id}` | A user connects |
| `presence-leave` | `{workspace_id, user_id}` | A user disconnects (90s timeout) |
| `sync-status` | `{workspace_id, status}` | Git sync status change |
| `conflict-detected` | `{workspace_id, path}` | Git merge conflict found |
| `bulk-sync` | `{workspace_id, changed_count, paths[]}` | Multiple files synced (>20 files) |

### Client messages

```json
{"type": "subscribe", "workspace_id": "01HJK..."}
{"type": "unsubscribe", "workspace_id": "01HJK..."}
```

---

## Security headers

DocPlatform sets the following headers on all responses:

| Header | Value |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| `X-Request-ID` | ULID (unique per request, included in error responses and logs) |

Published docs additionally set:

| Header | Value |
|---|---|
| `Cache-Control` | `public, max-age=300` |
| `ETag` | Content hash of the rendered page |

---

## Rate limiting

| Endpoint category | Community Edition |
|---|---|
| Read operations | 100 / minute per user |
| Write operations | 20 / minute per user |
| Search | 30 / minute per user |
| Auth (login, register, reset) | 5 / minute per IP |
| Git webhooks | 10 / minute per workspace |
| Published docs (public) | 1,000 / minute per IP |

Rate limit responses include `Retry-After` (seconds) and `X-RateLimit-Reset` (Unix timestamp) headers.
