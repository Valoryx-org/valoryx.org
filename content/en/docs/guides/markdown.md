---
title: Markdown & Components
description: Write documentation with CommonMark Markdown, YAML frontmatter, wikilinks, and 15 built-in interactive components.
weight: 2
---

# Markdown & Components

DocPlatform uses CommonMark-compliant Markdown with YAML frontmatter, wikilinks, and 15 custom components for rich, interactive documentation.

## Markdown basics

DocPlatform supports the full CommonMark specification plus common extensions.

### Headings

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```

Headings automatically generate anchor IDs for deep linking: `## My Section` → `#my-section`.

### Text formatting

```markdown
**Bold text**
*Italic text*
~~Strikethrough~~
`Inline code`
[Link text](https://example.com)
![Image alt text](./assets/screenshot.png)
```

### Lists

```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item

- [ ] Task item (unchecked)
- [x] Task item (checked)
```

### Blockquotes

```markdown
> This is a blockquote.
>
> It can span multiple paragraphs.
```

### Code blocks

Fenced code blocks with language-specific syntax highlighting (200+ languages via Chroma):

````markdown
```go
func main() {
    fmt.Println("Hello, DocPlatform!")
}
```
````

### Tables

```markdown
| Feature | Status | Notes |
|---|---|---|
| Editor | Complete | Tiptap-based |
| Search | Complete | Bleve engine |
| Git sync | Complete | Bidirectional |
```

