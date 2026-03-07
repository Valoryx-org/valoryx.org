---
title: Environment Variables
description: Complete reference for all DocPlatform environment variables — server, database, git, authentication, email, and operations.
weight: 1
---

# Environment Variables

DocPlatform reads configuration from environment variables. Set them in your shell, a `.env` file in the working directory, or your container orchestrator.

## Server

| Variable | Default | Description |
|---|---|---|
| `PORT` | `3000` | HTTP listen port |
| `HOST` | `0.0.0.0` | HTTP listen address. Set to `127.0.0.1` to restrict to localhost. |
| `DATA_DIR` | `.docplatform` | Root directory for all DocPlatform data (database, backups, workspaces, keys) |
| `BASE_URL` | `http://localhost:{PORT}` | Public URL used for OIDC callbacks, invitation links, and email templates. Set to your production URL (e.g., `https://docs.example.com`). |
| `BASE_DOMAIN` | — | Custom domain for published docs (e.g., `docs.yourcompany.com`). When set, published docs use this domain for canonical URLs and sitemap entries. |
| `PUBLISH_REQUIRE_AUTH` | `false` | When `true`, all published documentation sites require the visitor to be logged in as a workspace member. Unauthenticated visitors are redirected to the login page and returned to the original page after sign-in. |
| `CORS_ORIGINS` | — | Comma-separated list of allowed CORS origins. Leave empty for same-origin only. |

## Authentication

| Variable | Default | Description |
|---|---|---|
| `JWT_KEY_PATH` | `{DATA_DIR}/jwt-key.pem` | Path to the RS256 private key for JWT signing. Auto-generated on first run if missing (2048-bit RSA). |
| `JWT_ACCESS_TTL` | `1800` | Access token lifetime in seconds (default: 30 minutes) |
| `JWT_REFRESH_TTL` | `604800` | Refresh token lifetime in seconds (default: 7 days) |
| `ARGON2_MEMORY` | `65536` | Argon2id memory parameter in KiB (default: 64 MB) |
| `ARGON2_TIME` | `3` | Argon2id iteration count |
| `ARGON2_THREADS` | `2` | Argon2id parallelism |

## OIDC providers (optional)

Enable Google and/or GitHub sign-in by setting these variables. When unset, only local authentication (email + password) is available.

| Variable | Default | Description |
|---|---|---|
| `OIDC_GOOGLE_CLIENT_ID` | — | Google OAuth 2.0 client ID |
| `OIDC_GOOGLE_CLIENT_SECRET` | — | Google OAuth 2.0 client secret |
| `OIDC_GITHUB_CLIENT_ID` | — | GitHub OAuth client ID |
| `OIDC_GITHUB_CLIENT_SECRET` | — | GitHub OAuth client secret |

See [Authentication](authentication.md) for setup instructions.

## WebAuthn / Passkeys (optional)

Enable passwordless authentication with hardware security keys or biometrics. Disabled when `WEBAUTHN_RP_ID` is not set.

| Variable | Default | Description |
|---|---|---|
| `WEBAUTHN_RP_ID` | — | Relying Party ID — your domain name (e.g., `docs.example.com`). Required to enable WebAuthn. |
| `WEBAUTHN_RP_DISPLAY_NAME` | `DocPlatform` | Display name shown in browser passkey prompts. |
| `WEBAUTHN_RP_ORIGINS` | — | Comma-separated list of allowed origins for WebAuthn ceremonies (e.g., `https://docs.example.com`). |

See [Authentication](authentication.md) for setup instructions.

## Git

| Variable | Default | Description |
|---|---|---|
| `GIT_SSH_KEY_PATH` | `~/.ssh/docplatform_deploy_key` | Path to the SSH private key for git operations. Required for private repos over SSH. |
| `GIT_SSH_KNOWN_HOSTS` | — | Path to known_hosts file for strict host verification. If not set, uses built-in pinned keys for GitHub, GitLab, and Bitbucket. |
| `GIT_SYNC_INTERVAL` | `300` | Default polling interval in seconds for remote sync (minimum: 10). Overridden by per-workspace `sync_interval`. Set to `0` for webhook-only sync (no polling). |
| `GIT_AUTO_COMMIT` | `true` | Default auto-commit behavior. Overridden by per-workspace `git_auto_commit`. |
| `GIT_WEBHOOK_SECRET` | — | Shared secret for verifying webhook payloads (HMAC-SHA256) from GitHub, GitLab, or Bitbucket. |
| `GIT_COMMIT_NAME` | `DocPlatform` | Git committer name for auto-commits |
| `GIT_COMMIT_EMAIL` | `docplatform@local` | Git committer email for auto-commits |

## Email (optional)

Configure SMTP or Resend for workspace invitations and password reset emails. Without email configured, tokens are printed to stdout (server logs).

| Variable | Default | Description |
|---|---|---|
| `SMTP_HOST` | — | SMTP server hostname (e.g., `smtp.gmail.com`) |
| `SMTP_PORT` | `587` | SMTP port (587 for STARTTLS, 465 for SSL) |
| `SMTP_FROM` | — | Sender email address (e.g., `docs@yourcompany.com`) |
| `SMTP_USERNAME` | — | SMTP authentication username |
| `SMTP_PASSWORD` | — | SMTP authentication password |
| `RESEND_API_KEY` | — | Resend API key. When set alongside SMTP, Resend is preferred. |
| `RESEND_FROM` | — | Sender email for Resend (e.g., `docs@yourcompany.com`) |

