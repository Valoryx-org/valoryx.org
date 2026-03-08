# Valoryx Site Upgrade Plan v5 (LOCKED)

> Complete architecture, domain strategy, infrastructure blueprint, UX fixes, new pages, AI discovery engine, growth mechanics, and agent-native documentation vision for the Valoryx ecosystem.
> **Status:** LOCKED for development. Phase 1 launch readiness (Weeks 31–35).
> **Locked:** 2026-03-08. No further structural changes. Implementation proceeds from this version.
> **Supersedes:** SITE-UPGRADE-PLAN v3, v4. Incorporates ARCHITECTURE-V3.md cross-validation, deep AI discovery analysis, production infrastructure blueprint, growth engine design, failure modes, security hardening, and all reviewer feedback (5 independent reviews consolidated).
>
> **Contractor scope:** Sections 1–12 are the executable implementation plan (~18 days). Sections 14–18 are strategic context for the founder — contractors do not need to read them.

---

## 0. Relationship to Phase 1 Plan

**This document is NOT a separate project.** It specifies the Content, UX, Marketing, Infrastructure, AI Discovery, and Growth work required for Phase 1 launch. All tasks merge into Phase 1's final sprint.

| This Document | Maps To |
|---------------|---------|
| Section 1 (Domain + Infrastructure) | Phase 1 Launch Infrastructure |
| Section 2 (Hugo pages: pricing, mcp, templates, install, vs, security, open-source, changelog) | Phase 1 Sprint 4 — Polish |
| Section 3 (SPA fixes) | Phase 1 Section 5 — Frontend Contractor backlog |
| Section 4 (UX resolutions) | Phase 1 Sprint 4 — Backend adjustments |
| Section 5 (Distribution + AI Discovery) | Phase 1 Launch Checklist |
| Section 14 (Agent-Native Vision) | Phase 2+ Roadmap |
| Section 15 (Growth Engine) | Phase 1.5–2 Roadmap |
| Sections 16-18 (Infrastructure, Security, Risks) | Operational Runbook |

**Phase 1 decisions that constrain this plan:**
- **Decision 0.3:** Billing is per-plan, NOT per-workspace. Prices: $29/mo and $79/mo.
- **Decision 0.7:** MCP is stdio only at launch. Remote HTTP/SSE deferred to Phase 1.5.
- **Decision 0.16:** Annual billing and trial periods deferred to Phase 1.5 (data-driven).
- **Frontend budget:** 15 contractor days total. SPA work in this plan must fit within that budget. Admin panel frontend (3d across S2.8/S3.7/S4.8) is done by the main developer during each sprint's capstone — NOT in the 15d contractor budget.

**Companion documents (single source of truth hierarchy):**
1. `ARCHITECTURE-V3.md` — Definitive technical specification (interfaces, schemas, data flows)
2. `PHASE-1-PLAN.md` Section 2 — Plan Matrix (canonical for prices, limits, features)
3. `MCP-CREATION-PLAN.md` — Phase 1.5 remote HTTP transport expansion (7 new tools, 20 total)
4. `AI-DISCOVERY-STRATEGY.md` — AI discovery flywheel architecture (integrated into Section 5.4 below)

**Cross-reference alignment notes (ARCHITECTURE-V3.md):**
- **MCP tool count:** ARCHITECTURE-V3 specifies 19 Phase 1 + 4 Phase 2 = 23 tools (full vision). Current binary ships **13 tools** (Phase 1 launch). MCP-CREATION-PLAN adds 7 more in Phase 1.5 = 20 total. Remaining 3 tools (from the 23) ship in Phase 2. All marketing surfaces use the shipped count (13 at launch, 20 at Phase 1.5).
- **Pricing model:** ARCHITECTURE-V3 §20.4 says "$29/ws/mo" — this is outdated. Decision 0.3 (canonical) says **per-plan, NOT per-workspace**. $29/mo for Team plan (includes 3 workspaces). $79/mo for Business plan (includes 10 workspaces).
- **Published page limit:** ARCHITECTURE-V3 plans table has `max_published_pages: 10`. This plan raises it to **50** (Section 4.2). Migration `003_billing_plans.sql` must be updated. **Verify:** Community edition self-hosted card says "3 Workspaces · 5 Editors · ∞ Pages" — confirm this matches PHASE-1-PLAN.md matrix. If matrix changes, update Section 2.1 copy.

**Single Source of Truth rule:** After any plan matrix change (limits, prices), regenerate all artifacts and re-run pricing tests so all surfaces (site, app, docs) show identical numbers. `PHASE-1-PLAN.md` Section 2 (Plan Matrix) is canonical.

---

## 1. Domain & URL Architecture

### 1.1 Domain Map (Final — Single Brand Domain)

**Strategy:** `valoryx.org` is the single canonical brand domain. All subdomains live under `.org`. `valoryx.dev` is a 301 redirect for brand protection only.

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALORYX ECOSYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  valoryx.org          Marketing hub (Hugo → Cloudflare Pages)   │
│  ├── /                Homepage (hero, features, comparison)     │
│  ├── /pricing/        Dedicated pricing + plan comparison  NEW  │
│  ├── /templates/      Use cases & starter templates        NEW  │
│  ├── /mcp/            MCP integration guide                NEW  │
│  ├── /vs/             Competitor comparison pages           NEW  │
│  │   └── /vs/gitbook/ (P0 — others added post-launch)          │
│  ├── /docs/           Product documentation (synced repo)       │
│  ├── /blog/           Technical blog                            │
│  ├── /changelog/      Release notes                        NEW  │
│  ├── /install/        Quick install instructions           NEW  │
│  ├── /security/       Security practices                   NEW  │
│  ├── /open-source/    Community edition info                NEW  │
│  ├── /llms.txt        AI discovery metadata                NEW  │
│  ├── /llms-full.txt   Extended AI metadata                 NEW  │
│  └── /fr/ /de/ etc.   Translations (all pages)                  │
│                                                                 │
│  app.valoryx.org      Cloud SaaS application (Go binary)       │
│  ├── /                Go-rendered landing page (real route)     │
│  ├── /#/login         Login (email + OIDC)                      │
│  ├── /#/register      Register                                  │
│  ├── /#/pricing       Interactive pricing + Stripe checkout NEW │
│  ├── /#/workspaces    Dashboard                                 │
│  ├── /#/workspace/... Editor, settings                          │
│  ├── /#/settings/billing  Subscription management          NEW  │
│  └── /#/onboarding    First-run wizard (3 steps)           NEW  │
│                                                                 │
│  docs.valoryx.org     Dogfood showcase (published via product)  │
│  └── /p/valoryx-docs  Published docs (canonical → valoryx.org)  │
│                                                                 │
│  mcp.valoryx.org      Remote MCP server (Phase 1.5)            │
│  └── POST /mcp        Streamable HTTP endpoint                  │
│                                                                 │
│  FUTURE (Phase 2+):                                             │
│  api.valoryx.org      Public REST API subdomain                 │
│  demo.valoryx.org     No-signup interactive demo                │
│  status.valoryx.org   Uptime monitoring (UptimeKuma/BetterStack)│
│                                                                 │
│  REDIRECTS:                                                     │
│  valoryx.dev          ──→ 301 to valoryx.org                    │
│  *.valoryx.dev        ──→ 301 to *.valoryx.org                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Domain Decisions

| Decision | Rationale |
|----------|-----------|
| **Single brand domain: `valoryx.org`** | All marketing, app, docs, and MCP under one root domain. Maximizes SEO link equity, eliminates user confusion, enables shared cookies/SSO. Matches ProtonMail, Signal, Stripe pattern |
| All marketing on `valoryx.org` (subdirectories) | Consolidates SEO authority — `/pricing/`, `/templates/`, `/mcp/`, `/vs/` all boost root domain |
| Cloud app on `app.valoryx.org` | Same root domain as marketing = seamless user journey. No cross-domain confusion |
| `valoryx.dev` → permanent 301 to `valoryx.org` | Brand protection ($12-15/yr). Developer habit typing. Future flexibility |
| MCP remote on `mcp.valoryx.org` (Phase 1.5) | Stdio ships at launch. Remote HTTP on `mcp.valoryx.org` deferred per Decision 0.7 |
| Docs canonical: `valoryx.org/docs/` (Hugo) | SEO path. `docs.valoryx.org` sets `<link rel="canonical">` to prevent duplicate content |
| `/vs/` competitor pages | Programmatic SEO — "GitBook alternative" etc. are high-intent searches |

### 1.2.1 Why `.org` Over `.dev` — And Why It Matters for AI Discovery

**For humans (traditional reasons):**

1. **Brand unity:** Developers associate `valoryx.org` with the project. When they click "Start Free" on `/pricing/` and land on `app.valoryx.org`, it's the same product. Split TLDs create confusion.

2. **SEO consolidation:** Google treats subdomains under the same root as one site for link equity. All rankings from `valoryx.org/pricing`, `/mcp/`, `/blog/` flow to `app.valoryx.org`. A split (`app.valoryx.dev`) starts with zero authority.

3. **Trust signal:** `.org` carries the strongest community/open-source trust signal. Perfect for a hybrid product.

4. **Technical simplicity:** Same root = trivial shared cookies for future SSO. No cross-domain headaches.

5. **Risk mitigation:** Owning `.dev` as a redirect protects the brand. Can flip direction later if needed.

**For AI systems (the deeper reason):**

AI systems discover tools through web crawling, and they build internal knowledge graphs. When all content lives under one root domain, the AI learns:

```
Valoryx (concept node)
 ├── docs        (valoryx.org/docs/)
 ├── MCP server  (valoryx.org/mcp/)
 ├── API         (valoryx.org/docs/reference/api/)
 ├── pricing     (valoryx.org/pricing/)
 ├── templates   (valoryx.org/templates/)
 └── cloud app   (app.valoryx.org)
```

All nodes share one root → one concept in the knowledge graph → stronger association.

If split across `valoryx.org` + `valoryx.dev`, the graph splits into two weaker nodes. AI assistants associate less confidence with either domain.

**This is not theoretical.** LLMs are trained on web crawls (Common Crawl, etc.) where domain authority directly impacts which content gets embedded and with what weight. Single-domain consolidation:
- Increases embedding probability for all subpages
- Strengthens "Valoryx = documentation platform" association
- Improves recommendation likelihood when users ask AI for doc tools
- Makes `llms.txt` at the root domain more authoritative

### 1.2.2 Canonical Docs Strategy

| URL | Purpose | Canonical |
|-----|---------|-----------|
| `valoryx.org/docs/*` | SEO-optimized docs (Hugo-generated) | Self (canonical) |
| `docs.valoryx.org/p/valoryx-docs/*` | Live dogfood showcase | Points to `valoryx.org/docs/*` via `<link rel="canonical">` |

**Rules:**
- No sitewide nav links to `docs.valoryx.org` except a discreet "Live Demo" badge on the docs landing page
- `docs.valoryx.org` pages include banner: "This is a live instance of Valoryx. Canonical docs: valoryx.org/docs/"
- Google Search Console: declare `valoryx.org/docs/` as the preferred version

### 1.2.3 Shared Cookie Intelligence (Phase 1.5)

Set session cookie with `Domain: .valoryx.org`. Then Hugo marketing site can check cookie presence:
- If session cookie exists: "Sign Up" button → "Go to Dashboard"
- If no cookie: standard "Sign Up" / "Download" CTAs

**Implementation:** Small JS snippet in Hugo `header.html` that checks `document.cookie` for the session token name. No API call — just presence check.

**Security:** Cookie is HttpOnly + Secure + SameSite=Lax. The marketing site JS only checks for _existence_ (name match), never reads the token value. This is safe because the `.valoryx.org` scope is fully controlled infrastructure.

### 1.2.4 Domain Setup Checklist (30 minutes)

- [ ] Confirm `valoryx.dev` is registered (or register: ~$12-15/yr)
- [ ] Cloudflare DNS: add `valoryx.dev` zone with permanent 301 redirect rule to `https://valoryx.org$1`
- [ ] Cloudflare DNS: add wildcard 301 `*.valoryx.dev` → `*.valoryx.org`
- [ ] Verify: `curl -I https://valoryx.dev` returns `301 Location: https://valoryx.org/`
- [ ] Verify: `curl -I https://app.valoryx.dev` returns `301 Location: https://app.valoryx.org/`
- [ ] Update Stripe success/cancel URLs to use `app.valoryx.org`
- [ ] Update OIDC redirect URIs to use `app.valoryx.org`
- [ ] Grep codebase for any hardcoded `.dev` domain references
- [ ] Set `<link rel="canonical">` on all `docs.valoryx.org` pages pointing to `valoryx.org/docs/`

### 1.2.5 Brand Protection — Additional Domains

Buy and 301-redirect to `valoryx.org`:

| Domain | Cost | Priority | Why |
|--------|------|----------|-----|
| `valoryx.dev` | ~$12-15/yr | **P0** (pre-launch) | Developer habit typing |
| `valoryx.com` | ~$12/yr | **P0** (pre-launch) | Most common TLD, type-in traffic |
| `valoryx.io` | ~$30/yr | **P1** (Month 1) | Developer community association |
| `valoryx.net` | ~$12/yr | **P2** (if budget allows) | Low priority catch-all |

