---
title: "The Real Cost of Documentation Platforms"
description: "Per-seat pricing punishes documentation adoption. Here's a TCO comparison at 5, 15, 50, and 100 users — with actual numbers."
date: "2026-04-09"
author: "Valoryx Team"
tags: ["pricing", "comparison", "documentation"]
---

Per-seat pricing seems reasonable at first glance. Five users at $8/month? That's $40. Your team can afford $40.

But documentation is one of those tools where the number of people who *should* have access keeps growing. Engineers need to write. Product managers need to review. Support staff need to reference. New hires need to read and annotate. Suddenly you're not at 5 seats — you're at 50, and that "affordable" $8/seat is $400/month for a tool that stores text files.

Per-seat pricing for documentation has a perverse incentive: it punishes companies for letting more people contribute to docs. Managers start gatekeeping access. People share passwords. Docs become someone else's problem. And then you wonder why your documentation is always stale.

## The Numbers

Let's compare the actual monthly cost of four documentation platforms at different team sizes. These are list prices as of early 2026.

| Users | [GitBook](https://www.gitbook.com/pricing) ($8/user) | Notion ($10/user) | Confluence ($6/user) | Valoryx Cloud | Valoryx CE |
|------:|------:|------:|------:|------:|------:|
| 5 | $40 | $50 | $30 | $29 | $0 |
| 15 | $120 | $150 | $90 | $29 | $0 |
| 50 | $400 | $500 | $300 | $29 | $0 |
| 100 | $800 | $1,000 | $600 | $29 | $0 |

A few notes on these numbers:

**GitBook** charges $8/user/month on the Plus plan. The free tier is limited to 1 space with basic features. Published documentation is only available on paid plans.

**Notion** charges $10/user/month for the Plus plan. Notion is a general workspace tool, not a documentation platform — it lacks published docs, git sync, and purpose-built doc features. But many teams use it for docs, so it's a fair comparison on price.

**Confluence** charges $6.05/user/month (Standard) for cloud. This is Atlassian's current pricing for 1-100 users. The Data Center (self-hosted) version starts at $27,000/year for 500 users.

**Valoryx Cloud** is $29/month flat for the Team plan — 3 workspaces, 15 editors, 150 pages. Not per-seat. The [Free plan](/pricing/) gives you 1 workspace, 3 editors, 50 pages at $0.

**Valoryx Community Edition** is $0. Forever. Unlimited everything. You host it yourself.

## The Scaling Problem

Look at the 5-user column. Every platform is affordable. GitBook at $40/month is less than a team lunch. No one is going to fight over $40.

Now look at the 100-user column. GitBook is $800/month — $9,600/year for a tool that stores and renders markdown. At that point, you're in a budget review, someone is asking "do we really need this," and the answer is usually "let's limit access to people who actually write docs."

That decision — limiting access — is where documentation quality dies.

Good documentation happens when everyone can contribute. The engineer who just debugged a deployment issue should be able to update the deployment guide. The support agent who found a workaround should be able to add it to the troubleshooting page. The new hire who struggled with onboarding should be able to improve the onboarding docs.

Per-seat pricing makes each of those contributions cost $6-10/month. So instead, you get: "Email the docs team and ask them to update it." The docs team has a backlog. The update never happens. The knowledge stays in someone's head until they leave the company.

## Total Cost of Ownership

Monthly subscription price is only part of the cost. The real TCO includes:

### Infrastructure Cost (Self-Hosted Only)

If you choose Valoryx Community Edition, you need a server. A Hetzner CX22 (2 vCPU, 4GB RAM) costs EUR 3.99/month. DocPlatform uses ~100MB of RAM under normal load. That server can also run other things.

Annual infrastructure cost for self-hosted: **~$50/year.**

### Admin Time

**SaaS platforms** require almost no admin time for basic usage, but eat hours on SSO configuration, user provisioning/deprovisioning, and fighting with permission models that don't match your org structure.

**Self-hosted DocPlatform** requires initial setup (30 minutes), occasional updates (download new binary, restart — 5 minutes), and backup verification (automated, but worth checking monthly).

### Migration Cost

The hidden cost of any platform is what happens when you want to leave. Confluence's export is famously painful — years of content locked in a proprietary storage format. GitBook exports to markdown but loses metadata.

DocPlatform stores everything as markdown in a git repository. Your content is always accessible outside the platform, in a standard format, with full version history. Migration cost is zero because there's nothing to migrate — your content already lives in git.

## The Flat-Rate Argument

Valoryx Cloud uses flat-rate pricing instead of per-seat:

| Plan | Price | Workspaces | Editors | Pages |
|------|------:|------:|------:|------:|
| Free | $0/mo | 1 | 3 | 50 |
| Team | $29/mo | 3 | 15 | 150 |
| Business | Coming soon | More | More | More |

The limits are on workspaces and pages, not users. The Team plan at $29/month supports 15 editors — at any per-seat platform, 15 users would cost $90-150/month.

More importantly, viewers are free. If your company has 200 people who need to read docs but only 15 who write them, you don't pay for 200 seats. You pay for the Team plan.

This aligns incentives correctly: you want as many people as possible reading and contributing to your docs. The pricing model shouldn't punish that.

## When Per-Seat Makes Sense

Per-seat pricing isn't always wrong. For tools where each user generates significant cost (compute-heavy workloads, storage-intensive applications), charging per user reflects real resource usage.

Documentation platforms don't have this characteristic. Rendering markdown is cheap. Storing text is cheap. The marginal cost of adding the 51st user to a documentation platform is approximately zero. Charging $6-10/month for that 51st user is a business model choice, not a cost-reflective one.

## The Community Edition Calculation

For teams that can self-host, the Community Edition changes the calculation entirely:

| Expense | Annual Cost |
|---|---:|
| Server (Hetzner CX22) | $50 |
| Domain name | $12 |
| TLS certificate (Let's Encrypt) | $0 |
| DocPlatform CE license | $0 |
| **Total** | **$62/year** |

That's $62/year for unlimited users, unlimited pages, unlimited workspaces, full-text search, git sync, RBAC, WebAuthn, and MCP integration. No per-seat fees, no feature gates, no "contact sales for enterprise pricing."

At 100 users, that's $0.62/user/year versus $72-120/user/year for hosted per-seat platforms.

## Making the Decision

Here's a simple framework:

**Choose Valoryx Cloud ($29/mo)** if you don't want to manage infrastructure but want flat-rate pricing. Good for small-to-medium teams that want a hosted solution without per-seat cost scaling.

**Choose Valoryx Community Edition ($0)** if your team can manage a Linux server. Best for teams that care about data sovereignty, want zero recurring cost, or have compliance requirements that demand self-hosting. See the [install guide](/install/).

**Choose a per-seat platform** if your organization has fewer than 10 users, your team doesn't write many docs, and you're already embedded in that vendor's ecosystem (e.g., Confluence if you're all-in on Atlassian).

**Don't choose based on the 5-user price.** Choose based on the 50-user price, because that's where you're heading. Documentation tools have a way of expanding across organizations — if the tool is good, more people want access. Your pricing model should reward that, not penalize it.

Compare all plans on the [pricing page](/pricing/) or check out the [open-source page](/open-source/) for the full Community Edition feature list.
