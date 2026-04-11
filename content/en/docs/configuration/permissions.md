---
title: Roles & Permissions
description: Configure DocPlatform's 5-role hierarchy, workspace-level access control, editor permissions, and plan-based seat limits.
weight: 3
---

DocPlatform uses role-based access control (RBAC) powered by custom RBAC, an in-process authorization engine. Permissions are evaluated in under 0.1ms per check with no external service.

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

> **Platform Owner** is an internal-only role used by self-hosted operators for platform-level maintenance (database migrations, license management, system config). It does not appear in the UI or API and is not part of the public role hierarchy.

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
| Assign org members to workspace | | | | Yes | Yes |
| Remove workspace members | | | | Yes | Yes |
| Change member roles (within workspace) | | | | Yes | Yes |
| Manage workspace settings | | | | Yes | Yes |
| Manage theme & navigation | | | | Yes | Yes |
| Invite external users to org | | | | | Yes |
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

**Config file:**

```yaml
# .docplatform/config.yaml (per workspace)
permissions:
  editor_can_create_pages: true
  editor_can_delete_pages: false
```

When a permission is disabled, editors see the action as greyed out in the UI and receive `403 Forbidden` from the API.

## Assigning roles

### First user (Super Admin)

The first user to register on a new DocPlatform instance automatically receives the **Super Admin** role. This only happens once — subsequent registrations receive no workspace role until invited.

The Super Admin is the org owner and account creator. They have full control over every workspace, billing, git connections, and external user invitations.

### Inviting external users

Only the **Super Admin** can invite external users to the organization:

**Web UI:** Org Settings → Members → Invite External User

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/org/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "default_role": "editor"
  }'
```

The invited user joins the org and can then be assigned to workspaces by any Admin or Super Admin.

### Assigning members to workspaces

**Admins** assign existing org members to their workspace. Admins cannot invite external users — only the Super Admin can do that.

**Web UI:** Workspace Settings → Members → Add Member → select from org members → select role

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/:id/members \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "01HY5K3M7Q8P",
    "role": "editor"
  }'
```

### Default role

Set the default role for new members added to a workspace without a specific role:

```yaml
# .docplatform/config.yaml
permissions:
  default_role: viewer
```

Available values: `viewer`, `commenter`, `editor`, `admin`

## Page-level access control

Override workspace-level permissions on individual pages using frontmatter. Frontmatter access rules **restrict** within a user's role — they never grant permissions beyond the role.

### Access control syntax

Use role-based and user-based access rules to control who can access a page:

```yaml
---
title: Internal Security Policy
access:
  roles: ["security-team", "engineering-leads"]
  users: ["@01HY5K3M7Q8P"]
---
```

| Field | Value type | Description |
|---|---|---|
| `access.roles` | list of role names | Roles that can access this page |
| `access.users` | list of `@user_id` | Individual users that can access this page |

**Rules:**
- Prefix user IDs with `@` to target individual users
- Super Admin and Admin always have access regardless of frontmatter rules
- Frontmatter can only **restrict** — a page cannot grant access beyond the user's workspace role

### Examples

**Public page** (default — all workspace members can view):

```yaml
---
title: Getting Started
---
```

**Restricted to specific teams:**

```yaml
---
title: Infrastructure Runbook
access:
  roles: ["security-team", "sre-team"]
---
```

**Restricted with individual user access:**

```yaml
---
title: Budget Proposal
access:
  roles: ["finance-team"]
  users: ["@01HY5K3M7Q8P"]
---
```

### What restricted access means

When a page has `access` rules:

- Users without the required role **cannot view** the page
- The page **does not appear** in search results for unauthorized users
- Direct URL access returns **403 Forbidden**

### Published docs access

For the **published docs site** (`/p/{slug}/...`), access control works differently:

- All published pages are **public by default** — no login required
- To require login for the entire published site, set [`PUBLISH_REQUIRE_AUTH=true`](environment.md) — this applies to all pages in all workspaces
- Per-page access control in published docs (e.g., making one page workspace-only while others are public) is planned for a future release

> In v0.5, the `access` frontmatter field is stored and available for future use, but is not enforced on published routes. Use `PUBLISH_REQUIRE_AUTH` for site-wide access restriction.

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

### 5-step evaluation flow