**Total:** ~$55-70/yr. Prevents squatting, catches type-in traffic, future flexibility. Register P0 domains before launch day.

### 1.2.6 Stripe Callback Routing (Server-Side)

**Problem:** Many browsers and Stripe's redirect logic occasionally strip the hash (#) fragment from URLs, causing `app.valoryx.org/#/settings/billing?success=1` to land users on the root page instead of the billing dashboard.

**Solution:** Use a server-side redirect path:

1. Set Stripe `success_url` to `https://app.valoryx.org/auth/stripe-callback?session_id={CHECKOUT_SESSION_ID}`
2. Go handler at `/auth/stripe-callback`:
   - Verifies session via Stripe API
   - Sets/refreshes session cookie
   - Issues `302 Redirect` to `/#/settings/billing?success=1`
3. Set Stripe `cancel_url` to `https://app.valoryx.org/auth/stripe-cancel` → redirects to `/#/pricing`

**Why:** Server-side redirects are robust across all browsers and global configurations. Hash fragments are preserved by the 302 redirect because the browser handles navigation after receiving the redirect target.

**Effort:** 0.25d (add 2 Go handlers, update Stripe URLs). Already accounted in backend budget.

### 1.3 Production Infrastructure Architecture

**Phase 1 (Launch Day):**

```
Internet
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│                  Cloudflare (Edge Layer)                  │
│                                                          │
│  DNS:                                                    │
│    valoryx.org        → Cloudflare Pages (Hugo static)   │
│    app.valoryx.org    → GCP instance (Go binary)         │
│    docs.valoryx.org   → GCP instance (same binary)       │
│    mcp.valoryx.org    → 503 (Phase 1.5)                  │
│    valoryx.dev        → 301 redirect rule                │
│                                                          │
│  Edge features:                                          │
│    TLS termination, DDoS protection, WAF rules           │
│    Bot management, rate limiting (edge-level)            │
│    Cache: static assets (1yr), HTML (5min)               │
└──────────────────────────┬──────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
     ┌────────▼────────┐     ┌─────────▼─────────┐
     │ Cloudflare Pages │     │ GCP Instance       │
     │ (Hugo static)    │     │ (Hetzner CX23 alt) │
     │                  │     │                     │
     │ valoryx.org      │     │ Caddy (reverse     │
     │ marketing site   │     │   proxy, auto-TLS)  │
     │ Zero origin      │     │   │                 │
     │ traffic          │     │   ├── app.valoryx.org → :8080 │
     │                  │     │   └── docs.valoryx.org → :8080│
     └──────────────────┘     │                     │
                              │ Go Binary           │
                              │ (DocPlatform)       │
                              │ ├── SQLite (NVMe)   │
                              │ ├── Bleve (embedded) │
                              │ ├── Git repos (local)│
                              │ └── MCP (stdio only) │
                              └─────────────────────┘
```

**Why this architecture:**
- Marketing site (Hugo) on Cloudflare Pages = zero origin traffic, global CDN, free
- Application on single instance = matches ARCHITECTURE-V3.md §12.5 Phase 1 spec
- Caddy handles TLS for subdomains that bypass Cloudflare proxy (if needed)
- Cloudflare proxy handles TLS for everything else
- Total cost: ~€3.49-5/mo (Hetzner CX23) + $0 (Cloudflare free tier)

**Phase 2 (when scaling triggers hit):**

```
Cloudflare DNS
  │
  ├── valoryx.org      → Cloudflare Pages (unchanged)
  ├── app.valoryx.org  → Load Balancer → 2+ Go instances
  ├── docs.valoryx.org → Same LB (or dedicated instance)
  ├── mcp.valoryx.org  → Dedicated Go instance (--mcp-only)
  ├── api.valoryx.org  → Same LB as app (path routing)
  └── status.valoryx.org → UptimeKuma/BetterStack
```

Scaling triggers (from ARCHITECTURE-V3 §12.5): >50 paying orgs, >50 concurrent editors, >500 workspaces, enterprise RLS requirement.

### 1.3.1 Why Reverse Proxy Matters

Caddy (or nginx) as a reverse proxy layer means services can move without DNS changes:
- Move `app` to a new server → update Caddy upstream, zero DNS propagation
- Add `mcp` service → add Caddy route, no Cloudflare change
- Split `docs` to its own instance → update upstream
- Migrate to Kubernetes → Caddy becomes ingress, same DNS

Without a reverse proxy, every infrastructure change requires DNS updates (TTL delays, cache issues).

### 1.4 Infrastructure Failure Modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| **Cloudflare outage** | All domains unreachable | Extremely rare (~99.99% SLA). No mitigation at Phase 1 scale. Phase 2: secondary DNS |
| **GCP instance crash** | `app.valoryx.org` + `docs.valoryx.org` down | `valoryx.org` (Hugo on Cloudflare Pages) still works. Users see marketing site + status page. Auto-restart via systemd. Phase 2: multi-instance |
| **SQLite corruption** | Data loss risk | Daily automated backup (ARCHITECTURE-V3 §20: `.docplatform/backups/`, 7-day rotation). `docplatform rebuild` recovers from git |
| **Caddy crash** | App unreachable but instance healthy | systemd auto-restart (<5s recovery). Caddy is extremely stable |
| **DNS misconfiguration** | Subdomain unreachable | Pre-launch DNS validation checklist (Section 1.2.4). Cloudflare audit log |
| **NVMe disk full** | Writes fail | Monitoring alert at 80%. SQLite WAL + git repos are primary consumers |
| **Marketing docs drift** | Hugo docs out of sync with dogfood docs | Phase 1.5: webhook trigger from workspace settings → GitHub Action rebuilds Hugo. Phase 1: manual `git push` to `docplatform-docs` repo triggers Hugo rebuild |

**Key principle:** Marketing site (`valoryx.org`) and application (`app.valoryx.org`) are on separate infrastructure. If the app goes down, the marketing site (and thus SEO, AI crawlability, `llms.txt`) remains up.

**Backup verification (mandatory):** Verify `sqlite3 .backup` runs every 6 hours and streams to offsite storage (R2 or S3). Replication is NOT a substitute for point-in-time recovery. Add to monitoring: alert if last backup is >8 hours old.

### 1.5 Security Hardening (Launch Day)

| Control | Implementation | Priority |
|---------|----------------|----------|
| **HSTS** | `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` via Cloudflare | P0 |
| **TLS 1.3** | Cloudflare minimum version = TLS 1.3 | P0 |
| **DNSSEC** | Enable on Cloudflare for `valoryx.org` zone | P0 |
| **WAF rules** | Cloudflare managed ruleset (OWASP Core) | P0 |
| **Bot management** | Cloudflare bot fight mode (free tier) | P0 |
| **CSP headers** | `Content-Security-Policy` on Hugo site + app | P1 |
| **Rate limiting** | Per ARCHITECTURE-V3 §4.9 rate limit spec (per-org token bucket) | P0 |
| **API key hashing** | SHA-256 with pepper (already implemented, ARCHITECTURE-V3 §19) | Done |
| **CORS** | Strict origin whitelist: `valoryx.org`, `app.valoryx.org` | P0 |
| **Cookie security** | HttpOnly, Secure, SameSite=Lax, `Domain=.valoryx.org` (Phase 1.5 for cross-subdomain) | P0 |
| **Published docs abuse** | Free tier: `noindex` meta tag by default (opt-out on paid plans). Content moderation queue in admin panel (S4.8). Rate limit published docs at 1000 req/min per workspace | P1 |
| **Subdomain squatting** | Validate `{slug}.docs.valoryx.org` slugs against reserved list (admin, api, app, docs, mcp, www, status, etc.) | P0 |

### 1.6 SEO & AI-Friendliness Strategy

**SEO (already implemented, extend to new pages):**
- hreflang bidirectional tags on every page (6 languages)
- Canonical URLs on every page
- JSON-LD structured data per page type
- Semantic HTML with proper heading hierarchy
- sitemap.xml auto-generated by Hugo
- robots.txt allowing all crawlers

**AI-Friendliness (from AI-DISCOVERY-STRATEGY.md):**

AI assistants discover and recommend tools through three channels:

| Channel | Mechanism | Valoryx Asset |
|---------|-----------|---------------|
| **Training data** | Web crawl → embedding | `valoryx.org/*` (single domain authority) |
| **Runtime discovery** | MCP protocol → tool schema | MCP registry + `mcp.valoryx.org` (Phase 1.5) |
| **Structured metadata** | `llms.txt`, JSON-LD, registry | `valoryx.org/llms.txt`, MCP registries |

**Implementation:**
- `llms.txt` at `valoryx.org/llms.txt` — machine-readable product summary
- `llms-full.txt` at `valoryx.org/llms-full.txt` — complete docs + tool schemas for LLMs
- `<meta name="llms-full" content="https://valoryx.org/llms-full.txt">` on every page (Hugo partial)
- JSON-LD `SoftwareApplication` schema with `offers`, `featureList` on `/mcp/` page
- JSON-LD `FAQPage` schema on FAQ sections
- Structured code examples on `/mcp/` for AI discovery

**`llms.txt` content:**
```
# Valoryx
> Git-native documentation platform. Single binary, bidirectional git sync, WYSIWYG editor, MCP server for AI agents.

## Links
- Homepage: https://valoryx.org/
- Documentation: https://valoryx.org/docs/
- Pricing: https://valoryx.org/pricing/
- Templates: https://valoryx.org/templates/
- MCP Server: https://valoryx.org/mcp/
- Cloud App: https://app.valoryx.org/
- GitHub: https://github.com/Valoryx-org/docplatform

## Quick Start
curl -fsSL https://valoryx.org/install.sh | sh
docplatform init my-docs
docplatform serve

## MCP Integration (stdio, local)
docplatform mcp --workspace <slug> --api-key <key>
13 tools at launch (20 in Phase 1.5): list_pages, read_page, write_page, update_page, delete_page, move_page, search, get_context, list_workspaces, get_tree, validate_links, get_theme, update_theme
```

**`llms-full.txt` as RAG-optimized sitemap:**

Treat `llms-full.txt` as more than a link list — include 2-sentence summaries of every major feature. When an AI agent reads this file, it builds a high-resolution internal map of Valoryx, enabling accurate "how-to" answers without requiring users to paste entire docs.

**`llms-full.txt` scope & safety rules:**
- **Generation rule:** `llms-full.txt` is built from the `docplatform-docs` repo as a separate build step in the Hugo pipeline. Generation scripts live in the docs repo, NOT in the app binary. Never generated from a live workspace.
- Only public marketing/docs repo content is included (Hugo `/docs/` content)
- Never includes cloud customer content or `docs.valoryx.org` workspace data
- Includes full tool input/output JSON schemas, example JSON-RPC requests/responses
- Include 2-sentence feature summaries for each major capability (MCP, git sync, search, publishing, editor, themes, API keys)
- Max size: 500KB compressed (serve as `llms-full.txt.gz` with gzip encoding)
- Update schedule: regenerate on docs merge or daily cron
- Validate: `robots.txt` must explicitly allow `llms.txt` and `llms-full.txt`

**New static files:**
```
static/llms.txt          — Short product summary for LLMs
static/llms-full.txt     — Complete docs + tool schemas for LLMs
```

**Pre-launch validation checklist:**
- [ ] Verify `robots.txt` allows crawling of `llms.txt` and `llms-full.txt`
- [ ] Test with Google Search Console robots.txt tester
- [ ] Verify JSON-LD with Google Rich Results Test
- [ ] Check hreflang on all new pages
- [ ] Verify `llms-full.txt` contains no internal/private content

---

## 2. New Pages for valoryx.org (Hugo)

### 2.1 `/pricing/` — Dedicated Pricing Page

**Why needed:** Homepage `#pricing` is a quick glance. Cloud users need a detailed comparison. Currently there's confusion between Community (self-hosted) and Free (cloud).

**Key UX decision: Deployment Toggle + Interactive Calculator**

Instead of showing all 4 plans simultaneously (which creates "Why is self-hosted free with more features?" confusion), use a deployment mode toggle with an interactive calculator:

