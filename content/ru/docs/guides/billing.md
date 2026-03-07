---
title: Billing & Plans
description: Configure Stripe billing, understand plan tiers, feature gating, and subscription management.
weight: 999
---

# Billing & Plans

DocPlatform uses Stripe for subscription billing. Three plan tiers are available, each with different limits and features.

## Plans

| Feature | Community (Free) | Team ($99/mo) | Business ($299/mo) |
|---|---|---|---|
| **Editors** | 5 | 10 | 50 |
| **Workspaces** | 3 | Unlimited | Unlimited |
| **Viewers / Commenters** | Unlimited | Unlimited | Unlimited |
| **Pages** | Unlimited | Unlimited | Unlimited |
| **Published docs** | Unlimited | Unlimited | Unlimited |
| **Analytics** | — | Included | Included |
| **Custom domains** | — | Included | Included |
| **Advanced AI** | — | Included | Included |
| **Priority support** | — | — | Included |

### Annual pricing

Annual subscriptions include 2 months free:

| Plan | Monthly | Annual |
|---|---|---|
| **Team** | $99/mo | $990/yr ($82.50/mo) |
| **Business** | $299/mo | $2,990/yr ($249.17/mo) |

### Free trial

New organizations get a **14-day free trial** of the Team plan. During the trial:

- All Team features are available
- No credit card required to start
- At trial end, the organization reverts to Community Edition limits

The trial duration is configurable via `TRIAL_DURATION_DAYS`.

## Setup

### Prerequisites

1. A Stripe account (test or live mode)
2. Stripe Price IDs for each plan tier

### Configuration

Set the following environment variables:

```bash
# .env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Monthly prices
STRIPE_PRICE_TEAM=price_team_monthly_id
STRIPE_PRICE_BUSINESS=price_business_monthly_id

# Annual prices
STRIPE_PRICE_TEAM_ANNUAL=price_team_annual_id
STRIPE_PRICE_BUSINESS_ANNUAL=price_business_annual_id

# Optional
TRIAL_DURATION_DAYS=14
FF_BILLING=true
```

### Stripe webhook

Create a webhook endpoint in your Stripe dashboard pointing to:

```
https://your-domain.com/api/webhooks/stripe
```

Subscribe to these events:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

DocPlatform handles all webhook events idempotently — duplicate deliveries are safely ignored.

### Disabling billing

Set `FF_BILLING=false` to disable billing entirely. All organizations are treated as having unlimited features (useful for self-hosted single-tenant deployments).

## User experience

### Upgrading

Workspace admins can upgrade from the billing page:

1. Navigate to **Settings** → **Billing**
2. Click **Upgrade** on the desired plan
3. Complete payment via Stripe Checkout
4. Features activate immediately

### Managing subscription

```
POST /api/v1/billing/portal
```

Creates a Stripe Customer Portal session where users can:

- Update payment method
- Switch between monthly and annual billing
- Cancel subscription
- View invoice history

### Checking limits

```
GET /api/v1/billing/limits
```

Returns current plan limits and usage:

```json
{
  "plan": "team",
  "limits": {
    "max_editors": 10,
    "max_workspaces": -1,
    "features": ["analytics", "custom_domains", "ai_advanced"]
  },
  "usage": {
    "editors": 4,
    "workspaces": 2
  }
}
```

## Feature gating

When an organization exceeds its plan limits:

- **Editors**: New editor invitations are rejected. Existing editors retain access.
- **Workspaces**: New workspace creation is rejected. Existing workspaces remain accessible.
- **Gated features**: API returns `403` with a clear error message indicating the required plan.

## Super admin controls

Super admins can manage billing across all organizations:

```
GET  /api/admin/billing/overview        — Platform-wide billing summary
GET  /api/admin/billing/subscriptions   — All active subscriptions
GET  /api/admin/billing/events          — Webhook event log
PUT  /api/admin/orgs/:id/plan           — Change organization plan
POST /api/admin/orgs/:id/subscription/override — Override subscription (e.g., comp plans)
```

## Subscription lifecycle

```
Trial (14 days)
    │
    ├── User upgrades → Active subscription
    │
    └── Trial expires → Grace period (7 days)
                            │
                            ├── User upgrades → Active subscription
                            │
                            └── Grace expires → Restricted (Community limits)
```

During the grace period, all features remain available but a banner prompts the user to subscribe. After grace expires, the organization reverts to Community Edition limits.
