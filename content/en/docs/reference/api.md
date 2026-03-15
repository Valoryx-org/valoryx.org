---
title: REST API Reference
description: Complete reference for DocPlatform's REST API — authentication, content management, workspaces, search, and admin endpoints.
weight: 1
---

# REST API Reference

DocPlatform exposes a RESTful JSON API. Business endpoints live under `/api/v1/`, while infrastructure endpoints (auth, health, git webhooks) use the unversioned `/api/` prefix.

## Base URLs

```
/api/v1/*   — business endpoints (content, workspaces, search, admin)
/api/*      — infrastructure endpoints (auth, health, git webhook, AI)
```

## API Quickstart

### Create a page

```bash
# 1. Create a new page
curl -X POST https://app.example.com/api/v1/content/{workspace_id}/guides/deployment \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deployment Guide",
    "body": "# Deployment\n\nFollow these steps to deploy DocPlatform.",
    "tags": ["devops", "getting-started"],
    "publish": false
  }'
# Response: 201 Created
# If page already exists: 409 Conflict — use PUT to update
```

### Update a page (read-modify-write)

Updating requires a three-step flow to prevent concurrent edit conflicts:

```bash
# 1. Read the page to get the current content_hash
curl https://app.example.com/api/v1/content/{workspace_id}/guides/deployment \
  -H "Authorization: Bearer {token}"
# Response includes: "content_hash": "sha256:abc123..."

# 2. Modify the content locally, then PUT with the hash
curl -X PUT https://app.example.com/api/v1/content/{workspace_id}/guides/deployment \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "# Deployment\n\nUpdated deployment instructions...",
    "lastKnownHash": "sha256:abc123...",
    "frontmatter": {
      "title": "Deployment Guide (v2)"
    }
  }'
# Response: 200 OK with updated page

# If someone else edited the page since you read it:
# Response: 409 Conflict with current_hash — re-read and retry
```

### When to use POST vs PUT

| Scenario | Method | What happens |
|----------|--------|-------------|
| Creating a brand new page | `POST` | 201 if created, 409 if path already taken |
| Updating an existing page | `PUT` | 200 if hash matches, 409 if page was modified by someone else |
| Page might or might not exist (scripts, imports) | `POST`, catch 409, then `PUT` | Safe upsert pattern |
| AI agent writing via MCP | `write_page` tool | Handles create/update automatically |

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
| Refresh token | 7 days | Obtain new access tokens (rotated on each use) |

### API keys

For programmatic access (CI/CD, MCP, scripts), use API keys instead of JWT tokens. API keys use the `dp_live_` prefix and are scoped to specific workspaces and permissions.

```
Authorization: Bearer dp_live_abc123...
```

Create API keys from **Workspace Settings** → **API Keys**.

---

## Auth endpoints

Auth endpoints use the unversioned `/api/auth/` prefix.

### Register