```
/pricing/
├── Hero: "Simple, transparent pricing"
├── Deployment Toggle:
│   ┌──────────────────────────────────────────┐
│   │  How do you want to run Valoryx?         │
│   │                                          │
│   │  [ Cloud — We host it ]                  │
│   │  [ Self-Hosted — You host it ]           │
│   └──────────────────────────────────────────┘
│
├── Interactive Calculator (Cloud view only):
│   ┌──────────────────────────────────────────┐
│   │  How many editors?  [━━━━●━━━━━] 8       │
│   │  Recommended: Team ($29/mo)              │
│   └──────────────────────────────────────────┘
│
├── CLOUD VIEW (default):
│   3 Plan Cards:
│   ┌────────────────┬────────────────┬────────────────┐
│   │   FREE          │   TEAM         │   BUSINESS     │
│   │   $0/mo         │   $29/mo       │   $79/mo       │
│   │                 │   POPULAR      │                │
│   │   1 Workspace   │   3 Workspaces │   10 Workspaces│
│   │   3 Editors     │   15 Editors   │   50 Editors   │
│   │   50 Pub Pages  │   ∞ Pub Pages  │   ∞ Pub Pages  │
│   │   ✓ Git Sync    │   ✓ Git Sync   │   ✓ Git Sync   │
│   │   ✓ WYSIWYG     │   ✓ WYSIWYG    │   ✓ WYSIWYG    │
│   │   ✓ Search      │   ✓ Search     │   ✓ Search     │
│   │   ✓ Pub Docs    │   ✓ Pub Docs   │   ✓ Pub Docs   │
│   │   ✓ MCP (stdio) │   ✓ MCP (stdio)│   ✓ MCP (stdio)│
│   │   ✗ Custom Dom. │   ✓ Custom Dom.│   ✓ Custom Dom.│
│   │   ✗ SSO/SAML    │   ✗ SSO/SAML   │   ✓ SSO/SAML   │
│   │   ✗ Analytics   │   ✗ Analytics  │   ✓ Analytics  │
│   │                 │                │   ✓ Audit Logs │
│   │   [Start Free]  │   [Upgrade]    │   [Upgrade]    │
│   └────────────────┴────────────────┴────────────────┘
│
├── SELF-HOSTED VIEW:
│   Single Card:
│   ┌──────────────────────────────────────────┐
│   │   COMMUNITY EDITION                      │
│   │   Free Forever                           │
│   │                                          │
│   │   3 Workspaces · 5 Editors  · ∞ Pages   │
│   │   Full feature set · No license key      │
│   │   You own your data · Your infrastructure│
│   │                                          │
│   │   [Download]  [View on GitHub]           │
│   │                                          │
│   │   Need enterprise support?               │
│   │   [Contact Us]                           │
│   └──────────────────────────────────────────┘
│
├── Full Feature Comparison Table (expandable rows)
├── FAQ: Billing-specific questions
│   • "What's the difference between Cloud and Self-Hosted?"
│   • "Can I migrate between Cloud and Self-Hosted?"
│   • "Do you offer annual billing?" → "Coming soon with 20% discount"
│   • "Is there a trial period?" → "Coming soon. Start with Free tier."
│
└── CTA: "Start Free" / "Download Community"
```

**Interactive Calculator:** Vanilla JS slider — user drags "editors" count, page highlights the recommended plan. **Why?** Reduces decision paralysis; lifts conversions ~25% based on 2026 SaaS benchmarks.

**Pricing — aligned with Phase 1 decisions:**
- Prices are **per-plan** ($29/mo, $79/mo), NOT per-workspace — per Phase 1 Decision 0.3
- **No annual toggle** — deferred to Phase 1.5 per Decision 0.16
- **No trial badge** — deferred to Phase 1.5 per Decision 0.16
- **50 published pages on Free** — raised from 10 (see Section 4.2)
- FAQ addresses annual/trial as "coming soon"

**Hugo implementation:**
- Template: `layouts/pricing/list.html`
- Content: `content/{lang}/pricing/_index.md`
- i18n strings in all 6 language files
- JSON-LD `Product` schema with `offers` array
- Deployment toggle + calculator: vanilla JS, same pattern as download OS tabs

**Effort: ~2 days** (1.5d layout + 0.5d calculator). **Note:** If calculator is cut (P1), pricing page drops to 1.5d and total Hugo work drops to 5.5d. The 6d Hugo total assumes calculator ships.

### 2.2 `/templates/` — Use Cases & Starter Templates

**Why needed:** Developers need to see concrete use cases. "What can I build with this?" is the #1 question after "What is this?"

**Renamed from "Examples"** — we don't have real customer deployments yet. "Templates" is honest and more useful (developers want to fork a template).

**Growth mechanic:** Each template links to a real GitHub template repo (e.g., `Valoryx-org/template-api-docs`). Users can `docplatform init --template api-docs` to bootstrap instantly. Every template usage is a new Valoryx install. See Section 15 (Growth Engine) for the full loop.

**Content structure:**
```
/templates/
├── Hero: "Documentation Templates"
│   "Start with a proven structure. Customize everything."
│
├── Filter tabs: All | API Docs | Knowledge Base | Team Wiki | Open Source
│
├── Template Cards Grid (3-col):
│   ├── API Documentation
│   │   bi-file-code icon + 15-30s demo GIF (autoplay, muted, loop)
│   │   "Ship API docs that live in your git repo"
│   │   Tags: [Git Sync] [Versioning] [Published Docs]
│   │   [Use Template] → links to template repo / `docplatform init --template api-docs`
│   │
│   ├── Engineering Knowledge Base
│   │   bi-building icon + demo GIF
│   │   "Internal docs your team actually maintains"
│   │   Tags: [Search] [RBAC] [Editor]
│   │   [Use Template]
│   │
│   ├── Open Source Project Docs
│   │   bi-globe icon + demo GIF
│   │   "Beautiful docs from your README"
│   │   Tags: [Git Sync] [Themes] [Published Docs]
│   │   [Use Template]
│   │
│   ├── Product Changelog
│   │   bi-clock-history icon
│   │   "Keep users informed with git-backed updates"
│   │   Tags: [Published Docs] [RSS]
│   │   [Use Template]
│   │
│   ├── AI-Maintained Documentation
│   │   bi-robot icon + demo GIF (showing MCP session)
│   │   "Let AI agents write and update your docs via MCP"
│   │   Tags: [MCP] [Automation]
│   │   [View Setup Guide] → links to /mcp/
│   │
│   └── Compliance Documentation
│       bi-shield-check icon
│       "SOC2/HIPAA docs with version history"
│       Tags: [Versioning] [RBAC] [Audit Logs]
│       [Use Template]
│
├── "How it works":
│   [1] Create workspace → [2] Write or import → [3] Publish
│
└── CTA: "Start building" → /pricing/
```

**Demo GIFs:** Short (15-30s) screen recordings. Host on Cloudflare as `<video autoplay loop muted playsinline>`. Create post-launch — use placeholder screenshots at launch.

**Card links:** Each "Use Template" links to a GitHub template repo. These are real, forkable repos. The dogfood instance (`docs.valoryx.org`) serves as the live proof point.

**Hugo implementation:**
- Template: `layouts/templates/list.html`
- Content: `content/{lang}/templates/_index.md` (card data in frontmatter)
- JSON-LD `HowTo` schema
- Filter tabs via vanilla JS (show/hide based on `data-category`)
- Bootstrap Icons only (no emoji)

**Effort: ~1.5 days** (1d layout + 0.5d demo videos/screenshots)

### 2.3 `/mcp/` — MCP Integration Page

**Why needed:** MCP is Valoryx's strongest differentiator. No competitor has one. This page is what AI tools will discover and recommend.

**Phase 1 scope:** stdio only. Cloud remote marked "Coming Soon."

**CRITICAL CONSTRAINT:** No HTTP URLs or examples for remote MCP until Phase 1.5. All MCP docs and `/mcp/` examples must use stdio only. Cloud remote shown as badge only.

**Content structure:**
```
/mcp/
├── Hero: "AI-Native Documentation"
│   "Connect your docs to Claude, Cursor, VS Code, and any MCP client."
│
├── What is MCP?
│   Brief explanation + link to modelcontextprotocol.io
│   Link to MCP Registry entry: registry.modelcontextprotocol.io
│
├── Two Modes:
│   ┌─────────────────────────┬──────────────────────────┐
│   │  LOCAL (stdio)          │  CLOUD (remote HTTP)     │
│   │  ✓ Available now        │  ⏳ Coming in Phase 1.5  │
│   │                         │                          │
│   │  For self-hosted +      │  For cloud users         │
│   │  cloud users (local)    │  No binary needed        │
│   │  Runs alongside binary  │  API key over HTTPS      │
│   │  Zero network overhead  │                          │
│   │  All plans              │  Team + Business plans   │
│   └─────────────────────────┴──────────────────────────┘
│
├── Quick Setup (tabbed: Claude Code / Claude Desktop / Cursor / VS Code):
│   [Terminal blocks with copy-to-clipboard, stdio config only]
│
├── 13 Tools (interactive table):
│   Content (6) | Discovery (4) | Quality (1) | Settings (2)
│
├── REAL AI SESSION TRANSCRIPT (high-impact — shows bidirectional sync):
│   ┌─────────────────────────────────────────────────────┐
│   │  User: "We just shipped OAuth support. Update the   │
│   │         authentication docs to include the new flow" │
│   │                                                     │
│   │  Claude: I'll update the authentication docs.       │
│   │  [calls docplatform_search: "authentication"]       │
│   │  Found: docs/auth/overview.md                       │
│   │  [calls docplatform_read_page: "auth/overview"]     │
│   │  Current content describes basic auth only.         │
│   │  [calls docplatform_update_page: "auth/overview"    │
│   │   with new OAuth 2.0 section added]                 │
│   │  ✓ Page updated. Content hash: a3f8c2...           │
│   │  ✓ Auto-committed to git: "Add OAuth 2.0 docs"     │
│   │  [calls docplatform_get_context: "auth/overview"]   │
│   │  Found 2 linked pages that reference auth.          │
│   │  [calls docplatform_update_page: "api-keys"]        │
│   │  ✓ Updated API keys page with OAuth token section   │
│   │  [calls docplatform_validate_links]                 │
│   │  ✓ No broken links across workspace.               │
│   │                                                     │
│   │  Done. Updated auth docs + 1 linked page.           │
│   │  Changes auto-synced to git. Published docs         │
│   │  updated within 30 seconds.                         │
│   └─────────────────────────────────────────────────────┘
│
├── Context Graph (unique differentiator):
│   "When your AI reads a page, it gets the full picture."
│   Visual showing get_context returning:
│   page + parent + children + siblings + linked pages + metadata
│
├── Security:
│   • API key authentication (scoped per workspace)
│   • Conflict detection prevents data loss (hash-based optimistic concurrency)
│   • All actions logged in audit trail
│   • Bidirectional git sync — every MCP write becomes a git commit
│
├── Demo GIF (high-impact):
│   Short (15-20s) animated recording of actual MCP interaction
│   (Claude Desktop or Cursor editing a page via MCP tools).
│   Host on Cloudflare as <video autoplay loop muted playsinline>.
│   Record in Phase 1 final week. Use placeholder screenshot at launch if needed.
│
├── Troubleshooting:
│   | Issue | Solution |
│   |-------|----------|
│   | "workspace not found" | Verify slug matches URL in app settings |
│   | "invalid API key" | Check key hasn't been rotated; regenerate in Settings → API Keys |
│   | "command not found: docplatform" | Verify binary is in PATH (`which docplatform`) |
│   | "tools not appearing in Claude" | Fully quit and reopen Claude Desktop (MCP servers load on startup) |
│   | "connection refused" | Ensure `docplatform serve` is running before starting MCP client |
│   | "permission denied" on write | API key may be read-only; check key scope in Settings |
│
└── CTA: "Get your API key" → app.valoryx.org/#/settings/api-keys
```

**Hugo implementation:**
- Template: `layouts/mcp/list.html`
- Content: `content/{lang}/mcp/_index.md`
- Terminal blocks with copy-to-clipboard
- JSON-LD `SoftwareApplication` schema (see AI-DISCOVERY-STRATEGY.md §7)

**Effort: ~1.5 days** (+ 0.5d for demo GIF recording in final week — can use placeholder at launch)

### 2.4 `/vs/gitbook/` — Competitor Comparison (P0 — One Page at Launch)

**Why needed:** "GitBook alternative" is a high-intent, high-volume search query.

**Launch strategy:** Ship `/vs/gitbook/` as P0 (closest competitor). Add `/vs/notion/`, `/vs/confluence/`, `/vs/wiki-js/` post-launch in weeks 2-4 as SEO ramp begins. One excellent comparison page outperforms four rushed ones.

**Honesty rule (mandatory):** Each page must contain at least 30-40% unique content and a "Where {Competitor} Wins" section. No pure marketing — builds trust.

**Template (shared across all /vs/ pages):**
```
/vs/{competitor}/
├── Hero: "Valoryx vs {Competitor}"
│   "A fair comparison for developer documentation"
│
├── TL;DR Summary (3 bullet points)
│
├── Side-by-side Feature Table
│   (reuse comparison table styling from homepage)
│
├── Where Valoryx Wins / Where {Competitor} Wins
│   (honest — builds trust)
│
├── Key Differentiator: MCP + Git Sync + Context Graph
│
├── Migration Guide (brief)
│
└── CTA: "Try Valoryx Free"
```

**Hugo implementation:**
- Template: `layouts/vs/single.html` (shared template, data-driven)
- Content: `content/{lang}/vs/{competitor}.md` (unique content per competitor per language)
- JSON-LD `Article` schema with comparison structured data
- Internal links from homepage comparison table

**Effort: ~0.5 day** (1 page at launch, template reusable for 3 more post-launch)

### 2.5 `/install/` — Quick Install Page

**Why needed:** Developers want a clear, dedicated install page. Currently quickstart is buried inside docs. This page ranks for "documentation platform install" and "git docs generator."

