---
title: Roles & Permissions
description: Configure DocPlatform's 6-level role hierarchy, page-level access control, and permission caching.
weight: 3
---

# Roles & Permissions

DocPlatform uses role-based access control (RBAC) powered by Casbin, an in-process authorization engine. Permissions are evaluated in under 0.1ms per check with no external service.

## Role hierarchy

DocPlatform defines 6 roles in a strict hierarchy. Higher roles inherit all permissions of lower roles.

```
SuperAdmin          ← Full platform access (all workspaces)
    │
WorkspaceAdmin      ← Manage workspace settings, git config, theme
    │
SpaceAdmin          ← Manage pages under assigned path patterns (e.g., docs/api/**)
    │
Editor              ← Create, edit, delete pages
    │
Commenter           ← View pages, leave comments
    │
Viewer              ← View pages only
```

### Permission matrix

| Permission | Viewer | Commenter | Editor | Space Admin | WS Admin | Super Admin |
|---|---|---|---|---|---|---|
| View pages | Yes | Yes | Yes | Yes | Yes | Yes |
| Search content | Yes | Yes | Yes | Yes | Yes | Yes |
| Leave comments | | Yes | Yes | Yes | Yes | Yes |
| Create pages | | | Yes | Yes (scoped) | Yes | Yes |
| Edit pages | | | Yes | Yes (scoped) | Yes | Yes |
| Delete pages | | | Yes | Yes (scoped) | Yes | Yes |
| Upload assets | | | Yes | Yes | Yes | Yes |
| Invite members | | | | | Yes | Yes |
| Remove members | | | | | Yes | Yes |
| Change member roles | | | | | Yes | Yes |
| Manage workspace settings | | | | | Yes | Yes |
| Configure git remote | | | | | Yes | Yes |
| Manage theme & navigation | | | | | Yes | Yes |
| Access all workspaces | | | | | | Yes |
| Manage platform settings | | | | | | Yes |
| Create/delete workspaces | | | | | | Yes |

### Space Admin — path-scoped permissions

The **Space Admin** role is unique: it grants admin-level control but only over pages matching specific **path patterns**. This enables delegated ownership without full workspace admin access.

**Example:** A Space Admin with `path_patterns: ["docs/api/**"]` can create, edit, and delete any page under `docs/api/` but has no special access to `docs/guides/`.

Path patterns are assigned when adding a member:

```bash
curl -X POST http://localhost:3000/api/v1/admin/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "api-lead@example.com",
    "role": "space_admin",
    "path_patterns": ["docs/api/**", "docs/reference/**"]
  }'
```

Path patterns use glob-style matching (`*` for single level, `**` for recursive).

## Assigning roles

### First user

The first user to register on a new DocPlatform instance automatically receives the **SuperAdmin** role. This only happens once — subsequent registrations receive no workspace role until invited.

### Workspace members

When inviting a user to a workspace, specify their role:

**Web UI:** Workspace Settings → Members → Invite → select role

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/admin/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "role": "editor"
  }'
```

### Default role

Set the default role for new members who accept an invitation without a specific role assigned:

```yaml
# .docplatform/config.yaml
permissions:
  default_role: viewer
```

Available values: `viewer`, `commenter`, `editor`, `space_admin`, `workspace_admin`

## Page-level access control

Override workspace-level permissions on individual pages using frontmatter. Frontmatter access rules **restrict** within a user's role — they never grant permissions beyond the role.

### Access control syntax

Use per-operation access rules to control who can read, write, or administer a page:

```yaml
---
title: Internal Security Policy
access:
  read: ["security-team", "engineering-leads"]
  write: ["security-team"]
  admin: ["@01HY5K3M7Q8P"]
---
```

| Field | Value type | Description |
|---|---|---|
| `access.read` | list of role names | Roles that can view this page |
| `access.write` | list of role names | Roles that can edit this page |
| `access.admin` | list of role names or `@user_id` | Users/roles that can manage page settings |

**Rules:**
- Prefix user IDs with `@` to target individual users
- SuperAdmin and WorkspaceAdmin always have access regardless of frontmatter rules
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
  read: ["security-team", "sre-team"]
  write: ["security-team"]
---
```

