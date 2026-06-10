---
title: Teams & Collaboration
description: Invite your team, assign roles, and collaborate on documentation with real-time presence and audit trails.
weight: 4
---

# Teams & Collaboration

DocPlatform is designed for team documentation. Invite members, assign granular roles, and track every change with a full audit trail.

## Workspace membership

Every user belongs to one or more workspaces with a specific role. Roles determine what actions a user can perform.

### Invite members

**Via web UI:**

1. Open **Workspace Settings** → **Members**
2. Click **Invite Member**
3. Enter the person's email address
4. Select a role
5. Click **Send**

If SMTP is configured, an invitation email is sent with a unique link. Without SMTP, the invitation link is displayed on screen — copy and share it manually.

**Via API:**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{workspace-id}/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "colleague@example.com",
    "role": "editor"
  }'
```

### Remove members

Admins can remove members from **Settings** → **Members** → click the user → **Remove**.

Removing a member revokes their access immediately. Their past edits and audit log entries are preserved.

### Change roles

Click a member's current role to change it. Role changes take effect immediately — active sessions are updated on the next API call.

## Roles

DocPlatform uses a 5-level role hierarchy. Higher roles inherit all permissions of lower roles.

```
Super Admin
    └── Admin
            └── Editor
                  └── Commenter
                        └── Viewer
```

| Role | Scope | Capabilities |
|---|---|---|
| **Viewer** | Workspace | View pages and search |
| **Commenter** | Workspace | View + leave comments on pages |
| **Editor** | Workspace | View + comment + create, edit, delete pages |
| **Admin** | Workspace | Full workspace management (settings, git, theme, members) |
| **Super Admin** | Organization | Full access to all workspaces in the org + org settings and billing |

### Role at invitation

The role is chosen by the inviter at invitation time — there is no separate "default role" setting. To change someone's role later, use **Settings → Members**.

### Page-level access

Frontmatter `access` rules are **inconsistent — avoid them**: they are enforced on API reads while present, but the next git sync silently strips them from the file. Use workspace-level roles instead. See [Roles & Permissions](../configuration/permissions.md).

## Real-time presence

The server tracks who is online per workspace over authenticated WebSocket connections and broadcasts presence events in real time. **The current web UI does not yet display presence** — there are no online indicators or avatar stacks in the editor today. The events are available to custom clients built on the WebSocket API.

### How presence works

| Parameter | Value |
|---|---|
| **Protocol** | WebSocket (authenticated via the `dp_ws_token` HttpOnly cookie) |
| **Heartbeat interval** | Every 30 seconds |
| **Eviction timeout** | 90 seconds without heartbeat |
| **Events** | `presence-join`, `presence-update`, `presence-leave` |

The WebSocket connection also delivers real-time content events:

| Event | When |
|---|---|
| `page-created` | A new page is created (any source) |
| `page-updated` | A page is modified (any source) |
| `page-deleted` | A page is deleted |
| `page-moved` | A page is moved or renamed |
| `sync-status` | Git sync status changes (synced, ahead, behind, conflict) |
| `conflict-detected` | A git merge conflict is found |
| `bulk-sync` | Multiple files synced in one operation (single notification, not per-file) |

### Concurrent editing

DocPlatform does not support real-time collaborative editing (Google Docs-style). If two users edit the same page simultaneously:

1. The first save succeeds
2. The second save triggers a **conflict detection** (HTTP 409)
3. Both versions are preserved for manual resolution

To avoid conflicts:

- Use page-level ownership conventions (one writer per page at a time)
- Presence indicators help your team coordinate who's editing what
- For high-concurrency teams, consider shorter git sync intervals

## Activity feed

Every workspace has an activity feed recording who did what, when.

### Viewing activity

Open **Workspace Settings** → **Activity**, or use the API:

```bash
curl "http://localhost:3000/api/v1/workspaces/{id}/activity?limit=50&action=page_created" \
  -H "Authorization: Bearer {token}"
```

Per-page history is available at `GET /api/v1/workspaces/{id}/page-activity?page={path}`.

### Activity action types

Filter the feed with the `action` query parameter:

| Action | Description |
|---|---|
| `page_created` | New page created |
| `page_updated` | Page content or frontmatter modified |
| `page_deleted` | Page deleted |
| `comment_added` | Comment posted on a page |
| `comment_resolved` | Comment thread resolved |
| `member_joined` | User joined the workspace |
| `member_left` | User left or was removed |
| `sync_completed` | Git sync finished |

### Retention

Activity records are stored in SQLite alongside your regular data and included in daily backups.

## Email notifications

With SMTP configured, DocPlatform sends transactional emails for:

| Event | Recipient | Content |
|---|---|---|
| **Workspace invitation** | Invited user | Join link + workspace name |
| **Password reset** | Requesting user | One-time reset token |

DocPlatform does not send notification emails for content changes. Real-time WebSocket updates serve that purpose for active users, and the audit log covers historical review.

### SMTP configuration

```bash
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_FROM=docs@yourcompany.com
export SMTP_USERNAME=docs@yourcompany.com
export SMTP_PASSWORD=your-app-password
```

Without email configured, invitation and password-reset emails are simply not sent — links and tokens are **not** written to the server logs. For password resets, an admin can generate a one-time link with [`docplatform reset-password`](../reference/cli.md).

## Tips for team workflows

- **One writer per page** — use presence indicators to avoid conflicts
- **Editors write, reviewers publish** — drafts stay off the published site until someone sets `publish: true`
- **Use tags for ownership** — tag pages with `owner:jane` to clarify responsibility
- **Git for review workflows** — push changes to a branch, open a PR, merge after review
- **Review before publish** — check the activity feed for unexpected changes before making content public