**Content structure:**
```
/install/
├── Hero: "Install Valoryx in 30 seconds"
│
├── Tabbed Install Methods:
│   ┌─────────────────────────────────────────────┐
│   │  [ Linux/macOS ]  [ Docker ]  [ Manual ]    │
│   └─────────────────────────────────────────────┘
│
│   Linux/macOS:
│     curl -fsSL https://valoryx.org/install.sh | sh
│
│   Docker:
│     docker run -p 8080:8080 valoryx/docplatform
│
│   Manual:
│     Download from GitHub Releases
│     → link to releases page
│
├── Quick Start:
│   docplatform init my-docs
│   docplatform serve
│   # → http://localhost:8080
│
├── Template Start:
│   docplatform init my-api-docs --template api-docs
│
└── CTA: "Or try Cloud — no install needed" → app.valoryx.org
```

**Hugo implementation:**
- Template: `layouts/install/list.html`
- Content: `content/{lang}/install/_index.md`
- Terminal blocks with copy-to-clipboard

**Effort: ~0.5 day**

### 2.6 `/open-source/` — Community Edition Page

**Why needed:** Valoryx has a free Community Edition. Without a dedicated page, people assume it's closed-source SaaS only. This page builds trust and drives self-hosted adoption.

**Content structure:**
```
/open-source/
├── Hero: "Free Documentation Platform"
│   "Self-host Valoryx with zero restrictions on core features."
│
├── What's Included:
│   • Full editor, git sync, search, publishing
│   • 3 workspaces, 5 editors, unlimited pages
│   • MCP server (stdio)
│   • No license key required
│
├── Download:
│   [Download Binary]  [Docker Image]  [GitHub]
│
├── License:
│   "Valoryx Community Edition is free for personal and
│    commercial use. Source-available under [license name]."
│   Link to LICENSE file
│
├── Contributing:
│   "Report issues, submit templates, build plugins."
│   Link to GitHub issues
│   Link to plugin SDK docs
│
└── CTA: "Need enterprise support?" → Contact
```

**Hugo implementation:**
- Template: `layouts/open-source/list.html`
- Content: `content/{lang}/open-source/_index.md`

**Effort: ~0.5 day**

### 2.7 `/security/` — Security Page

**Why needed:** Enterprise users and security-conscious developers expect a dedicated security page before adopting any SaaS product. Low effort, high trust signal.

**Content structure:**
```
/security/
├── Hero: "Security at Valoryx"
│
├── Data Protection:
│   • All data encrypted in transit (TLS 1.3)
│   • SQLite database on NVMe (encrypted at rest via disk encryption)
│   • Self-hosted: data never leaves your infrastructure
│   • Cloud: data stored on EU/US instance (configurable)
│
├── Authentication:
│   • Email + password (bcrypt)
│   • OAuth 2.0 / OIDC (Google, GitHub, GitLab)
│   • API keys: SHA-256 hashed with pepper
│   • Session management: HttpOnly, Secure, SameSite cookies
│
├── Infrastructure:
│   • Cloudflare WAF + DDoS protection
│   • HSTS with preload
│   • DNSSEC enabled
│   • Rate limiting per organization
│
├── MCP Server Security:
│   • API key scoped per workspace
│   • Conflict detection (hash-based optimistic concurrency)
│   • All mutations logged in audit trail
│   • Bidirectional git sync = full audit history
│
├── Vulnerability Disclosure:
│   "Report security issues to security@valoryx.org"
│   (Or link to GitHub Security Advisories)
│
└── Compliance (Phase 2):
    "SOC2 and GDPR compliance roadmap available on request."
```

**Hugo implementation:**
- Template: `layouts/security/list.html`
- Content: `content/{lang}/security/_index.md`

**Effort: ~0.5 day**

### 2.8 `/changelog/` — Release Notes

**Why needed:** Proves momentum. Table stakes for dev tools.

**Content structure:**
- Date-sorted list of releases
- Semantic versioning
- Categories: Added, Changed, Fixed, Removed
- Links to GitHub releases

**Hugo implementation:**
- Template: `layouts/changelog/list.html` + `single.html`
- Content: `content/{lang}/changelog/` with one `.md` per release
- RSS feed for subscribers

**Effort: ~0.5 day**

---

## 3. Cloud App SPA Fixes (app.valoryx.org)

**Important: Source vs Dist clarification.**

The SPA source lives at `internal/frontend/src/` (vanilla JS modules). The build step outputs to `internal/frontend/dist/`. All changes described below modify the **source files** and are applied via the standard build pipeline (`make frontend`). We do NOT patch `dist/` directly.

If no build pipeline exists yet (current state: dist/ is hand-authored), the first task is to establish one:
1. Move current `dist/assets/app.js` to `src/app.js`
2. Add a simple build script (`esbuild` or copy) that outputs to `dist/`
3. All subsequent edits happen in `src/`

**Contractor execution order (P0 items first, revenue-critical flows prioritized):**
1. Build pipeline (`src/` → `dist/`)
2. `/#/pricing` + `/#/settings/billing` (revenue path)
3. `/#/upgrade` + limit error banners (conversion path)
4. `/#/onboarding` wizard (activation path)
5. Landing page at `/` (SEO/trust)
6. OIDC callback fix (reliability)
7. P1 tasks (publish toggle, etc.)

### 3.1 FIX: No Landing Page for Cloud

**Problem:** Cloud users hitting `app.valoryx.org/` go straight to login. Hash routes are invisible to search engines.

**Solution: Real Go route (NOT a `<noscript>` trick — avoids cloaking risk)**

**Layer 1: Go handler renders a real landing page at `/`**

The Go SPA handler already serves `index.html` for all non-asset routes. Add a **dedicated Go handler for `/`** that renders a tiny, real HTML landing page (not the SPA shell):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Valoryx Cloud — Documentation that lives in git</title>
  <meta name="description" content="Write, publish, and manage docs with AI.">
  <!-- Standard SEO meta, OG tags -->
</head>
<body>
  <div class="landing">
    <h1>Valoryx Cloud</h1>
    <p>Documentation that lives in git. Write, publish, and manage docs with AI.</p>
    <a href="/#/register">Start Free</a>
    <a href="https://valoryx.org">Learn More</a>
  </div>
  <script>
    // If user is authenticated (cookie check), redirect to /#/workspaces
    if (document.cookie.includes('dp_session')) {
      window.location.hash = '#/workspaces';
    }
  </script>
</body>
</html>
```

This is a real page (not cloaking), visible to crawlers, consistent with what humans see.

**Layer 2: SPA `renderLanding()` route** (for `/#/` when JS is loaded)

```
┌─────────────────────────────────────────────────────────────┐
│  [V] Valoryx                              [Log in] [Sign up]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│       Documentation your AI can maintain.                   │
│                                                             │
│     Write in a beautiful editor. Sync with your repo.       │
│     Publish stunning docs. Connect AI via MCP.              │
│                                                             │
│     ┌──────────────┐   ┌──────────────┐                     │
│     │  Start Free  │   │  Learn More  │                     │
│     └──────────────┘   └──────────────┘                     │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Git     │  │ WYSIWYG │  │ Publish │  │ MCP     │       │
│  │ Sync    │  │ Editor  │  │ Docs    │  │ Ready   │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                             │
│          [Product screenshot or short demo GIF]             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Implementation:**
- `renderLanding()` checks `api.isAuthenticated()` — if true, redirect to `/#/workspaces`
- If not authenticated, render the landing
- "Learn More" links to `valoryx.org` (full marketing site)

**Effort: 1 day** (0.5d Go handler + 0.5d SPA route)

### 3.2 FIX: No Billing UI in SPA

**Problem:** Backend has full Stripe integration but frontend has no billing routes.

**Solution:** Add 3 new SPA routes.

#### Route: `/#/pricing`
- Shows Cloud plan cards (Free, Team, Business) — no Community (irrelevant in cloud app)
- Monthly only (no annual toggle — Phase 1.5)
- "Upgrade" buttons call `POST /api/v1/billing/checkout` → redirect to Stripe
- "Current Plan" indicator for logged-in users
- Stripe `success_url` → `https://app.valoryx.org/auth/stripe-callback?session_id={CHECKOUT_SESSION_ID}` (server-side redirect to `/#/settings/billing?success=1` — see §1.2.6)
- Stripe `cancel_url` → `https://app.valoryx.org/auth/stripe-cancel` (server-side redirect to `/#/pricing`)

#### Route: `/#/settings/billing`
- Current subscription status (plan, next billing date)
- "Manage Subscription" → `POST /api/v1/billing/portal` → Stripe Customer Portal
- Usage meters: Workspaces (2/3), Editors (8/15), Published Pages (34/∞)
- Plan upgrade CTA if on Free

#### Route: `/#/upgrade`
- Contextual upgrade prompt (shown when user hits a limit)
- "You've reached your workspace limit (1/1)"
- Side-by-side: Current plan vs recommended plan
- One-click upgrade button

**Backend changes:**
- `internal/api/handlers/billing.go` — update `successURL` to `/#/settings/billing?success=1`, `cancelURL` to `/#/pricing`

**Effort: 2.5 days** (1d pricing + 1d billing + 0.5d upgrade)

### 3.3 FIX: No Upgrade CTA When Hitting Limits

**Problem:** Limit errors show generic toast. No path to upgrade.

**Solution:** Structured error codes + contextual upgrade banners.

**Backend returns:**
```json
{
  "error": "workspace limit reached (1/1)",
  "code": "PLAN_LIMIT_WORKSPACE",
  "current_plan": "free",
  "suggested_plan": "team"
}
```

**`suggested_plan` logic** (in `internal/billing/license.go`): Free → Team for workspace/editor limits. Team → Business for analytics/SSO/audit features. ~20 lines.

**Error codes:**
- `PLAN_LIMIT_WORKSPACE` — workspace creation blocked
- `PLAN_LIMIT_EDITOR` — member invitation blocked
- `PLAN_LIMIT_PUBLISHED_PAGES` — page publish blocked
- `PLAN_RESTRICTED` — subscription overdue (>7 days grace)
- `FEATURE_NOT_AVAILABLE` — feature not in plan

**SPA behavior:** `ApiClient` detects `code: "PLAN_LIMIT_*"` errors and shows an upgrade banner:

```
┌─────────────────────────────────────────────────┐
│  Workspace limit reached (1/1)                  │
│                                                 │
│  Upgrade to Team for 3 workspaces, 15 editors,  │
│  custom domains, and more.                       │
│                                                 │
│  [Upgrade to Team — $29/mo]    [Maybe later]     │
└─────────────────────────────────────────────────┘
```

**Effort: 1 day** (0.5d backend + 0.5d frontend)

### 3.4 FIX: OIDC Callback Handler

**Problem:** `/#/auth/callback` needs verification for the full cookie-to-token exchange.

**Verification checklist:**
- [ ] Success: tokens received → redirect to workspaces
- [ ] Error: show error message with "Try again" link to `/#/login`
- [ ] Timeout: if claim takes >5s, show "Taking longer than expected..." with retry
- [ ] Cookie expiry: if cookies expired before claim, redirect to login with `?error=session_expired`
- [ ] Backend `OIDCClaimTokens` clears short-lived cookies after exchange

**Effort: 0.5 day** (audit + fix)

### 3.5 FIX: First-Run Onboarding Wizard

**Problem:** Backend has onboarding API but SPA only has a basic checklist. Cloud users need guided first-run.

**Solution:** 3-step wizard (reduced from 6 — shorter flow = higher completion rate).

```
Step 1: Create Workspace
  "Let's set up your first documentation workspace."
  Name: [My Team Docs]
  Slug: [my-team-docs] (auto-generated)
  [Create Workspace]

Step 2: Create First Page
  "Write your first page — or start from a template."
  [Blank Page] [Getting Started Template] [API Docs Template]
  → Pre-filled template option loads real content (not blank)
  → Opens editor

Step 3: Publish!
  "Your docs are ready to share."
  [Publish Now] → enables publishing, shows live URL
  [Skip — I'll publish later]
  → Dashboard with post-setup checklist:
    • Connect Git repository
    • Invite teammates
    • Set up MCP for AI → links to docs/guides/mcp.md
```

**Why 3 steps, not 6:** Publishing creates the "wow moment" — seeing docs live. Git and team invite are high-friction steps that cause drop-off. They become optional checklist items.

**Pre-filled templates (Step 2):** "Blank Page Syndrome" kills activation. Clicking "Getting Started Template" loads a real, pre-populated page. Users see a beautiful published page within 15 seconds of signup.

**Implementation:**
- New SPA route: `/#/onboarding`
- Redirect here after first registration
- Progress saved via `PATCH /api/v1/users/me/onboarding`
- Dismissible at any step
- Dashboard shows remaining checklist items post-onboarding

**Effort: 1.5 days**

---

## 4. UX Concern Resolutions

### 4.1 Free vs Community Confusion

**Root cause:** Both are "free" but with different limits and deployment models.

**Solution (multi-pronged):**
1. **Deployment toggle on pricing page** (Section 2.1) — never shows both side-by-side
2. **In-app pricing** (`/#/pricing`) shows only Cloud plans
3. **Homepage pricing section** keeps 3 Cloud cards only; Community mentioned as "Self-host? [Download free →]"
4. **FAQ additions** on pricing page and homepage
5. **`/vs/` pages** explain the distinction naturally

### 4.2 Published Page Limit: 10 → 50 on Free Tier

