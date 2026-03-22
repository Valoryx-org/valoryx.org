---
title: Your Account
description: Manage your profile, password, billing, and data.
weight: 6
---

# Your Account

## Signing up

Visit [app.valoryx.dev](https://app.valoryx.dev/#/register) and create an account with your email and a password. You'll need to accept the [Terms of Service](/terms/) and [Privacy Policy](/privacy/).

You can also sign in with **Google** or **GitHub** if those options are available.

## Profile settings

Click your avatar in the top-left corner, then **Profile** to:

- Change your display name
- Update your email
- Change your password
- Set up a passkey (WebAuthn) for passwordless login

## Billing

Go to **Workspace Settings** → **Billing** to:

- See your current plan and usage
- Upgrade to Team ($29/mo) or Business ($79/mo)
- Manage your subscription through the Stripe portal
- View invoices and payment history

## Your data

### What we store

- Your email, name, and password (hashed with Argon2id)
- Your documentation content (in workspaces)
- Activity logs (who edited what, when)

### What we don't store

- Credit card numbers (handled entirely by Stripe)
- Your Git credentials (OAuth tokens, not stored long-term)
- Tracking cookies (analytics are opt-in, GDPR compliant)

### Exporting your data

Your content is always portable:

- **With GitHub sync** — your docs are already in your GitHub repo as Markdown files
- **Without GitHub sync** — use the **Export** button in workspace settings to download a ZIP of all your Markdown files
- **Account data** — request a full data export by contacting us

### Deleting your account

Contact us at valoryxeu@gmail.com to request account deletion. We'll remove all your data within 30 days as required by GDPR.

## Security

- Passwords are hashed with Argon2id (OWASP recommended)
- Sessions use HttpOnly cookies (not accessible to JavaScript)
- All traffic is encrypted with TLS
- Optional passkey/WebAuthn for passwordless login
- Full audit trail of all account actions
