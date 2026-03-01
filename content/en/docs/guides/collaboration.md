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

Workspace Admins can remove members from **Settings** → **Members** → click the user → **Remove**.

Removing a member revokes their access immediately. Their past edits and audit log entries are preserved.

### Change roles

Click a member's current role to change it. Role changes take effect immediately — active sessions are updated on the next API call.

## Roles

DocPlatform uses a 6-level role hierarchy. Higher roles inherit all permissions of lower roles.

```
SuperAdmin
    └── WorkspaceAdmin
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
| **Admin** | Workspace | Editor + manage members and roles |
| **WorkspaceAdmin** | Workspace | Admin + manage workspace settings, git config, theme |
| **SuperAdmin** | Platform | Full access to all workspaces + platform settings |

### Default role for new members

Configure the default role assigned when users accept an invitation:

```yaml
# .docplatform/config.yaml
permissions:
  default_role: viewer
```

### Page-level access

Restrict individual pages to specific roles using frontmatter:

```yaml
---
title: Internal Runbook
access: restricted
allowed_roles: [admin, editor]
---
```

Pages with `access: restricted` are invisible to users without the required role — they won't appear in search results, navigation, or published docs.

## Real-time presence

When multiple users are active in the same workspace, the web editor shows who's online:

- **Sidebar indicators** — colored dots next to pages being viewed or edited by other users
- **Avatar stack** — user avatars in the page header showing who else is viewing the current page

Presence is powered by WebSocket connections and updates in real time.

### How presence works

| Parameter | Value |
|---|---|
| **Protocol** | WebSocket (authenticated via one-time ticket) |
| **Heartbeat interval** | Every 30 seconds |
| **Eviction timeout** | 90 seconds without heartbeat |
| **Events** | `presence-join` (first connect), `presence-leave` (timeout or disconnect) |
| **Buffer** | 256 events per workspace (prevents backpressure) |

The WebSocket connection also delivers real-time content events:

| Event | When |
|---|---|
| `page-created` | A new page is created (any source) |
| `page-updated` | A page is modified (any source) |
| `page-deleted` | A page is deleted |
| `sync-status` | Git sync status changes (synced, ahead, behind, conflict) |
| `conflict-detected` | A git merge conflict is found |
| `bulk-sync` | 20+ files synced in one operation (single notification, not per-file) |

### Concurrent editing

DocPlatform does not support real-time collaborative editing (Google Docs-style). If two users edit the same page simultaneously:

1. The first save succeeds
2. The second save triggers a **conflict detection** (HTTP 409)
3. Both versions are preserved for manual resolution

To avoid conflicts:

- Use page-level ownership conventions (one writer per page at a time)
- Presence indicators help your team coordinate who's editing what
- For high-concurrency teams, consider shorter git sync intervals

## Audit trail

Every content mutation is logged with:

| Field | Description |
|---|---|
| **Timestamp** | When the action occurred (UTC) |
| **User** | Who performed the action (email, user ID) |
| **Operation** | What happened: `create`, `update`, `delete`, `publish`, `unpublish` |
| **Page** | Which page was affected (ID, title, path) |
| **Source** | Where the change came from: `web_editor`, `git_sync`, `api` |
| **Content hash** | SHA-256 of the new content (for verification) |

### Viewing the audit log

Access the audit log from **Workspace Settings** → **Activity**.

Filter by:

- **User** — see all changes by a specific team member
- **Page** — see the full history of a specific page
- **Date range** — narrow to a time window
- **Operation type** — filter to creates, updates, deletes, etc.

### Audit action types

The `action` field in the audit log uses dot-notation for precise filtering:

| Action | Description |
|---|---|
| `page.create` | New page created |
| `page.update` | Page content or frontmatter modified |
| `page.delete` | Page deleted |
| `page.publish` | Page published (made public) |
| `page.unpublish` | Page unpublished |
| `auth.login` | User signed in |
| `auth.register` | New user registered |
| `auth.password_reset` | Password reset completed |
| `workspace.create` | New workspace created |
| `workspace.member_add` | User added to workspace |
| `workspace.member_remove` | User removed from workspace |
| `workspace.role_change` | User's role changed |

### Retention

Audit logs are stored in SQLite alongside your regular data. They're included in daily backups. Default retention is 1 year (configurable). A weekly cleanup job removes entries older than the retention period.

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

Without SMTP, invitation links and password reset tokens are printed to stdout (server logs).

## Tips for team workflows

- **One writer per page** — use presence indicators to avoid conflicts
- **Editors write, Admins publish** — separate concerns with roles
- **Use tags for ownership** — tag pages with `owner:jane` to clarify responsibility
- **Git for review workflows** — push changes to a branch, open a PR, merge after review
- **Audit before publish** — review the audit log for unexpected changes before making content public