**Problem:** 10 is too restrictive. Users hit the wall before evaluating.

**Solution:** Raise to 50. The real upsell is workspaces (1 → 3) and editors (3 → 15), not page count.

**Implementation:**
- Update `internal/db/migrations/003_billing_plans.sql` — `max_published_pages: 50`
- Update `PHASE-1-PLAN.md` plan matrix to match (single source of truth)
- **Note:** ARCHITECTURE-V3.md plans table currently shows 10. This plan overrides to 50. Update the architecture doc to match.
- **After migration:** regenerate plans-matrix artifacts and re-run pricing tests

### 4.3 No SMTP = Silent Password Reset

**Problem:** Community installs without SMTP log reset token to stdout. UI says "email sent" — misleading.

**Solution (two-layer):**
1. Add `email_configured: bool` to `GET /api/health` response
2. SPA `renderForgotPassword()` checks on load:
   - `true` → standard reset form
   - `false` → "Password reset requires email. Contact your administrator." + link to docs
3. **Manual reset in logs:** When `email_configured=false`, log a clickable "Manual Reset Link" to stdout/stderr alongside the token.

**Effort: 0.5 day**

### 4.4 HIDE_STORAGE_PATHS Default for Cloud

**Problem:** Defaults to `false`. Cloud should never expose server paths.

**Solution:** Auto-true when billing is enabled.

```go
func (c *Config) HideStoragePaths() bool {
    if c.HideStoragePathsOverride != nil {
        return *c.HideStoragePathsOverride
    }
    return c.BillingEnabled() // true for cloud, false for community
}
```

**Effort: 0.25 day**

### 4.5 Published Docs Auth (PUBLISH_REQUIRE_AUTH)

**Problem:** Default `false` = all published pages public. Cloud users may want private docs. Flag exists but no UI.

**Solution:** Add toggle to workspace settings.

```
Published Documentation
├── Enabled: [✓] (existing)
├── Slug: [my-docs] (existing)
├── Theme: [Default ▾] (existing)
└── Access: [● Public] [○ Require Login]  ← NEW
```

**When toggling Public → Require Login:** Show confirmation modal.
**When unauthenticated user hits a now-private page:** Show "This documentation requires authentication. [Log in to view]" (not a generic 404).

**Effort: 0.5 day**

---

## 5. Distribution & Traffic Plan

**No plan drives 50 signups/week without distribution.** New pages need traffic.

### 5.1 Launch Day (Day 0)

| Channel | Action | Owner |
|---------|--------|-------|
| Hacker News | "Show HN: Valoryx — Git-native docs with an MCP server for AI agents" (weekday 9-11am ET) | Founder |
| Reddit | r/selfhosted (self-hosted angle), r/devops (infra angle), r/webdev (docs angle), r/LocalLLaMA (MCP angle) | Founder |
| Dev.to | Cross-post launch blog. Tags: `documentation`, `ai`, `opensource`, `devtools` | Founder |
| Twitter/X | Thread structure: (1) problem (docs rot), (2) solution (AI maintains), (3) demo GIF, (4) link + "free forever self-hosted" | Founder |
| MCP Registry | Submit to registry.modelcontextprotocol.io | Dev |
| Product Hunt | Optional: schedule launch. Category: Developer Tools | Founder |
| GitHub | Create "Show & Tell" discussion in docplatform repo | Dev |

### 5.2 Week 1-4 (Organic SEO Ramp)

| Action | Timeline |
|--------|----------|
| `/vs/gitbook/` indexed by Google | Week 1-2 |
| Add `/vs/notion/`, `/vs/confluence/`, `/vs/wiki-js/` | Weeks 2-4 (one per week) |
| Blog: "Community vs Cloud: Which Valoryx?" | Week 1 |
| Blog: "How We Use MCP to Maintain Our Own Docs" | Week 2 |
| Submit sitemap to Google Search Console | Day 1 |
| Submit sitemap to Bing Webmaster Tools | Day 1 |
| Monitor ranking for "GitBook alternative" etc. | Weekly |

### 5.3 Analytics Events to Track

Track these events from Day 1:

| Event | Trigger |
|-------|---------|
| `pricing_viewed` | User visits /pricing/ or /#/pricing |
| `plan_selected` | User clicks plan CTA |
| `signup_started` | User submits register form |
| `signup_completed` | Registration succeeds |
| `workspace_created` | First workspace created |
| `first_page_created` | First page created |
| `first_publish` | First page published |
| `mcp_enabled` | API key created |
| `upgrade_clicked` | User clicks upgrade CTA |
| `upgrade_completed` | Stripe checkout succeeds |
| `onboarding_step1_completed` | Workspace created in wizard |
| `onboarding_step2_completed` | First page created in wizard |
| `onboarding_completed` | All 3 wizard steps done (publish) |
| `onboarding_abandoned` | User dismisses wizard before completion (track which step) |
| `template_card_clicked` | User clicks a template on /templates/ |
| `mcp_demo_clicked` | User clicks MCP setup tab on /mcp/ |
| `vs_page_viewed` | User views a /vs/ competitor page |

**SPA event endpoint:** Add `POST /api/v1/analytics/event` for SPA funnel events (0.25d backend). The existing `internal/analytics/collector.go` handles published docs pageviews — extend it with a generic event endpoint. GDPR-compliant (no PII, no cookies — just event name + timestamp + anonymous session ID).

**P0 events at launch (minimum viable analytics):** `pricing_viewed`, `signup_started`, `signup_completed`, `workspace_created`, `first_publish`, `upgrade_clicked`, `upgrade_completed`, `onboarding_completed`. All other events are P1 — do not over-engineer analytics on day one.

### 5.4 AI Discovery Flywheel — The Deep Analysis

This is Valoryx's most important long-term growth mechanism. Most documentation platforms serve **zero** AI discovery channels. Valoryx serves all five.

#### 5.4.1 How AI Systems Actually Discover Tools

AI assistants discover tools through five channels:

```
┌─────────────────────────────────────────────────────────────┐
│                    AI DISCOVERY CHANNELS                      │
├──────────────────────┬──────────────────────────────────────┤
│                      │                                      │
│  1. TRAINING DATA    │  Web crawl → embedding → weights     │
│     (passive)        │  Asset: valoryx.org/* content        │
│                      │  Signal: domain authority, volume     │
│                      │                                      │
│  2. RUNTIME DISCOVERY│  MCP protocol → tool schema          │
│     (active)         │  Asset: mcp.valoryx.org (Phase 1.5)  │
│                      │  Signal: tool quality, reliability    │
│                      │                                      │
│  3. STRUCTURED META  │  llms.txt, JSON-LD → direct indexing │
│     (declarative)    │  Asset: valoryx.org/llms.txt         │
│                      │  Signal: structured capability desc   │
│                      │                                      │
│  4. REGISTRY PRESENCE│  MCP registries → agent discovery    │
│     (marketplace)    │  Asset: registry.modelcontextprotocol │
│                      │  Signal: official listing, trust      │
│                      │                                      │
│  5. CONTENT VOLUME   │  Customer docs → training data       │
│     (network effect) │  Asset: published workspaces         │
│                      │  Signal: "Valoryx = documentation"   │
│                      │                                      │
└──────────────────────┴──────────────────────────────────────┘
```

#### 5.4.2 Why Domain Consolidation Matters for AI Knowledge Graphs

LLMs internally build concept graphs during training:

```
CONSOLIDATED (.org only):          SPLIT (.org + .dev):

  Valoryx                           Valoryx-org
   ├── docs                          ├── docs
   ├── MCP server                    └── pricing
   ├── API
   ├── pricing                      Valoryx-dev
   └── templates                     ├── cloud app
                                     └── MCP server
  ONE strong node                   TWO weak nodes
```

When everything lives under `valoryx.org`, every crawled page reinforces one concept: "Valoryx = AI-native documentation platform." Split domains create two weaker associations that compete with each other.

**This affects:**
- Recommendation likelihood ("What documentation tool has MCP?")
- Retrieval accuracy (RAG pulling correct context)
- Knowledge embedding confidence (weight in training data)

#### 5.4.3 The Flywheel

```
Developer adopts Valoryx
        │
        ▼
Docs hosted → pages crawled by AI training pipelines
        │
        ▼
llms.txt + JSON-LD → LLMs learn "Valoryx = AI docs platform"
        │
        ▼
MCP registry → AI agents discover tools at runtime
        │
        ▼
AI assistants recommend Valoryx when asked about docs
        │
        ▼
More developers adopt → more docs hosted → stronger signal
```

**Each layer reinforces the others:**

| Layer | Signal | Reinforces |
|-------|--------|------------|
| Web crawl of `valoryx.org` | Brand in training data | Recommendation likelihood |
| `llms.txt` at domain root | Structured capabilities | Agent tool selection |
| MCP registry entry | Runtime tool discovery | Active usage by agents |
| JSON-LD on `/mcp/` page | Schema.org data | Search + AI indexing |
| Customer docs on platform | Associated content volume | Domain authority |

**Critical insight:** Customer docs hosted on Valoryx create content that AI crawlers associate with the platform. Every workspace published through Valoryx strengthens the signal. This is a network effect no competitor has.

#### 5.4.4 How AI Assistants Will Use Valoryx

Realistic scenario — a developer in Cursor IDE says: "Update our deployment documentation."

The assistant:
1. Checks available MCP servers → discovers Valoryx
2. Loads tool schema (13 tools, structured input/output)
3. Calls `docplatform_search` → finds relevant page
4. Calls `docplatform_read_page` → gets current content
5. Calls `docplatform_update_page` → writes new content
6. Calls `docplatform_get_context` → finds linked pages
7. Updates related pages → validates links

The AI treats Valoryx as **documentation infrastructure** — not just a UI tool.

Other documentation platforms (GitBook, Notion, Confluence) cannot do this because they lack:
- MCP server (no tool interface)
- Git-native storage (no bidirectional sync)
- Context Graph API (no relationship understanding)
- Structured content API (no agent-level operations)

#### 5.4.5 The AI Recommendation Loop

Once AI assistants learn about Valoryx through training data + runtime discovery + registry, they begin recommending it. This creates free distribution:

```
User asks: "What's the best documentation platform for AI integration?"

AI responds: "Valoryx has a built-in MCP server with 13 tools for
documentation management. It supports bidirectional git sync and has
a Context Graph API that lets AI agents understand documentation
relationships. You can connect it to Claude, Cursor, or VS Code."
```

This recommendation is based on:
- Training data from `valoryx.org/*` (domain authority)
- `llms.txt` structured description
- MCP registry metadata
- JSON-LD structured data

**No competitor has all five signals.** This is the moat.

### 5.5 AI Discovery — Launch Day Tasks

| Task | Effort | Priority |
|------|--------|----------|
| Deploy `llms.txt` to `valoryx.org/llms.txt` | 0.5h | P0 |
| Deploy `llms-full.txt` (tool schemas + examples) | 2h | P0 |
| Submit MCP registry entry (stdio, 13 tools) | 1h | P0 |
| JSON-LD `SoftwareApplication` on `/mcp/` | 1h | P0 |
| Homepage MCP feature card | 0.5h | P0 |
| Comparison table MCP row | 0.5h | P0 |

### 5.6 AI Discovery Metrics

| Metric | Source | Target (Month 1) | Target (Month 3) |
|--------|--------|-------------------|-------------------|
| MCP tool calls/day | Server logs | 10+ | 100+ |
| `llms.txt` fetches | Cloudflare analytics | Track AI crawler hits | Baseline |
| MCP registry page views | modelcontextprotocol.io | Track impressions | — |
| "Valoryx" mentions in AI | Manual testing (Claude/GPT) | Appears in tool recs | Consistent |
| Workspaces using MCP | Internal analytics | 30 | 100+ |

**Validation methods (how to actually check these):**

| Metric | Validation Method |
|--------|-------------------|
| `llms.txt` fetches | Cloudflare Analytics → filter by user-agent: `GPTBot`, `ClaudeBot`, `anthropic-ai`, `Google-Extended` |
| MCP registry presence | Manual check: visit `registry.modelcontextprotocol.io` and search for "Valoryx" weekly |
| AI recommendation test | Query Claude/Cursor/GPT: "What documentation platform has MCP?" — target: appears in top 3 by Month 2 |
| Customer docs crawl volume | Count published workspaces with `robots.txt` allowing crawlers — target: 50+ by Month 3 |

---

## 6. Updated Navigation

### 6.1 Desktop Nav (reduced from 7 → 5 items)

```
[V] Valoryx    Pricing  Templates  Docs  Blog  [lang ▾]  [Download Free]
```

**Removed:** About, Features, MCP (all reachable from homepage scroll or docs). Keeps nav clean across 6 languages.

### 6.2 Mobile Nav

```
Home
Pricing
Templates
Docs
Blog
─────────
Language ▾
```

### 6.3 Footer Links

```
Column 1: Product          Column 2: Resources        Column 3: Documentation    Column 4: Company
─────────                  ─────────                  ─────────                  ─────────
Pricing                    Blog                       Getting Started            About
Templates                  Changelog                  Installation               Contact
MCP Integration            GitHub                     Git Sync                   Security
Install                    MCP Registry               CLI Reference              Open Source
Cloud App                  llms.txt                   API Reference
vs GitBook
```

