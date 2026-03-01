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
| **Environment variables** | Platform-wide | `.env` file or shell environment |
| **Workspace config** | Per workspace | `.docplatform/config.yaml` |
| **Page frontmatter** | Per page | YAML block in each `.md` file |

Higher-specificity layers override lower ones. For example, a page's `access: restricted` overrides the workspace default of `access: public`.

## Guides

| Guide | What it covers |
|---|---|
| [Environment Variables](environment.md) | All platform-level settings: port, data directory, git, SMTP, telemetry |
| [Workspace Settings](workspace-config.md) | Per-workspace config: git remote, theme, navigation, publishing defaults |
| [Authentication](authentication.md) | Local auth, OIDC providers (Google, GitHub), JWT settings, password policies |
| [Roles & Permissions](permissions.md) | 6-level RBAC hierarchy, page-level access control, Casbin configuration |

## Quick reference

The most common configuration tasks:

| Task | Where |
|---|---|
| Change the server port | `PORT` environment variable |
| Connect a git repository | Workspace config `git_remote` |
| Enable Google/GitHub sign-in | `OIDC_*` environment variables |
| Set up email (invitations, password reset) | `SMTP_*` environment variables |
| Change the default role for new users | Workspace config `permissions.default_role` |
| Restrict published docs to team members only | `PUBLISH_REQUIRE_AUTH=true` environment variable |
| Restrict a page to specific roles (web editor) | Page frontmatter `access: restricted` |
| Disable telemetry | `DOCPLATFORM_TELEMETRY=off` |
