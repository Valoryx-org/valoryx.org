---
title: Roles & Permissions
description: Configure DocPlatform's 5-role hierarchy, workspace-level access control, editor permissions, and plan-based seat limits.
weight: 3
---

# Roles & Permissions

DocPlatform uses role-based access control (RBAC) evaluated in-process — there is no external authorization service to deploy or configure.

## Role hierarchy

DocPlatform defines 5 public-facing roles in a strict hierarchy. Higher roles inherit all permissions of lower roles.

```
Super Admin         ← Org owner / account creator (highest public role)
    │
Admin               ← Manage workspace settings, members, git, theme
    │
Editor              ← Create and edit pages (configurable per workspace)
    │
Commenter           ← View pages, leave comments
    │
Viewer              ← View pages only
```

> **Platform Owner** is an internal flag used by the Valoryx-operated Cloud service. It has no functionality in Community Edition and is not part of the public role hierarchy.

### Permission matrix

| Permission | Viewer | Commenter | Editor | Admin | Super Admin |
|---|---|---|---|---|---|
| View pages | Yes | Yes | Yes | Yes | Yes |
| Search content | Yes | Yes | Yes | Yes | Yes |
| Leave comments | | Yes | Yes | Yes | Yes |
| Edit pages | | | Yes | Yes | Yes |
| Create pages | | | Configurable | Yes | Yes |
| Delete pages | | | Configurable | Yes | Yes |
| Upload assets | | | Yes | Yes | Yes |
| Invite members to the workspace | | | | Yes | Yes |
| Remove workspace members | | | | Yes | Yes |
| Change member roles (within workspace) | | | | Yes | Yes |
| Manage workspace settings | | | | Yes | Yes |
| Manage theme & navigation | | | | Yes | Yes |
| Assign existing org members to any workspace | | | | | Yes |
| Create/delete workspaces | | | | | Yes |
| Configure git remote | | | | | Yes |
| Manage billing & subscription | | | | | Yes |
| Access all workspaces | | | | | Yes |
| Manage org-level settings | | | | | Yes |

### Configurable Editor permissions

Editor capabilities can be tuned per workspace. Admins and Super Admins configure these in workspace settings:

| Setting | Default | Description |
|---|---|---|
| `editor_can_create_pages` | `true` | Editors can create new pages |
| `editor_can_delete_pages` | `false` | Editors can delete pages |

**API:**

```bash
curl -X PATCH http://localhost:3000/api/v1/workspaces/:id \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "editor_can_create_pages": true,
    "editor_can_delete_pages": false
  }'
```

When a permission is disabled, editors see the action as greyed out in the UI and receive `403 Forbidden` from the API.

## Assigning roles

### Super Admin (org owner)

Registering an account creates a new organization, and the registering user becomes its **Super Admin**. The Super Admin has full control over every workspace in the org, billing, git connections, and org settings.

### Inviting members to a workspace

Workspace **Admins** (and the Super Admin) invite people by email and choose the role at invite time:

**Web UI:** Workspace Settings → Members → Invite

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/:id/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "role": "editor"
  }'
```

If email is configured the invitation is sent automatically; otherwise a shareable invitation link is displayed. Share links (`POST /api/v1/workspaces/:id/share-links`) are an alternative for inviting several people with the same role.

### Assigning existing org members to workspaces

The org **Super Admin** can assign an existing org member to a workspace:

```bash
curl -X POST http://localhost:3000/api/v1/org/members/:uid/workspaces \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{ "workspace_id": "01HY5K3M7Q8P", "role": "editor" }'
```

Workspace Admins can change the role of existing members of their workspace (**Workspace Settings → Members**, or `PUT /api/v1/workspaces/:id/admin/members/:user_id/role`).

## Page-level access control (not yet enforced)

Page frontmatter may contain an `access` block. DocPlatform **parses and preserves** it (it round-trips through git and the editor unchanged), but it is **not enforced** — all access control today is role-based at the workspace level. Do not rely on frontmatter `access` rules to protect content.

### Published docs access

For the **published docs site** (`/p/{slug}/...`), access is controlled per site:

- Each published site has a `visibility` setting: `authenticated` (the default — visitors must sign in as workspace members) or `public` (world-readable, no login)
- The server-wide override [`PUBLISH_REQUIRE_AUTH=true`](environment.md) forces login for **all** published sites regardless of per-site visibility
- Per-page access control on published sites is not available

## Internal role levels

For reference, each role maps to a numeric level. Higher levels inherit all permissions of lower levels:

| Role | Level | Scope | Minimum action |
|---|---|---|---|
| Viewer | 10 | Workspace | `read` |
| Commenter | 20 | Workspace | `read`, `comment` |
| Editor | 30 | Workspace | `read`, `comment`, `edit` (+ `create`/`delete` if enabled) |
| Admin | 40 | Workspace | All workspace actions |
| Super Admin | — | Org | Bypasses all workspace checks |

> The internal code uses `workspace_admin` for Admin and `super_admin` for Super Admin. Super Admin is an **org-level role** (not a workspace role with a numeric level) — it bypasses workspace permission checks entirely. Platform Owner is a boolean flag on the user record that bypasses all checks globally.

Actions have minimum levels: `read` requires level 10+, `comment` requires 20+, `edit` requires 30+, `write`/`delete` requires 40+ (Editors get `edit` but not `write`/`delete` unless configurable flags are enabled), `admin` requires 40+. A user's role level is compared against the action's minimum level.

## How permissions are evaluated

```
API Request
    │
    ▼