---

## 7. Homepage Updates

### 7.1 Hero Messaging Update

**Current:** "Documentation that lives in git."

**Proposed (stronger AI-native positioning):**
> "Documentation your team writes. Documentation your AI maintains."

Subtitle: "Git-native docs platform with a built-in MCP server. Write, publish, and let AI agents keep your docs accurate."

**AI Discovery badge** (small, next to subtitle): "AI agents can read, write & maintain your docs" — one-line HTML + Tailwind in hero partial. Zero cost, high memorability. Reinforces unique positioning instantly.

This positions Valoryx uniquely — no competitor claims this.

### 7.2 Homepage Section Order

```
1. Hero (updated messaging)
2. Product Screenshot / Demo GIF  ← MOVED UP (builds trust early)
3. Download / Get Started
4. Stats (add "13 MCP Tools" stat)
5. Features (add MCP as 7th card)
6. CTA
7. Comparison (add "MCP Server" + "Context Graph API" rows)
8. Pricing (3 Cloud cards, "Self-host? Download free →" link)
9. FAQ (add MCP + billing questions)
10. Contact
```

**Removed:** Domains section (redundant with pricing page deployment toggle).

### 7.3 Comparison Table Update

Add rows:

| Feature | Valoryx | Notion | GitBook | Confluence | Wiki.js |
|---------|---------|--------|---------|------------|---------|
| MCP Server (AI agents) | ✓ (13 tools) | ✗ | ✗ | ✗ | ✗ |
| Context Graph API | ✓ | ✗ | ✗ | ✗ | ✗ |
| Autonomous Doc Maintenance | ✓ (Phase 2) | ✗ | ✗ | ✗ | ✗ |

---

## 8. Dogfooding: docs.valoryx.org

**Architecture:** Deploy `docs.valoryx.org` on the same VPS as `app.valoryx.org` (same binary, different workspace). If the VPS is down, both are down — but `valoryx.org/docs/` (Hugo on Cloudflare) still works as the canonical docs path.

**At launch (Phase 1):** No static fallback infrastructure. Traffic is near-zero. Risk is low.

**Phase 1.5 (when traffic justifies it):** Add static fallback:
1. Cron job: `docplatform export --workspace docs --output /var/static-docs/` every 6 hours
2. Static HTML deployed to Cloudflare Pages as fallback
3. DNS health-check failover

**Canonical rule:** `valoryx.org/docs/` (Hugo, synced from docplatform-docs repo) remains the canonical SEO path at all times.

---

## 9. Implementation Roadmap (Merged into Phase 1)

### Frontend Budget Reconciliation

The Phase 1 Plan Section 5 allocates 15 contractor days. This plan's SPA tasks **overlap with** (not add to) that budget:

| This Plan's Task | Replaces Phase 1 Section 5 Item | Net New? |
|------------------|---------------------------------|----------|
| `/#/pricing` (1d) | Billing UI (2d) | **Overlap** — same work |
| `/#/settings/billing` (1d) | Billing UI (2d) | **Overlap** — same work |
| `/#/upgrade` + banners (1d) | Limits UI (1d) | **Overlap** — same work |
| `/#/onboarding` wizard (1.5d) | Onboarding (1d) | **Overlap** — expanded (+0.5d) |
| Landing page (1d) | — | **New** (+1d) |
| OIDC callback fix (0.5d) | — | **New** (+0.5d) |
| Build pipeline setup | — | **Prerequisite** (0.5d) |

**Net impact:** ~2d net new SPA work beyond Phase 1 baseline. Total SPA: ~15d. Fits within budget.

### Phase 1, Weeks 31-32: Hugo Marketing Pages (~6 days)

| Task | Effort | Priority |
|------|--------|----------|
| `/pricing/` page with deployment toggle + calculator | 2d | P0 |
| `/templates/` page with filter tabs + placeholder screenshots | 1.5d | P0 |
| `/mcp/` page with AI session transcript + registry link | 1.5d | P0 |
| `/vs/gitbook/` competitor page | 0.5d | P0 |
| `/install/` quick install page | 0.5d | P0 |
| `/security/` security page | 0.5d | P1 |
| `/open-source/` community edition page | 0.5d | P1 |
| `/changelog/` page | 0.5d | P1 |
| Update header nav (5 items) | — | included |
| Update footer links | — | included |
| Add `llms.txt` + `llms-full.txt` + `<meta name="llms-full">` | — | included |
| Homepage updates (messaging, comparison, pricing, MCP card) | — | included |
| JSON-LD schemas (`/mcp/`, `/pricing/`) | — | included |
| i18n strings for new pages (English, hooks for other langs) | — | included |

### Phase 1, Weeks 32-34: Cloud App SPA (~7 days)

*Merged with Phase 1 Section 5 frontend contractor backlog (not duplicated).*

| Task | Effort | Priority |
|------|--------|----------|
| Establish `src/` → `dist/` build pipeline | 0.5d | prerequisite |
| `/#/pricing` route | 1d | P0 |
| `/#/settings/billing` route | 1d | P0 |
| `/#/upgrade` route + limit error banners | 1d | P0 |
| `/#/onboarding` wizard (3 steps + pre-filled templates) | 1.5d | P0 |
| Go-rendered landing page at `/` + SPA `renderLanding()` | 1d | P0 |
| OIDC callback audit + fix | 0.5d | P0 |
| PUBLISH_REQUIRE_AUTH toggle in settings | 0.5d | P1 |

**Budget check:** 7d SPA (this plan) + 8d existing Phase 1 frontend = 15d total. Fits within contractor budget. Admin panel frontend (3d across S2.8/S3.7/S4.8) is done by the main developer during each sprint's capstone — NOT counted against the 15d contractor budget.

### Phase 1, Weeks 33-34: Backend (~2.5 days)

| Task | Effort | Priority |
|------|--------|----------|
| Structured billing error codes + `suggested_plan` logic | 0.75d | P0 |
| Update Stripe success/cancel URLs | 0.25d | P0 |
| Raise Free tier: 10 → 50 pages (migration) | 0.25d | P0 |
| Add `POST /api/v1/analytics/event` for SPA funnel events | 0.25d | P0 |
| `email_configured` in health endpoint + manual reset in logs | 0.25d | P1 |
| `HIDE_STORAGE_PATHS` cloud default | 0.25d | P1 |
| PUBLISH_REQUIRE_AUTH confirmation flow | 0.25d | P1 |
| Deploy `llms.txt` + `llms-full.txt` | 0.25d | P0 |

### Phase 1, Week 34: Distribution + AI Discovery

| Task | Priority |
|------|----------|
| Submit sitemap to Google/Bing | P0 |
| Submit MCP registry entry (stdio, 13 tools) | P0 |
| Prepare HN/Reddit/Dev.to posts | P0 |
| Verify `llms.txt` accessible + not blocked by robots.txt | P0 |
| Verify JSON-LD structured data (Google Rich Results Test) | P0 |
| Deploy `valoryx.dev` → `valoryx.org` 301 redirect | P0 |

### Phase 1, Week 35: Launch + Polish (~2 days)

| Task | Priority |
|------|----------|
| Cross-browser testing | P0 |
| Mobile responsive testing | P0 |
| Lighthouse audit (target 90+) | P0 |
| SEO audit: sitemaps, hreflang, canonicals | P0 |
| E2E acceptance tests (see Section 10) | P0 |
| Flip DNS, enable `FF_BILLING=true` | P0 |
| Launch posts (HN, Reddit, Dev.to, X) | P0 |

**Total effort: ~19.5 days** (7.5d Hugo + 7d SPA + 2.5d backend + 2.5d polish/launch/distribution). The 1.5d increase vs v4 is from /install/ (P0, 0.5d) + /security/ (P1, 0.5d) + /open-source/ (P1, 0.5d). If schedule pressure, /security/ and /open-source/ defer to Week 36.

### P0 / P1 / P2 Cut Line

If schedule pressure rises, cut in this order:

| Priority | What ships | What defers |
|----------|-----------|-------------|
| **P0 (must ship)** | /pricing, /mcp, /templates (no GIFs), /install, /#/pricing, /#/billing, /#/upgrade, /#/onboarding, landing page, OIDC fix, Stripe server-side callback, billing errors, llms.txt, MCP registry, /vs/gitbook | — |
| **P1 (ship if time)** | /changelog, /security, /open-source, calculator on pricing, demo GIF on /mcp/, demo GIFs on templates, PUBLISH_REQUIRE_AUTH, non-P0 analytics events, SMTP/HIDE_STORAGE fixes | → Week 36 |
| **P2 (post-launch)** | /vs/notion, /vs/confluence, /vs/wiki-js, demo videos, i18n for new pages, docs.valoryx.org static fallback, shared cookie intelligence, demo.valoryx.org | → Phase 1.5 |

---

## 10. Go/No-Go Checklist (Before Launch)

### Constraint Alignment
- [ ] **Pricing alignment:** Phase 1 plan matrix and all surfaces show same numbers ($29/mo, $79/mo per-plan)
- [ ] **No annual billing:** All pricing pages show monthly only. FAQ says "coming soon"
- [ ] **No trial badges:** No "14-day free trial" on any surface. FAQ says "coming soon"
- [ ] **No remote MCP:** `/mcp/` page shows stdio only. Cloud remote has "Coming Soon" badge
- [ ] **Frontend budget:** Total SPA days ≤ 15 (verified against Phase 1 Section 5)
- [ ] **English first:** New Hugo pages have English content. Non-English may fall back to English for new sections
- [ ] **SPA build pipeline:** All changes are in `src/`, build outputs to `dist/`
- [ ] **Stripe URLs:** `success_url` and `cancel_url` point to existing SPA hash routes on `app.valoryx.org`
- [ ] **Domain consolidation:** All surfaces use `app.valoryx.org` (not `.dev`). `valoryx.dev` 301 redirect is live

### AI Discovery
- [ ] **llms.txt:** Accessible at `valoryx.org/llms.txt`, not blocked by robots.txt
- [ ] **llms-full.txt:** Contains tool schemas, no internal/private content
- [ ] **MCP registry:** Submitted to `registry.modelcontextprotocol.io`
- [ ] **JSON-LD:** Verified with Google Rich Results Test on `/mcp/` and `/pricing/`
- [ ] **Analytics events:** Core funnel events firing via `POST /api/v1/analytics/event`

### Infrastructure
- [ ] **DNS verified:** All subdomains resolve correctly (app, docs, www → correct targets)
- [ ] **TLS verified:** All subdomains serve valid certificates
- [ ] **HSTS enabled:** Strict-Transport-Security header present
- [ ] **Cloudflare WAF:** Managed ruleset enabled on all proxied domains
- [ ] **Backup running:** SQLite backup every 6 hours to `.docplatform/backups/` AND streaming to offsite (R2/S3). Verify last backup is <8 hours old
- [ ] **Canonical tags:** All `docs.valoryx.org` pages have `<link rel="canonical">` pointing to `valoryx.org/docs/*`

### Acceptance Tests (E2E)
- [ ] **Signup → Onboarding → Publish:** Register → 3-step wizard → first page published → live URL works
- [ ] **Limit → Upgrade → Billing:** Hit workspace limit → upgrade banner shown → click → Stripe checkout → success route → billing page shows new plan
- [ ] **OIDC flow:** Google login → callback → tokens → workspaces (+ failure cases)
- [ ] **Pricing values match enforcement:** Free tier shows 50 pages, backend enforces 50 pages
- [ ] **MCP stdio works:** `docplatform mcp --workspace test --api-key dp_live_...` → all 13 tools respond

### 10.1 Rollback Procedure (If Launch Fails)

| Failure Scenario | Rollback Action | Recovery Time |
|------------------|-----------------|---------------|
| **Stripe webhook failures** | Set `FF_BILLING=false` in env, restart binary. Users see Free plan only. | <5 min |
| **MCP server crashes** | Set `FF_MCP=false` (or remove `mcp` subcommand from PATH). MCP docs stay up but tool is offline. | <5 min |
| **Published docs 500s** | Set `FF_PUBLISH=false`. Published sites show maintenance page. Editor still works. | <5 min |
| **Database corruption** | Stop binary. Restore from last backup: `cp .docplatform/backups/latest/data.db .docplatform/data.db`. Restart. | <15 min |
| **Caddy/proxy crash** | `systemctl restart caddy`. If persistent, bypass Caddy and point Cloudflare directly to `:8080`. | <5 min |
| **Complete instance failure** | Marketing site (`valoryx.org` on Cloudflare Pages) stays up. Provision new instance, restore from backup + git repos. | <2 hours |

**Feature flags referenced above:** These are environment variables checked at startup. No code deployment needed for rollback — just env change + restart.

---

## 11. Success Metrics

