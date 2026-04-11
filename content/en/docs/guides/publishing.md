---
title: Publishing Docs
description: Publish your documentation as a beautiful site with syntax highlighting, SEO support, and per-workspace access control.
weight: 5
---

# Publishing Docs

DocPlatform can serve your documentation as a website — complete with a navigation sidebar, syntax highlighting, and SEO metadata. No separate static site generator required. By default, published docs are visible only to authenticated workspace members. Admins can opt in to make them fully public.

## How publishing works

Published docs are served at `/p/{workspace-slug}/{page-path}`:

```
http://localhost:3000/p/my-docs/              → docs/index.md
http://localhost:3000/p/my-docs/quickstart    → docs/quickstart.md
http://localhost:3000/p/my-docs/api/auth      → docs/api/auth.md
```

Pages are rendered from Markdown to HTML on request using goldmark (CommonMark-compliant) with Chroma syntax highlighting (Dracula theme) for code blocks.

### Page status lifecycle

Pages have a `status` field that controls their visibility:

| Status | In editor | In published site | In search |
|---|---|---|---|
| `draft` (default) | Visible | Hidden | Visible to members only |
| `published` | Visible | Visible | Visible per access rules |
| `archived` | Visible (dimmed) | Hidden | Hidden |

Set the status in frontmatter:

```yaml
---
title: My Page
status: published    # draft, published, or archived
publish: true        # shorthand — equivalent to status: published
---
```

The `publish: true` shorthand and `status: published` are equivalent. Use whichever you prefer.

## Enable publishing

### Per-page

Set `published: true` in the page's frontmatter:

```yaml
---
title: API Authentication
description: How to authenticate with the API.
published: true
---
```

Or toggle the **Published** switch in the frontmatter form of the web editor.

### Workspace-level default

Set a workspace-level default so new pages are published automatically:

```yaml
# .docplatform/config.yaml
publishing:
  default_published: true
  require_explicit_unpublish: false
```

## Themes

DocPlatform ships with 7 built-in themes for published documentation:

| Theme | Description |
|---|---|
| **Default** | Clean light theme with blue accents |
| **Dark** | Dark background with high-contrast text |
| **Forest** | Green-toned natural palette |
| **Rose** | Warm pink and red accents |
| **Amber** | Warm amber and gold tones |
| **Minimal** | Stripped-down, typography-focused |
| **Corporate** | Professional blue/gray palette |

Set the theme in your workspace config:

```yaml
# .docplatform/config.yaml
theme:
  mode: auto    # light, dark, or auto (follows system preference)
  accent: blue  # or use a named theme
```

Each theme supports automatic light/dark mode switching based on the visitor's system preference when `mode: auto` is set.

## Published site features

### Navigation

The published site generates a sidebar navigation from your page hierarchy. The order matches the sidebar in the web editor.

To customize navigation order, adjust the `navigation` section in your workspace config:

```yaml
# .docplatform/config.yaml
navigation:
  - title: "Getting Started"
    path: "getting-started/index.md"
    children:
      - title: "Installation"
        path: "getting-started/installation.md"
      - title: "Quickstart"
        path: "getting-started/quickstart.md"
```

### Syntax highlighting

Code blocks are highlighted using **Chroma** (Dracula theme). Over 200 languages are supported.

Specify the language after the opening triple backticks:

````markdown
```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```
````

### SEO

DocPlatform generates SEO metadata automatically from your page frontmatter:

| Tag | Source |
|---|---|
| `<title>` | Frontmatter `title` |
| `<meta name="description">` | Frontmatter `description` |
| `<meta property="og:title">` | Frontmatter `title` |
| `<meta property="og:description">` | Frontmatter `description` |
| `<link rel="canonical">` | Generated from page path |
| `sitemap.xml` | Auto-generated at `/p/{slug}/sitemap.xml` |
| `robots.txt` | Auto-generated at `/p/{slug}/robots.txt` |
| RSS feed | Auto-generated at `/p/{slug}/rss.xml` |

### Access control

By default, published docs require **viewer authentication** — only logged-in workspace members can read them. This protects your documentation from accidental public exposure.

To make a workspace's published docs fully public (world-readable without login), a workspace admin must explicitly set the visibility to "public" in the workspace settings:

```
PUT /api/v1/workspaces/:id/admin/settings
{ "visibility": "public" }
```

| Visibility | Who can read | When to use |
|---|---|---|
| **authenticated** (default) | Logged-in workspace members only | Internal docs, client portals, team knowledge bases |
| **public** | Anyone with the URL | Open-source docs, product documentation, public guides |

When visibility is "authenticated":

- Visitors who are not logged in are redirected to `/#/login?next=<url>`
- After signing in, they are returned to the page they requested
- Any workspace member (any role, including Viewer) can read published pages
- Non-members are redirected away even after logging in
- Sitemaps, robots.txt, and RSS feeds are also protected

**Server-level override:** The `PUBLISH_REQUIRE_AUTH=true` environment variable forces authentication on **all** published sites, regardless of their per-workspace visibility setting. This is useful for fully private installations where no documentation should ever be public.

