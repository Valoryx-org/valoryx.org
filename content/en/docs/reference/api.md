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

Create a new user account. Registration creates the user's own organization (they become its Super Admin) plus a starter workspace. Terms acceptance is required. Rate limited to 5 registrations per hour per IP.

**Request:**

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure-password-here",
  "terms_accepted": true
}
```

**Response:** `201 Created` with the user object; sign in via `/api/auth/login` to obtain tokens.

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
PATCH /api/v1/content/{workspace}/{...path}
```

Moving a page is a first-class operation. It preserves the stable `page_id` and updates all wikilinks across the workspace.

Include the new path in the request body:

```json
{
  "move_to": "new/path/for/page"
}
```

(`POST /api/v1/content/{workspace}/move` exists as a compatibility alias.)

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

Requires Super Admin role.

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

Full-text search within one workspace. Requires read access to that workspace; every query is scoped to it at the search-engine level.

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `q` | string | Search query (required) |
| `limit` | int | Max results (optional) |

Results include the matching pages with relevance scores and highlighted snippets.

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

### Webhook endpoint

```
POST /api/git/webhook/:workspace_id
```

A single endpoint that receives push event payloads from GitHub (`X-Hub-Signature-256`), GitLab (`X-Gitlab-Token`), or Bitbucket (`X-Hub-Signature`). Payloads are validated against the workspace's auto-generated **per-workspace webhook secret** (shown in Workspace Settings → Git). Pushes to branches other than the workspace's configured branch are ignored. Rate limited to 30/min.

### Sync conflicts

```
GET  /api/v1/workspaces/:id/sync/conflicts/:conflict_id          — Inspect a sync conflict (read access)
POST /api/v1/workspaces/:id/sync/conflicts/:conflict_id/resolve  — Apply a resolution (edit access; commits and pushes as you)
```

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

Transform text with one of six actions.

**Request:**

```json
{
  "action": "improve",
  "content": "This is the text to improve.",
  "language": "de"
}
```

**Actions:** `improve`, `simplify`, `expand`, `summarize`, `fix_grammar`, `translate` (only `translate` uses `language`). Unknown actions return a validation error. Returns `503 AI_DISABLED` when no AI provider is configured.

### Doc chat

```
POST /api/v1/ai/chat
```

Multi-turn conversation about workspace documentation.

**Request:**

```json
{
  "messages": [
    { "role": "user", "content": "How do I configure git sync?" }
  ]
}
```

---

## Invitations & share links

```
GET    /api/v1/workspaces/:id/invitations               — List pending invitations (admin)
POST   /api/v1/workspaces/:id/invitations               — Create invitation (admin)
DELETE /api/v1/workspaces/:id/invitations/:invitationId — Revoke invitation (admin)
GET    /api/v1/workspaces/:id/share-links               — List share links (admin)
POST   /api/v1/workspaces/:id/share-links               — Create a share link (admin)
DELETE /api/v1/workspaces/:id/share-links/:linkId       — Revoke a share link (admin)
POST   /api/v1/share-links/:token/use                   — Join a workspace via share link
```

Invitations are email-based and accepted via `POST /api/auth/invitations/accept`. Inviting an Editor or Admin counts against the plan's seat limit (`403 PLAN_LIMIT_REACHED` when full).

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

## Billing (Cloud edition only)

These routes exist only in the Cloud edition that powers app.valoryx.dev — the Community binary contains no billing code and returns `404` for all of them.

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

