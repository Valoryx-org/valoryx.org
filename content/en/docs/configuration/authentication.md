---
title: Authentication
description: Configure local authentication, Google and GitHub OIDC sign-in, WebAuthn/Passkeys, JWT settings, and password policies.
weight: 2
---

# Authentication

DocPlatform supports local authentication (email + password) out of the box, with optional Google/GitHub OIDC sign-in and WebAuthn/Passkeys for passwordless login.

## Local authentication (default)

Local auth works without any configuration. Users register with an email and password, and sign in with the same credentials.

### How it works

1. **Registration** — User submits email + password. Password is hashed with argon2id (OWASP 2024 recommended algorithm).
2. **Login** — User submits credentials. Server verifies the password hash and returns JWT tokens.
3. **Session** — Access token (RS256, 15-minute lifetime) is sent with each API request. Refresh token (7-day lifetime, rotated on each use) is used to obtain new access tokens without re-authentication.

### Password hashing

DocPlatform uses argon2id with the following parameters (OWASP 2024 standard):

| Parameter | Value |
|---|---|
| **Algorithm** | argon2id |
| **Memory** | 64 MB |
| **Iterations** | 3 |
| **Parallelism** | 2 |
| **Salt length** | 16 bytes |
| **Key length** | 32 bytes |

The memory, iterations, and parallelism parameters are configurable via `ARGON2_MEMORY`, `ARGON2_TIME`, and `ARGON2_THREADS` environment variables. See [Environment Variables](environment.md). Password hashes are stored in the SQLite database and never leave the server.

### Password reset

When a user requests a password reset:

- **With SMTP configured** — a one-time reset link is emailed to the user
- **Without SMTP** — the reset token is printed to stdout (server logs)

```bash
# Check server logs for the reset token
docplatform serve 2>&1 | grep "password reset"
```

The token expires after 1 hour and can only be used once.

## JWT tokens

DocPlatform issues RS256 (RSA-SHA256) JSON Web Tokens for authentication.

### Token lifecycle

```
User logs in
    │
    ▼
┌─────────────────────────────────┐
│ Access Token (15 min)            │  ──►  Sent with every API request
│ Refresh Token (7 days)           │  ──►  Used to get new access tokens
└─────────────────────────────────┘
    │
    │  Access token expires
    ▼
┌─────────────────────────────────┐
│ POST /api/auth/refresh            │
│ Body: { refresh_token: "..." }   │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ New Access Token (15 min)        │  ──►  Old refresh token rotated
│ New Refresh Token (7 days)       │  ──►  Old one invalidated
└─────────────────────────────────┘
```

### Refresh token rotation

Each time a refresh token is used, a new refresh token is issued and the old one is invalidated. This limits the window of exposure if a token is compromised.

### Configuration

| Variable | Default | Description |
|---|---|---|
| `JWT_KEY_PATH` | `{DATA_DIR}/jwt-private.pem` | Path to the RS256 private key |
| `JWT_ACCESS_TTL` | `900` | Access token lifetime in seconds (default: 15 minutes) |
| `JWT_REFRESH_TTL` | `604800` | Refresh token lifetime in seconds (default: 7 days) |

### Key management

The RS256 key pair is auto-generated on first startup if the file doesn't exist. To rotate keys:

1. Stop the server
2. Delete the key file (`{DATA_DIR}/jwt-private.pem`)
3. Start the server — a new key is generated

All existing sessions are invalidated on key rotation. Users must log in again.

## Google OIDC sign-in (optional)

Allow users to sign in with their Google account.

### Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Add authorized redirect URI: `https://your-domain.com/api/auth/oidc/google/callback`
7. Copy the Client ID and Client Secret

Set the environment variables:

```bash
export OIDC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
export OIDC_GOOGLE_CLIENT_SECRET=your-client-secret
```

Restart the server. A **Sign in with Google** button appears on the login page.

### User provisioning

When a user signs in via Google for the first time:

- A DocPlatform account is created with their Google email
- They're assigned the default role (`permissions.default_role`) in any workspace they're invited to
- No password is set (they can add one later from their profile)

## GitHub OIDC sign-in (optional)

Allow users to sign in with their GitHub account.

### Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Set the authorization callback URL: `https://your-domain.com/api/auth/oidc/github/callback`
4. Copy the Client ID and generate a Client Secret

Set the environment variables:

```bash
export OIDC_GITHUB_CLIENT_ID=your-client-id
export OIDC_GITHUB_CLIENT_SECRET=your-client-secret
```

