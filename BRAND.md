# Valoryx Brand Book & Design System

Canonical reference for all Valoryx ecosystem visual identity. Every color, font, shadow, and component spec is extracted from the **live production site** at `https://valoryx.org/` (Hugo SSG, Tailwind CDN, vanilla JS). All Valoryx properties (site, docs, dashboards, marketing assets) must follow this guide.

---

## 3 Core Brand Colors (non-negotiable)

| Role | Hex | CSS Var | Tailwind | Usage |
|------|-----|---------|----------|-------|
| **Heading** | `#124265` | `--heading` | `text-heading` | All titles h1-h6, table headers, nav logo, card titles |
| **Accent** | `#1d7fc2` | `--accent` | `text-accent` / `bg-accent` | Buttons, links, icons, highlights, stats numbers, CTA |
| **Navy** | `#0c1e2e` | `--navy` | `bg-navy` | Hero BG overlay, dark buttons, header CTA, footer accents |

### Full Palette

```css
:root {
  /* Brand core */
  --heading:     #124265;
  --accent:      #1d7fc2;
  --accent-dark: #155d91;   /* hover/pressed state */
  --accent-glow: rgba(29,127,194,0.35);
  --navy:        #0c1e2e;
  --navy-light:  #122d42;   /* hover on dark buttons */
  --navy-deep:   #080f18;

  /* Text */
  --body:        #444444;
  --muted:       #6b7b8d;   /* subtitles, captions, secondary */

  /* Surfaces */
  --light:       #f6fafd;   /* alternating section bg tint */
  --border:      #e2e8f0;

  /* Status */
  --success:     #059652;
  --danger:      #df1529;
}
```

### Feature Card Accent Colors (inline, not CSS vars)

| Variant | Hex | Class |
|---------|-----|-------|
| Cyan | `#0dcaf0` | `.item-cyan` |
| Orange | `#fd7e14` | `.item-orange` |
| Teal | `#20c997` | `.item-teal` |
| Red | `#df1529` | `.item-red` |
| Indigo | `#6610f2` | `.item-indigo` |
| Pink | `#f3268c` | `.item-pink` |

### Terminal Block Colors

```css
--terminal-bg:      #0d1117;
--terminal-bar:     #161b22;
--terminal-text:    #c9d1d9;
--terminal-prompt:  #58a6ff;
--terminal-cmd:     #e6edf3;
--terminal-comment: #484f58;
--terminal-success: #3fb950;
/* Traffic-light dots: #ff5f57, #febc2e, #28c840 */
```

### Table Colors

```
Header bg:        var(--heading)     white text
Valoryx col head: var(--accent)      white text
Valoryx col body: rgba(29,127,194,0.06)
Alt row:          #f8fbfe
Hover row:        #edf4fa
Check:            var(--success)     (#059652)
Cross:            #d1d5db
Partial:          #f59e0b            (amber)
```

### Tailwind Config

```js
tailwind.config = {
  theme: {
    extend: {
      colors: {
        heading: '#124265',
        accent: { DEFAULT: '#1d7fc2', light: '#3a9be0', dark: '#155d91', glow: 'rgba(29,127,194,0.35)' },
        body: '#444444',
        muted: '#6b7b8d',
        light: '#f6fafd',
        surface: '#ffffff',
        success: '#059652',
        danger: '#df1529',
        border: '#e2e8f0',
        navy: { DEFAULT: '#0c1e2e', light: '#122d42', deep: '#080f18' },
      },
      fontFamily: {
        heading: ['"Plus Jakarta Sans"', 'sans-serif'],
        body: ['"DM Sans"', 'system-ui', 'sans-serif'],
        nav: ['"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
}
```

---

## Typography — 3 Fonts Only

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Headings h1-h6, nav, UI labels | Plus Jakarta Sans | 400-800 | Titles, buttons, badges, pricing |
| Body copy | DM Sans | 300-700 | Paragraphs, lists, form inputs |
| Code / Terminal | JetBrains Mono | 400-500 | Terminal blocks, inline code, CLI |

**Never use:** Raleway, Roboto, Poppins — removed in design refresh, do not re-introduce.