GDPR-compliant analytics with cookie consent. Reporting requires a plan with the analytics feature (included in Community Edition and Cloud Team/Business; not in Cloud Free — returns `403 PLAN_LIMIT`).

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
POST /api/v1/workspaces/:id/export   — Start the export
GET  /api/v1/workspaces/:id/export   — Check status / download
```

Export all published pages as a static HTML ZIP file.

---

## Outbound webhooks (not yet active)

Workspace admins can manage outbound webhook definitions:

```
GET    /api/v1/workspaces/:id/webhooks                 — List webhooks (admin)
POST   /api/v1/workspaces/:id/webhooks                 — Create webhook (admin)
GET    /api/v1/workspaces/:id/webhooks/:wid            — Get webhook (admin)
PUT    /api/v1/workspaces/:id/webhooks/:wid            — Update webhook (admin)
DELETE /api/v1/workspaces/:id/webhooks/:wid            — Delete webhook (admin)
GET    /api/v1/workspaces/:id/webhooks/:wid/deliveries — Delivery log (admin)
```

> ⚠️ **Outbound webhook delivery is not yet active.** Webhook definitions can be created and validated (URLs are SSRF-checked), but events are **not currently delivered** — the deliveries list will remain empty. Use the WebSocket event stream or the activity feed for change notifications until delivery ships.

---

## Comments

```
GET    /api/v1/workspaces/:id/comments?page={path}  — List comments (filter by page)
POST   /api/v1/workspaces/:id/comments              — Create a comment (commenter+)
PUT    /api/comments/:id                            — Edit a comment
DELETE /api/comments/:id                            — Delete a comment
POST   /api/comments/:id/resolve                    — Resolve a thread
POST   /api/comments/:id/unresolve                  — Reopen a thread
```

---

## Activity feed

```
GET /api/v1/workspaces/:id/activity?limit=50&action=page_created  — Workspace activity
GET /api/v1/workspaces/:id/page-activity?page={path}              — Per-page history
```

---

## GDPR / data portability (Cloud edition)

```
GET    /api/v1/users/me/export      — Export your personal data
DELETE /api/v1/users/me             — Delete your account (password-gated)
GET    /api/v1/orgs/:handle/export  — Export org data (org super admin)
```

Export endpoints are rate-limited to once per 24 hours.

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

## MCP server

DocPlatform includes a built-in MCP (Model Context Protocol) server exposing **26 tools** for AI agent integration. Two transports are available:

```bash
# stdio (single workspace, for local AI tools)
docplatform mcp --workspace my-docs --api-key dp_live_abc123

# Streamable HTTP (multi-workspace, for remote/cloud access)
docplatform mcp-server --addr :8081
```

### MCP tools (26)

| Tool | Category | Description |
|---|---|---|
| `docplatform_list_pages` | Content | List all pages with paths and titles |
| `docplatform_read_page` | Content | Read full page content, frontmatter, and metadata |
| `docplatform_write_page` | Content | Smart upsert — creates or updates automatically |
| `docplatform_update_page` | Content | Update with optimistic concurrency (requires `last_known_hash`) |
| `docplatform_delete_page` | Content | Soft-delete a page |
| `docplatform_move_page` | Content | Move/rename with automatic wikilink updates |
| `docplatform_search` | Discovery | Full-text search with scored results |
| `docplatform_get_context` | Discovery | RAG bundle: page + parent + siblings + linked pages |
| `docplatform_list_workspaces` | Discovery | List accessible workspaces |
| `docplatform_get_tree` | Discovery | Hierarchical page tree |
| `docplatform_get_manifest` | Discovery | Complete workspace manifest with link relationships |
| `docplatform_validate_links` | Quality | Scan for broken wikilinks |
| `docplatform_quality_scan` | Quality | Quality score (0–100) with detailed findings |
| `docplatform_get_theme` | Settings | Get current published site theme |
| `docplatform_update_theme` | Settings | Update theme (default, dark, forest, rose, amber, minimal, corporate) |
| `docplatform_create_workspace` | Management | Create a new workspace |
| `docplatform_get_workspace` | Management | Workspace details, role, git sync, publish settings |
| `docplatform_publish_workspace` | Management | Enable/disable the workspace's published site |
| `docplatform_list_versions` | Versioning | List documentation versions |
| `docplatform_create_version` | Versioning | Create a named version (e.g., v2.0) |
| `docplatform_export` | Export | Export workspace as static site |
| `docplatform_writing_assist` | AI | Improve, shorten, expand, fix grammar, summarize, translate |
| `docplatform_get_activity` | Activity | Recent workspace activity feed |
| `docplatform_list_comments` | Comments | Threaded comments on a page |
| `docplatform_add_comment` | Comments | Add a comment with @mentions and threading |
| `docplatform_resolve_sync_conflict` | Sync | Resolve a git-sync conflict (conditional — requires server-URL configuration) |

All tools respect workspace permissions and require a valid API key. See the [MCP Server guide](../guides/mcp.md) for complete setup and tool reference.

---

## Prometheus metrics

```
GET /metrics
```

Available on the main port when `FF_METRICS=true` (platform-owner authentication required). Alternatively, set `METRICS_PORT` to expose an unauthenticated `/metrics` listener bound to `127.0.0.1:{port}` for local scraping.

---

## Health

These endpoints use the unversioned `/api/` prefix and do not require authentication.

```
GET /api/health    → 200 OK { "status": "ok", "version": "v0.10.0" }
GET /api/ready     → 200 OK { "status": "ready", "checks": { ... } }
```

The `/api/ready` endpoint reports readiness of the database, git engine, and job outbox.

---

## Error format

Error responses share a single JSON shape:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "title is required",
  "details": { "field": "title" },
  "request_id": "01HJK..."
}
```