Restart the server. A **Sign in with GitHub** button appears on the login page.

### User provisioning

Same as Google — a DocPlatform account is created using the GitHub primary email. If the GitHub account has no public email, the user is prompted to enter one.

## WebAuthn / Passkeys (optional)

Allow users to sign in with hardware security keys, biometrics, or platform authenticators (Touch ID, Face ID, Windows Hello). This provides passwordless, phishing-resistant authentication.

### Setup

Set the following environment variables:

```bash
export WEBAUTHN_RP_ID=docs.example.com
export WEBAUTHN_RP_DISPLAY_NAME="My Docs"
export WEBAUTHN_RP_ORIGINS=https://docs.example.com
```

Restart the server. A **Sign in with Passkey** button appears on the login page.

### How it works

1. **Registration** — User goes to Profile → Security → **Register Passkey**
2. Browser prompts for biometric or security key verification
3. A credential is stored on the server (public key only — the private key never leaves the device)
4. **Login** — User clicks "Sign in with Passkey" and authenticates with their device

### Managing credentials

Users can manage their passkeys from their profile:

- **List credentials** — `GET /api/auth/webauthn/credentials`
- **Delete a credential** — `DELETE /api/auth/webauthn/credentials/:id`

Each credential stores a name, last-used timestamp, and sign count for clone detection.

### Requirements

| Requirement | Details |
|---|---|
| **HTTPS** | Required — WebAuthn only works over secure connections |
| **Browser support** | Chrome 67+, Firefox 60+, Safari 14+, Edge 79+ |
| **RP ID** | Must match the domain users access (no wildcards) |

## API keys

For programmatic access (CI/CD pipelines, MCP integrations, scripts), use API keys instead of JWT tokens.

### How it works

1. Create an API key from the web UI or API: `POST /api/v1/api-keys`
2. The key is returned once in full (prefixed with `dp_live_`) — store it securely
3. Use the key as a Bearer token: `Authorization: Bearer dp_live_...`
4. Only the key hash is stored server-side (HMAC with configurable pepper)

### Key management

| Operation | Endpoint |
|---|---|
| Create key | `POST /api/v1/api-keys` |
| List keys (prefix only) | `GET /api/v1/api-keys` |
| Delete key | `DELETE /api/v1/api-keys/:id` |
| Rotate key | `POST /api/v1/api-keys/:id/rotate` |

Keys are scoped to the organization. Set `API_KEY_PEPPER` (or `DOCPLATFORM_API_KEY_PEPPER`) for HMAC hashing security.

## Session management

DocPlatform tracks active sessions per user:

| Field | Description |
|---|---|
| **Device** | User-agent string |
| **IP address** | Client IP (for audit purposes) |
| **Created** | When the session was established |
| **Last active** | Most recent API request |

Users can view and revoke sessions from their profile page. Admins can view all sessions from the admin panel.

### Revoking sessions

- **User-initiated** — Profile → Sessions → Revoke
- **Admin-initiated** — Admin → Users → select user → Revoke All Sessions
- **Key rotation** — Deleting the JWT key invalidates all sessions globally

## Password policy

| Constraint | Value |
|---|---|
| Minimum length | 8 characters |
| Hashing | argon2id (64 MB memory, 3 iterations, parallelism 2) |

Passwords are validated on registration and password reset. DocPlatform does not enforce character-class requirements (uppercase, special characters) — length is the primary security measure per current NIST guidelines.

## WebSocket authentication

WebSocket connections use an HttpOnly cookie mechanism to avoid exposing tokens in URLs (which would appear in server logs and browser history).

**Flow:**

1. Client calls `POST /api/auth/ws-token` with a valid JWT
2. Server sets a `dp_ws_token` HttpOnly cookie (valid for **30 seconds**, single-use)
3. Client connects to `ws://host/ws` — the browser sends the cookie automatically
4. Server validates the cookie, establishes the WebSocket, and clears the cookie

This is transparent to users — the web editor handles token acquisition automatically.

## Security recommendations

- **Enable OIDC** for teams with Google or GitHub accounts — delegates password management to established providers
- **Use HTTPS** in production — JWT tokens are bearer tokens; intercepted tokens grant full access
- **Keep token lifetimes short** — 15-minute access tokens limit exposure
- **Monitor sessions** — review active sessions periodically for unexpected devices or IPs
- **Rotate keys** annually or after any suspected compromise
- **Use HttpOnly cookies** — DocPlatform stores tokens in HttpOnly + Secure + SameSite=Strict cookies, preventing XSS token theft
