---
title: Referencia de la API REST
description: Referencia completa de la API REST de DocPlatform — autenticación, gestión de contenido, workspaces, búsqueda y endpoints de administración.
weight: 1
---

# Referencia de la API REST

DocPlatform expone una API JSON RESTful en `/api/v1/`. Todos los endpoints requieren autenticación a menos que se indique lo contrario.

## URL base

```
http://localhost:3000/api/v1
```

## Autenticación

La mayoría de los endpoints requieren un token de acceso JWT en el header `Authorization`:

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

Obtenga tokens mediante los endpoints de login o OIDC.

### Ciclo de vida del token

| Token | Tiempo de vida | Propósito |
|---|---|---|
| Token de acceso | 15 minutos | Autenticación de API |
| Token de actualización | 30 días | Obtener nuevos tokens de acceso |

---

## Endpoints de autenticación

### Registro

```
POST /api/v1/auth/register
```

Cree una nueva cuenta de usuario. El primer usuario se convierte en SuperAdmin.

**Solicitud:**

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Respuesta:** `201 Created`

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

### Inicio de sesión

```
POST /api/v1/auth/login
```

Autentíquese con correo electrónico y contraseña.

**Solicitud:**

```json
{
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Respuesta:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

**Errores:**

| Código | Descripción |
|---|---|
| `401` | Credenciales inválidas |
| `429` | Demasiados intentos de inicio de sesión (limitación de tasa) |

### Actualizar token

```
POST /api/v1/auth/refresh
```

Intercambie un token de actualización por un nuevo token de acceso. El token de actualización se rota (el anterior se invalida).

**Solicitud:**

```json
{
  "refresh_token": "eyJhbG..."
}
```

**Respuesta:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

### Solicitud de restablecimiento de contraseña

```
POST /api/v1/auth/password-reset
```

Solicite un token de restablecimiento de contraseña. Con SMTP configurado, se envía un correo electrónico. Sin SMTP, el token se registra en stdout.

**Solicitud:**

```json
{
  "email": "jane@example.com"
}
```

**Respuesta:** `200 OK` (siempre, independientemente de si el correo existe — previene enumeración)

### Confirmación de restablecimiento de contraseña

```
POST /api/v1/auth/password-reset/confirm
```

Establezca una nueva contraseña usando un token de restablecimiento.

**Solicitud:**

```json
{
  "token": "reset-token-here",
  "new_password": "new-secure-password"
}
```

**Respuesta:** `200 OK`

---

## Endpoints de contenido

Todos los endpoints de contenido están limitados a un workspace.

### Listar páginas

```
GET /api/v1/workspaces/{workspace_id}/pages
```

Devuelve todas las páginas que el usuario actual tiene permiso para ver.

**Parámetros de consulta:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `parent_id` | string | Filtrar por página padre (para navegación en árbol) |
| `tag` | string | Filtrar por etiqueta |
| `published` | boolean | Filtrar por estado de publicación |
| `limit` | int | Máximo de resultados (predeterminado: 100) |
| `offset` | int | Desplazamiento de paginación |

**Respuesta:** `200 OK`

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

### Obtener página

```
GET /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Respuesta:** `200 OK`

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

**Errores:**

| Código | Descripción |
|---|---|
| `403` | Permisos insuficientes |
| `404` | Página no encontrada |

### Crear página

```
POST /api/v1/workspaces/{workspace_id}/pages
```

**Solicitud:**

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

**Respuesta:** `201 Created` — devuelve el objeto completo de la página.

### Actualizar página

```
PUT /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Solicitud:**

```json
{
  "title": "Updated Title",
  "content": "# Updated Title\n\nUpdated content...",
  "content_hash": "sha256:abc123..."
}
```

El campo `content_hash` habilita concurrencia optimista. Si el hash no coincide con la versión actual, el servidor devuelve `409 Conflict`.

**Respuesta:** `200 OK` — devuelve el objeto de página actualizado.

**Errores:**

| Código | Descripción |
|---|---|
| `409` | Hash de contenido no coincide (edición concurrente detectada) |

### Eliminar página

```
DELETE /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Respuesta:** `204 No Content`