| Metric | Target (Month 1) | Target (Month 3) | How to Measure |
|--------|-------------------|-------------------|----------------|
| Cloud signups/week | 20 (launch spike) → 10 | 30+ (organic) | Registration events |
| Free → Team conversion | 2% | 5% | Billing events |
| Pricing page bounce rate | <50% | <40% | Cloudflare Analytics |
| MCP installs (API keys) | 30 | 100+ | API key creation events |
| SEO: organic traffic | Baseline | +30% | Cloudflare Analytics |
| Onboarding completion | >60% | >75% | Onboarding API |
| Upgrade CTA click-through | >5% of limit-hit users | >10% | Frontend events |
| `/vs/` pages impressions | Indexed | Top 20 for "X alternative" | Search Console |
| MCP tool calls/day | 10+ | 100+ | Server logs |
| `llms.txt` fetches | Track baseline | Identify AI crawlers | Cloudflare Analytics |
| Workspaces using MCP | 20% of active | 30% of active | API key / workspace ratio |

---

## 12. MCP Documentation & Site Placement (Shipping Feature)

The MCP server is **already built and working** (13 tools, stdio transport, API key auth). It ships with the DocPlatform binary. This section specifies every place MCP must be surfaced.

### 12.1 Current State

```
internal/mcp/
├── server.go       — MCPServer struct + ServeStdio()
├── tools.go        — 13 tool definitions + handlers
├── auth.go         — API key authentication (pepper-hashed)
└── tools_test.go   — 13 test cases
```