1. **Is user Platform Owner?** → ALLOW (global bypass)
2. **Is user Org Super Admin for this workspace's org?** → ALLOW (org-level bypass)
3. **Look up user's workspace role** → if not a workspace member, DENY
4. **Does user's role level meet the action's minimum level?** → compare `role_level >= action_min_level`, plus editor permission flags
5. **Does page frontmatter have access rules?** → check `access.roles`/`access.users`, RESTRICT within role

Frontmatter RESTRICTS within role, never GRANTS beyond it. A malformed frontmatter defaults to **strict mode** — page restricted to Admin only.

### Performance

| Metric | Value |
|---|---|
| **Engine** | custom RBAC (in-process, in-memory) |
| **Evaluation time** | < 0.1ms per check |
| **Batch check** | < 1ms per 100 pages |
| **Cache** | Versioned (auto-invalidated on role or permission change) |
| **Policy storage** | SQLite (loaded into memory on startup) |

## Permission caching

Custom RBAC policies are loaded from SQLite into memory on server startup. Changes to roles or frontmatter access declarations trigger a cache invalidation:

1. Admin changes a user's role → permission cache version incremented
2. Editor updates page frontmatter with new `access` rules → cache invalidated for that page
3. Next permission check loads fresh policy from SQLite

The cache is versioned, not time-based — there's no stale-permission window.

## Plans and seat limits

### Seat counting

**Super Admin**, **Admin**, and **Editor** roles all count toward the plan's `max_editors` seat limit. Commenter and Viewer roles are **unlimited on all plans** and never count toward any seat limit.

When the seat limit is reached, new org members can still be invited — but they can only be assigned Commenter or Viewer roles until a seat is freed.

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
| **Workspaces** | 1 | 5 | 15 |
| **Seats** (Super Admin + Admin + Editor) | 3 | 15 | 50 |
| **Viewers & Commenters** | Unlimited | Unlimited | Unlimited |
| **Pages** | Unlimited | Unlimited | Unlimited |

> Need more? [Contact sales](https://valoryx.org/contact) for Enterprise plans with custom limits, SSO, and SLA.

## Common patterns

### Read-only public docs with restricted internal pages

```yaml
# Most pages: no access rules (open to all workspace members)

# Internal pages: restricted
---
title: Incident Response Playbook
access:
  roles: ["sre-team", "admin"]
---
```

### Editor creates, Admin publishes

1. Set `publishing.default_published: false` in workspace config
2. Editors create and edit pages (unpublished by default)
3. Admins review and toggle `published: true`

### Team-specific workspaces

Create separate workspaces per team with independent member lists:

- `eng-docs` workspace → engineering team
- `product-docs` workspace → product team
- `internal-wiki` workspace → everyone

Super Admin has access to all workspaces for cross-team visibility. Admins manage membership within their assigned workspaces.

### Restricting Editor capabilities

For workspaces where editors should only modify existing content:

```yaml
# .docplatform/config.yaml
permissions:
  editor_can_create_pages: false
  editor_can_delete_pages: false
```

Editors can still edit existing pages but cannot create new ones or delete any.

## Troubleshooting

### "403 Forbidden" on a page I should have access to

1. Check your role: Profile → Workspace Membership
2. Check the page's frontmatter: does `access.roles` include your role?
3. Ask a workspace Admin to verify your role assignment
4. If you are an Editor, check whether the action requires `editor_can_create_pages` or `editor_can_delete_pages` to be enabled

### Permission changes not taking effect

Permission changes should be instant (cache invalidation is synchronous). If they're not:

1. Sign out and sign back in (refresh your JWT tokens)
2. Check the server logs for cache invalidation errors
3. Run `docplatform doctor` to verify permission system health

### First user is not Super Admin

This happens if the first user registers while the database already contains user records (e.g., from a previous installation). To fix:

1. Stop the server
2. Delete the database: `rm {DATA_DIR}/data.db`
3. Start the server and register again

This resets all data. Use only on fresh installations.

### "Seat limit reached" when inviting a member

The plan's `max_editors` limit has been reached. Options:

1. Downgrade an existing Admin or Editor to Commenter or Viewer to free a seat
2. Invite the new user as a Commenter or Viewer (these are unlimited)
3. Upgrade your plan for more seats
