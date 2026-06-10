---
title: Analytics
description: Track page views, search queries, and documentation usage with built-in GDPR-compliant analytics.
weight: 9
---

# Analytics

DocPlatform includes built-in analytics for tracking how your documentation is used. No third-party tracking scripts or external services required.

## How it works

Analytics data is collected in a separate `analytics.db` SQLite database (not in the main database). This separation ensures analytics never impact content performance.

### What is tracked

| Data point | Description |
|---|---|
| **Page path** | Which page was viewed |
| **Referrer** | Where the visitor came from |
| **Timestamp** | When the page was viewed |
| **Search queries** | What users searched for |

### What is NOT tracked

- Raw IP addresses are never stored (consent records keep only a salted SHA-256 hash — set `DOCPLATFORM_IP_SALT` in production)
- Cookies or cross-session identifiers (without consent)
- Personally identifiable information

Visitors with **Do-Not-Track** enabled are never tracked, regardless of consent.

## GDPR compliance

Analytics requires explicit cookie consent from visitors.

### Consent flow

1. First-time visitors see a consent banner on published docs
2. If they accept, a consent cookie is set and pageviews are tracked
3. If they decline, no tracking occurs — the banner is dismissed
4. Consent status is recorded: `POST /api/analytics/consent`

### Data retention

Analytics data is automatically pruned after **90 days**. No manual cleanup required.

## Dashboard

Access analytics from the workspace sidebar or via the API.

### Top pages

```
GET /api/v1/workspaces/:id/analytics/pages?days=30
```

Returns the most-viewed pages in the workspace over the specified time period.

```json
{
  "pages": [
    { "path": "getting-started/quickstart.md", "views": 1234 },
    { "path": "guides/git-integration.md", "views": 892 },
    { "path": "reference/api.md", "views": 567 }
  ],
  "days": 30
}
```

### Top searches

```
GET /api/v1/workspaces/:id/analytics/searches?days=30
```

Returns the most popular search queries.

```json
{
  "searches": [
    { "query": "git sync", "count": 45 },
    { "query": "authentication", "count": 32 },
    { "query": "docker deploy", "count": 18 }
  ],
  "days": 30
}
```

### Overview

```
GET /api/v1/workspaces/:id/analytics/overview
```

Returns a summary dashboard with total views, total searches, and unique pages viewed.

## Feature gating

Analytics **reporting** is gated by plan feature, not edition:

| Edition / plan | Analytics |
|---|---|
| **Community Edition** (self-hosted) | ✔ Included, unlimited |
| **Cloud Free** | ✘ Not included |
| **Cloud Team / Business** | ✔ Included |

Pageview **collection** itself is consent-based and not plan-gated — if an org later upgrades, history recorded under consent is already there. On plans without analytics, the reporting endpoints return `403 PLAN_LIMIT`.

## Configuration

Analytics is enabled automatically — no configuration required. The analytics database is stored at `{DATA_DIR}/analytics.db` alongside the main database.
