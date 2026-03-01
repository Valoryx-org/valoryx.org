---
title: REST-API-Referenz
description: Vollständige Referenz der REST-API von DocPlatform — Authentifizierung, Inhaltsverwaltung, Workspaces, Suche und Admin-Endpunkte.
weight: 1
---

# REST-API-Referenz

DocPlatform stellt eine RESTful-JSON-API unter `/api/v1/` bereit. Alle Endpunkte erfordern Authentifizierung, sofern nicht anders angegeben.

## Basis-URL

```
http://localhost:3000/api/v1
```

## Authentifizierung

Die meisten Endpunkte erfordern einen JWT-Access-Token im `Authorization`-Header:

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

Token erhalten Sie über die Login- oder OIDC-Endpunkte.

### Token-Lebenszyklus

| Token | Lebensdauer | Zweck |
|---|---|---|
| Access-Token | 15 Minuten | API-Authentifizierung |
| Refresh-Token | 30 Tage | Neue Access-Token erhalten |

---

## Auth-Endpunkte

### Registrieren

```
POST /api/v1/auth/register
```

Erstellt ein neues Benutzerkonto. Der erste Benutzer wird zum SuperAdmin.

**Anfrage:**

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Antwort:** `201 Created`

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

### Anmelden

```
POST /api/v1/auth/login
```

Authentifizierung mit E-Mail und Passwort.

**Anfrage:**

```json
{
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Antwort:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

**Fehler:**

| Code | Beschreibung |
|---|---|
| `401` | Ungültige Anmeldedaten |
| `429` | Zu viele Anmeldeversuche (Rate-Limit) |

### Token aktualisieren

```
POST /api/v1/auth/refresh
```

Tauscht einen Refresh-Token gegen einen neuen Access-Token. Der Refresh-Token wird rotiert (alter wird invalidiert).

**Anfrage:**

```json
{
  "refresh_token": "eyJhbG..."
}
```

**Antwort:** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

### Passwort-Zurücksetzung anfordern

```
POST /api/v1/auth/password-reset
```

Fordert einen Token zur Passwort-Zurücksetzung an. Mit konfiguriertem SMTP wird eine E-Mail gesendet. Ohne SMTP wird der Token auf stdout geloggt.

**Anfrage:**

```json
{
  "email": "jane@example.com"
}
```

**Antwort:** `200 OK` (immer, unabhängig davon, ob die E-Mail existiert — verhindert Enumeration)

### Passwort-Zurücksetzung bestätigen

```
POST /api/v1/auth/password-reset/confirm
```

Setzt ein neues Passwort mit einem Reset-Token.

**Anfrage:**

```json
{
  "token": "reset-token-here",
  "new_password": "new-secure-password"
}
```

**Antwort:** `200 OK`

---

## Inhalts-Endpunkte

Alle Inhalts-Endpunkte sind einem Workspace zugeordnet.

### Seiten auflisten

```
GET /api/v1/workspaces/{workspace_id}/pages
```

Gibt alle Seiten zurück, für die der aktuelle Benutzer Leserechte hat.

**Query-Parameter:**

| Parameter | Typ | Beschreibung |
|---|---|---|
| `parent_id` | string | Nach übergeordneter Seite filtern (für Baumnavigation) |
| `tag` | string | Nach Tag filtern |
| `published` | boolean | Nach Veröffentlichungsstatus filtern |
| `limit` | int | Maximale Ergebnisse (Standard: 100) |
| `offset` | int | Paginierungsoffset |

**Antwort:** `200 OK`

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

### Seite abrufen

```
GET /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Antwort:** `200 OK`

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

**Fehler:**

| Code | Beschreibung |
|---|---|
| `403` | Unzureichende Berechtigungen |
| `404` | Seite nicht gefunden |

### Seite erstellen

```
POST /api/v1/workspaces/{workspace_id}/pages
```

**Anfrage:**

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

**Antwort:** `201 Created` — gibt das vollständige Seitenobjekt zurück.

### Seite aktualisieren