## Built-in components

Published docs support 15 custom components that render as rich, interactive elements. Here are the most commonly used ones (see [Markdown & Components](markdown.md) for the full list):

### Callout

```markdown
:::callout[info]
This is an informational callout.
:::

:::callout[warning]
Be careful with this operation.
:::

:::callout[danger]
This action is irreversible.
:::

:::callout[tip]
Pro tip: use keyboard shortcuts for faster editing.
:::
```

**Types:** `info`, `warning`, `danger`, `tip`, `note`

### Tabs

```markdown
:::tabs
::tab[npm]
npm install docplatform
::
::tab[yarn]
yarn add docplatform
::
::tab[pnpm]
pnpm add docplatform
::
:::
```

### Accordion

```markdown
:::accordion[How does sync work?]
DocPlatform uses a hybrid git engine that combines go-git for small repositories
with native git CLI for large ones. Changes are synced via polling or webhooks.
:::
```

### Cards

```markdown
:::cards
::card[Getting Started, link="/getting-started"]
Install and configure DocPlatform in under 10 minutes.
::
::card[User Guide, link="/guides/editor"]
Learn the web editor, git sync, and publishing features.
::
:::
```

### Steps

```markdown
:::steps
::step[Install]
Download the binary or pull the Docker image.
::
::step[Initialize]
Run `docplatform init` to create your workspace.
::
::step[Start]
Run `docplatform serve` and open the browser.
::
:::
```

### API Block

```markdown
:::api[GET /api/v1/content/{workspace}/{...path}]
Retrieve a single page by workspace and path.

**Parameters:**
- `workspace` (path, required) — Workspace slug
- `path` (path, required) — Page file path

**Response:** `200 OK`
```json
{
  "page_id": "01HJKL...",
  "title": "Getting Started",
  "content": "..."
}
```
:::
```

## Custom domains

DocPlatform supports per-workspace custom domains with automatic TLS provisioning via Caddy integration.

### Setup

1. **Configure Caddy** as your reverse proxy with the on-demand TLS ask endpoint:

```
{
    on_demand_tls {
        ask http://localhost:3000/internal/caddy/ask
    }
}

:443 {
    tls {
        on_demand
    }
    reverse_proxy localhost:3000
}
```

2. **Set environment variables:**

```bash
export BASE_DOMAIN=docs.yourcompany.com
export CADDY_ADMIN_URL=http://localhost:2019
export CADDY_ASK_SECRET=your-shared-secret
```

3. **Assign a custom domain** to a workspace via the API or admin UI:

```bash
curl -X PUT /api/v1/workspaces/{id}/custom-domain \
  -H "Authorization: Bearer ..." \
  -d '{"domain": "docs.yourcompany.com"}'
```

4. **Point DNS** — Add a CNAME or A record pointing to your DocPlatform server.

DocPlatform verifies DNS automatically and provisions TLS certificates on first request. No manual certificate management required.

### Managing custom domains

| Operation | Endpoint |
|---|---|
| Set domain | `PUT /api/v1/workspaces/:id/custom-domain` |
| Check status | `GET /api/v1/workspaces/:id/custom-domain` |
| Remove domain | `DELETE /api/v1/workspaces/:id/custom-domain` |

Super admins can manage all domains from the admin panel:

| Operation | Endpoint |
|---|---|
| List all domains | `GET /api/admin/domains` |
| Verify DNS | `POST /api/admin/domains/:id/verify` |
| Provision TLS | `POST /api/admin/domains/:id/provision` |
| Delete domain | `DELETE /api/admin/domains/:id` |

## Caching

Published pages are cached for performance:

| Header | Value | Description |
|---|---|---|
| `Cache-Control` | `public, max-age=300` | Browsers and CDNs cache for 5 minutes |
| `ETag` | Content hash | Enables conditional requests (304 Not Modified) |

The cache key is based on the page's content hash. When content changes, the ETag changes automatically and cached versions are invalidated.

### Asset URL rewriting

In the web editor, assets use relative paths (`assets/screenshot.png`). In published docs, these are automatically rewritten to absolute paths (`/p/{slug}/assets/screenshot.png`) so images and files load correctly at any URL depth.

## Static export

Export your published docs as a self-contained static HTML ZIP for CDN deployment or offline distribution.

### Via CLI

```bash
docplatform export --workspace my-docs --output ./my-docs-export.zip
```

### Via API

```
GET /api/v1/workspaces/{id}/export
```

Returns a ZIP file containing:

- Rendered HTML for all published pages
- `sitemap.xml` and `robots.txt`
- Sidebar navigation and CSS
- Ready to deploy to any static file host (Netlify, Vercel, S3, GitHub Pages)

## Preview before publishing

Preview published docs locally without building a static export:

```bash
docplatform preview --workspace my-docs --port 4000
```

This starts a lightweight local server that renders pages in real-time — useful for reviewing changes before deploying.

Pages with `published: false` are still accessible to authenticated workspace members at the `/p/` path — they're just excluded from the public navigation and sitemap.