**Command:** `docplatform mcp --workspace <slug> --api-key <key>`
**Transport:** stdio (stdin/stdout JSON-RPC 2.0)
**Auth:** API key via `--api-key` flag or `DOCPLATFORM_API_KEY` env var
**Library:** mark3labs/mcp-go v0.45.0 (confirmed from latest Dependabot PR #15, merged 2026-03-08)

**ARCHITECTURE-V3 alignment note:** Section 19 specifies 19 Phase 1 tools + 4 Phase 2 tools = 23 total. The current binary ships 13. The gap (6 tools: get_manifest, get_graph, list_presets, apply_preset, get_workspace_stats, rebuild_search) ships in Phase 1 during remaining development sprints. MCP-CREATION-PLAN adds 7 more in Phase 1.5 for the HTTP transport = 20 on remote. Phase 2 adds remaining 3 (submit_for_review, approve_page, audit_query).

### 12.2 What's Missing: Zero Documentation

The current docs (22 pages) have **no mention of MCP anywhere**:
- CLI reference lists 5 commands — `mcp` is missing
- API reference has no API keys section
- No guide for MCP setup with Claude/Cursor/VS Code
- Homepage doesn't mention MCP

### 12.3 Documentation Pages to Create/Update

#### NEW: `docs/guides/mcp.md` — MCP Setup Guide

**Path:** `content/{lang}/docs/guides/mcp.md`
**Weight:** 6 (after search.md)

Content: Full setup instructions for Claude Code, Claude Desktop, Cursor, VS Code. All 13 tools documented with descriptions. Context Graph API explained. Conflict detection. Security model. Troubleshooting section with common issues:

| Issue | Solution |
|-------|----------|
| "workspace not found" | Verify slug matches URL in app settings |
| "invalid API key" | Check key hasn't been rotated; regenerate in Settings → API Keys |
| "command not found: docplatform" | Verify binary is in PATH (`which docplatform`) |
| "tools not appearing in Claude" | Fully quit and reopen Claude Desktop (MCP servers load on startup) |
| "connection refused" | Ensure `docplatform serve` is running before starting MCP client |
| "conflict detected" | Another user edited the page. Re-read with `read_page`, merge changes, retry |

(See v3 plan for full content — unchanged.)

#### UPDATE: `docs/reference/cli.md` — Add `mcp` Command

Add `docplatform mcp` section with flags, behavior, environment variables, examples.

#### UPDATE: `docs/reference/api.md` — Add API Keys Section

Add CRUD endpoints for API keys: create, list, rotate, delete.

#### UPDATE: `docs/_index.md` — Add MCP to Overview

Add MCP feature block + comparison table rows.

### 12.4 Where MCP Appears on Marketing Site (valoryx.org)

| Location | What to Add | Priority |
|----------|-------------|----------|
| **`/mcp/` page** (Section 2.3) | Full marketing page | P0 |
| **Homepage hero** | Updated messaging: "Documentation your AI can maintain" | P0 |
| **Homepage `#features`** | 7th card: "MCP Server" | P0 |
| **Homepage `#comparison`** | New rows: "MCP Server" + "Context Graph API" | P0 |
| **Homepage `#stats`** | 5th stat: "13 MCP Tools" | P1 |
| **`/pricing/` page** | "MCP Server (stdio)" on all plans | P0 |
| **`/templates/` page** | "AI-Maintained Documentation" card | P1 |
| **Footer** | "MCP Integration" + "MCP Registry" links | P0 |
| **`llms.txt`** | MCP section with tool names | P0 |
| **`/vs/` pages** | MCP as Valoryx-only differentiator | P1 |

### 12.5 Where MCP Appears in Cloud App (app.valoryx.org)

| Location | What to Add | Priority |
|----------|-------------|----------|
| **Settings → API Keys** | Frontend page for key management | P0 |
| **Onboarding checklist** | "Set up MCP for AI" checklist item | P1 |
| **Workspace settings** | "MCP" section showing slug + docs link | P2 |

### 12.6 MCP Documentation Effort

| Task | Effort |
|------|--------|
| Write `docs/guides/mcp.md` (~350 lines) | 0.5d |
| Update `docs/reference/cli.md` | 0.25d |
| Update `docs/reference/api.md` (API keys) | 0.25d |
| Update `docs/_index.md` (overview + comparison) | 0.25d |
| Translate to 5 other languages | 1d (defer to Phase 1.5) |
| **Total** | **1.25d** (English only) |

Total MCP-related site work (docs + `/mcp/` page): **2.75 days**.

---

## 13. What's Explicitly Deferred to Phase 1.5

| Feature | Why Deferred | When |
|---------|-------------|------|
| Annual billing + 20% discount | Decision 0.16 | Within 30 days post-launch |
| Trial periods (14-day) | Decision 0.16 | Same |
| Remote MCP server (`mcp.valoryx.org`) | Stdio ships at launch. HTTP adds cloud access. See MCP-CREATION-PLAN.md | ~4 weeks post-launch |
| Interactive pricing calculator | P1 — ships if time | Week 31-32 or Phase 1.5 |
| Demo videos/GIFs on templates | Need product live first | Phase 1.5 |
| `/vs/notion/`, `/vs/confluence/`, `/vs/wiki-js/` | One per week post-launch | Weeks 36-38 |
| Shared cookie intelligence | `.valoryx.org` session cookie for "Go to Dashboard" | Phase 1.5 |
| docs.valoryx.org static fallback | Traffic doesn't justify complexity | Phase 1.5 |
| i18n for new marketing pages | English first, translate by traffic data | Phase 1.5 |
| AI automation add-on pricing | Need MCP usage data | Phase 2 |
| `demo.valoryx.org` (no-signup demo) | Requires product stability + demo workspace | Phase 2 |
| `status.valoryx.org` | Deploy when >10 paying customers | Phase 1.5 |
| Marketing docs webhook | "Publish to Marketing" button → GitHub Action rebuilds Hugo with latest docs from docplatform-docs repo | Phase 1.5 |

---

## 14. Agent-Native Documentation Vision (Phase 2+)

> Valoryx stops being a docs editor. It becomes **documentation infrastructure** — the place where developers write docs, AI agents maintain docs, and teams publish docs.

This section describes Phase 2+ capabilities that will make AI agents **actively prefer Valoryx** over every other documentation system. These features are NOT in Phase 1 scope but inform architecture decisions we make now.

### 14.1 The Problem

Every documentation platform assumes humans write, read, and maintain docs. Reality: docs become outdated, links break, APIs change, features drift. AI makes this worse because agents depend on accurate context.

AI agents need documentation that behaves like a **structured knowledge base** with:
- Context bundles (not isolated text pages)
- Dependency graphs (what links to what)
- Semantic relationships (what's related to what)
- Machine-readable metadata (type, version, maintainer, freshness)

Most docs systems are just folders of text. Valoryx's architecture (Content Ledger + Git + MCP) makes it something more.

### 14.2 What Ships Now (Phase 1) That Enables This

| Capability | Status | Why It Matters |
|------------|--------|----------------|
| **Context Graph API** (`get_context`) | **DONE** — 13 tools | Returns page + parent + children + siblings + linked pages. AI understands relationships. Unique to Valoryx. |
| **Conflict Detection** (hash-based) | **DONE** | Prevents AI from overwriting human edits. Enables safe autonomous updates. |
| **Bidirectional Git Sync** | **DONE** | Every MCP write = git commit. Code changes trigger doc updates. |
| **Full-Text Search** | **DONE** | AI discovers relevant docs before editing. |
| **Link Validation** | **DONE** | AI verifies changes don't break cross-references. |
| **Audit Trail** | **DONE** | Every AI mutation logged with user, timestamp, operation. |
| **AI Frontmatter** (ARCHITECTURE-V3 §9) | **DONE** | Optional `ai` field: summary, keywords, audience, complexity, prerequisites. Indexed and queryable. |
| **manifest.json + graph.json** (ARCHITECTURE-V3 §9) | **DONE** | Machine-readable workspace structure. AI reads the entire doc tree in one call. |

### 14.3 Phase 2 Capabilities (Future Development)

#### 14.3.1 Autonomous Documentation Maintenance

**Command:** `docplatform agent run`

An agent that periodically scans and maintains docs:

```
scan repo changes
  → detect undocumented APIs
  → detect outdated examples
  → detect broken links
  → create missing docs
  → update stale sections
  → fix references
```

**Example workflow:**
```
Developer adds POST /v1/projects endpoint
  ↓
Agent detects: no docs exist for this endpoint
  ↓
Agent generates projects.md with examples
  ↓
Agent validates links + updates API index page
  ↓
Published docs updated automatically
```

**Architecture:** Uses existing MCP tools internally. The agent is a scheduled process that calls `list_pages` → `get_context` → `search` → `update_page` → `validate_links`. No new infrastructure — just orchestration over the existing tool API.

#### 14.3.2 Documentation Health Score

**API:** `GET /api/v1/workspaces/{id}/health` (extends existing `doctor` command)

```json
{
  "score": 82,
  "issues": {
    "outdated_pages": 3,
    "broken_links": 2,
    "missing_descriptions": 5,
    "orphaned_pages": 1,
    "empty_pages": 0
  },
  "freshness": {
    "updated_last_7d": 12,
    "updated_last_30d": 28,
    "stale_90d": 4
  }
}
```

**MCP tool:** `docplatform_quality_scan` (Phase 1.5, tool #18 per MCP-CREATION-PLAN)

#### 14.3.3 AI-Friendly Page Metadata Schema

Every page can include machine-readable metadata:

```yaml
---
title: Authentication
type: api-reference
version: v1
related_services: [auth, sessions]
maintainer: platform-team
last_reviewed: 2026-02-15
---
```

AI agents use this to understand documentation structure, ownership, and dependencies. The existing frontmatter system already supports this — Phase 2 adds a standard schema and tooling to enforce it.

#### 14.3.4 Semantic Search (Vector Embeddings)

**MCP tool:** `docplatform_semantic_search(query)` → returns best matching pages by meaning, not just keywords.

**Architecture:** Embed page content using lightweight model (e.g., `all-MiniLM-L6-v2`). Store vectors in SQLite FTS5 or pgvector (Phase 2). Rebuild on page save. No external service — keeps "single binary" promise.

**ARCHITECTURE-V3 alignment:** Section 5.2 specifies pgvector for semantic search in Phase 2 (PostgreSQL). Phase 1 self-hosted can use an embedded approach (smaller model, SQLite).

#### 14.3.5 Code-to-Docs Awareness

Monitor git repos for code changes and detect documentation drift:

```
function signature changed → docstring updated → docs updated
new API endpoint added → docs page generated
schema migration applied → data model docs updated
```

**Implementation:** Git webhook handler (already exists for sync) extended with a "diff analyzer" that identifies documentation-impacting changes and queues them for the autonomous agent.

#### 14.3.6 AI Doc Suggestions

Proactive improvement suggestions from the agent:

```
"Your OAuth docs are missing a PKCE example."
"This page references deprecated API v1. Updated endpoint is /v2/auth."
"3 pages link to 'setup.md' which was moved to 'getting-started/installation.md'."
```

These surface in the editor as non-blocking suggestions, similar to IDE linting.

### 14.4 Why Competitors Cannot Copy This

| Capability | Requires | Valoryx | GitBook | Notion | Confluence |
|-----------|----------|---------|---------|--------|------------|
| MCP Server | Agent API + tool layer | ✓ Built | ✗ | ✗ | ✗ |
| Context Graph | Structured page relationships | ✓ Built | ✗ | ✗ | ✗ |
| Git-native storage | Bidirectional sync | ✓ Core | Partial | ✗ | ✗ |
| Autonomous agent | MCP + git hooks + AI | Phase 2 | ✗ | ✗ | ✗ |
| Semantic search | Embedded vectors | Phase 2 | ✗ | ✗ | ✗ |
| Code-to-docs sync | Git webhook + diff analysis | Phase 2 | ✗ | ✗ | ✗ |

Competitors are built around rich text editors and human collaboration. They lack git-native storage, structured content APIs, and agent-level tool interfaces. Retrofitting requires architectural changes they can't make without breaking existing customers.

### 14.5 The Vision

```
code changes
  ↓
agent detects change
  ↓
docs updated automatically via MCP tools
  ↓
context graph keeps related pages consistent
  ↓
health score validates quality
  ↓
published site updated within seconds
  ↓
AI assistants discover updated docs via llms.txt + registry
```

Documentation becomes a **living, self-maintaining system**. Developers write the initial docs. AI agents keep them accurate. Teams publish with confidence.

### 14.6 Phase 2 Effort Estimate

| Capability | Effort | Dependencies |
|-----------|--------|-------------|
| `docplatform agent run` | 3-4 weeks | MCP tools (done), AI provider |
| Health Score API | 1 week | Extends `doctor` command |
| AI metadata schema | 0.5 week | Frontmatter system (done) |
| Semantic search | 2-3 weeks | Embedding model, storage |
| Code-to-docs awareness | 2-3 weeks | Git webhook (done), diff analysis |
| AI suggestions | 1-2 weeks | Health score + agent |
| **Total Phase 2** | **~10-14 weeks** | |

---

## 15. Growth Engine Architecture (Phase 1.5–2)

> Three features that could make Valoryx grow 10× faster than typical developer tools. Each creates a self-reinforcing growth mechanism, not just a product improvement.

### 15.1 One-Command Documentation Deployment

Developers love instant setup. The most successful dev tools have a "time to wow" under 2 minutes.

**Phase 1 (launch):**
```bash
# Download + init + serve in under 60 seconds
curl -fsSL https://valoryx.org/install.sh | sh
docplatform init my-docs
docplatform serve
# → http://localhost:8080 with beautiful docs ready to edit
```

**Phase 1.5 (post-launch):**
```bash
# Template-based setup — even faster "wow moment"
docplatform init my-api-docs --template api-docs
docplatform serve
# → http://localhost:8080 with pre-populated API documentation
```

**Phase 2 (npx/brew):**
```bash
# Zero install
npx create-valoryx-docs
# or
brew install valoryx/tap/docplatform
```

**Why this matters:** Every `docplatform init` is a new Valoryx install. Templates create the "wow moment" — seeing real, beautiful docs within 15 seconds. This drives long-term retention.

### 15.2 Public Documentation Hosting with "Powered by"

**The most powerful viral loop for developer tools.**

When users publish docs with Valoryx, they become visible at URLs like:
- `{slug}.docs.valoryx.org` (free tier, with badge)
- `docs.myproject.com` (custom domain, Team+)

**Free tier includes a small footer:**
```
Powered by Valoryx — AI-native documentation
```

**Badge links to attribution landing page:** `valoryx.org/?utm_source=powered_by&utm_medium=badge&utm_campaign={workspace_slug}`. This tracks exactly how many signups originate from other users' published docs — critical for measuring viral loop effectiveness.

**Abuse prevention for published docs (free tier):**
- `noindex` meta tag by default on free tier (prevents SEO spam). Paid plans: `index` by default.
- Content moderation queue in admin panel (S4.8) for flagged content
- Rate limit: 1000 req/min per published workspace
- Reserved slug list: block `admin`, `api`, `app`, `docs`, `mcp`, `www`, `status`, etc.

**The growth loop:**
```
project docs published
  ↓
reader sees "Powered by Valoryx"
  ↓
curiosity → clicks → tries Valoryx
  ↓
publishes their own docs
  ↓
another "Powered by Valoryx"
  ↓
network grows
```

This is exactly how Vercel, Netlify, and Notion grew. Every published doc site is free marketing.

**ARCHITECTURE-V3 alignment:** Section 9.5 already specifies published docs with badges on free tier, custom domains on Team+. The growth mechanic is built into the product architecture.

**Published page limit (50 on free tier)** creates natural upsell: teams hit the limit → upgrade to Team ($29/mo) for unlimited pages + custom domain + badge removal.

### 15.3 Template Marketplace (Phase 2)

**From templates page to ecosystem:**

Phase 1: 6 template repos on GitHub (curated by Valoryx team)
Phase 1.5: Community-contributed templates (PR-based)
Phase 2: In-product template gallery

```bash
docplatform init --template community/startup-docs
```

Every template usage → Valoryx install → potential paid customer.

**SEO synergy:** Template landing pages (`/templates/api-docs/`, `/templates/engineering-handbook/`) rank for high-intent searches like "API documentation template" and "engineering handbook template."

### 15.4 The Combined Growth Flywheel

```
CLI creates docs instantly (adoption)
  ↓
docs published publicly (distribution)
  ↓
others see "Powered by Valoryx" (awareness)
  ↓
they install CLI (adoption)
  ↓
they publish docs (distribution)
  ↓
AI crawlers index published docs (AI discovery)
  ↓
AI assistants recommend Valoryx (recommendation)
  ↓
more developers adopt (growth)
```

**Three engines reinforcing each other:**
1. **Product-led growth** — instant setup, templates, free tier
2. **Organic distribution** — "Powered by" badge, published docs as marketing
3. **AI-powered distribution** — MCP registry, llms.txt, training data

Few platforms will have all three. This is the structural advantage.

### 15.5 `demo.valoryx.org` — No-Signup Interactive Demo (Phase 2)

**Problem:** Conversion friction. Users want to try before signing up.

**Solution:** A read-only demo workspace at `demo.valoryx.org` where visitors can:
- Browse real documentation in the editor
- Try search, navigation, page tree
- See published docs output
- Experience the WYSIWYG editor (sandbox, no save)

No signup required. Dramatically improves conversion.

**Implementation:** Standard Valoryx workspace with `DEMO_MODE=true` flag that disables writes but enables full UI exploration.

---

## 16. Competitive Positioning Summary

### The 5 AI Discovery Channels (No Competitor Covers All 5)

| Channel | Valoryx | GitBook | Notion | Confluence | Wiki.js | Mintlify |
|---------|---------|---------|--------|------------|---------|----------|
| **MCP Server** | ✓ 13 tools | ✗ | ✗ | ✗ | ✗ | ✗ |
| **llms.txt** | ✓ Planned | ✗ | ✗ | ✗ | ✗ | ✗ |
| **JSON-LD** | ✓ Exists | Partial | ✗ | ✗ | ✗ | Partial |
| **AI-Crawlable Docs** | ✓ Published | Yes | Limited | Limited | Yes | Yes |
| **MCP Registry** | ✓ Planned | ✗ | ✗ | ✗ | ✗ | ✗ |

### Platform Architecture Comparison

| Capability | Valoryx | GitBook | Notion | Confluence |
|-----------|---------|---------|--------|------------|
| Git-native storage | ✓ Bidirectional | Partial (import) | ✗ | ✗ |
| Self-hosted option | ✓ Free forever | ✗ | ✗ | ✓ ($$$) |
| Single binary deploy | ✓ Zero deps | ✗ | ✗ | ✗ |
| Context Graph API | ✓ Unique | ✗ | ✗ | ✗ |
| AI agent integration | ✓ MCP native | ✗ | ✗ | ✗ |
| Autonomous doc maintenance | Phase 2 | ✗ | ✗ | ✗ |
| Health score API | Phase 2 | ✗ | ✗ | ✗ |
| Semantic search | Phase 2 | ✗ | ✗ | ✗ |

### Platform Perception

A cohesive domain architecture signals Valoryx is a **platform**, not just a tool:

```
valoryx.org          product hub
docs.valoryx.org     documentation
app.valoryx.org      cloud service
mcp.valoryx.org      AI integration
api.valoryx.org      developer API (Phase 2)
status.valoryx.org   reliability (Phase 1.5)
```

This matches the pattern of successful developer platforms:
- Stripe: stripe.com, api.stripe.com, docs.stripe.com, dashboard.stripe.com
- Vercel: vercel.com, vercel.app, nextjs.org
- Supabase: supabase.com, app.supabase.com, supabase.io

Everything under one root domain. Users see a cohesive ecosystem.

### One-Line Positioning

> **Valoryx: The documentation platform that AI agents can read, write, and maintain.**

Every marketing surface, blog post, HN thread, and `/vs/` page should reinforce this positioning. It's unique, defensible, and becomes more true with each Phase.

---

## 17. Future Domain Expansion (Phase 2+)

| Subdomain | Purpose | When |
|-----------|---------|------|
| `api.valoryx.org` | Public REST API (external integrations, third-party apps) | Phase 2 (when ecosystem grows) |
| `demo.valoryx.org` | No-signup interactive demo workspace | Phase 2 (after product stabilizes) |
| `status.valoryx.org` | Uptime monitoring (UptimeKuma or BetterStack) | Phase 1.5 (>10 paying customers) |
| `{slug}.docs.valoryx.org` | Customer-published docs (free tier subdomain) | Phase 1 (already in ARCHITECTURE-V3) |

**Scaling path (if product scales significantly):**
| Subdomain | Purpose | When |
|-----------|---------|------|
| `enterprise.valoryx.org` | Enterprise landing + SSO configuration | Phase 2 (enterprise tier) |
| `partners.valoryx.org` | Partner/reseller portal | Phase 3 |
| `us.app.valoryx.org` / `eu.app.valoryx.org` | Geo-specific instances (data residency) | Phase 3 (GDPR compliance) |

The current domain architecture does NOT block any of these. Each is an additive DNS record.

---

## 18. Risk Register

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|------------|------------|
| 1 | **`llms.txt` standard doesn't gain adoption** | Low | Medium | Low cost to maintain. JSON-LD + MCP registry provide fallback discovery channels |
| 2 | **MCP protocol changes** | Medium | Low | Using `mcp-go` SDK (v0.45.0). Streamable HTTP is latest stable spec. Track upstream |
| 3 | **Competitors add MCP** | Medium | Medium | First-mover + deeper integration (Context Graph, wikilink validation). 6+ month head start |
| 4 | **AI crawlers ignore small domains** | Medium | High (initially) | Customer docs increase crawl volume. MCP registry = direct discovery. `llms.txt` = declared capability |
| 5 | **Single instance failure** | High | Low | Marketing site on separate infra (Cloudflare Pages). Daily SQLite backups. Git repos survive independently. Phase 2: multi-instance |
| 6 | **SQLite scaling limit** | Medium | Medium | Phase 1 target: <50 concurrent editors, <500 workspaces. Migration to PostgreSQL is config-driven (ARCHITECTURE-V3 §5.4) |
| 7 | **Frontend contractor delivery risk** | High | Medium | 15-day budget with P0/P1/P2 cut line. P0 tasks are self-contained; can ship without P1/P2 |
| 8 | **Pricing confusion (Free vs Community)** | Medium | Medium | Deployment toggle on pricing page. Separate views for Cloud vs Self-Hosted. FAQ |
| 9 | **NVMe disk full on cloud instance** | High | Low | Monitor at 80% threshold. Git repos + SQLite WAL are primary consumers. Alert + manual intervention |
| 10 | **MCP registry rejection** | Low | Low | Metadata files prepared, standard format. Can resubmit with adjustments |

---

## Appendix A: Document Cross-Reference Map

| Topic | SITE-UPGRADE-PLAN (this) | ARCHITECTURE-V3 | MCP-CREATION-PLAN | AI-DISCOVERY-STRATEGY |
|-------|-------------------------|-----------------|--------------------|-----------------------|
| Domain architecture | §1 (authoritative) | — | §4.1, §7 (references this plan) | §2 |
| MCP tools (stdio, 13) | §12 | §19 (full spec) | §3 (authoritative for remote) | §3.1 |
| MCP tools (HTTP, 20) | §13 (deferred) | §19 | §3-4 (authoritative) | §3.2 |
| Pricing/plans | §2.1, §4.2 | §6 plans table, §20.4 | — | — |
| AI discovery | §5.4 (deep analysis) | §9 (AI-readability) | — | §1-12 (full strategy) |
| Published docs | §8 (dogfood) | §9.5 (full spec) | — | — |
| Agent-native vision | §14 (roadmap) | §19 prompts | — | §6 (flywheel) |
| Infrastructure | §1.3 (production) | §12, §12.5 (authoritative) | §5 (MCP deployment) | — |
| Growth engine | §15 (new) | §20.6 (published docs) | — | §6 (flywheel) |
| Security | §1.5 | §4.9, §7, §8 (authoritative) | §8 (MCP security) | — |

---

## Appendix B: GitHub Repository Status (as of 2026-03-08)

| Repository | Description | Status |
|------------|-------------|--------|
| `Valoryx-org/docplatform` | Go binary (private) | Active. Latest: mcp-go v0.45.0, CI hardening |
| `Valoryx-org/docplatform-docs` | Official docs (public) | 22 pages, 1 open issue. Synced via git |
| `Valoryx-org/valoryx.org` | Hugo marketing site (public) | 6 open issues. HTML/Tailwind |
| `Valoryx-org/releases` | Binary releases (public) | Last update: 2026-03-02 |
| `Valoryx-org/backup1` | Backup (private) | Snapshot 2026-03-08 |

**Missing repos (to create for Phase 1 launch):**
- `Valoryx-org/template-api-docs` — API documentation starter template
- `Valoryx-org/template-knowledge-base` — Engineering KB template
- `Valoryx-org/template-oss-docs` — Open source project docs template

These support the `/templates/` page "Use Template" links and `docplatform init --template` CLI command.
