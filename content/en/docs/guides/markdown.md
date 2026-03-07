---
title: Markdown & Components
description: Write documentation with CommonMark Markdown, YAML frontmatter, wikilinks, and 15+ built-in interactive components.
weight: 2
---

# Markdown & Components

DocPlatform uses CommonMark-compliant Markdown with YAML frontmatter, wikilinks, and 15+ custom components for rich, interactive documentation.

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

Fenced code blocks with language-specific syntax highlighting (200+ languages via Shiki):

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

DocPlatform supports **wikilinks** for linking between pages without specifying full paths. Wikilinks use double-bracket syntax:

```markdown
See [[Getting Started]] for setup instructions.
Check [[API Authentication|the auth guide]] for token details.
Link by page ID for rename-proof references: [[01HJK...]]
```

| Syntax | Description |
|---|---|
| `[[Page Title]]` | Link by page title (auto-resolved to path) |
| `[[Page Title\|display text]]` | Link with custom display text |
| `[[01HJK...]]` | Link by stable page ID (survives renames) |

**Wikilink features:**
- **Hover preview** — hovering a wikilink shows a preview popup with the target page's title and description
- **Auto-repair on rename** — when a page is renamed or moved, all wikilinks pointing to it are automatically updated across the workspace
- **Broken link detection** — `docplatform doctor` reports wikilinks that point to nonexistent pages

## Frontmatter

Every page starts with a YAML frontmatter block delimited by `---`:

```yaml
---
title: Page Title
description: A brief summary for search results and SEO.
tags: [guide, getting-started]
published: true
access:
  read: ["engineering", "product"]
  write: ["engineering"]
---
```

### Frontmatter fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `title` | string | Yes | — | Page title shown in navigation and headings |
| `id` | string | No | Auto-generated ULID | Stable page identifier (survives renames, enables ID-based wikilinks) |
| `description` | string | No | — | Summary for search results, SEO meta tags |
| `tags` | string[] | No | `[]` | Categories for filtering and search |
| `published` | boolean | No | `false` | Include in the published documentation site |
| `status` | string | No | `draft` | Page lifecycle: `draft`, `published`, `archived` |
| `access` | object | No | — | Per-operation access rules (see [Permissions](../configuration/permissions.md)) |
| `access.read` | string[] | No | — | Roles that can view this page |
| `access.write` | string[] | No | — | Roles that can edit this page |
| `access.admin` | string[] | No | — | Roles/user IDs (`@01HJK...`) that can manage this page |

The `id` field is auto-generated as a ULID when a page is created. On git import, if the `id` is missing, DocPlatform generates one and writes it back on the next sync. This ID enables rename-proof wikilinks and survives database rebuilds.

## Custom components

DocPlatform includes 15+ built-in components that render as rich, interactive elements in both the web editor preview and published docs.

Components use a directive syntax:

```
:::component-name{attributes}
Content goes here.
:::
```

### Callout

Highlight important information with styled callout boxes.

```markdown
:::callout{type="info"}
DocPlatform automatically indexes all content for search.
:::

:::callout{type="warning"}
Changing the workspace slug will break existing published URLs.
:::

:::callout{type="danger"}
Running `rebuild` drops the pages table and re-indexes from the filesystem.
This is irreversible.
:::

:::callout{type="tip"}
Press Cmd+K to open search from anywhere in the editor.
:::

:::callout{type="note"}
This feature is available in Community Edition.
:::
```

**Available types:** `info`, `warning`, `danger`, `tip`, `note`

### Code block (enhanced)

Standard fenced code blocks are automatically enhanced with:

- **Syntax highlighting** — 200+ languages via Shiki
- **Copy button** — one-click copy to clipboard
- **Language label** — displayed in the top-right corner
- **Line numbers** — optional, enabled with `showLineNumbers`

````markdown
```typescript {showLineNumbers}
interface Page {
  id: string;
  title: string;
  content: string;
  published: boolean;
}
```
````

### Tabs

Group related content into switchable tab panels.

```markdown
:::tabs
::tab{label="macOS"}
```bash
brew install docplatform
```
::
::tab{label="Linux"}
```bash
curl -fsSL https://valoryx.org/install.sh | sh
```
::
::tab{label="Docker"}
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
:::accordion{title="What happens during initialization?"}
The `init` command creates a `.docplatform` directory, initializes the SQLite
database, generates an RS256 signing key, and optionally clones a git repository.
:::

:::accordion{title="Can I use an existing database?"}
No. DocPlatform manages its own SQLite database and does not support connecting
to external database servers in Community Edition.
:::
```

### Cards

Grid of linked cards for navigation pages or feature overviews.

```markdown
:::cards
::card{title="Getting Started" link="/getting-started"}
Install and configure DocPlatform in under 10 minutes.
::
::card{title="Git Integration" link="/guides/git-integration"}
Bidirectional sync between the web editor and your git repository.
::
::card{title="Publishing" link="/guides/publishing"}
Publish beautiful documentation sites with dark mode and SEO.
::
::card{title="Search" link="/guides/search"}
Instant full-text search with permission filtering.
::
:::
```

### Steps

Numbered step-by-step instructions with visual progress indicators.

```markdown
:::steps
::step{title="Download"}
Get the latest binary from GitHub Releases.
::
::step{title="Initialize"}
Run `docplatform init` to create your workspace.
::
::step{title="Start the server"}
Run `docplatform serve` and open http://localhost:3000.
::
::step{title="Register"}
Create your admin account — the first user becomes SuperAdmin.
::
:::
```

### API Block

Document API endpoints with method badges, parameters, and response examples.

```markdown
:::api{method="POST" path="/api/auth/login"}
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

Render diagrams from text using Mermaid syntax.

````markdown
```mermaid
graph TD
    A[Web Editor] --> B[Content Ledger]
    C[Git Push] --> B
    B --> D[Filesystem]
    B --> E[Database]
    B --> F[Search Index]
```
````

Supports flowcharts, sequence diagrams, class diagrams, state diagrams, and more.

### KaTeX math

Render mathematical notation using LaTeX syntax.

```markdown
Inline math: $E = mc^2$

Block math:
$$
\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

### Version selector

Display version-specific content with a dropdown selector.

```markdown
:::version-selector
::version{label="v0.5" default}
Current stable release with all Community Edition features.
::
::version{label="v0.4"}
Previous release. Upgrade recommended.
::
:::
```

## Component usage in the editor

### Rich text mode

In the rich editor, components render as interactive blocks. Insert them using:

- **Slash commands** — type `/` then the component name (e.g., `/callout`, `/tabs`)
- **Toolbar** — click the **+** button → select a component
- **Keyboard** — no dedicated shortcuts (use slash commands)

### Raw Markdown mode

In raw mode, write the directive syntax directly. The editor provides syntax highlighting for component blocks.

## Markdown extensions

Beyond CommonMark, DocPlatform supports:

| Extension | Syntax | Description |
|---|---|---|
| **Wikilinks** | `[[Page Title]]` | Cross-page linking with hover preview and auto-repair |
| **Task lists** | `- [ ] item` | Interactive checkboxes |
| **Strikethrough** | `~~text~~` | Struck-through text |
| **Tables** | GFM tables | With alignment support |
| **Autolinks** | `https://...` | URLs auto-linked |
| **Footnotes** | `[^1]` | Reference-style footnotes |
| **Heading anchors** | Auto-generated | Deep linking to sections |
| **Mermaid** | ` ```mermaid ` | Inline diagrams from text |
| **KaTeX** | `$...$` / `$$...$$` | Mathematical notation |
