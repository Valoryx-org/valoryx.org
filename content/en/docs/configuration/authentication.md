---
title: Authentication
description: Configure local authentication, Google and GitHub OIDC sign-in, JWT settings, and password policies.
weight: 2
---

# Authentication

DocPlatform supports local authentication (email + password) out of the box, with optional Google and GitHub OIDC sign-in for teams that use those providers.

## Local authentication (default)

Local auth works without any configuration. Users register with an email and password, and sign in with the same credentials.

### How it works

1. **Registration** — User submits email + password. Password is hashed with argon2id (OWASP 2024 recommended algorithm).
2. **Login** — User submits credentials. Server verifies the password hash and returns JWT tokens.
3. **Session** — Access token (RS256, 15-minute lifetime) is sent with each API request. Refresh token (30-day lifetime) is used to obtain new access tokens without re-authentication.

### Password hashing

DocPlatform uses argon2id with the following parameters (OWASP 2024 standard):

| Parameter | Value |
|---|---|
| **Algorithm** | argon2id |
| **Memory** | 64 MB |
| **Iterations** | 3 |
| **Parallelism** | 4 |
| **Salt length** | 16 bytes |
| **Key length** | 32 bytes |

These parameters are not configurable — they follow security best practices. Password hashes are stored in the SQLite database and never leave the server.

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
│ Refresh Token (30 days)          │  ──►  Used to get new access tokens
└─────────────────────────────────┘
    │
    │  Access token expires
    ▼
┌─────────────────────────────────┐
│ POST /api/v1/auth/refresh        │
│ Body: { refresh_token: "..." }   │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ New Access Token (15 min)        │  ──►  Old refresh token rotated
│ New Refresh Token (30 days)      │  ──►  Old one invalidated
└─────────────────────────────────┘
```

### Refresh token rotation

Each time a refresh token is used, a new refresh token is issued and the old one is invalidated. This limits the window of exposure if a token is compromised.

### Configuration

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET_PATH` | `{DATA_DIR}/jwt-key.pem` | Path to the RS256 private key |
| `JWT_ACCESS_TTL` | `900` | Access token lifetime (seconds) |
| `JWT_REFRESH_TTL` | `2592000` | Refresh token lifetime (seconds) |

### Key management

The RS256 key pair is auto-generated on first startup if the file doesn't exist. To rotate keys:

1. Stop the server
2. Delete the key file (`{DATA_DIR}/jwt-key.pem`)
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
6. Add authorized redirect URI: `https://your-domain.com/api/v1/auth/callback/google`
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
3. Set the authorization callback URL: `https://your-domain.com/api/v1/auth/callback/github`
4. Copy the Client ID and generate a Client Secret

Set the environment variables:

```bash
export OIDC_GITHUB_CLIENT_ID=your-client-id
export OIDC_GITHUB_CLIENT_SECRET=your-client-secret
```

Restart the server. A **Sign in with GitHub** button appears on the login page.

### User provisioning

Same as Google — a DocPlatform account is created using the GitHub primary email. If the GitHub account has no public email, the user is prompted to enter one.

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
| Maximum length | 128 characters |
| Hashing | argon2id (64 MB memory, 3 iterations, parallelism 4) |

Passwords are validated on registration and password reset. DocPlatform does not enforce character-class requirements (uppercase, special characters) — length is the primary security measure per current NIST guidelines.

## WebSocket authentication

WebSocket connections use a one-time ticket pattern to avoid exposing JWT tokens in URLs (which would appear in server logs and browser history).

**Flow:**

1. Client calls `POST /api/v1/auth/ws-ticket` with a valid JWT
2. Server returns a random ticket (valid for **30 seconds**, single-use)
3. Client connects to `ws://host/ws?ticket={ticket}`
4. Server validates the ticket, establishes the WebSocket, and discards the ticket

This is transparent to users — the web editor handles ticket acquisition automatically.

## Security recommendations

- **Enable OIDC** for teams with Google or GitHub accounts — delegates password management to established providers
- **Use HTTPS** in production — JWT tokens are bearer tokens; intercepted tokens grant full access
- **Keep token lifetimes short** — 15-minute access tokens limit exposure
- **Monitor sessions** — review active sessions periodically for unexpected devices or IPs
- **Rotate keys** annually or after any suspected compromise
- **Use HttpOnly cookies** — DocPlatform stores tokens in HttpOnly + Secure + SameSite=Strict cookies, preventing XSS token theft