Tables support left, center, and right alignment:

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| A    |   B    |     C |
```

### Horizontal rules

```markdown
---
```

### Links between pages

Link to other pages using standard Markdown relative paths:

```markdown
See the [Installation guide](../getting-started/installation.md).
Check the [API reference](../reference/api.md) for endpoint details.
```

DocPlatform validates internal links. The `doctor` command reports any broken references.

### Wikilinks

DocPlatform supports **wikilinks** with double-bracket syntax. The link target is the page's path (without the `.md` extension):

```markdown
See [[getting-started/index]] for setup instructions.
Check [[api/authentication|the auth guide]] for token details.
Jump to a section: [[api/authentication#tokens]]
```

| Syntax | Description |
|---|---|
| `[[page/path]]` | Link by page path |
| `[[page/path\|display text]]` | Link with custom display text |
| `[[page/path#heading]]` | Link to a specific heading |

**Wikilink features:**
- **Auto-repair on rename** — when a page is renamed or moved, all wikilinks pointing to it are automatically updated across the workspace
- **Broken link detection** — `docplatform doctor` and the `docplatform_validate_links` MCP tool report wikilinks that point to nonexistent pages

## Frontmatter

Every page starts with a YAML frontmatter block delimited by `---`:

```yaml
---
title: Page Title
description: A brief summary for search results and SEO.
tags: [guide, getting-started]
publish: true
status: draft
nav_order: 2
---
```

### Frontmatter fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `title` | string | Yes | — | Page title shown in navigation and headings |
| `id` | string | No | Auto-generated ULID | Stable page identifier that survives renames and database rebuilds |
| `description` | string | No | — | Summary for search results, SEO meta tags |
| `tags` | string[] or string | No | `[]` | Categories for filtering and search — accepts a YAML list or a comma-separated string |
| `publish` | boolean | No | `false` | Include in the published documentation site (the `.docplatform/publish.yaml` overlay can override this per path) |
| `status` | string | No | `draft` | Page lifecycle: `draft`, `published`, `archived` |
| `nav_order` | int | No | — | Ordering hint for sidebar navigation |
| `seo` | map | No | — | Per-page SEO overrides |
| `access` | object | No | — | Parsed and preserved, but **not enforced** — see [Permissions](../configuration/permissions.md) |

## Custom components

DocPlatform includes 15 built-in components that render as rich, interactive elements in both the web editor preview and published docs.

Components use a directive syntax:

```
:::component-name[attributes]
Content goes here.
:::
```

### Callout

Highlight important information with styled callout boxes.

```markdown
:::callout[info]
DocPlatform automatically indexes all content for search.
:::

:::callout[warning]
Changing the workspace slug will break existing published URLs.
:::

:::callout[danger]
Running `rebuild` drops the pages table and re-indexes from the filesystem.
This is irreversible.
:::

:::callout[tip]
Press Cmd+K to open search from anywhere in the editor.
:::

:::callout[note]
This feature is available in Community Edition.
:::
```

**Available types:** `info`, `warning`, `danger`, `tip`, `note`

### Code block (enhanced)

Standard fenced code blocks are automatically enhanced with:

- **Syntax highlighting** — 200+ languages via Chroma
- **Copy button** — one-click copy to clipboard

````markdown
```typescript
interface Page {
  id: string;
  title: string;
  content: string;
}
```
````

### Tabs

Group related content into switchable tab panels.

```markdown
:::tabs
::tab[macOS]
```bash
brew install docplatform
```
::
::tab[Linux]
```bash
curl -fsSL https://valoryx.org/install.sh | sh
```
::
::tab[Docker]
```bash
docker pull ghcr.io/valoryx-org/docplatform:latest
```
::
:::
```

Tab selection persists across page navigation — if a user selects "Docker", all tab groups on subsequent pages default to "Docker" when that label exists.

### Accordion

Collapsible sections for supplementary content.

```markdown
:::accordion[What happens during initialization?]
The `init` command creates a `.docplatform` directory, initializes the SQLite
database, generates an RS256 signing key, and optionally clones a git repository.
:::

:::accordion[Can I use an existing database?]
No. DocPlatform manages its own SQLite database and does not support connecting
to external database servers in Community Edition.
:::
```

### Cards

Grid of linked cards for navigation pages or feature overviews.

```markdown
:::cards
::card[Getting Started, link="/getting-started"]
Install and configure DocPlatform in under 10 minutes.
::
::card[Git Integration, link="/guides/git-integration"]
Bidirectional sync between the web editor and your git repository.
::
::card[Publishing, link="/guides/publishing"]
Publish beautiful documentation sites with dark mode and SEO.
::
::card[Search, link="/guides/search"]
Instant full-text search with permission filtering.
::
:::
```

### Steps

Numbered step-by-step instructions with visual progress indicators.

```markdown
:::steps
::step[Download]
Get the latest binary from GitHub Releases.
::
::step[Start the server]
Run `docplatform serve` and open http://localhost:3000.
::
::step[Register]
Create your account — registering creates your organization and starter workspace.
::
:::
```

### API Block

Document API endpoints with method badges, parameters, and response examples.

```markdown
:::api[POST /api/auth/login]
Authenticate a user and receive JWT tokens.

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 1800
}
```

**Errors:**
- `401 Unauthorized` — Invalid credentials
- `429 Too Many Requests` — Rate limit exceeded
:::
```

The API Block renders with Scalar-powered method badges and expandable parameter/response sections.

### File tree

Display directory structures with syntax highlighting.

```markdown
:::filetree
- .docplatform/
  - data.db
  - jwt-key.pem
  - backups/
  - search-index/
  - workspaces/
    - {workspace-id}/
      - docs/
      - assets/
      - .git/
:::
```

### Mermaid diagrams

Render diagrams from text using Mermaid syntax inside the `mermaid` directive:

```markdown
:::mermaid
graph TD
    A[Web Editor] --> B[Content Ledger]
    C[Git Push] --> B
    B --> D[Filesystem]
    B --> E[Database]
    B --> F[Search Index]
:::
```

Supports flowcharts, sequence diagrams, class diagrams, state diagrams, and more. Diagrams render client-side on published pages.

### KaTeX math

Render mathematical notation using LaTeX syntax inside the `katex` directive:

```markdown
:::katex
\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
:::
```

### Badge

Inline status labels: `:::badge[variant]` with the label text as content.

### Table of contents

`:::toc` renders a table of contents generated from the page's headings.

### Embed

`:::embed` embeds external content by URL.

## Component usage in the editor

### Rich text mode

In the rich editor, insert components from the toolbar (**+** button → select a component).

### Raw Markdown mode

In raw mode, write the directive syntax directly.

## Markdown extensions

Beyond CommonMark, DocPlatform supports the GitHub Flavored Markdown (GFM) extension set plus DocPlatform-specific additions:

| Extension | Syntax | Description |
|---|---|---|
| **Wikilinks** | `[[page/path]]` | Cross-page linking with auto-repair on rename |
| **Task lists** | `- [ ] item` | Checkboxes (GFM) |
| **Strikethrough** | `~~text~~` | Struck-through text (GFM) |
| **Tables** | GFM tables | With alignment support |
| **Autolinks** | `https://...` | URLs auto-linked (GFM) |
| **Heading anchors** | Auto-generated | Deep linking to sections |
| **Directives** | `:::component` | 15 built-in components (above) |

Footnote syntax (`[^1]`) is not supported.
