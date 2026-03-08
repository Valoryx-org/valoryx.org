# Valoryx.org — Master Upgrade Plan (Integrated)

**Date:** 2026-03-08
**Sources:** `SITE-AUDIT-AND-UPGRADE-PLAN.md` + `SITE-IMPROVEMENTS.md` — deduplicated, reconciled, prioritized
**Repo:** https://github.com/Valoryx-org/valoryx.org
**Brand:** `BRAND.md` — 3 colors (#124265, #1d7fc2, #0c1e2e), 3 fonts (Plus Jakarta Sans, DM Sans, JetBrains Mono), light theme, Bootstrap Icons only, no emoji

---

## Table of Contents

1. [P0 — Launch Blockers](#1-p0--launch-blockers)
2. [P1 — Conversion & Trust](#2-p1--conversion--trust)
3. [P2 — SEO Infrastructure](#3-p2--seo-infrastructure)
4. [P3 — Content Expansion](#4-p3--content-expansion)
5. [P4 — Performance & Polish](#5-p4--performance--polish)
6. [Complete FAQ Bank](#6-complete-faq-bank)
7. [Week-by-Week Execution Plan](#7-week-by-week-execution-plan)

---

## 1. P0 — Launch Blockers

These 8 issues must be fixed before any launch campaign (HN, Reddit, Product Hunt). They directly block conversion or break social sharing.

### 1.1 Dual-Path Hero CTA — Community vs Cloud

**Problem:** Single "Get Started Free" button with no context about deployment options. Cloud users see terminal commands and bounce. Self-hosted users don't realize they get the full product free.

**Hero change** (`layouts/partials/sections/hero.html`, replace lines 24-29):

```html
<div class="flex flex-col sm:flex-row justify-center items-center gap-4 mb-16 reveal">
  <!-- Self-Hosted -->
  <a href="{{ $homeURL }}#download"
     class="btn-glow inline-flex items-center gap-3 text-white px-8 py-4 rounded-lg text-base font-bold no-underline group"
     style="background: var(--accent); transition: background 0.3s ease, transform 0.2s ease;">
    <i class="bi bi-download text-lg"></i>
    <span class="text-left">
      <span class="block text-[15px] font-bold">{{ i18n "hero_cta_selfhosted" }}</span>
      <span class="block text-[11px] font-normal opacity-80">{{ i18n "hero_cta_selfhosted_sub" }}</span>
    </span>
    <i class="bi bi-arrow-right ml-1 transition-transform group-hover:translate-x-1"></i>
  </a>
  <!-- Cloud -->
  <a href="https://app.valoryx.org/"
     class="inline-flex items-center gap-3 px-8 py-4 rounded-lg text-base font-bold no-underline border-2 group hover:bg-accent hover:text-white hover:border-accent"
     style="color: var(--heading); border-color: var(--accent); transition: all 0.3s ease;">
    <i class="bi bi-cloud text-lg"></i>
    <span class="text-left">
      <span class="block text-[15px] font-bold">{{ i18n "hero_cta_cloud" }}</span>
      <span class="block text-[11px] font-normal opacity-70">{{ i18n "hero_cta_cloud_sub" }}</span>
    </span>
    <i class="bi bi-arrow-right ml-1 transition-transform group-hover:translate-x-1"></i>
  </a>
</div>
```

**Get Started section** (`layouts/partials/sections/download.html`): Add Self-Hosted / Cloud toggle above OS tabs. Cloud path shows a card with "Open Valoryx Cloud" CTA → app.valoryx.org. Self-hosted path is existing OS tabs + terminal blocks.

**i18n strings** (`i18n/en.toml` — add to all 6 language files):

```toml
[hero_cta_selfhosted]
other = "Download Free"
[hero_cta_selfhosted_sub]
other = "Self-hosted · Single binary · Free forever"
[hero_cta_cloud]
other = "Try Cloud Free"
[hero_cta_cloud_sub]
other = "We host it · No setup · Start in 30 seconds"

[download_deploy_selfhosted]
other = "Self-Hosted"
[download_deploy_selfhosted_sub]
other = "Download & run on your server"
[download_deploy_cloud]
other = "Cloud"
[download_deploy_cloud_sub]
other = "We host everything for you"
[download_cloud_title]
other = "Start with Valoryx Cloud"
[download_cloud_description]
other = "No installation needed. Create your workspace in seconds. We handle infrastructure, updates, and backups."
[download_cloud_cta]
other = "Open Valoryx Cloud"
[download_cloud_free_note]
other = "Free plan: 1 workspace · 3 editors · 50 published pages"
[download_cloud_pill1]
other = "No setup required"
[download_cloud_pill2]
other = "Automatic updates"
[download_cloud_pill3]
other = "Free forever tier"
[download_cloud_prefer_selfhosted]
other = "Prefer full control?"
[download_cloud_switch_selfhosted]
other = "Download the self-hosted edition"
```

**JavaScript** (add to page script, same pattern as `switchOsTab`):

```javascript
function switchDeployTab(target) {
  document.querySelectorAll('.deploy-tab').forEach(btn => {
    const isActive = btn.dataset.deploy === target;
    btn.style.background = isActive ? 'white' : 'transparent';
    btn.style.color = isActive ? 'var(--accent)' : 'var(--body)';
    btn.style.boxShadow = isActive ? '0 1px 3px rgba(0,0,0,0.1)' : 'none';
  });
  document.getElementById('deploy-selfhosted').classList.toggle('hidden', target === 'cloud');
  document.getElementById('deploy-cloud').classList.toggle('hidden', target !== 'cloud');
}
```

**Also update:**
- `/install/` page: add "Looking for cloud?" link at top → app.valoryx.org
- Footer: add "Cloud App" link under Product column
- Header CTA "Download Free" → keeps anchor to `#download` (now has toggle)

---

### 1.2 Social Share Images (og:image)

**Problem:** `twitter:card` is `summary_large_image` but NO `og:image` or `twitter:image` exists anywhere. Every social share is blank.

**Fix `layouts/partials/head.html`** (replace OG section):

```html
{{ $ogImage := .Params.ogImage | default "/images/og-default.png" | absURL }}
<meta property="og:image"        content="{{ $ogImage }}">
<meta property="og:image:width"  content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:image"       content="{{ $ogImage }}">
```

**Also fix per-page og:title and og:description** (currently hardcoded to i18n keys):

```html
{{ $pageTitle := cond .IsHome (i18n "og_title") (printf "%s — Valoryx" .Title) }}
{{ $pageDesc := .Params.description | default (i18n "og_description") }}
<meta property="og:title"       content="{{ $pageTitle }}">
<meta property="og:description" content="{{ $pageDesc }}">
<meta name="twitter:title"       content="{{ $pageTitle }}">
<meta name="twitter:description" content="{{ $pageDesc }}">
```

**Create 7 OG images** (`static/images/`):

| File | Content | Used on |
|------|---------|---------|
| `og-default.png` | Logo + "Git-Native Documentation Platform" + product screenshot on navy gradient | Homepage + fallback |
| `og-pricing.png` | "Simple Pricing" + 3 plan cards | /pricing/ |
| `og-templates.png` | "Documentation Templates" + 6 icons | /templates/ |
| `og-install.png` | Terminal with `curl` command | /install/ |
| `og-mcp.png` | "13 AI Tools" + tool icons | /mcp/ |
| `og-vs-gitbook.png` | Valoryx vs GitBook split | /vs/gitbook/ |
| `og-blog.png` | "Valoryx Blog" + abstract graphic | /blog/ |

**Spec:** 1200x630px, navy (#0c1e2e) → heading (#124265) gradient, white Plus Jakarta Sans text, Valoryx logo top-left, < 300KB PNG.

---

### 1.3 Per-Page Meta Descriptions

**Problem:** `head.html` line 8 uses `{{ .Site.Params.description }}` for ALL non-home pages. Every SERP snippet is identical.

**Fix `head.html` line 8:**

```html
<meta name="description" content="{{ with .Params.description }}{{ . }}{{ else }}{{ i18n "meta_description" }}{{ end }}">
```

**Add `description` frontmatter to every content file:**

| Page | `description` value (< 155 chars) |
|------|----------------------------------|
| `/pricing/_index.md` | "Free forever for 5 editors. Team $29/mo, Business $79/mo per workspace. Self-hosted or cloud. No vendor lock-in — your docs stay in git." |
| `/templates/_index.md` | "6 ready-to-use documentation templates: API docs, knowledge base, open source, changelog, AI-maintained, and compliance. Git-native, free." |
| `/install/_index.md` | "Install Valoryx with one command. Single Go binary, zero dependencies. Linux, macOS, Windows, Docker. Running in under 30 seconds." |
| `/mcp/_index.md` | "Built-in MCP server with 13 tools for Claude, Cursor, and VS Code. Let AI agents read, write, search, and validate your docs automatically." |
| `/vs/gitbook.md` | "Valoryx vs GitBook: self-hosted, bidirectional git sync, built-in MCP server. See which documentation platform fits your team." |
| `/blog/_index.md` | "Technical blog about documentation engineering, self-hosted tools, git workflows, and AI-powered documentation maintenance." |

Also add `ogImage` frontmatter pointing to the corresponding OG image.

---

### 1.4 Product Screenshots

**Problem:** Zero `<img>` tags showing the product on the ENTIRE site. Biggest conversion blocker.

**Minimum viable set:**

| Screenshot | Where | Spec |
|-----------|-------|------|
| `hero-editor.webp` | Hero (after CTA, before icon boxes) | WYSIWYG editor with realistic content, `loading="eager"` |
| `hero-published.webp` | Homepage features section | Published docs with theme applied |
| `mcp-session.webp` | /mcp/, homepage | Claude using MCP tools |
| `git-sync.webp` | Homepage features | Split: IDE left, web editor right |
| `install-terminal.gif` | /install/ | 15s GIF: curl → serve → browser |
| `pricing-dashboard.webp` | /pricing/ | Admin dashboard |

**Hero insertion** (`layouts/partials/sections/hero.html`, after CTA div, before icon boxes):

```html
<div class="mt-12 mb-16 max-w-4xl mx-auto reveal">
  <img src="/images/hero-editor.webp"
       alt="Valoryx WYSIWYG editor with bidirectional git sync and live Markdown preview"
       class="rounded-2xl w-full"
       style="box-shadow: 0 16px 48px rgba(0,0,0,0.12);"
       width="1200" height="675" loading="eager">
</div>
```

**Image spec:** WebP, 2x retina, displayed at 1x, `rounded-2xl`, layered shadow, `loading="lazy"` for below-fold, explicit `width`/`height` to prevent CLS.

---

### 1.5 Fix Title Tag Duplicates

| Page | Current | Fix |
|------|---------|-----|
| `/templates/` | "Documentation Templates — Valoryx — Valoryx" | "Documentation Templates — Valoryx" |
| Homepage | "Valoryx — Git-Native Documentation Platform \| Self-Hosted, Open Source" (73 chars, truncated) | "Valoryx — Git-Native Documentation Platform" (44 chars) |

Fix in `head.html` — ensure no double brand name. The current template logic should prevent this; check `_index.md` title frontmatter for duplicates.

---

### 1.6 Fix SSO/SAML on Free Plan

**Problem:** Free cloud plan lists SSO/SAML and Custom Domains — premium features shown on free tier undermines upgrade motivation.

**Fix:** Remove SSO/SAML and Custom Domains from Free plan. Move to Team+ only. Update in `layouts/pricing/list.html` and all i18n files.

---

### 1.7 Fix Heading Hierarchy

**Problem:** Homepage hero goes h1 → h4 (icon boxes), skipping h2/h3.

**Fix** (`layouts/partials/sections/hero.html`): Change icon-box `<h4>` to `<h3>`. Keep visual styles identical:

```html
<h3 class="text-lg font-bold" style="color: var(--heading);">{{ i18n "hero_box1_title" }}</h3>
```

---

### 1.8 Fix Contact Form Labels

**Problem:** Form inputs use `placeholder` only — no `<label>`. WCAG Level A violation.

**Fix** (`layouts/partials/sections/contact.html`):

```html
<label for="contact-name" class="sr-only">Your Name</label>
<input type="text" id="contact-name" name="name" placeholder="Your Name" required>
```

Repeat for email, subject, message fields.

---

## 2. P1 — Conversion & Trust

### 2.1 Pricing Page — Feature Comparison Table

**Problem:** Only individual cards, no side-by-side comparison. Every competitor has this.

**Add below plan cards, above FAQ** (`layouts/pricing/list.html`):

```
| Feature               | Free    | Team       | Business   |
|-----------------------|---------|------------|------------|
| Workspaces            | 1       | 3          | 10         |
| Editors               | 3       | 15         | 50         |
| Published Pages       | 50      | Unlimited  | Unlimited  |
| Git Sync              | check   | check      | check      |
| WYSIWYG Editor        | check   | check      | check      |
| Full-Text Search      | check   | check      | check      |
| MCP Server (stdio)    | check   | check      | check      |
| Custom Domains        | —       | check      | check      |
| SSO / SAML            | —       | —          | check      |
| Priority Support      | —       | check      | check      |
| Analytics Dashboard   | —       | —          | check      |
| Audit Logs            | —       | —          | check      |
```

Style: existing `.compare-table` CSS. Brand accent for checks, muted for dashes.

### 2.2 Pricing Page — Plan Personas & Trust Signals

**Add one-liner under each plan name:**

| Plan | Persona |
|------|---------|
| Free | "For individuals and small teams getting started" |
| Team | "For growing teams that need collaboration and publishing" |
| Business | "For organizations that need security, compliance, and scale" |

**Trust signals below cards:**

```html
<div class="flex flex-wrap justify-center gap-6 mt-8 text-sm" style="color: var(--muted);">
  <span><i class="bi bi-credit-card" style="color: var(--success);"></i> No credit card required</span>
  <span><i class="bi bi-arrow-repeat" style="color: var(--success);"></i> Cancel anytime</span>
  <span><i class="bi bi-shield-check" style="color: var(--success);"></i> 14-day money-back guarantee</span>
</div>
```

### 2.3 Per-Workspace Pricing Callout

**Problem:** Flat-rate per-workspace is a major advantage over per-seat competitors, but it's not called out.

**Add between hero and plan cards:**

```html
<div class="rounded-xl p-6 text-center max-w-2xl mx-auto mb-12" style="background: rgba(29,127,194,0.06); border: 1px solid rgba(29,127,194,0.15);">
  <p class="text-lg font-semibold" style="color: var(--heading);">
    Unlike per-seat pricing, Valoryx charges per workspace.
  </p>
  <p class="text-sm mt-2" style="color: var(--muted);">
    A 15-person team on Team plan pays $29/mo total — not $142+ like per-seat alternatives.
  </p>
</div>
```

### 2.4 Enterprise Tier

Add a 4th option (card or row):

```
Enterprise — Custom pricing
"For large organizations with custom requirements"
- Unlimited workspaces & editors
- SAML/SSO, dedicated support, custom SLA
- On-premises deployment
- [Contact Sales]
```

### 2.5 Templates — Per-Card CTAs

**Problem:** Template cards have no actionable button. Only a generic CTA at bottom.

**Add to each card:**

```html
<div class="mt-4 flex gap-3">
  <a href="https://github.com/Valoryx-org/template-api-docs" target="_blank" rel="noopener"
     class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold text-white no-underline"
     style="background: var(--accent);">
    <i class="bi bi-github"></i> Use Template
  </a>
  <a href="/templates/api-docs/"
     class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold no-underline border"
     style="color: var(--heading); border-color: var(--border);">
    Preview
  </a>
</div>
```

### 2.6 Templates — Expanded Descriptions

Expand each card from 1 sentence to structured content:

```
### API Documentation
Ship API docs that live in your git repo.

Includes: 5 pre-built pages (Overview, Authentication, Endpoints, Errors, Changelog)
Best for: Backend teams, API-first companies, developer platforms
Features used: Git Sync, Versioning, Published Docs, Search
```

### 2.7 Install Page — Verification + What's Next

**After install commands, add:**

```bash
# Verify installation
$ docplatform version
DocPlatform v0.5.2

# Start the server
$ docplatform serve
Server running at http://localhost:3000
```

**"What's Next" section:**

```html
<div class="rounded-xl p-8 mt-8" style="background: rgba(5,150,82,0.06); border: 1px solid rgba(5,150,82,0.15);">
  <h3 class="text-xl font-bold mb-4" style="color: var(--heading);">You're all set!</h3>
  <div class="space-y-2">
    <a href="/docs/getting-started/quickstart/" class="block text-sm font-semibold" style="color: var(--accent);">
      <i class="bi bi-arrow-right"></i> Quick Start Guide
    </a>
    <a href="/docs/getting-started/first-workspace/" class="block text-sm font-semibold" style="color: var(--accent);">
      <i class="bi bi-arrow-right"></i> Create Your First Workspace
    </a>
    <a href="/docs/guides/git-integration/" class="block text-sm font-semibold" style="color: var(--accent);">
      <i class="bi bi-arrow-right"></i> Connect a Git Repository
    </a>
    <a href="/mcp/" class="block text-sm font-semibold" style="color: var(--accent);">
      <i class="bi bi-arrow-right"></i> Set Up MCP for AI Agents
    </a>
  </div>
</div>
```

### 2.8 Install Page — System Requirements

**Add before install tabs:**

```
Requirements:
- OS: Linux (amd64/arm64), macOS (Intel/Apple Silicon), Windows (amd64)
- Disk: ~50 MB (binary + SQLite database)
- RAM: 128 MB minimum, 256 MB recommended
- Port: 3000 (default, configurable)
- Dependencies: None. Single binary includes everything.
```

### 2.9 Install Page — Troubleshooting

```
Troubleshooting:

Permission denied → Run with sudo: sudo curl -fsSL https://valoryx.org/install.sh | sh
Port 3000 in use → docplatform serve --port 8080
Wrong binary → Check OS/arch: uname -sm
Behind a proxy → Set HTTP_PROXY and HTTPS_PROXY before running installer

Still stuck? Open an issue on GitHub or check the full troubleshooting guide.
```

### 2.10 Social Proof Signals

**Now (pre-PMF):**

| Signal | Where | Implementation |
|--------|-------|---------------|
| MIT License badge | Hero | `<img src="https://img.shields.io/badge/license-MIT-green">` |
| Go version badge | /install/ | "Built with Go 1.25" |
| "709 tests passing" | /install/ | Test badge |
| Binary size | /install/ stats | "~15 MB binary, zero dependencies" |

**Later (when users arrive):**

| Signal | Where |
|--------|-------|
| GitHub stars badge | Hero, /install/ |
| "Used by X teams" | Homepage stats |
| Customer logos | Homepage (new section) |
| Testimonial card | Homepage (before pricing) |

### 2.11 FAQPage JSON-LD (All Pages)

Create `layouts/partials/faq-jsonld.html`:

```html
{{ if .Params.faq }}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{ range $i, $item := .Params.faq }}
    {{ if $i }},{{ end }}
    {
      "@type": "Question",
      "name": {{ $item.q | jsonify }},
      "acceptedAnswer": {
        "@type": "Answer",
        "text": {{ $item.a | jsonify }}
      }
    }
    {{ end }}
  ]
}
</script>
{{ end }}
```

Include in `head.html`: `{{ partial "faq-jsonld.html" . }}`

Add `faq:` array to frontmatter of: homepage `_index.md`, `/pricing/_index.md`, `/templates/_index.md`, `/install/_index.md`, `/mcp/_index.md`.

See **Section 6** for complete FAQ content.

### 2.12 Accessibility — Skip-to-Content + Keyboard Nav

**Skip link** (first element in `<body>` in `baseof.html`):

```html
<a href="#main-content" class="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:bg-white focus:px-4 focus:py-2 focus:rounded focus:shadow-lg" style="color: var(--accent);">
  Skip to content
</a>
```

**Language dropdown** — add keyboard support:

```javascript
const langDropdown = document.querySelector('.language-dropdown');
if (langDropdown) {
  langDropdown.addEventListener('focusin', () => langDropdown.classList.add('is-open'));
  langDropdown.addEventListener('focusout', (e) => {
    if (!langDropdown.contains(e.relatedTarget)) langDropdown.classList.remove('is-open');
  });
}
```

**Copy buttons** — add `aria-label="Copy command to clipboard"`.

**FAQ** — consider migrating to native `<details>/<summary>` for built-in keyboard + screen-reader support.

---

## 3. P2 — SEO Infrastructure

### 3.1 BreadcrumbList JSON-LD

Create `layouts/partials/breadcrumb-jsonld.html`:

```html
{{ if not .IsHome }}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "{{ .Site.BaseURL }}" }
    {{ if .Parent }}
    ,{ "@type": "ListItem", "position": 2, "name": "{{ .Parent.Title }}", "item": "{{ .Parent.Permalink }}" }
    ,{ "@type": "ListItem", "position": 3, "name": "{{ .Title }}", "item": "{{ .Permalink }}" }
    {{ else }}
    ,{ "@type": "ListItem", "position": 2, "name": "{{ .Title }}", "item": "{{ .Permalink }}" }
    {{ end }}
  ]
}
</script>
{{ end }}
```

### 3.2 Page-Specific JSON-LD

| Page | Add Schema | Key Fields |
|------|-----------|-----------|
| Homepage | `Organization` | name, url, logo, sameAs (GitHub) |
| `/pricing/` | `Product` + `AggregateOffer` | 3 offers with price, billing period |
| `/templates/` | `CollectionPage` + `ItemList` | 6 templates with names + URLs |
| `/install/` | `HowTo` | 3 steps, totalTime PT30S |
| `/mcp/` | Dedicated `SoftwareApplication` | 13 tools, categories |
| `/vs/*` | `Article` | comparison content |
| `/blog/*` | `Article` | headline, datePublished, author |

### 3.3 Fix Existing JSON-LD Inconsistencies

| Issue | Fix |
|-------|-----|
| Product name "Valoryx" in JSON-LD | Change to "DocPlatform" (Valoryx = company) |
| URL field points to homepage on all pages | Use `{{ .Permalink }}` |
| "Docker" listed as operatingSystem | Remove (Docker = deployment method) |
| "7 themes" in featureList | Verify actual count, update to match |
| Missing `softwareVersion` | Add `"softwareVersion": "{{ .Site.Params.releaseTag }}"` |
| Missing `downloadUrl` | Add `"downloadUrl": "https://valoryx.org/install/"` |

### 3.4 Sitemap Configuration

```toml
# hugo.toml
[sitemap]
  changefreq = "weekly"
  filename = "sitemap.xml"
  priority = 0.5

# Override per-page in frontmatter:
# Homepage: 1.0/daily, /pricing/: 0.9/monthly, /install/: 0.8/monthly
# /templates/: 0.8/monthly, /mcp/: 0.8/monthly, /vs/*: 0.7/monthly
# /blog/: 0.7/weekly, /docs/*: 0.6/monthly, /changelog/: 0.5/weekly
```

### 3.5 Internal Linking Matrix

Every page must link to at least 3 other pages:

| From | Must Link To |
|------|-------------|
| Homepage | /pricing/, /templates/, /mcp/, /install/, /docs/, /blog/ |
| /pricing/ | /install/, /templates/, /mcp/, /vs/*, /docs/ |
| /templates/ | /pricing/, /install/, /mcp/ |
| /install/ | /pricing/, /templates/, /mcp/, /docs/getting-started/ |
| /mcp/ | /install/, /pricing/, /docs/ |
| /vs/* | /pricing/, /install/, /mcp/ |
| /blog/* | /pricing/, /templates/, /mcp/, related posts |

### 3.6 RSS Feed

Verify and add to `head.html`:

```html
{{ with .OutputFormats.Get "rss" }}
<link rel="alternate" type="application/rss+xml" title="Valoryx Blog" href="{{ .Permalink }}">
{{ end }}
```

### 3.7 Robots.txt — AI Bot Rules

```
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: Claude-Web
Allow: /
User-agent: Anthropic-AI
Allow: /

Sitemap: https://valoryx.org/sitemap.xml
```

### 3.8 Miscellaneous SEO

- Remove Hugo generator: `disableHugoGeneratorInject = true` in `hugo.toml`
- Add Apple touch icon: `<link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png">`
- Fix "Learn More" links: add `aria-label` with specific feature name
- Blog posts: add `Article` JSON-LD, author byline, related posts, social share buttons

---

## 4. P3 — Content Expansion

### 4.1 Missing /vs/ Pages (Programmatic SEO)

Create using existing `layouts/vs/single.html`:

| Page | Target Keywords | Est. Volume |
|------|----------------|-------------|
| `/vs/notion/` | notion alternative self-hosted | 4,800/mo |
| `/vs/confluence/` | confluence alternative open source | 3,600/mo |
| `/vs/wikijs/` | wiki.js alternative | 1,000/mo |
| `/vs/readme/` | readme.com alternative | 500/mo |
| `/vs/docusaurus/` | docusaurus alternative | 500/mo |
| `/vs/mkdocs/` | mkdocs alternative | 300/mo |

**Content structure per page:**
Hero → TL;DR (3 bullets) → Feature Table → Where Valoryx Wins → Where {Competitor} Wins (honest per SKILL.md) → MCP Differentiator → Migration Guide → CTA

### 4.2 Individual Template Pages

Create `layouts/templates/single.html` + 6 content files:

- `/templates/api-docs/`
- `/templates/knowledge-base/`
- `/templates/open-source/`
- `/templates/changelog/`
- `/templates/ai-maintained/`
- `/templates/compliance/`

Each: 500+ words, screenshots, GitHub template repo link, related templates.

**Also create GitHub template repos:**

| Repo | Structure |
|------|-----------|
| `Valoryx-org/template-api-docs` | overview, auth, endpoints/, errors, changelog |
| `Valoryx-org/template-knowledge-base` | onboarding/, architecture/, runbooks/, how-to/ |
| `Valoryx-org/template-oss-docs` | getting-started, installation, guides/, api-ref, contributing |
| `Valoryx-org/template-changelog` | YYYY/MM-DD-version.md |
| `Valoryx-org/template-ai-docs` | knowledge-base + .docplatform.yaml MCP config |
| `Valoryx-org/template-compliance` | policies/, procedures/, controls/, evidence/ |

### 4.3 Blog Content Calendar (8 weeks)

| Week | Title | Keyword | Links to |
|------|-------|---------|----------|
| 1 | "Confluence Alternative for Developer Teams" | confluence alternative | /vs/confluence/, /pricing/ |
| 2 | "How to Set Up AI Documentation with MCP" | mcp documentation tool | /mcp/, /install/ |
| 3 | "Wiki.js vs Valoryx: Self-Hosted Comparison" | wiki.js alternative | /vs/wikijs/, /pricing/ |
| 4 | "5 Documentation Templates Every Team Needs" | documentation templates | /templates/, /pricing/ |
| 5 | "Bidirectional Git Sync Deep Dive" | git sync documentation | /docs/guides/git-integration/ |
| 6 | "Self-Hosted vs Cloud: Decision Guide" | self-hosted documentation | /pricing/, /install/ |
| 7 | "API Documentation Best Practices 2026" | api docs best practices | /templates/api-docs/ |
| 8 | "Building a Single-Binary Docs Platform in Go" | go single binary | /open-source/, /install/ |

### 4.4 Resolve Content Inconsistencies

| Item | Current Conflict | Resolution |
|------|-----------------|------------|
| Free editors (cloud) | 3 (pricing page) vs 5 (work.md) | **Decide one number. Update all surfaces.** |
| Published docs themes | "7" (JSON-LD) vs "5" (work.md) | **Count actual themes. Update everywhere.** |
| Product name | "Valoryx" (JSON-LD, install H1) vs "DocPlatform" (binary) | **DocPlatform = product, Valoryx = company.** |
| Context Graph API | In comparison table but unexplained | **Either add explanation or remove from comparison.** |
| "Coming soon" language | Appears for annual billing + trials | **Replace with positive framing** (see Section 2) |

---

## 5. P4 — Performance & Polish

### 5.1 Replace Tailwind CDN with Compiled CSS

**Current:** `<script src="https://cdn.tailwindcss.com">` — Play CDN, ~300KB JS, generates CSS at runtime, FOUC risk. Not production-ready.

**Option A (recommended):**

```bash
npm init -y && npm install -D tailwindcss postcss autoprefixer
```

1. Extract inline config from `head.html` → `tailwind.config.js`
2. Create `assets/css/tailwind.css` with Tailwind directives
3. In `head.html`: `{{ $css := resources.Get "css/tailwind.css" | postCSS | minify | fingerprint }}`
4. Remove `<script src="https://cdn.tailwindcss.com">` and inline `<script>` config

**Result:** CSS drops from ~300KB JS to ~15-30KB CSS. LCP improves. No FOUC.

**Option B (simpler):**
`npx tailwindcss -o static/css/tailwind.min.css --minify` before each deploy.

### 5.2 Font Optimization

- Verify `&display=swap` in Google Fonts URL (already present)
- Consider self-hosting (eliminates render-blocking request to fonts.googleapis.com)
- Subset to Latin + Cyrillic (for RU/UK support)
- Preload critical font weights:

```html
<link rel="preload" href="/fonts/PlusJakartaSans-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/DMSans-400.woff2" as="font" type="font/woff2" crossorigin>
```

### 5.3 Image Optimization

- WebP format with PNG fallback
- `srcset` for responsive images
- `loading="lazy"` below fold, `loading="eager"` for hero
- Explicit `width`/`height` to prevent CLS
- Compress: 80% quality WebP

### 5.4 Bootstrap Icons Subset

Only ~15 icons used. Either:
- Inline SVGs for used icons (best performance)
- Or keep CDN (simpler, acceptable since it's cached)

### 5.5 Preload Critical Assets

```html
<link rel="preload" href="/css/main.css" as="style">
<link rel="preload" href="/assets/hero-bg.jpg" as="image">
```

### 5.6 Homebrew Install Method

```bash
brew install valoryx/tap/docplatform
```

Requires creating `Valoryx-org/homebrew-tap` repo.

### 5.7 Update/Uninstall Instructions on Install Page

```
Update: Re-run curl -fsSL https://valoryx.org/install.sh | sh
Uninstall: sudo rm /usr/local/bin/docplatform && rm -rf ~/.docplatform
```

---

## 6. Complete FAQ Bank

### 6.1 Homepage (10 questions)

**Keep existing 6, add these 4:**

**Q7: What is MCP and how does it work with Valoryx?**
A: MCP (Model Context Protocol) is an open standard that lets AI tools interact with external services. Valoryx includes a built-in MCP server with 13 tools that allow Claude, Cursor, and VS Code to read, write, search, and manage your documentation programmatically. Every change creates a git commit with full attribution. Setup takes 2 minutes with a single CLI command.

**Q8: What file format does Valoryx use?**
A: Standard Markdown. All documentation is stored as .md files in a git repository. No proprietary format, no database lock-in. You can read, edit, and migrate your content with any tool that understands Markdown and git.

**Q9: How does Valoryx compare to GitBook?**
A: GitBook is cloud-only with one-way git sync. Valoryx offers true bidirectional sync, self-hosted deployment, and a built-in MCP server for AI integration. GitBook has a more polished UI and larger integration ecosystem. See our detailed comparison at /vs/gitbook/.

**Q10: Is Valoryx suitable for large teams?**
A: Yes. The Business plan supports 50 editors across 10 workspaces with SSO/SAML, audit logging, granular RBAC, and SLA guarantees. For larger deployments, contact us for enterprise pricing.

---

### 6.2 Pricing Page (12 questions)

**Q1: What's the difference between Cloud and Self-Hosted?**
A: Cloud is hosted and managed by us at app.valoryx.org — we handle updates, backups, and infrastructure. Self-Hosted means you run Valoryx on your own server with a single binary or Docker container. Both have the same core features. Cloud adds managed infrastructure. Self-Hosted gives you full data sovereignty and unlimited usage.

**Q2: Can I migrate between Cloud and Self-Hosted?**
A: Yes. Your content is stored as Markdown in a git repository. Clone your repo and point a new instance at it — migration is instant.

**Q3: Do you offer annual billing?**
A: Annual billing with a 20% discount launches soon. Start monthly today and switch when it becomes available — no disruption.

**Q4: Is there a trial period?**
A: Our Free tier has no time limit and no credit card required. Use it as long as you want. When your team grows, upgrade in one click.

**Q5: What happens if I exceed my plan limits?**
A: You'll see a clear message. Existing content remains fully accessible — we never lock your data. Upgrade instantly or adjust your usage.

**Q6: What payment methods do you accept?**
A: All major credit and debit cards via Stripe. Invoice billing available for Business and Enterprise plans.

**Q7: Can I upgrade or downgrade at any time?**
A: Yes. Upgrades take effect immediately. Downgrades activate at the end of your billing period. No penalties, no lock-in.

**Q8: Do you offer discounts for education or nonprofits?**
A: The Self-Hosted Community Edition is free forever for everyone. For Cloud plans, contact us — we offer case-by-case discounts.

**Q9: Is my data encrypted?**
A: Yes. All data in transit is encrypted with TLS 1.3. Self-hosted instances use SQLite on your infrastructure — you control encryption at rest. Cloud uses encrypted storage with regular backups.

**Q10: What is a "workspace"?**
A: A workspace is an independent documentation project with its own pages, git repo, published docs site, and team. Each workspace can have its own custom domain.

**Q11: Do you offer refunds?**
A: Yes. 14-day money-back guarantee on all paid plans. No questions asked.

**Q12: What is your uptime SLA?**
A: Cloud plans target 99.9% uptime. Self-hosted uptime depends on your infrastructure.

---

### 6.3 Templates Page (6 questions)

**Q1: What is a template?**
A: A pre-built documentation structure — organized Markdown files and folders that give you a head start for a specific use case. Start with proven sections instead of a blank workspace.

**Q2: Can I customize a template?**
A: Absolutely. Templates are starting points. Every page, folder, and setting is fully editable.

**Q3: Can I create my own template?**
A: Yes. Any workspace can be used as a template. Organize your docs, then share the git repository.

**Q4: Do templates work with both Cloud and Self-Hosted?**
A: Yes. Templates are standard git repos with Markdown files. They work identically everywhere.

**Q5: How do I use a template?**
A: Click "Use Template" to open the GitHub template repo. Click "Use this template" on GitHub. Connect the repo to a Valoryx workspace via Git Sync.

**Q6: Are templates free?**
A: Yes. All official templates are free and open source. Use them with any plan.

---

### 6.4 Install Page (6 questions)

**Q1: What are the system requirements?**
A: Linux (amd64/arm64), macOS (Intel/Apple Silicon), Windows (amd64). ~50 MB disk, 128 MB RAM. No external dependencies — no Node.js, no database server, no Redis.

**Q2: How do I update?**
A: Re-run `curl -fsSL https://valoryx.org/install.sh | sh`. Downloads the latest version, replaces the binary. Data is preserved.

**Q3: Can I install without root/sudo?**
A: Yes. Download the binary manually and place it anywhere in your PATH.

**Q4: Is the install script safe to pipe to sh?**
A: The script is open source — inspect it at valoryx.org/install.sh. It downloads from GitHub Releases with SHA256 checksum verification. No data is collected.

**Q5: How do I uninstall?**
A: `sudo rm /usr/local/bin/docplatform && rm -rf ~/.docplatform`. That's everything — no registry entries, no leftover files.

**Q6: Can I run multiple instances?**
A: Yes. Each instance uses its own data directory (configurable with `--data-dir`). Run multiple on different ports.

---

### 6.5 MCP Page (7 questions)

**Q1: What is MCP?**
A: Model Context Protocol — an open standard that lets AI tools interact with external systems. Valoryx includes a built-in MCP server so AI agents can directly read, write, search, and manage your documentation.

**Q2: Which AI tools work with Valoryx MCP?**
A: Any MCP-compatible client: Claude Code, Claude Desktop, Cursor, VS Code with MCP extension, and any custom client using the MCP SDK.

**Q3: Is the MCP server free?**
A: Yes. All 13 MCP tools are included in every plan, including the free Community Edition.

**Q4: Is remote MCP available?**
A: Coming in Phase 1.5. Currently MCP runs locally via stdio (zero network overhead). Remote HTTP mode will be available for Team and Business plans.

**Q5: How do AI agents authenticate?**
A: Via API key. Keys are SHA-256 hashed with pepper before storage. Each workspace has its own key for isolation.

**Q6: Can AI agents break my documentation?**
A: Every change creates a git commit with full attribution. Review, revert, or approve changes through normal git workflows. Link validation runs automatically.

**Q7: What can AI agents do with 13 tools?**
A: Content management (list, read, write, update, delete, move pages), discovery (search, context graph, workspace listing, tree navigation), quality assurance (link validation), and settings (theme management).

---

## 7. Week-by-Week Execution Plan

### Week 1 — P0 Launch Blockers

| Day | Task | Files |
|-----|------|-------|
| 1 | Create 7 OG images (1200x630, brand colors) | `static/images/og-*.png` |
| 1 | Fix `head.html`: per-page meta desc, og:image, og:title | `layouts/partials/head.html` |
| 1 | Add ogImage + description frontmatter to all content files | `content/en/*/_index.md` |
| 2 | Implement dual-path hero CTA (2 buttons) | `layouts/partials/sections/hero.html`, `i18n/*.toml` |
| 2 | Add Self-Hosted/Cloud toggle to Get Started section | `layouts/partials/sections/download.html`, `i18n/*.toml` |
| 3 | Create 4-6 product screenshots (editor, published, git sync, MCP) | `static/images/` |
| 3 | Add hero product screenshot | `layouts/partials/sections/hero.html` |
| 4 | Fix heading hierarchy (h4 → h3 in hero icon boxes) | `layouts/partials/sections/hero.html` |
| 4 | Fix contact form labels (add sr-only labels) | `layouts/partials/sections/contact.html` |
| 4 | Fix SSO/SAML on Free plan | `layouts/pricing/list.html`, `i18n/*.toml` |
| 5 | Fix title duplicates (/templates/ double brand name) | Content frontmatter |
| 5 | Verify all changes build: `hugo --minify` | — |

### Week 2 — P1 Conversion & Trust

| Day | Task | Files |
|-----|------|-------|
| 1 | Add pricing comparison table | `layouts/pricing/list.html`, `i18n/en.toml` |
| 1 | Add plan personas + trust signals | `layouts/pricing/list.html`, `i18n/en.toml` |
| 1 | Add per-workspace pricing callout | `layouts/pricing/list.html` |
| 2 | Add template per-card CTAs + expanded descriptions | `layouts/templates/list.html`, `i18n/en.toml` |
| 2 | Add Enterprise tier | `layouts/pricing/list.html`, `i18n/en.toml` |
| 3 | Add install verification + "What's Next" + system reqs | `layouts/install/list.html`, `i18n/en.toml` |
| 3 | Add install troubleshooting section | `layouts/install/list.html`, `i18n/en.toml` |
| 4 | Create FAQPage JSON-LD partial + include in head.html | `layouts/partials/faq-jsonld.html` |
| 4 | Add FAQ frontmatter to all 5 pages (41 total questions) | All `_index.md` files |
| 5 | Add skip-to-content + keyboard nav fixes | `layouts/_default/baseof.html`, JS |
| 5 | Add aria-labels to copy buttons, Learn More links | Various layouts |

### Week 3 — P2 SEO Infrastructure

| Day | Task | Files |
|-----|------|-------|
| 1 | Add BreadcrumbList JSON-LD partial | New `layouts/partials/breadcrumb-jsonld.html` |
| 1 | Add Organization schema to homepage | `layouts/partials/head.html` |
| 2 | Add page-specific JSON-LD (HowTo, CollectionPage, Product) | Various layout files |
| 2 | Fix existing JSON-LD inconsistencies | `layouts/partials/head.html` |
| 3 | Configure sitemap with per-page priorities | `hugo.toml`, content frontmatter |
| 3 | Add RSS feed link to head | `layouts/partials/head.html` |
| 4 | Update robots.txt with AI bot rules | `layouts/robots.txt` or `static/robots.txt` |
| 4 | Remove Hugo generator tag | `hugo.toml` |
| 5 | Add Apple touch icon | `static/assets/apple-touch-icon.png` |
| 5 | Audit internal links — add missing cross-links per matrix | All content files |

### Week 4 — P3 Content Expansion

| Day | Task | Files |
|-----|------|-------|
| 1-2 | Create `/vs/notion/` page | `content/en/vs/notion.md` |
| 2-3 | Create `/vs/confluence/` page | `content/en/vs/confluence.md` |
| 3-4 | Create `/vs/wikijs/` page | `content/en/vs/wikijs.md` |
| 4-5 | Create `layouts/templates/single.html` + 3 individual template pages | New layout + content |

### Week 5 — P4 Performance

| Day | Task | Files |
|-----|------|-------|
| 1-2 | Replace Tailwind CDN with compiled CSS | `layouts/partials/head.html`, new `tailwind.config.js` |
| 3 | Self-host fonts or add preload | `layouts/partials/head.html` |
| 4 | Create remaining 3 individual template pages | Content files |
| 5 | Full Lighthouse audit + fix remaining issues | Various |

### Weeks 6-8 — Blog & Ongoing

- Write 1 blog post per week (see calendar in Section 4.3)
- Create remaining /vs/ pages (readme, docusaurus, mkdocs)
- Create GitHub template repos (6 repos)
- Add social proof as users arrive
- Monitor Search Console, iterate

### Ongoing

- Update `llms.txt` when features ship
- Update `llms-full.txt` when docs change
- Add blog posts with 2+ internal links each
- Resolve content inconsistencies (Section 4.4) — **this requires a product decision on free tier limits**
- Track Core Web Vitals post-Tailwind migration
