---
title: Configuration
description: Configure DocPlatform with environment variables, workspace settings, authentication providers, and role-based permissions.
weight: 3
---

# Configuration

DocPlatform follows a convention-over-configuration approach. It runs with sensible defaults out of the box, but every aspect is configurable for production deployments.

## Configuration layers

Configuration is applied in three layers, from broadest to most specific:

| Layer | Scope | Method |
|---|---|---|
| **Environment variables** | Platform-wide | Shell environment / service unit / container env |
| **Workspace settings** | Per workspace | Web UI (Settings) — stored in the database; display settings also live in `.docplatform/workspace.yaml` |
| **Page frontmatter** | Per page | YAML block in each `.md` file |

Higher-specificity layers override lower ones. For example, a page's frontmatter `publish:` flag controls whether that page appears on the published site, and the `.docplatform/publish.yaml` overlay can override it per path.

## Guides

| Guide | What it covers |
|---|---|
| [Environment Variables](environment.md) | All platform-level settings: port, data directory, git, SMTP, telemetry |
| [Workspace Settings](workspace-config.md) | Per-workspace config: git remote, theme, navigation, publishing defaults |
| [Authentication](authentication.md) | Local auth, OIDC providers (Google, GitHub), JWT settings, password policies |
| [Roles & Permissions](permissions.md) | 5-level RBAC hierarchy and how permissions are evaluated |

## Quick reference

The most common configuration tasks:

| Task | Where |
|---|---|
| Change the server port | `PORT` environment variable |
| Connect a git repository | **Workspace Settings → Git** in the web UI |
| Enable Google/GitHub sign-in | `OIDC_*` environment variables |
| Set up email (invitations, password reset) | `SMTP_*` or `RESEND_*` environment variables |
| Choose a role when inviting a member | **Workspace Settings → Members → Invite** |
| Restrict published docs to team members only | `PUBLISH_REQUIRE_AUTH=true` environment variable, or per-site `visibility: authenticated` (the default) |
| Telemetry | Off by default; opt in with `DOCPLATFORM_TELEMETRY=on` |