## Backups

| Variable | Default | Description |
|---|---|---|
| `BACKUP_ENABLED` | `true` | Enable daily automated SQLite backups |
| `BACKUP_RETENTION_DAYS` | `7` | Number of days to retain backup files. Older backups are deleted automatically. |
| `BACKUP_DIR` | `{DATA_DIR}/backups` | Directory for backup files |

## Telemetry

| Variable | Default | Description |
|---|---|---|
| `DOCPLATFORM_TELEMETRY` | `off` | Set to `on` to enable anonymous, opt-in usage metrics. When enabled, a SHA-256 install ID (no personally identifiable information) is sent weekly. |
| `DOCPLATFORM_TELEMETRY_ENDPOINT` | — | Custom endpoint for telemetry data (advanced — for air-gapped environments with internal analytics) |

### What telemetry sends (when enabled)

- SHA-256 install ID (derived from data directory, not reversible)
- Workspace count and total page count
- DocPlatform version
- OS and architecture

Telemetry **never** sends: page content, user emails, IP addresses, file names, or any personally identifiable information. Frequency: weekly.

## Stripe billing (optional)

Enable subscription billing with Stripe. When `STRIPE_SECRET_KEY` is not set, billing is disabled and all organizations are treated as unlimited.

| Variable | Default | Description |
|---|---|---|
| `STRIPE_SECRET_KEY` | — | Stripe secret API key (starts with `sk_test_` or `sk_live_`) |
| `STRIPE_WEBHOOK_SECRET` | — | Stripe webhook endpoint signing secret (starts with `whsec_`) |
| `STRIPE_PRICE_TEAM` | — | Stripe Price ID for Team plan monthly ($99/mo) |
| `STRIPE_PRICE_BUSINESS` | — | Stripe Price ID for Business plan monthly ($299/mo) |
| `STRIPE_PRICE_TEAM_ANNUAL` | — | Stripe Price ID for Team plan annual ($990/yr) |
| `STRIPE_PRICE_BUSINESS_ANNUAL` | — | Stripe Price ID for Business plan annual ($2,990/yr) |
| `TRIAL_DURATION_DAYS` | `14` | Number of free trial days for new paid subscriptions |
| `FF_BILLING` | `true` | Master billing switch. Set to `false` to disable billing entirely and treat all orgs as unlimited. |

## AI features (optional)

Enable AI writing assist and doc chat. Disabled when `AI_API_KEY` is not set.

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `anthropic` | AI provider: `anthropic` (Claude) or `openai` |
| `AI_API_KEY` | — | API key for the selected provider |
| `AI_MODEL` | — | Model ID (e.g., `claude-sonnet-4-6` or `gpt-4o`). Uses provider default if empty. |

## Custom domains

Configure Caddy integration for automatic TLS provisioning on custom domains.

| Variable | Default | Description |
|---|---|---|
| `CADDY_ADMIN_URL` | `http://localhost:2019` | Caddy admin API URL for dynamic TLS provisioning |
| `CADDY_ASK_SECRET` | — | Shared secret for the `/internal/caddy/ask` endpoint. Required for custom domain TLS — empty rejects all TLS requests. |

## API security

| Variable | Default | Description |
|---|---|---|
| `API_KEY_PEPPER` | — | HMAC pepper for API key hashing. Warns if empty (reduced entropy). Can also be set as `DOCPLATFORM_API_KEY_PEPPER`. |
| `HIDE_STORAGE_PATHS` | `false` | Suppress disk paths in API responses (recommended for cloud/SaaS deployments). |
| `SHOW_DISK_PATHS_TO_WS_ADMIN` | `false` | Opt-in: show disk paths to workspace admins in storage info responses. |

## Observability

| Variable | Default | Description |
|---|---|---|
| `FF_METRICS` | `false` | Enable Prometheus metrics at `/metrics` (super admin authentication required). |

## Frontmatter handling

| Variable | Default | Description |
|---|---|---|
| `FRONTMATTER_ERROR_MODE` | `strict` | How to handle invalid YAML frontmatter: `strict` restricts the page to admin-only access (prevents accidental exposure); `lenient` keeps the last-known-good frontmatter and shows a warning. |

## Development

| Variable | Default | Description |
|---|---|---|
| `DEV_FRONTEND_URL` | — | Proxy non-API requests to this URL for frontend hot module reloading during development. |

## Using a `.env` file

Create a `.env` file in the directory where you run `docplatform serve`:

```bash
# .env
PORT=8080
DATA_DIR=/var/lib/docplatform
GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_FROM=docs@example.com
SMTP_USERNAME=docs@example.com
SMTP_PASSWORD=app-specific-password
BACKUP_RETENTION_DAYS=30
```

DocPlatform loads the `.env` file automatically. Environment variables set in the shell take precedence over `.env` values.

## Docker environment

Pass environment variables to Docker with `-e` flags or an env file:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  -e DATA_DIR=/data \
  -e SMTP_HOST=smtp.example.com \
  -e SMTP_FROM=docs@example.com \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

## Security notes

- **Never commit `.env` files** to version control. Add `.env` to your `.gitignore`.
- **JWT keys** are auto-generated. If you need to rotate, delete the key file and restart — a new key is generated and all existing sessions are invalidated.
- **SMTP passwords** — use app-specific passwords or API keys, not your primary account password.
- **Git tokens** — use repository-scoped tokens with minimal permissions (read + write for sync).
