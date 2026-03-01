# Valoryx.org — Site Specification

Build specification for the Valoryx marketing + documentation site. Hugo SSG, Tailwind CDN, Cloudflare Pages. All design tokens reference `BRAND.md` as the single source of truth.

---

## Design System Summary

### Colors
See `BRAND.md` for the complete palette. 3 core colors: Heading `#124265`, Accent `#1d7fc2`, Navy `#0c1e2e`.

### Typography
3 fonts only: Plus Jakarta Sans (headings/UI), DM Sans (body), JetBrains Mono (code). See `BRAND.md` for the full type scale.

### Tailwind Config
Inline in `layouts/partials/head.html` via Tailwind CDN play script. Extended colors, fontFamily, and spacing. See `BRAND.md` for the exact config object.

### Shadows
```css
/* Icon boxes (hero) */
box-shadow: 0 0 29px 0 rgba(0,0,0,0.1);

/* Service cards (features) */
box-shadow: 0px 5px 90px 0px rgba(0,0,0,0.1);

/* Pricing cards */
box-shadow: 0 3px 20px -2px rgba(0,0,0,0.08);

/* Terminal block */
box-shadow: 0 4px 8px rgba(0,0,0,0.12), 0 16px 48px rgba(0,0,0,0.2);
```

---

## Page Sections (Top to Bottom)

### 1. Navigation Bar (Header)

**Layout:** Fixed top-0, z-50, `bg-white/90` + `backdrop-blur-md`
**Height:** h-16 (mobile) / h-[68px] (desktop)

**Content:**
- Left: Logo — navy box icon (8x8 rounded-lg) + "Valoryx" (Plus Jakarta Sans 22px extrabold, letter-spacing -0.04em)
- Center: Nav links — Download, About, Features, Compare, Pricing, FAQ, Blog, Docs (13px / 500 / `text-body/80`)
- Right: Language switcher (dropdown on hover) + "Download Free" button (`bg-navy text-white px-5 py-2 rounded-lg text-[13px] font-semibold`)

**Behavior:**
- Border-bottom appears on scroll (transparent → `#e8ecf0` at 50px)
- Background transitions: `rgba(255,255,255,0.9)` → `rgba(255,255,255,0.95)` on scroll
- Mobile: hamburger → overlay (`rgba(8,15,24,0.6)` + backdrop-blur) + slide-in panel (300px from right)
- Active nav link (docs/blog): `text-accent font-semibold`

---

### 2. Hero Section

**Background:** `hero-bg.jpg` (low-poly geometric polygon mesh), `center center / cover`, white overlay `rgba(255,255,255,0.55)` via `::after`
**Min-height:** 90vh, flex centered
**Padding:** pt-20, py-20 md:py-28

**Content (centered):**
1. **Badge pill:** `rgba(29,127,194,0.08)` bg, accent text, text-xs, font-semibold, rounded-full, px-4 py-1.5
2. **h1:** text-3xl → sm:4xl → md:5xl → lg:6xl, extrabold, leading-tight, `var(--heading)`
3. **Subtitle:** text-base sm:lg, `var(--muted)`, line-height 1.8, max-w-2xl centered
4. **CTA button:** `bg-accent text-white px-8 py-3 rounded-lg font-semibold` + `.btn-glow`
5. **Terminal mockup:** Dark terminal block with install commands (see Terminal Block in `BRAND.md`)
6. **4 Icon boxes:** Grid 1→2→4 columns, white cards with shadows

---

### 3. Download / Get Started Section