```
PUT /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Anfrage:**

```json
{
  "title": "Updated Title",
  "content": "# Updated Title\n\nUpdated content...",
  "content_hash": "sha256:abc123..."
}
```

Das Feld `content_hash` ermöglicht optimistische Nebenläufigkeit. Wenn der Hash nicht mit der aktuellen Version übereinstimmt, gibt der Server `409 Conflict` zurück.

**Antwort:** `200 OK` — gibt das aktualisierte Seitenobjekt zurück.

**Fehler:**

| Code | Beschreibung |
|---|---|
| `409` | Content-Hash-Abweichung (gleichzeitige Bearbeitung erkannt) |

### Seite löschen

```
DELETE /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Antwort:** `204 No Content`

---

## Workspace-Endpunkte

### Workspaces auflisten

```
GET /api/v1/workspaces
```

Gibt Workspaces zurück, in denen der aktuelle Benutzer Mitglied ist.

### Workspace erstellen

```
POST /api/v1/workspaces
```

Erfordert die SuperAdmin-Rolle.

**Anfrage:**

```json
{
  "name": "API Docs",
  "slug": "api-docs",
  "git_remote": "git@github.com:org/api-docs.git",
  "git_branch": "main"
}
```

### Workspace-Mitglieder

```
GET /api/v1/workspaces/{workspace_id}/members
POST /api/v1/workspaces/{workspace_id}/invitations
DELETE /api/v1/workspaces/{workspace_id}/members/{user_id}
PUT /api/v1/workspaces/{workspace_id}/members/{user_id}/role
```

---

## Suche

```
GET /api/v1/workspaces/{workspace_id}/search?q={query}
```

**Query-Parameter:**

| Parameter | Typ | Beschreibung |
|---|---|---|
| `q` | string | Suchabfrage (erforderlich) |
| `tag` | string | Nach Tag filtern |
| `limit` | int | Maximale Ergebnisse (Standard: 20) |

**Antwort:** `200 OK`

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

Ergebnisse werden nach Berechtigungen gefiltert — Benutzer sehen nur Seiten, auf die sie Zugriff haben.

---

## Git-Synchronisation

### Synchronisation auslösen

```
POST /api/v1/workspaces/{workspace_id}/sync
```

Löst manuell einen Git-Pull + Reconciliation aus. Erfordert die Admin-Rolle.

**Antwort:** `200 OK`

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

### Webhook-Endpunkte

```
POST /api/v1/webhooks/github
POST /api/v1/webhooks/gitlab
POST /api/v1/webhooks/bitbucket
```

Diese Endpunkte empfangen Push-Event-Payloads von Git-Hosting-Anbietern. Kein Authentication-Header erforderlich — sie validieren über das `GIT_WEBHOOK_SECRET`-Shared-Secret.

---

## Health

Diese Endpunkte erfordern keine Authentifizierung.

```
GET /health    → 200 OK { "status": "ok" }
GET /ready     → 200 OK { "status": "ready", "db": "ok", "search": "ok" }
```

---

## Fehlerformat

Alle Fehlerantworten verwenden ein einheitliches Format:

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

### Häufige Fehlercodes

| HTTP | Code | Beschreibung |
|---|---|---|
| `400` | `BAD_REQUEST` | Ungültiger Anfragekörper oder Parameter |
| `401` | `UNAUTHORIZED` | Fehlende oder ungültige Authentifizierung |
| `403` | `FORBIDDEN` | Unzureichende Berechtigungen |
| `404` | `NOT_FOUND` | Ressource nicht gefunden |
| `409` | `CONFLICT` | Gleichzeitige Modifikation erkannt |
| `429` | `RATE_LIMITED` | Zu viele Anfragen |
| `500` | `INTERNAL_ERROR` | Serverfehler (Logs prüfen) |

## Paginierung

Inhaltsauflistungs-Endpunkte verwenden **Cursor-basierte Paginierung** mit ULIDs für stabile Ergebnisse, auch wenn Inhalte hinzugefügt oder gelöscht werden.

**Query-Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|---|---|---|---|
| `cursor` | string | — | ULID des letzten Elements der vorherigen Seite. Weglassen für die erste Seite. |
| `limit` | int | 20 | Anzahl der Ergebnisse pro Seite (max: 100) |

**Antwort-Metadaten:**

```json
{
  "data": [...],
  "next_cursor": "01HJK...",
  "has_more": true
}
```

Übergeben Sie `next_cursor` als `cursor`-Parameter in der nächsten Anfrage. Wenn `has_more` den Wert `false` hat, haben Sie das Ende erreicht.

---

## Asset-Uploads

```
POST /api/v1/workspaces/{workspace_id}/assets
```