### Google Fonts Import

```
Plus+Jakarta+Sans:wght@400;500;600;700;800
DM+Sans:wght@300;400;500;600;700
JetBrains+Mono:wght@400;500
```

### Type Scale

| Element | Size | Weight | Line-height | Extras |
|---------|------|--------|-------------|--------|
| Hero h1 | text-3xl → sm:4xl → md:5xl → lg:6xl | 800 (extrabold) | tight (1.15) | letter-spacing -0.04em |
| Section h2 | 32px (mobile: 24px) | 700 | — | uppercase, letter-spacing 0.04em (mobile: 0.02em) |
| Card h3 | 22px | 700 | — | |
| Card h4 / Icon box h4 | 18px | 700 | — | |
| Stats number | 48px | 800 | 1 | letter-spacing -0.04em, Plus Jakarta Sans |
| Body | 15px | 400 | 1.7 | DM Sans |
| Small / caption | 13-14px | — | — | |
| Nav links | 13px | 500 | — | Plus Jakarta Sans |
| Footer headings | 12px | 700 | — | uppercase, letter-spacing 0.1em |
| Price h4 | 48px | 800 | 1 | letter-spacing -0.04em |

### Section Title Pattern (`.section-title`)

```css
.section-title h2 {
  font-size: 32px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--heading);
  padding-bottom: 18px;
  margin-bottom: 12px;
  position: relative;
}
.section-title h2::after {
  content: '';
  width: 48px;
  height: 3px;
  background: var(--accent);
  display: block;
  margin: 18px auto 0;
  border-radius: 2px;
}
.section-title p {
  font-size: 15px;
  color: var(--muted);
  line-height: 1.7;
  max-width: 520px;
  margin: 0 auto;
}
```

---

## Section Backgrounds — Alternating Pattern

```
#download   → var(--light)  #f6fafd
#about      → #ffffff
#stats      → var(--light)
#features   → #ffffff
#comparison → var(--light)
#pricing    → #ffffff
#domains    → var(--light)
#faq        → #ffffff
#contact    → var(--light)
```

Section padding: `py-20 md:py-28`

---

## Hero

- Background: `hero-bg.jpg` (low-poly geometric polygon mesh) at `center center / cover`
- Overlay: `rgba(255,255,255,0.55)` via `::after`
- Min-height: `90vh`, flex centered
- Content: badge pill → h1 → subtitle → CTA button → terminal mockup → 4 icon boxes
- Badge: `rgba(29,127,194,0.08)` bg, accent text, text-xs font-semibold, rounded-full, px-4 py-1.5
- CTA button: `bg-accent text-white px-8 py-3 rounded-lg font-semibold` + `.btn-glow`

---

## Components

### Icon Boxes (hero feature cards)
- White bg, `box-shadow: 0 0 29px 0 rgba(0,0,0,0.1)`, `border-radius: 8px`
- Padding: 50px 30px (mobile: 36px 20px), height: 100%
- Border-bottom: 3px solid transparent → accent on hover
- Hover: `scale(1.08)`, shadow `0 8px 40px rgba(0,0,0,0.14)`
- Icon: 36px, `var(--accent)`, Bootstrap Icons, margin-bottom 20px
- h4: 18px / 700 / `var(--heading)`
- p: 14px / 1.7 / `rgba(68,68,68,0.65)`

### Feature Service Cards
- White bg, `box-shadow: 0px 5px 90px 0px rgba(0,0,0,0.1)`, `border-radius: 5px`
- Padding: 60px 30px, centered, height 100%
- Border-bottom: 3px solid transparent → card accent color on hover
- Hover: shadow `0px 8px 40px rgba(0,0,0,0.16)`, `translateY(-5px)`
- Icon: 100x100px container with organic SVG blob behind Bootstrap Icon (36px)
- Blob default fill: `rgba(68,68,68,0.05)` → on hover fills with card accent color, icon turns white
- h3: 22px / 700, p: 14px / 1.7 / `var(--muted)`