```
POST /api/auth/register
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
POST /api/auth/login
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
POST /api/auth/refresh
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
POST /api/auth/forgot-password
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
POST /api/auth/reset-password
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

### OIDC providers

```
GET  /api/auth/providers          — List available OIDC providers
POST /api/auth/oidc/:provider     — Start OIDC flow (google or github)
GET  /api/auth/oidc/:provider/callback  — OIDC callback
POST /api/auth/oidc/claim         — Claim OIDC tokens after callback
```

### WebAuthn / Passkeys

```
POST   /api/auth/webauthn/register/begin   — Start passkey registration
POST   /api/auth/webauthn/register/finish  — Complete passkey registration
POST   /api/auth/webauthn/login/begin      — Start passkey login
POST   /api/auth/webauthn/login/finish     — Complete passkey login
GET    /api/auth/webauthn/credentials      — List stored credentials
DELETE /api/auth/webauthn/credentials/:id  — Delete a credential
```

### Other auth endpoints

```
POST /api/auth/logout                   — Logout (revoke refresh token)
GET  /api/auth/me                       — Current user info
GET  /api/auth/sessions                 — List active sessions
POST /api/auth/ws-token                 — Set WebSocket auth cookie
POST /api/auth/invitations/accept       — Accept workspace invitation
```

---

## Content endpoints

Content is addressed by **workspace slug and file path**, not by ID. All content endpoints use the `/api/v1/content/{workspace}/{...path}` pattern.

### Get page

```
GET /api/v1/content/{workspace}/{...path}
```

Retrieve a page by its workspace slug and file path.

**Example:** `GET /api/v1/content/my-docs/guides/getting-started`

**Response:** `200 OK`

```json
{
  "page_id": "01HJK...",
  "path": "guides/getting-started.md",
  "title": "Getting Started",
  "description": "Install and configure DocPlatform.",
  "content": "# Getting Started\n\nThis guide walks you through...",
  "content_hash": "sha256:abc123...",
  "frontmatter_hash": "sha256:def456...",
  "tags": ["guide"],
  "status": "published",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-16T14:30:00Z"
}
```

**Errors:**

| Code | Description |
|---|---|
| `403` | Insufficient permissions |
| `404` | Page not found or no read access |

### Create page

```
POST /api/v1/content/{workspace}/{...path}
```

Create a new page at the given path. Returns `409 Conflict` if a page already exists at this path — use PUT to update existing pages.

**Request:**

```json
{
  "title": "Getting Started",
  "body": "# Getting Started\n\nWelcome to DocPlatform.",
  "description": "Optional description",
  "publish": false,
  "tags": ["quickstart"]
}
```

**Response:** `201 Created` with the page object.

**Errors:**

| Code | Description |
|---|---|
| `409` | Page already exists at this path — use PUT to update |
| `400` | Missing title or invalid path |
| `403` | Insufficient permissions (requires write role) |

### Update page

```
PUT /api/v1/content/{workspace}/{...path}
```

Update an existing page. Requires `lastKnownHash` for optimistic concurrency control — read the page first to get the current hash.

**Request:**

```json
{
  "body": "# Getting Started\n\nUpdated content...",
  "lastKnownHash": "sha256:abc123...",
  "frontmatter": {
    "title": "Updated Title",
    "tags": ["updated"]
  }
}
```

The `lastKnownHash` field enables **optimistic concurrency**. Echo the `content_hash` from the server's last response. If the hash doesn't match the current version, the server returns `409 Conflict`. For new pages, omit `lastKnownHash`.

**Response:** `200 OK` — returns the full page object with updated hashes.

**Errors:**

| Code | Description |
|---|---|
| `409` | Content hash mismatch — concurrent edit detected. Response includes `current_hash`, `your_hash`, `modified_by`, `modified_at`. |

### Delete page

```
DELETE /api/v1/content/{workspace}/{...path}
```

**Response:** `204 No Content`

### Move/Rename page

```
PUT /api/v1/content/{workspace}/{...path}
```

Moving a page is a first-class operation. It preserves the stable `page_id`, updates all wikilinks across the workspace, and creates redirect aliases for the old URL.

Include the `move_to` field in the request body:

```json
{
  "move_to": "new/path/for/page"
}
```

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

### Get workspace

```
GET /api/v1/workspaces/:id
```

### Delete workspace

```
DELETE /api/v1/workspaces/:id
```

Soft-deletes the workspace.

### Page tree

```
GET /api/v1/content/:workspace/tree
```

Returns the hierarchical page tree for a workspace, including nested structure and ordering.

### Reorder pages

```
POST /api/v1/content/:workspace/reorder
```

Reorder pages within a tree level. Requires write permission.

**Request:**

```json
{
  "parent_path": "guides",
  "order": [
    { "id": "01HJK...", "sort_order": 0 },
    { "id": "01HJL...", "sort_order": 1 },
    { "id": "01HJM...", "sort_order": 2 }
  ]
}
```

**Response:** `204 No Content`

---

## Search

```
GET /api/v1/workspaces/:id/search?q={query}
```

Full-text search across workspaces the user has access to.

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `q` | string | Search query (required) |
| `workspace` | string | Filter by workspace slug |
| `tag` | string | Filter by tag |
| `limit` | int | Max results (default: 20) |

**Response:** `200 OK`

```json
{
  "results": [
    {
      "page_id": "01HJK...",
      "title": "Git Integration",
      "path": "guides/git-integration.md",
      "score": 0.95,
      "snippet": "...bidirectional <mark>git sync</mark> lets your team..."
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

Manually trigger a git pull + reconciliation. Requires workspace_admin role.

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

### Webhook endpoint

```
POST /api/git/webhook/:workspace_id
```

A single endpoint that receives push event payloads from GitHub, GitLab, or Bitbucket. The payload format is auto-detected. No authentication header required — payloads are validated using the `GIT_WEBHOOK_SECRET` shared secret (HMAC-SHA256).

---

## AI features

### AI status

```
GET /api/v1/ai/status
```

Check whether AI features are enabled and which provider is configured.

### Writing assist

```
POST /api/v1/ai/writing-assist
```

Rewrite, improve, shorten, or expand selected content.

**Request:**

```json
{
  "workspace_id": "01HJK...",
  "operation": "improve",
  "content": "This is the text to improve."
}
```

**Operations:** `rewrite`, `improve`, `shorten`, `expand`

**Response:** `200 OK`

```json
{
  "result": "Here is the improved text..."
}
```

### Doc chat

```
POST /api/v1/ai/chat
```

Multi-turn conversation about workspace documentation.

**Request:**

```json
{
  "workspace_id": "01HJK...",
  "messages": [
    { "role": "user", "content": "How do I configure git sync?" }
  ]
}
```

---

## Invitations

```
GET    /api/v1/workspaces/:id/invitations              — List pending invitations (admin)
POST   /api/v1/workspaces/:id/invitations              — Create invitation (admin)
DELETE /api/v1/workspaces/:id/invitations/:invitationId — Revoke invitation (admin)
```

Invitations are email-based with a 7-day TTL. Accepted via `POST /api/auth/invitations/accept`.

---

## API keys

```
POST   /api/v1/api-keys           — Create API key (returns full key once)
GET    /api/v1/api-keys           — List API keys (prefix only)
DELETE /api/v1/api-keys/:id       — Delete API key
POST   /api/v1/api-keys/:id/rotate — Rotate API key
```

API keys use the `dp_live_` prefix and are scoped to the organization.

---

## Billing

Requires Stripe configuration. Disabled when `STRIPE_SECRET_KEY` is not set.

```
POST /api/v1/billing/checkout       — Create Stripe Checkout session
POST /api/v1/billing/portal         — Create Stripe Customer Portal session
GET  /api/v1/billing/subscription   — Current subscription status
GET  /api/v1/billing/plans          — Available plans and pricing
GET  /api/v1/billing/limits         — Plan limits and current usage
```

### Stripe webhook

```
POST /api/webhooks/stripe
```

Receives Stripe webhook events (signature-verified). Handles subscription lifecycle events with idempotency.

---

## Analytics

GDPR-compliant analytics with cookie consent. Feature-gated to paid plans.

```
POST /api/analytics/consent                          — Record GDPR consent
GET  /api/v1/workspaces/:id/analytics/pages          — Top pages (configurable days)
GET  /api/v1/workspaces/:id/analytics/searches       — Top search queries
GET  /api/v1/workspaces/:id/analytics/overview       — Dashboard overview
```

---

## Doc versioning

Named documentation versions (e.g., v1, v2) within a workspace.

```
GET    /api/v1/workspaces/:id/versions              — List versions
POST   /api/v1/workspaces/:id/versions              — Create version (admin)
GET    /api/v1/workspaces/:id/versions/:slug         — Get version details
PUT    /api/v1/workspaces/:id/versions/:slug/default — Set default version (admin)
DELETE /api/v1/workspaces/:id/versions/:slug         — Delete version (admin)
```

---

## Templates

```
GET /api/v1/templates      — List available templates
GET /api/v1/templates/:id  — Get template content
```

---

## Quality scanner

```
GET /api/v1/workspaces/:id/quality
```

Scan a workspace for documentation quality issues. Returns readability scores, dead links, and completeness checks.

---

## Static export

```
GET /api/v1/workspaces/:id/export
```

Export all published pages as a static HTML ZIP file.

---

## Custom domains

```
PUT    /api/v1/workspaces/:id/custom-domain  — Set custom domain (admin)
GET    /api/v1/workspaces/:id/custom-domain  — Get domain status (admin)
DELETE /api/v1/workspaces/:id/custom-domain  — Remove domain (admin)
```

---

## Workspace admin

```
GET /api/v1/workspaces/:id/admin/members              — List members
PUT /api/v1/workspaces/:id/admin/members/:user_id/role — Update member role
GET /api/v1/workspaces/:id/admin/settings              — Get workspace settings
PUT /api/v1/workspaces/:id/admin/settings              — Update workspace settings
```

---

## Onboarding

```
GET   /api/v1/users/me/onboarding  — Get onboarding state
PATCH /api/v1/users/me/onboarding  — Update onboarding state
```

---

## Super admin panel

These endpoints require the `super_admin` role. All prefixed with `/api/v1/admin/`.

### Organization management

```
GET  /api/v1/admin/orgs                          — List all organizations
GET  /api/v1/admin/orgs/:id                      — Get organization details
PUT  /api/v1/admin/orgs/:id/plan                 — Change organization plan
POST /api/v1/admin/orgs/:id/subscription/override — Override subscription
PUT  /api/v1/admin/orgs/:id/rate-limits          — Override rate limits
POST /api/v1/admin/orgs/:id/export               — Export org data (GDPR)
```

### User management

```
GET    /api/v1/admin/users              — List all users
GET    /api/v1/admin/users/:id          — Get user details
POST   /api/v1/admin/users/:id/impersonate — Impersonate user
POST   /api/v1/admin/users/:id/export   — Export user data (GDPR)
DELETE /api/v1/admin/users/:id          — Delete user (GDPR right to erasure)
```

### Audit log

```
GET /api/v1/admin/audit-log    — Query audit log (filterable by user, action, resource, date range)
```

### Billing overview

```
GET /api/v1/admin/billing/overview       — Platform-wide billing summary
GET /api/v1/admin/billing/subscriptions  — All active subscriptions
GET /api/v1/admin/billing/events         — Webhook event log
```

### Domain management

```
GET    /api/v1/admin/domains              — List all custom domains
POST   /api/v1/admin/domains/:id/verify   — Verify domain DNS
POST   /api/v1/admin/domains/:id/provision — Provision TLS certificate
DELETE /api/v1/admin/domains/:id          — Delete domain
```

### System health

```
GET /api/v1/admin/system/health    — System health metrics (disk, memory, uptime, DB stats)
```

### Platform analytics

```
GET /api/v1/admin/analytics/overview  — Platform-wide analytics overview
GET /api/v1/admin/analytics/growth    — Platform growth metrics
```

---

## MCP server

DocPlatform includes a built-in MCP (Model Context Protocol) server exposing 13 tools for AI agent integration. The MCP server runs on stdio and is started via the CLI:

```bash
docplatform mcp --workspace my-docs --api-key dp_live_abc123
```

### MCP tools

| Tool | Category | Description |
|---|---|---|
| `get_page` | Read | Fetch page content by path |
| `list_pages` | Read | List all pages with metadata |
| `get_page_tree` | Read | Hierarchical page tree |
| `get_page_metadata` | Read | Frontmatter, tags, timestamps |
| `get_page_links` | Read | Inbound/outbound wikilinks |
| `search` | Search | Full-text search with snippets |
| `search_by_tag` | Search | Find pages by tag |
| `create_page` | Write | Create a new page |
| `update_page` | Write | Update with concurrency check |
| `move_page` | Write | Move/rename with wikilink updates |
| `delete_page` | Write | Delete a page |
| `quality_check` | Maintain | Readability, dead links, completeness |
| `workspace_stats` | Maintain | Page count, word count, health summary |

All tools respect workspace permissions and require a valid API key. See the [AI Features guide](../guides/ai-features.md) for setup instructions.

---

## Prometheus metrics

```
GET /metrics
```

Available when `FF_METRICS=true`. Requires super admin authentication. Exposes HTTP latency histograms, request counts, auth event counters, and more.

---

## Health

These endpoints use the unversioned `/api/` prefix and do not require authentication.

```
GET /api/health    → 200 OK { "status": "ok", "db": "ok", "git": "ok" }
GET /api/ready     → 200 OK { "status": "ready" }
```

The `/api/ready` endpoint returns `503 Service Unavailable` while the initial reconciliation is in progress (startup).

---

## Error format

All error responses follow [RFC 7807](https://datatracker.ietf.org/doc/html/rfc7807) (Problem Details for HTTP APIs):

```json
{
  "type": "https://docplatform.io/errors/conflict-detected",
  "title": "Conflict Detected",
  "status": 409,
  "detail": "Content hash mismatch. The page was modified by another user.",
  "current_hash": "sha256:def456...",
  "your_hash": "sha256:abc123...",
  "modified_by": "jane@example.com",
  "modified_at": "2025-01-16T14:30:00Z"
}
```

Validation errors include a `fields` array:

```json
{
  "type": "https://docplatform.io/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "One or more fields are invalid.",
  "fields": [
    { "field": "content", "error": "required" },
    { "field": "lastKnownHash", "error": "must be 64 hex characters" }
  ]
}
```

### Common error codes

| HTTP | Code | Description |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Invalid request body or parameters |
| `401` | `UNAUTHORIZED` | Missing or invalid authentication |
| `403` | `FORBIDDEN` | Insufficient permissions |
| `404` | `NOT_FOUND` | Resource not found (or no read access) |
| `409` | `CONFLICT_DETECTED` | Concurrent modification detected |
| `422` | `UNPROCESSABLE` | Valid syntax but semantic error (e.g., circular wikilink) |
| `429` | `RATE_LIMITED` | Too many requests |
| `500` | `INTERNAL_ERROR` | Server error (check logs) |
| `503` | `SERVICE_UNAVAILABLE` | Reconciliation in progress |

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
POST /api/v1/content/{workspace}/assets
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
  "url": "/api/v1/content/{workspace}/assets/screenshot-2025-01-15.png",
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

### Obtain a WebSocket auth cookie

```
POST /api/auth/ws-token
```

WebSocket connections use an HttpOnly cookie mechanism to avoid exposing tokens in URLs.

**Response:** `200 OK`

Sets a `dp_ws_token` HttpOnly cookie (valid for **30 seconds**, single-use). No JSON body is returned.

Connect via:

```
ws://localhost:3000/ws
```

The browser sends the `dp_ws_token` cookie automatically. The server validates it, establishes the WebSocket, and clears the cookie.

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
| `page-moved` | `{workspace_id, old_path, new_path, actor}` | A page is moved/renamed |
| `bulk-sync` | `{workspace_id, changed_count, paths[]}` | Multiple files synced in one pull |

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

Rate limits are tier-based and scale with your plan. Token bucket algorithm, per-org for authenticated requests, per-IP for unauthenticated.

| Endpoint category | Community / Free | Team | Business | Enterprise |
|---|---|---|---|---|
| Content read | 100/min | 300/min | 600/min | 1,200/min |
| Content write | 20/min | 60/min | 120/min | 300/min |
| Search | 30/min | 100/min | 200/min | 500/min |
| Auth (login, register, reset) | 5/min per IP | 5/min | 5/min | 5/min |
| Git webhooks | 10/min | 30/min | 60/min | 120/min |
| Published docs (public) | 1,000/min per IP | 3,000/min | 6,000/min | Unlimited |

Rate limit responses include these headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
Retry-After: 30
```