Auth Middleware
(extract JWT, identify user)
    │
    ▼
Permission Middleware
(custom RBAC check: user + role + resource + action)
    │
    ├── Allowed → proceed to handler
    │
    └── Denied → 403 Forbidden
```

### 4-step evaluation flow

1. **Is user Platform Owner?** → ALLOW (global bypass; Cloud edition only)
2. **Is user Org Super Admin for this workspace's org?** → ALLOW (org-level bypass)
3. **Look up user's workspace role** → if not a workspace member, DENY
4. **Does user's role level meet the action's minimum level?** → compare `role_level >= action_min_level`, plus editor permission flags

For requests authenticated with an **API key**, the key's scopes are checked first (e.g., a `read`-only key can never write), and then the same role evaluation applies — a scope never grants more than the underlying role allows.

Permission checks run in-process against the local SQLite database — there is no external authorization service, and role changes take effect on the next request.

## Plans and seat limits

### Seat counting

Workspace members holding the **Editor** or **Admin** role count toward the plan's `max_editors` seat limit (each user is counted once across the org, even if they belong to several workspaces). **Commenter and Viewer roles are unlimited on all plans** and never count toward any seat limit.

When the seat limit is reached, new members can still be invited — but only with the Commenter or Viewer role until a seat is freed.

### Community Edition

Community Edition is free and self-hosted with no license key required:

| Resource | Limit |
|---|---|
| Workspaces | Unlimited |
| Editors (Super Admin + Admin + Editor) | Unlimited |
| Viewers and Commenters | Unlimited |
| Pages | Unlimited |

### Cloud plans

| | Free | Team | Business |
|---|---|---|---|
| **Workspaces** | 1 | 3 | 10 |
| **Seats** (Super Admin + Admin + Editor) | 3 | 15 | 50 |
| **Viewers & Commenters** | Unlimited | Unlimited | Unlimited |
| **Pages** | 50 | 150 | Unlimited |

> Need more? [Contact sales](https://valoryx.org/contact) for Enterprise plans with custom limits, SSO, and SLA.

## Common patterns

### Public site, private drafts

Pages are excluded from the published site unless marked for publishing — so editors can draft freely while only reviewed pages go public:

1. Editors create and edit pages (not published by default)
2. A reviewer sets `publish: true` in the page frontmatter (or via the editor's publish control)
3. The `.docplatform/publish.yaml` overlay can override publish decisions per path when you want git-reviewable publish control

### Team-specific workspaces

Create separate workspaces per team with independent member lists:

- `eng-docs` workspace → engineering team
- `product-docs` workspace → product team
- `internal-wiki` workspace → everyone

Super Admin has access to all workspaces for cross-team visibility. Admins manage membership within their assigned workspaces.

### Restricting Editor capabilities

For workspaces where editors should only modify existing content, disable the editor flags in workspace settings (or via the API):

```bash
curl -X PATCH http://localhost:3000/api/v1/workspaces/:id \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{ "editor_can_create_pages": false, "editor_can_delete_pages": false }'
```

Editors can still edit existing pages but cannot create new ones or delete any.

## Troubleshooting

### "403 Forbidden" on a page I should have access to

1. Check your role: Profile → Workspace Membership
2. Ask a workspace Admin to verify your role assignment
3. If you are an Editor, check whether the action requires `editor_can_create_pages` or `editor_can_delete_pages` to be enabled
4. If you authenticated with an API key, check the key's scopes — a `read` key cannot write regardless of your role

### Permission changes not taking effect

Permission changes are evaluated per request and should be effective immediately. If they're not:

1. Sign out and sign back in (refresh your JWT tokens)
2. Run `docplatform doctor` to check instance health

### I can't see a workspace I expect to see

Workspaces are visible only to their members (the org Super Admin sees all workspaces in their org). If a teammate created a workspace in *their* organization, they must invite you — registering your own account creates a separate organization with its own workspaces.

### "Seat limit reached" when inviting a member

The plan's `max_editors` limit has been reached. Options:

1. Downgrade an existing Admin or Editor to Commenter or Viewer to free a seat
2. Invite the new user as a Commenter or Viewer (these are unlimited)
3. Upgrade your plan for more seats