### Pricing Cards
- Padding: 60px 40px, `box-shadow: 0 3px 20px -2px rgba(0,0,0,0.08)`, `border-radius: 5px`
- `border: 1px solid #e8ecf0`, hover: `translateY(-5px)`, shadow `0 8px 30px -2px rgba(0,0,0,0.14)`
- Price h4: 48px / `var(--accent)` / 800 / letter-spacing -0.04em
- Plan badge: `bg-accent text-white`, 10px, 700, uppercase, tracking 0.1em, rounded-full
- Buy button: `border 1px solid rgba(68,68,68,0.35)`, 15px, 600, Plus Jakarta Sans
- Buy hover: `bg-accent border-accent text-white`
- **Featured card:** `border: 2px solid var(--accent)`, shadow `0 3px 30px -2px rgba(29,127,194,0.22)`, `scale(1.02)` (removed on mobile)
- Featured button: pre-filled `bg-accent text-white`, hover `bg-accent-dark`

### Comparison Table
- Header: `background: var(--heading)` / white text / Plus Jakarta Sans 600 / 13px
- Valoryx header: `background: var(--accent)`
- Body: `border: 1px solid #e8ecf0`, even rows `#f8fbfe`, hover `#edf4fa`
- Check: `var(--success)` / Cross: `#d1d5db` / Partial: `#f59e0b`
- Valoryx column: `background: rgba(29,127,194,0.06)`, font-weight 700

### FAQ Accordion
- Default: white bg, `border: 1px solid rgba(68,68,68,0.15)`, `border-radius: 5px`
- Padding: 20px 24px, cursor pointer
- Hover: border → `rgba(29,127,194,0.4)`
- **Active:** `background: var(--accent)`, white text, `box-shadow: 0 5px 25px rgba(29,127,194,0.28)`
- Expand: CSS `grid-template-rows` transition (0fr → 1fr, 0.35s ease)
- Toggle chevron: rotates 90deg when active
- Number prefix: `var(--accent)`, active `rgba(255,255,255,0.7)`

### Terminal Block
- Background: `#0d1117`, border-radius 8px, font-family JetBrains Mono 13px / line-height 1.9
- Bar: `#161b22`, padding 12px 16px
- Shadow: `0 4px 8px rgba(0,0,0,0.12), 0 16px 48px rgba(0,0,0,0.2)`
- Border: `1px solid rgba(255,255,255,0.06)`
- Dots: `#ff5f57` / `#febc2e` / `#28c840` (12px circles)

### CTA Section
- Background: `var(--accent)`, padding 80px 0, color #fff
- h3: 28px / 700, p: 16px / 1.7 / `rgba(255,255,255,0.85)`
- Buttons: `border 2px solid rgba(255,255,255,0.6)`, 16px / 600, padding 12px 40px
- Hover: `background #fff`, `color var(--accent)`, `border-color #fff`

### Buttons
- **Primary (CTA):** `bg-accent text-white px-8 py-3 rounded-lg font-semibold` + `.btn-glow`
- **Header CTA:** `bg-navy text-white px-5 py-2 rounded-lg text-[13px] font-semibold`
- **Header CTA hover:** `bg-navy-light`, active `scale(0.97)`, spring easing `cubic-bezier(0.34,1.56,0.64,1)`
- **Secondary:** `border border-border text-heading` hover `border-accent text-accent`
- **`.btn-glow`:** `::after` with `box-shadow: 0 0 28px rgba(29,127,194,0.4)`, opacity 0 → 1 on hover

### Contact Form
- Input: `border: 1px solid var(--border)`, padding 13px 18px, radius 5px, font DM Sans 15px
- Focus: `border-color: var(--accent)`, `box-shadow: 0 0 0 3px rgba(29,127,194,0.12)`
- Submit: `bg-accent text-white`, padding 13px 48px, 15px / 700, Plus Jakarta Sans
- Submit hover: `bg-accent-dark`, `translateY(-2px)`

### Blog Cards
- `border: 1px solid #e8ecf0`, radius 8px, padding 28px 32px
- `border-left: 4px solid transparent` → accent on hover
- Hover: shadow `0 4px 28px rgba(29,127,194,0.1)`, `translateX(4px)`

---

## Navigation / Header