**ID:** `#download`
**Background:** `var(--light)` (#f6fafd)
**Padding:** py-20 md:py-28

**Content:**
- Section title (centered, uppercase h2 + accent underline)
- OS tab switcher (auto-detects Windows/macOS/Linux/Docker)
- Tab container: `bg-[#f0f4f8]`, rounded-xl, p-1.5
- Active tab: white bg, accent text, shadow
- Terminal block with platform-specific install commands
- Download buttons linking to GitHub Releases (`Valoryx-org/releases`)
- Architecture variants: amd64, arm64, Apple Silicon, Intel

---

### 4. About Section

**ID:** `#about`
**Background:** White (#ffffff)
**Padding:** py-20 md:py-28

**Layout:** Section title + 2-column (md:grid-cols-2 gap-12)
- Left: Description + 3 bullet points with success-colored check icons
- Right: Description + "Explore Features" CTA link (accent)

---

### 5. Stats Section

**ID:** `#stats`
**Background:** `var(--light)` (#f6fafd)
**Padding:** py-16 md:py-20

**Layout:** Grid 2→4 columns
- Number: 48px / 800 / accent / Plus Jakarta Sans / letter-spacing -0.04em
- Label: 13px / 600 / muted / uppercase / letter-spacing 0.07em
- Stats: "1 Single Binary" | "<30s Install Time" | "100% Git-Native" | "$0 Free Forever"

---

### 6. Features Section

**ID:** `#features`
**Background:** White (#ffffff)
**Padding:** py-20 md:py-28

**Layout:** Section title + Grid 1→2→3 columns, gap-7

6 service cards with colored SVG blob icons:

| Color | Class | Icon | Title |
|-------|-------|------|-------|
| Cyan #0dcaf0 | `.item-cyan` | bi-journal-check | Content Ledger |
| Orange #fd7e14 | `.item-orange` | bi-git | Git Sync |
| Teal #20c997 | `.item-teal` | bi-pencil-square | WYSIWYG Editor |
| Red #df1529 | `.item-red` | bi-globe2 | Published Docs |
| Indigo #6610f2 | `.item-indigo` | bi-search | Full-Text Search |
| Pink #f3268c | `.item-pink` | bi-shield-lock | Access Control |

Hover: card `translateY(-5px)`, icon blob fills with card color, icon turns white, border-bottom matches card color.

---

### 7. Call to Action

**Background:** `var(--accent)` (#1d7fc2), padding 80px 0, color white
**Content:** Headline h3 (28px/700) + subtitle + outline buttons
**Buttons:** `border 2px solid rgba(255,255,255,0.6)` → hover: white bg, accent text

---

### 8. Comparison Table

**ID:** `#comparison`
**Background:** `var(--light)` (#f6fafd)
**Padding:** py-20 md:py-28

**Layout:** Full-width responsive table (overflow-x auto, min-width 580px)
- Valoryx vs Notion vs GitBook vs Confluence vs Wiki.js on key features
- Header: `bg-heading` (white text), Valoryx column `bg-accent`
- Valoryx body column: light blue highlight `rgba(29,127,194,0.06)`, bold text
- Alt rows: `#f8fbfe`, hover: `#edf4fa`
- Check: green `var(--success)`, Cross: gray `#d1d5db`, Partial: amber `#f59e0b`

---

### 9. Pricing Section

**ID:** `#pricing`
**Background:** White (#ffffff)
**Padding:** py-20 md:py-28

**Layout:** Grid 1→3 columns, items-stretch

3 tiers:

| Plan | Price | Featured |
|------|-------|----------|
| Community | $0 | No |
| Team | $29/mo | Yes (accent border, scale 1.02, stronger shadow) |
| Business | $79/mo | No |

- Plan badge: `bg-accent text-white`, 10px uppercase, rounded-full
- Price: 48px / 800 / accent / letter-spacing -0.04em
- Feature list: check (success) or cross (#d1d5db), `.na` items dimmed
- Buy button: outlined → hover fills accent. Featured: pre-filled accent → hover accent-dark.
- Featured card: `border: 2px solid var(--accent)`, `scale(1.02)` (desktop only)

---

### 10. Domains Section

**ID:** `#domains`
**Background:** `var(--light)` (#f6fafd)
**Padding:** py-20 md:py-28

**Layout:** Grid 1→2 columns, gap-8
- Two domain cards (`.org` and `.dev`) with logo boxes, status badges, feature lists
- `.org` badge: success green bg/text (LIVE)
- `.dev` badge: accent blue bg/text (COMING SOON)
- CTA link: accent, inline-flex with arrow icon

---

### 11. FAQ Section

**ID:** `#faq`
**Background:** White (#ffffff)
**Padding:** py-20 md:py-28

**Layout:** Max-w-3xl centered, 6 accordion items
- Default: white bg, `border 1px solid rgba(68,68,68,0.15)`, radius 5px
- Hover: border `rgba(29,127,194,0.4)`
- **Active:** `bg-accent`, white text, glow shadow `0 5px 25px rgba(29,127,194,0.28)`
- Expand: CSS `grid-template-rows` (0fr → 1fr, 0.35s ease)
- Only one open at a time (JS toggle)

---

### 12. Contact Section

**ID:** `#contact`
**Background:** `var(--light)` (#f6fafd)
**Padding:** py-20 md:py-28

**Layout:** Grid 1→2 columns (md:grid-cols-5, left 2/5, right 3/5)
- Left: 4 contact items (email, GitHub, Discord, Twitter) with accent icon boxes
- Right: Name, email, role, message form + submit button
- Form validation: client-side email regex
- Submission: webhook POST to n8n
- Button states: loading "…", success checkmark (green), error "✕" (red), reset after 3s

---

### 13. Footer

**Background:** White, `border-top: 1px solid #e8ecf0`
**Padding:** pt-14

**Layout:** Grid 1→2→4 columns, gap-10, pb-12
- Column 1: Logo (26px font-light) + about text + social links (Twitter, LinkedIn)
- Column 2: Quick Links
- Column 3: Documentation links
- Column 4: Resources links

**Copyright bar:** `bg-accent`, white text, py-5, text-sm, centered
- Links: `rgba(255,255,255,0.6)` → hover white

---

### 14. Blog

**URL:** `/{lang}/blog/` (listing) and `/{lang}/blog/{slug}/` (article)
**Built by:** Hugo from `content/{lang}/blog/*.md`

**Blog Listing:**
- Section title with accent underline
- Stacked cards (`.blog-card`): 1px border, 8px radius, 28px 32px padding
- Left border: 4px transparent → accent on hover, `translateX(4px)`
- Card: date + reading time, title (h2 text-xl bold heading), description, tags
- JSON-LD Blog schema

**Blog Article:**
- Reading progress bar: fixed top, 3px tall, accent color, JS-driven width
- Header: title (h1 text-3xl+ bold), meta (date, reading time, tags), on light bg
- Sidebar: table of contents + related posts
- Body: `.article-body` typography (see `BRAND.md`)
- Previous/Next navigation
- Full SEO: BlogPosting JSON-LD, OG article tags, canonical

---

### 15. Documentation

**URL:** `/{lang}/docs/` and sub-sections
**Built by:** Hugo from `content/{lang}/docs/` (22 pages per language)
**Source:** Content authored in `Valoryx-org/docplatform-docs` repo, synced via DocPlatform git sync

**Docs Layout:**
- Header: gradient navy (`bg-gradient-to-br from-navy via-navy-light to-navy`) with title, breadcrumb
- Sidebar: `lg:w-64 sticky top-20`, collapsible sections, active page highlighted
- Content: `.article-body` typography, max-w-none
- Section headings: 12px uppercase tracked, accent-colored active state
- Active page: `rgba(29,127,194,0.06)` bg, font-semibold

---

## Technical Requirements

### Performance
- Lighthouse Performance: 90+
- First Contentful Paint: <1.5s
- Fonts: loaded async via Google Fonts `display=swap`
- Tailwind: CDN play script (async)
- Total page weight: <500KB (no frameworks, no bundling)
- Images: lazy-loaded where applicable

### Accessibility
- Lighthouse Accessibility: 95+
- All interactive elements keyboard-navigable
- ARIA labels on icon-only buttons
- Semantic HTML (header, main, section, footer, nav)
- WCAG AA color contrast
- Reduced motion preference: respect `prefers-reduced-motion`

### SEO
- hreflang tags (bidirectional, self-referencing, x-default → EN)
- Canonical tags on every page
- JSON-LD: SoftwareApplication (homepage), BlogPosting (articles), FAQPage (FAQ section)
- Open Graph + Twitter Card meta
- Auto-generated sitemap.xml
- Semantic heading hierarchy (h1 → h2 → h3 → h4)
- BCP 47 language codes (`uk` not `ua`)

---

## File Reference

```
hugo.toml                           — Site config, i18n, Tailwind
layouts/index.html                  — Homepage (11 section partials)
layouts/_default/baseof.html        — Base template
layouts/partials/head.html          — Meta, fonts, Tailwind config
layouts/partials/header.html        — Navigation
layouts/partials/footer.html        — Footer
layouts/partials/sections/*.html    — 11 homepage sections
layouts/blog/{list,single}.html     — Blog templates
layouts/docs/{list,single}.html     — Docs templates
layouts/partials/docs/sidebar.html  — Docs sidebar nav
static/css/main.css                 — Design system CSS
static/js/main.js                   — All JS interactions
static/hero-bg.jpg                  — Hero background image
static/favicon.svg                  — Favicon
static/install.sh                   — Linux/macOS installer
static/_headers                     — Cloudflare security headers
static/_redirects                   — URL redirects
content/{en,fr,de,es,ru,uk}/        — Markdown content per language
i18n/{en,fr,de,es,ru,uk}.toml       — UI string translations
BRAND.md                            — Design system (source of truth)
CLAUDE.md                           — System prompt (architecture + rules)
```