---

## Endpoints de workspace

### Listar workspaces

```
GET /api/v1/workspaces
```

Devuelve los workspaces de los que el usuario actual es miembro.

### Crear workspace

```
POST /api/v1/workspaces
```

Requiere rol SuperAdmin.

**Solicitud:**

```json
{
  "name": "API Docs",
  "slug": "api-docs",
  "git_remote": "git@github.com:org/api-docs.git",
  "git_branch": "main"
}
```

### Miembros del workspace

```
GET /api/v1/workspaces/{workspace_id}/members
POST /api/v1/workspaces/{workspace_id}/invitations
DELETE /api/v1/workspaces/{workspace_id}/members/{user_id}
PUT /api/v1/workspaces/{workspace_id}/members/{user_id}/role
```

---

## Búsqueda

```
GET /api/v1/workspaces/{workspace_id}/search?q={query}
```

**Parámetros de consulta:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `q` | string | Consulta de búsqueda (obligatorio) |
| `tag` | string | Filtrar por etiqueta |
| `limit` | int | Máximo de resultados (predeterminado: 20) |

**Respuesta:** `200 OK`

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

Los resultados están filtrados por permisos — los usuarios solo ven páginas a las que tienen acceso.

---

## Sincronización git

### Activar sincronización

```
POST /api/v1/workspaces/{workspace_id}/sync
```

Active manualmente un git pull + reconciliación. Requiere rol Admin.

**Respuesta:** `200 OK`

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

### Endpoints de webhook

```
POST /api/v1/webhooks/github
POST /api/v1/webhooks/gitlab
POST /api/v1/webhooks/bitbucket
```

Estos endpoints reciben payloads de eventos push de proveedores de hosting git. No requieren header de autenticación — validan usando el secreto compartido `GIT_WEBHOOK_SECRET`.

---

## Salud

Estos endpoints no requieren autenticación.

```
GET /health    → 200 OK { "status": "ok" }
GET /ready     → 200 OK { "status": "ready", "db": "ok", "search": "ok" }
```

---

## Formato de errores

Todas las respuestas de error usan un formato consistente:

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

### Códigos de error comunes

| HTTP | Código | Descripción |
|---|---|---|
| `400` | `BAD_REQUEST` | Cuerpo de solicitud o parámetros inválidos |
| `401` | `UNAUTHORIZED` | Autenticación faltante o inválida |
| `403` | `FORBIDDEN` | Permisos insuficientes |
| `404` | `NOT_FOUND` | Recurso no encontrado |
| `409` | `CONFLICT` | Modificación concurrente detectada |
| `429` | `RATE_LIMITED` | Demasiadas solicitudes |
| `500` | `INTERNAL_ERROR` | Error del servidor (verifique los logs) |

## Paginación

Los endpoints de listado de contenido usan **paginación basada en cursor** con ULIDs para resultados estables incluso cuando se agrega o elimina contenido.

**Parámetros de consulta:**

| Parámetro | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `cursor` | string | — | ULID del último elemento de la página anterior. Omita para la primera página. |
| `limit` | int | 20 | Número de resultados por página (máximo: 100) |

**Metadatos de respuesta:**

```json
{
  "data": [...],
  "next_cursor": "01HJK...",
  "has_more": true
}
```

Pase `next_cursor` como el parámetro `cursor` en la siguiente solicitud. Cuando `has_more` es `false`, ha llegado al final.

---

## Subida de assets

```
POST /api/v1/workspaces/{workspace_id}/assets
```

Suba imágenes y archivos a un workspace. Los assets se almacenan en el directorio `assets/` del workspace y se confirman en git si la sincronización está habilitada.