- Fixed top, z-50, `bg-white/90` + `backdrop-blur-md`
- Height: h-16 (mobile) / h-[68px] (desktop)
- Border-bottom: transparent → `#e8ecf0` on scroll (>50px)
- Background on scroll: `rgba(255,255,255,0.9)` → `rgba(255,255,255,0.95)`
- Logo: Plus Jakarta Sans 22px extrabold, letter-spacing -0.04em, navy box icon (8x8 rounded-lg)
- Nav links: 13px / 500 / `text-body/80` → hover `text-heading`
- Language switcher: dropdown on hover, absolute positioned, shadow-lg, 150ms transition
- Mobile: overlay `rgba(8,15,24,0.6)` + backdrop-blur(4px), panel slides from right 300px wide

---

## Footer

- White bg, `border-top: 1px solid #e8ecf0`, padding pt-14
- 4-column grid (lg), 2-col (sm), 1-col (mobile), gap-10
- Headings: 12px / 700 / uppercase / letter-spacing 0.1em / `var(--heading)`
- Links: 14px / `#6b7b8d` → hover `var(--accent)`
- Logo: 26px / font-light / `var(--heading)`
- **Copyright bar:** `background: var(--accent)`, white text, py-5, text-sm, centered
- Copyright links: `rgba(255,255,255,0.6)` → hover `#fff`

---

## Scroll Animations

```css
.will-reveal {
  opacity: 0;
  transform: translateY(22px);
  transition: opacity 0.65s ease, transform 0.65s ease;
}
.will-reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
/* Staggered delays: 0.08s increments */
.reveal-delay-1 { transition-delay: 0.08s; }
.reveal-delay-2 { transition-delay: 0.16s; }
.reveal-delay-3 { transition-delay: 0.24s; }
.reveal-delay-4 { transition-delay: 0.32s; }
.reveal-delay-5 { transition-delay: 0.40s; }
```

JS: IntersectionObserver (threshold 0.08, rootMargin '0px 0px -30px 0px') adds `.visible`.

---

## Article/Blog Typography (`.article-body`)

```css
h2: 26px / 700, margin 48px 0 16px, border-bottom 2px solid #f0f4f8, padding-bottom 12px
h3: 21px / 700, margin 36px 0 12px
h4: 17px / 700, margin 28px 0 8px
p:  16px / line-height 1.85, color #333, margin-bottom 18px
blockquote: border-left 4px solid var(--accent), bg rgba(29,127,194,0.04), radius 0 6px 6px 0
code (inline): JetBrains Mono 13px, bg #f3f7fb, color var(--accent), border 1px solid #dde5ed
pre: bg #0d1117, radius 8px, padding 20px 24px
```

---

## Global CSS

```css
html { scroll-behavior: smooth; }
* { box-sizing: border-box; }
body { font-family: 'DM Sans'; font-size: 15px; line-height: 1.7; color: var(--body); -webkit-font-smoothing: antialiased; }
h1,h2,h3,h4,h5,h6 { font-family: 'Plus Jakarta Sans'; color: var(--heading); }
a { color: var(--accent); text-decoration: none; transition: color 0.2s ease; }
::selection { background: rgba(29,127,194,0.15); color: var(--heading); }
```

---

## Icon Library

Bootstrap Icons v1.11.3 (CDN)

---

## Rules

1. **3 standard colors only** — `#124265`, `#1d7fc2`, `#0c1e2e`. Feature card accents are the only exception.
2. **3 fonts only** — Plus Jakarta Sans, DM Sans, JetBrains Mono. No Raleway, Roboto, Poppins.
3. **Light theme** — white/light backgrounds. NOT dark theme. Hero uses image overlay, not dark gradient.
4. **Never add features/pages/sections** not explicitly asked for.
5. **Docs pages** are generated by the DocPlatform product — do not create them manually.
6. **All interactive elements** need hover, focus-visible, and active states.
7. **Shadows** — layered, color-tinted, low opacity. Never flat `shadow-md`.
8. **Animations** — only `transform` and `opacity`. Never `transition-all`. Spring-style easing on buttons.
9. **Consistent spacing** — section padding `py-20 md:py-28`, container `max-w-7xl px-4 sm:px-6 lg:px-8`.
