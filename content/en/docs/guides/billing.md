---
title: Billing & Plans
description: Configure Stripe billing, understand plan tiers, feature gating, and subscription management.
weight: 10
---

# Billing & Plans

> **Cloud edition only.** Billing applies to **DocPlatform Cloud** ([app.valoryx.dev](https://app.valoryx.dev)). The self-hosted Community Edition contains no billing code at all — it is free forever and unlimited, and nothing on this page applies to it.

DocPlatform Cloud uses Stripe for subscription billing across three cloud tiers: Free, Team, and Business.

## Plans

| Feature | Community (self-hosted) | Cloud Free | Cloud Team ($29/mo) | Cloud Business ($79/mo) |
|---|---|---|---|---|
| **Editor seats** (Editor + Admin roles) | Unlimited | 3 | 15 | 50 |
| **Workspaces** | Unlimited | 1 | 3 | 10 |
| **Viewers / Commenters** | Unlimited | Unlimited | Unlimited | Unlimited |
| **Pages per workspace** | Unlimited | 50 | 150 | Unlimited |
| **Published docs** | Unlimited | Unlimited | Unlimited | Unlimited |
| **Analytics** | Included | — | Included | Included |
| **Custom domains** | Included | — | Included | Included |
| **"Powered by Valoryx" badge** | Always shown | Always shown | Hidden by default (opt-in to show) | Hidden by default (opt-in to show) |
| **Priority support** | — | — | — | Included |

> "Community Edition" and the cloud "Free tier" are different things: Community is the unlimited self-hosted binary; Free is the restricted $0 tier of the hosted cloud service.

### Annual pricing

Annual subscriptions include 2 months free:

| Plan | Monthly | Annual |
|---|---|---|
| **Team** | $29/mo | $290/yr ($24.17/mo) |
| **Business** | $79/mo | $790/yr ($65.83/mo) |

### Free trial

Paid subscriptions start with a **14-day free trial** — all plan features are available during the trial. If the trial ends without an active subscription, the organization enters a grace period and then reverts to **Free tier** limits.

## Setup (Cloud operators)

This section documents how the Cloud edition's billing is configured server-side. It is informational for Cloud customers — these variables only exist in the cloud binary.

### Prerequisites

1. A Stripe account (test or live mode)
2. Stripe Price IDs for each plan tier

### Configuration

```bash
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
- `invoice.paid`
- `invoice.payment_failed`
- `customer.subscription.updated`
- `customer.subscription.deleted`

DocPlatform handles all webhook events idempotently — duplicate deliveries are safely ignored.

### Disabling billing

Set `FF_BILLING=false` to disable billing enforcement entirely on a cloud binary — all organizations are treated as unlimited. (Self-hosters don't need this: the Community Edition has no billing to disable.)

## User experience

### Upgrading

Admins can upgrade from the billing page:

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

Returns current plan limits and usage (`null` limits mean unlimited):

```json
{
  "plan_id": "team",
  "plan_name": "Team",
  "status": "active",
  "max_workspaces": 3,
  "current_workspaces": 2,
  "max_editors": 15,
  "current_editors": 4,
  "max_pages_per_workspace": 150,
  "features": { "analytics": true, "custom_domains": true, "published_docs": true, "hide_badge": true }
}
```

## Feature gating

When an organization hits its plan limits:

- **Editor seats**: New editor/admin invitations are rejected with `403 PLAN_LIMIT_REACHED`. Existing editors retain access; Commenter/Viewer invitations still work.
- **Workspaces / pages**: New creation is rejected with the same error code. Existing content remains accessible.
- **Gated features** (e.g., analytics on Free): API returns `403` indicating the required plan.

## Subscription lifecycle

```
Trial (14 days)
    │
    ├── User subscribes → Active subscription
    │
    └── Trial expires → Grace period (7 days)
                            │
                            ├── User subscribes → Active subscription
                            │
                            └── Grace expires → Restricted
```

During the grace period, everything keeps working while the customer is prompted to subscribe. In the **restricted** state, creating new workspaces, pages, or editor invitations is blocked until billing resumes (a **paused** subscription blocks writes only). Existing content remains readable throughout.