`details` is optional; `request_id` correlates with the server logs.

### Common error codes

| HTTP | Code | Description |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Invalid request body or parameters |
| `401` | `UNAUTHORIZED` | Missing or invalid authentication |
| `403` | `FORBIDDEN` | Insufficient permissions |
| `403` | `PLAN_LIMIT_REACHED` | Plan limit hit (Cloud edition) |
| `404` | `NOT_FOUND` | Resource not found (or no read access) |
| `409` | `CONFLICT` | Concurrent modification detected |
| `429` | `RATE_LIMITED` | Too many requests |
| `500` | `INTERNAL_ERROR` | Server error (check logs) |

## Pagination

List endpoints accept `limit` and `cursor` query parameters and return a `next_cursor` when more results are available:

```
GET /api/v1/workspaces/:id/activity?limit=50&cursor={cursor}
```

Pass the returned `next_cursor` as `cursor` in the next request.

---

## Uploads

```
POST /api/v1/content/{workspace}/uploads             — Upload a file (multipart/form-data, field "file")
GET  /api/v1/content/{workspace}/uploads/{filename}  — Serve an uploaded file
```

Uploads require edit permission. Files referenced by published pages on a `public`-visibility site are publicly readable. Upload size is bounded by the global 10 MB request body limit, with upload-bomb protection on archives.

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

Sets a `dp_ws_token` HttpOnly, SameSite=Strict cookie (valid for 1 hour).

Connect via:

```
ws://localhost:3000/ws
```

The browser sends the `dp_ws_token` cookie automatically; the server validates it and establishes the WebSocket.

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

---

## Security headers

DocPlatform sets the following headers:

| Header | Value |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `Content-Security-Policy` | Set per surface (API, published sites, SPA) with nonce-based policies |

`HSTS` and `X-Frame-Options` are left to the reverse proxy. Published docs additionally set:

| Header | Value |
|---|---|
| `Cache-Control` | `public, max-age=300` |
| `ETag` | Content hash of the rendered page |

---

## Rate limiting

HTTP rate limits are per category — per-org for authenticated requests, per-IP for unauthenticated:

| Endpoint category | Limit |
|---|---|
| Content read | 300/min |
| Content write | 60/min |
| Search | 60/min |
| Auth endpoints | 20/min |
| Registration | 5/hour per IP |
| Password reset | 5 per 15 min |
| Git webhooks | 30/min |
| Published docs (public) | 600/min |
| Data export (GDPR) | 1 per 24 h |

(The MCP transport has its own per-plan limits — see the [MCP guide](../guides/mcp.md).)

Rate limit responses include these headers:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
Retry-After: 30
```