**Solicitud:** `multipart/form-data` con un campo `file`.

**Límites:**

| Restricción | Valor |
|---|---|
| Tamaño máximo de archivo | 10 MB |
| Tipos aceptados | PNG, JPG, GIF, SVG, WebP, PDF |

**Respuesta:** `201 Created`

```json
{
  "path": "assets/screenshot-2025-01-15.png",
  "url": "/api/v1/workspaces/{workspace_id}/assets/screenshot-2025-01-15.png",
  "size": 245760,
  "content_type": "image/png"
}
```

---

## Resolución de conflictos

### Listar conflictos

```
GET /api/v1/workspaces/{workspace_id}/conflicts
```

**Respuesta:** `200 OK`

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

### Descargar una versión del conflicto

```
GET /api/v1/conflicts/{page_id}/{timestamp}/{version}
```

El parámetro `version` es `ours` (local) o `theirs` (remoto).

**Respuesta:** `200 OK` con `Content-Type: text/markdown` — contenido del archivo sin procesar.

### Resolver un conflicto

```
POST /api/v1/conflicts/{page_id}/{timestamp}/resolve
```

Elimina los artefactos de conflicto después de la resolución manual.

**Respuesta:** `200 OK`

```json
{
  "message": "Conflict resolved",
  "page_id": "01HJK..."
}
```

---

## WebSocket

### Obtener un ticket de conexión

```
POST /api/v1/auth/ws-ticket
```

Las conexiones WebSocket usan un patrón de ticket de un solo uso para evitar exponer tokens JWT en URLs.

**Respuesta:** `200 OK`

```json
{
  "ticket": "random-ticket-value",
  "expires_in": 30
}
```

El ticket es válido durante **30 segundos** y solo puede usarse una vez. Conéctese mediante:

```
ws://localhost:3000/ws?ticket={ticket}
```

### Eventos del servidor

| Tipo de evento | Payload | Cuándo |
|---|---|---|
| `page-created` | `{workspace_id, path, actor}` | Se crea una nueva página |
| `page-updated` | `{workspace_id, path, actor}` | Se modifica una página |
| `page-deleted` | `{workspace_id, path, actor}` | Se elimina una página |
| `presence-join` | `{workspace_id, user_id}` | Un usuario se conecta |
| `presence-leave` | `{workspace_id, user_id}` | Un usuario se desconecta (timeout de 90s) |
| `sync-status` | `{workspace_id, status}` | Cambio de estado de sincronización git |
| `conflict-detected` | `{workspace_id, path}` | Se encuentra un conflicto de merge en git |
| `bulk-sync` | `{workspace_id, changed_count, paths[]}` | Múltiples archivos sincronizados (>20 archivos) |

### Mensajes del cliente

```json
{"type": "subscribe", "workspace_id": "01HJK..."}
{"type": "unsubscribe", "workspace_id": "01HJK..."}
```

---

## Headers de seguridad

DocPlatform establece los siguientes headers en todas las respuestas:

| Header | Valor |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| `X-Request-ID` | ULID (único por solicitud, incluido en respuestas de error y logs) |

La documentación publicada adicionalmente establece:

| Header | Valor |
|---|---|
| `Cache-Control` | `public, max-age=300` |
| `ETag` | Hash del contenido de la página renderizada |

---

## Limitación de tasa

| Categoría de endpoint | Community Edition |
|---|---|
| Operaciones de lectura | 100 / minuto por usuario |
| Operaciones de escritura | 20 / minuto por usuario |
| Búsqueda | 30 / minuto por usuario |
| Autenticación (login, registro, restablecimiento) | 5 / minuto por IP |
| Webhooks de git | 10 / minuto por workspace |
| Documentación publicada (pública) | 1.000 / minuto por IP |

Las respuestas de limitación de tasa incluyen los headers `Retry-After` (segundos) y `X-RateLimit-Reset` (marca de tiempo Unix).