Laden Sie Bilder und Dateien in einen Workspace hoch. Assets werden im `assets/`-Verzeichnis des Workspace gespeichert und in Git committet, wenn die Synchronisation aktiviert ist.

**Anfrage:** `multipart/form-data` mit einem `file`-Feld.

**Limits:**

| Einschränkung | Wert |
|---|---|
| Maximale Dateigröße | 10 MB |
| Akzeptierte Typen | PNG, JPG, GIF, SVG, WebP, PDF |

**Antwort:** `201 Created`

```json
{
  "path": "assets/screenshot-2025-01-15.png",
  "url": "/api/v1/workspaces/{workspace_id}/assets/screenshot-2025-01-15.png",
  "size": 245760,
  "content_type": "image/png"
}
```

---

## Konfliktauflösung

### Konflikte auflisten

```
GET /api/v1/workspaces/{workspace_id}/conflicts
```

**Antwort:** `200 OK`

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

### Konfliktversion herunterladen

```
GET /api/v1/conflicts/{page_id}/{timestamp}/{version}
```

Der `version`-Parameter ist entweder `ours` (lokal) oder `theirs` (remote).

**Antwort:** `200 OK` mit `Content-Type: text/markdown` — roher Dateiinhalt.

### Konflikt auflösen

```
POST /api/v1/conflicts/{page_id}/{timestamp}/resolve
```

Entfernt Konflikt-Artefakte nach manueller Auflösung.

**Antwort:** `200 OK`

```json
{
  "message": "Conflict resolved",
  "page_id": "01HJK..."
}
```

---

## WebSocket

### Verbindungs-Ticket erhalten

```
POST /api/v1/auth/ws-ticket
```

WebSocket-Verbindungen verwenden ein Einmal-Ticket-Verfahren, um zu vermeiden, dass JWT-Token in URLs offengelegt werden.

**Antwort:** `200 OK`

```json
{
  "ticket": "random-ticket-value",
  "expires_in": 30
}
```

Das Ticket ist **30 Sekunden** gültig und kann nur einmal verwendet werden. Verbinden Sie sich über:

```
ws://localhost:3000/ws?ticket={ticket}
```

### Server-Events

| Event-Typ | Payload | Wann |
|---|---|---|
| `page-created` | `{workspace_id, path, actor}` | Eine neue Seite wird erstellt |
| `page-updated` | `{workspace_id, path, actor}` | Eine Seite wird geändert |
| `page-deleted` | `{workspace_id, path, actor}` | Eine Seite wird gelöscht |
| `presence-join` | `{workspace_id, user_id}` | Ein Benutzer verbindet sich |
| `presence-leave` | `{workspace_id, user_id}` | Ein Benutzer trennt sich (90s Timeout) |
| `sync-status` | `{workspace_id, status}` | Git-Synchronisationsstatus ändert sich |
| `conflict-detected` | `{workspace_id, path}` | Git-Merge-Konflikt gefunden |
| `bulk-sync` | `{workspace_id, changed_count, paths[]}` | Mehrere Dateien synchronisiert (>20 Dateien) |

### Client-Nachrichten

```json
{"type": "subscribe", "workspace_id": "01HJK..."}
{"type": "unsubscribe", "workspace_id": "01HJK..."}
```

---

## Sicherheits-Header

DocPlatform setzt folgende Header auf allen Antworten:

| Header | Wert |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| `X-Request-ID` | ULID (eindeutig pro Anfrage, in Fehlerantworten und Logs enthalten) |

Veröffentlichte Dokumentation setzt zusätzlich:

| Header | Wert |
|---|---|
| `Cache-Control` | `public, max-age=300` |
| `ETag` | Content-Hash der gerenderten Seite |

---

## Rate-Limiting

| Endpunkt-Kategorie | Community Edition |
|---|---|
| Leseoperationen | 100 / Minute pro Benutzer |
| Schreiboperationen | 20 / Minute pro Benutzer |
| Suche | 30 / Minute pro Benutzer |
| Auth (Login, Registrierung, Zurücksetzung) | 5 / Minute pro IP |
| Git-Webhooks | 10 / Minute pro Workspace |
| Veröffentlichte Dokumentation (öffentlich) | 1.000 / Minute pro IP |

Rate-Limit-Antworten enthalten `Retry-After` (Sekunden) und `X-RateLimit-Reset` (Unix-Zeitstempel) Header.
