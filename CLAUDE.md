# CLAUDE.md — Valoryx.org (Hugo)

## Project Overview

Marketing + documentation site for **Valoryx** — a git-native, self-hosted documentation platform (single Go binary, bidirectional git sync, Tiptap editor, published docs). This is the front door for organic developer acquisition.

- **Live URL:** `https://valoryx.org/`
- **Repo:** `Valoryx-org/valoryx.org` (GitHub)
- **SSG:** Hugo (Go-based, zero Node.js dependency)
- **Styling:** Tailwind CSS (CDN) + custom CSS (`static/css/main.css`)
- **Icons:** Bootstrap Icons v1.11.3 (CDN)
- **JS:** Vanilla JS (`static/js/main.js`) — scroll-reveal, mobile nav, FAQ accordion, OS detection, form
- **Hosting:** Cloudflare Pages (free tier)

## Always Do First

1. **Read `BRAND.md`** before any visual or styling changes — it defines the exact design system
2. **Read this file** for architecture, workflow, and rules
3. **Never speculate** — read the actual template/partial before modifying

## Architecture

```
valoryx-hugo/
├── hugo.toml                    — Site config, Tailwind config, i18n settings
├── content/
│   ├── en/                      — English content (root URL /)
│   │   ├── _index.md            — Homepage
│   │   ├── blog/                — Blog articles (4 posts)
│   │   └── docs/                — Documentation (22 pages)
│   ├── fr/ de/ es/ ru/ uk/      — Translated content (same structure)
├── i18n/
│   ├── en.toml ... uk.toml      — UI string translations (6 files)
├── layouts/
│   ├── index.html               — Homepage (assembles 11 section partials)
│   ├── _default/baseof.html     — Base template (head, nav, main, footer)
│   ├── blog/
│   │   ├── list.html            — Blog listing
│   │   └── single.html          — Blog article (reading progress, sidebar, prev/next)
│   ├── docs/
│   │   ├── list.html            — Docs index with sidebar
│   │   └── single.html          — Docs page with sidebar
│   └── partials/
│       ├── head.html            — SEO meta, fonts, Tailwind config, CSS
│       ├── header.html          — Fixed nav, logo, language switcher, mobile menu
│       ├── footer.html          — 4-column footer + copyright bar
│       ├── docs/sidebar.html    — Docs navigation tree
│       └── sections/            — 11 homepage section partials
│           ├── hero.html
│           ├── download.html    — OS-detection tabs, terminal, download links
│           ├── about.html
│           ├── stats.html
│           ├── features.html    — 6 service cards with colored SVG blobs
│           ├── cta.html
│           ├── comparison.html  — Feature matrix table
│           ├── pricing.html     — 3-tier pricing cards
│           ├── domains.html     — .org vs .dev domain strategy
│           ├── faq.html         — 6-item accordion
│           └── contact.html     — Contact form + info
├── static/
│   ├── css/main.css             — Design system CSS (custom properties + components)
│   ├── js/main.js               — All interactivity (scroll-reveal, nav, FAQ, form, tabs)
│   ├── favicon.svg
│   ├── hero-bg.jpg              — Low-poly geometric hero background
│   ├── install.sh               — Linux/macOS installer script
│   └── _headers                 — Cloudflare security + cache headers
│   └── _redirects               — URL redirects
├── BRAND.md                     — Complete design system reference
└── CLAUDE.md                    — This file
```

## i18n — 6 Languages

| Language | Code | Content Dir | URL | Weight |
|----------|------|-------------|-----|--------|
| English | `en` | `content/en` | `/` (root) | 1 |
| French | `fr` | `content/fr` | `/fr/` | 2 |
| German | `de` | `content/de` | `/de/` | 3 |
| Spanish | `es` | `content/es` | `/es/` | 4 |
| Russian | `ru` | `content/ru` | `/ru/` | 5 |
| **Ukrainian** | **`uk`** | `content/uk` | `/uk/` | 6 |

**CRITICAL:** Ukrainian BCP 47 code is `uk` — never `ua`.

