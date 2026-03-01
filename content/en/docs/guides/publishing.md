---
title: Publishing Docs
description: Publish your documentation as a beautiful public site with syntax highlighting, SEO support, and optional team-only access.
weight: 5
---

# Publishing Docs

DocPlatform can serve your documentation as a public website — complete with a navigation sidebar, syntax highlighting, and SEO metadata. No separate static site generator required.

## How publishing works

Published docs are served at `/p/{workspace-slug}/{page-path}`:

```
http://localhost:3000/p/my-docs/              → docs/index.md
http://localhost:3000/p/my-docs/quickstart    → docs/quickstart.md
http://localhost:3000/p/my-docs/api/auth      → docs/api/auth.md
```

Pages are rendered from Markdown to HTML on request using goldmark (CommonMark-compliant) with Chroma syntax highlighting for code blocks.

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

Code blocks are highlighted using **Chroma** (goldmark-highlighting, Dracula theme). Over 200 languages are supported.

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
| `sitemap.xml` | Auto-generated from all published pages |
| `robots.txt` | Auto-generated |

### Access control

By default, published docs are **public** — no login required. Anyone with the URL can view them.

To restrict your entire published site to workspace members only, set `PUBLISH_REQUIRE_AUTH`:

```bash
# .env
PUBLISH_REQUIRE_AUTH=true
```

When enabled:

- Visitors who are not logged in are redirected to `/#/login?next=<url>`
- After signing in, they are returned to the page they requested
- Any workspace member (any role) can view — even Viewers
- Non-members who log in are still redirected away

Restart the server for this change to take effect. No rebuild required.

> **Per-page access control** (restricting individual pages to specific roles) is planned for a future release. In v0.5, access control is all-or-nothing at the site level via `PUBLISH_REQUIRE_AUTH`.

## Built-in components

Published docs support 7 custom components that render as rich, interactive elements:

### Callout

```markdown
:::callout{type="info"}
This is an informational callout.
:::

:::callout{type="warning"}
Be careful with this operation.
:::

:::callout{type="danger"}
This action is irreversible.
:::

:::callout{type="tip"}
Pro tip: use keyboard shortcuts for faster editing.
:::
```

**Types:** `info`, `warning`, `danger`, `tip`, `note`

### Tabs

```markdown
:::tabs
::tab{label="npm"}
npm install docplatform
::
::tab{label="yarn"}
yarn add docplatform
::
::tab{label="pnpm"}
pnpm add docplatform
::
:::
```

### Accordion

```markdown
:::accordion{title="How does sync work?"}
DocPlatform uses a hybrid git engine that combines go-git for small repositories
with native git CLI for large ones. Changes are synced via polling or webhooks.
:::
```

### Cards

```markdown
:::cards
::card{title="Getting Started" link="/getting-started"}
Install and configure DocPlatform in under 10 minutes.
::
::card{title="User Guide" link="/guides/editor"}
Learn the web editor, git sync, and publishing features.
::
:::
```

### Steps

```markdown
:::steps
::step{title="Install"}
Download the binary or pull the Docker image.
::
::step{title="Initialize"}
Run `docplatform init` to create your workspace.
::
::step{title="Start"}
Run `docplatform serve` and open the browser.
::
:::
```

### API Block

```markdown
:::api{method="GET" path="/api/v1/pages/{id}"}
Retrieve a single page by ID.

**Parameters:**
- `id` (path, required) — Page ULID

**Response:** `200 OK`
```json
{
  "id": "01HJKL...",
  "title": "Getting Started",
  "content": "..."
}
```
:::
```

## Custom domain

To serve published docs on your own domain:

1. Set the `BASE_DOMAIN` environment variable:

```bash
export BASE_DOMAIN=docs.yourcompany.com
```

2. Configure DNS to point your domain to the DocPlatform server
3. Set up a reverse proxy (nginx, Caddy, or cloud load balancer) with TLS termination

Example Caddy configuration:

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy automatically provisions and renews TLS certificates via Let's Encrypt.

## Caching

Published pages are cached for performance:

| Header | Value | Description |
|---|---|---|
| `Cache-Control` | `public, max-age=300` | Browsers and CDNs cache for 5 minutes |
| `ETag` | Content hash | Enables conditional requests (304 Not Modified) |

The cache key is based on the page's content hash. When content changes, the ETag changes automatically and cached versions are invalidated.

### Asset URL rewriting

In the web editor, assets use relative paths (`assets/screenshot.png`). In published docs, these are automatically rewritten to absolute paths (`/p/{slug}/assets/screenshot.png`) so images and files load correctly at any URL depth.

## Preview before publishing

Before making a page public, preview it at the published URL. Pages with `published: false` are still accessible to authenticated workspace members at the `/p/` path — they're just excluded from the public navigation and sitemap.