**Restricted with individual user access:**

```yaml
---
title: Budget Proposal
access:
  read: ["finance-team"]
  write: ["@01HY5K3M7Q8P"]
  admin: ["@01HY5K3M7Q8P"]
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

| Role | Level | Minimum action |
|---|---|---|
| Viewer | 10 | `read` |
| Commenter | 20 | `read` |
| Editor | 30 | `read`, `write`, `delete` |
| SpaceAdmin | 40 | `read`, `write`, `delete` within path patterns |
| WorkspaceAdmin | 50 | All workspace actions |
| SuperAdmin | 60 | All platform actions (bypasses all checks) |

Actions have minimum levels: `read` requires level 10+, `write` requires 30+, `delete` requires 30+, `admin` requires 50+. A user's role level is compared against the action's minimum level.

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
(Casbin check: user + role + resource + action)
    │
    ├── Allowed → proceed to handler
    │
    └── Denied → 403 Forbidden
```

### 6-step evaluation flow

1. **Is workspace public + action is read?** → assign anonymous viewer role
2. **Is user SuperAdmin?** → ALLOW (bypasses all checks)
3. **Is user WorkspaceAdmin?** → ALLOW for this workspace
4. **Does user's role permit action?** → Casbin RBAC check with `keyMatch2(path)`
5. **Do path_patterns match?** (Space Admin only) → check glob patterns
6. **Does page frontmatter have access rules?** → check whitelist, RESTRICT within role

Frontmatter RESTRICTS within role, never GRANTS beyond it. A malformed frontmatter defaults to **strict mode** — page restricted to WorkspaceAdmin only.

### Performance

| Metric | Value |
|---|---|
| **Engine** | Casbin (in-process, in-memory) |
| **Evaluation time** | < 0.1ms per check |
| **Batch check** | < 1ms per 100 pages |
| **Cache** | Versioned (auto-invalidated on role or permission change) |
| **Policy storage** | SQLite (loaded into memory on startup) |

## Permission caching

Casbin policies are loaded from SQLite into memory on server startup. Changes to roles or frontmatter access declarations trigger a cache invalidation:

1. Admin changes a user's role → permission cache version incremented
2. Editor updates page frontmatter with new `access` rules → cache invalidated for that page
3. Next permission check loads fresh policy from SQLite

The cache is versioned, not time-based — there's no stale-permission window.

## Common patterns

### Read-only public docs with restricted internal pages

```yaml
# Most pages: no access rules (open to all workspace members)

# Internal pages: restricted
---
title: Incident Response Playbook
access:
  read: ["sre-team", "workspace_admin"]
  write: ["sre-team"]
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

SuperAdmin has access to all workspaces for cross-team visibility.

### Delegated ownership with Space Admin

Assign Space Admin roles for teams that own specific documentation areas:

- API team → `space_admin` with `path_patterns: ["docs/api/**"]`
- Design team → `space_admin` with `path_patterns: ["docs/design/**"]`

## Community Edition limits

Community Edition enforces the following resource limits:

| Resource | Limit |
|---|---|
| Users with Editor role or above | 5 |
| Workspaces | 3 |
| Viewers and Commenters | Unlimited |
| Pages | Unlimited |

These limits are hardcoded (no license key required). Viewers and commenters are never counted against the editor limit. When the editor limit is reached, new users can still be invited as Viewers or Commenters.

## Troubleshooting

### "403 Forbidden" on a page I should have access to

1. Check your role: Profile → Workspace Membership
2. Check the page's frontmatter: does `access.read` include your role?
3. If using Space Admin, verify your `path_patterns` cover the page's path
4. Ask a workspace admin to verify your role assignment

### Permission changes not taking effect

Permission changes should be instant (cache invalidation is synchronous). If they're not:

1. Sign out and sign back in (refresh your JWT tokens)
2. Check the server logs for cache invalidation errors
3. Run `docplatform doctor` to verify permission system health

### First user is not SuperAdmin

This happens if the first user registers while the database already contains user records (e.g., from a previous installation). To fix:

1. Stop the server
2. Delete the database: `rm {DATA_DIR}/data.db`
3. Start the server and register again

This resets all data. Use only on fresh installations.