- English at root (no `/en/` prefix): `defaultContentLanguageInSubdir = false`
- UI strings: `i18n/{en,fr,de,es,ru,uk}.toml`
- Templates use `{{ i18n "key" }}` for translated strings
- Language switcher: dropdown in header with hover reveal

## Design Rules

See `BRAND.md` for the full design system. Key constraints:

### Theme: Light (always)
White backgrounds (`#ffffff`) with alternating light sections (`#f6fafd`). Professional, clean. Hero uses `hero-bg.jpg` with white overlay — NOT a dark gradient.

### 3 Standard Colors — never deviate
- **Heading:** `#124265` — all titles, table headers, nav logo, card titles
- **Accent:** `#1d7fc2` — buttons, links, icons, highlights, stats, CTA backgrounds
- **Navy:** `#0c1e2e` — hero bg, header CTA button, dark accents

### 3 Fonts — no others
- **Headings/UI:** Plus Jakarta Sans (700-800)
- **Body:** DM Sans (300-500), line-height 1.7
- **Code:** JetBrains Mono (400-500)

### Frontend Design Rules
- **Shadows:** Layered, color-tinted, low opacity. Never flat `shadow-md`.
- **Animations:** Only `transform` and `opacity`. Never `transition-all`. Use `0.65s ease` for scroll-reveal, `0.3s ease` for hover transitions.
- **Interactive states:** Every clickable element needs hover, focus-visible, and active states.
- **Spacing:** `py-20 md:py-28` for sections, `max-w-7xl px-4 sm:px-6 lg:px-8` for containers.
- **Section titles:** Centered, uppercase h2, accent underline bar (48px wide, 3px tall).

### Hard Rules
1. NEVER add features/pages/sections not explicitly requested
2. NEVER introduce new fonts or colors outside the brand palette
3. Docs pages are generated by the DocPlatform product — do not create them manually
4. Blog content lives in `content/{lang}/blog/` as Hugo markdown
5. Mobile-first responsive (Tailwind breakpoints: sm, md, lg)

## Local Development

```bash
# Serve with live reload
hugo server --port 1313

# Build for production
hugo --minify

# Output goes to public/ (gitignored)
```

Hugo binary location: system PATH or `C:/Users/apmin/AppData/Local/Microsoft/WinGet/Packages/Hugo.Hugo.Extended_.../hugo.exe`

## Deployment

- **Platform:** Cloudflare Pages (auto-deploys on git push)
- **Build command:** `hugo --minify`
- **Output directory:** `public`
- **Base URL:** `https://valoryx.org/`
- **Security headers:** Configured in `static/_headers` (X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Cache-Control)
- **Redirects:** `static/_redirects`

## Content Tone

- **Developer-first:** Technical precision, no marketing fluff
- **Problem-first:** Lead with pain points, then show solution
- **Honest:** Don't oversell. Features not yet available are labeled accordingly
- **Concise:** Every word earns its place

## SEO (implemented)

### Current (all languages)
- [x] Dynamic `<title>` and `<meta description>` per language
- [x] hreflang tags (bidirectional, self-referencing, x-default → EN root)
- [x] Canonical tags on every page
- [x] Open Graph + Twitter Card tags
- [x] JSON-LD structured data (SoftwareApplication, BlogPosting)
- [x] Semantic HTML (header, main, section, footer, nav)
- [x] Proper heading hierarchy (h1 → h2 → h3 → h4)
- [x] ARIA labels on interactive elements
- [x] Auto-generated sitemap.xml

### SEO Rules (mandatory for all changes)
1. **hreflang** on every page — bidirectional, self-referencing, x-default to EN
2. **Canonical** on every page — `{{ .Permalink }}`
3. **BCP 47 codes** — `en`, `fr`, `de`, `es`, `ru`, `uk` (never `ua`)
4. **Taxonomy pages** need `_index.{lang}.md` per language
5. **No JS/IP-based redirects** to language — hides content from Googlebot
6. **Subdirectory i18n** — consolidates SEO authority under one domain

## Product Context

For product decisions, pricing, domain strategy, and competitive positioning, see `C:\Valoryx\.workspace\DECISIONS.md` (private repo, not committed here).
