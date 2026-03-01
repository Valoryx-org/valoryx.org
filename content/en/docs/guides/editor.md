---
title: The Web Editor
description: Write and edit documentation using DocPlatform's rich web editor with Markdown toggle, frontmatter form, and autosave.
weight: 1
---

# The Web Editor

DocPlatform includes a rich text editor built on Tiptap (ProseMirror-based) that renders Markdown in real time while preserving full Markdown source compatibility. Every change you make produces a clean `.md` file — no proprietary format, no lock-in.

## Editor layout

```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar          │  Editor                                 │
│                   │                                         │
│  📁 Getting       │  ┌──────────────────────────────────┐   │
│     Started       │  │ Frontmatter (collapsible)        │   │
│  📁 Guides        │  │ Title: ___________________       │   │
│  📁 API           │  │ Description: ______________      │   │
│    > auth.md      │  │ Tags: [api] [auth]               │   │
│    > endpoints    │  └──────────────────────────────────┘   │
│  📄 changelog     │                                         │
│                   │  Start writing here...                  │
│  ┌────────────┐   │                                         │
│  │ + New Page │   │                                         │
│  └────────────┘   │  ┌──────────────────────────────────┐   │
│                   │  │ Toolbar: B I Link Image Code ... │   │
└───────────────────┴──┴──────────────────────────────────┘   │
```

### Sidebar

- **Page tree** — Nested list of all pages in the workspace. Drag to reorder.
- **New Page** — Create a new page at root level or nested under an existing page.
- **Search shortcut** — Click or press `Cmd+K` / `Ctrl+K` to open full-text search.

### Frontmatter form

The collapsible frontmatter section at the top of the editor provides form fields for page metadata:

| Field | Description | Required |
|---|---|---|
| **Title** | Page heading and navigation label | Yes |
| **Description** | Summary shown in search results and SEO meta tags | No |
| **Tags** | Categorization labels for filtering and discovery | No |
| **Published** | Toggle to include/exclude from the public site | No |
| **Access** | Visibility level: `public`, `workspace`, `restricted` | No |

Changes to frontmatter fields update the YAML block in the `.md` file automatically.

### Toolbar

The formatting toolbar provides quick access to:

| Action | Shortcut | Description |
|---|---|---|
| **Bold** | `Cmd+B` | Bold text |
| **Italic** | `Cmd+I` | Italic text |
| **Code** | `Cmd+E` | Inline code |
| **Link** | `Cmd+K` | Insert or edit hyperlink |
| **Heading 1-3** | `Cmd+Shift+1/2/3` | Section headings |
| **Bullet list** | `Cmd+Shift+8` | Unordered list |
| **Ordered list** | `Cmd+Shift+7` | Numbered list |
| **Task list** | `Cmd+Shift+9` | Checkbox list |
| **Blockquote** | `Cmd+Shift+>` | Block quote |
| **Code block** | `Cmd+Alt+C` | Fenced code block with language selector |
| **Image** | — | Upload or paste an image |
| **Table** | — | Insert a table |
| **Horizontal rule** | `---` | Divider line |

## Writing modes

### Rich text mode (default)

The editor renders Markdown as formatted content. Headings appear as headings, links are clickable, code blocks have syntax highlighting.

### Raw Markdown mode

Click the `</>` toggle in the toolbar to switch to raw Markdown editing. This gives you a plain-text view of the file with syntax highlighting.

Raw mode is useful for:

- Fine-tuning Markdown formatting
- Editing frontmatter YAML directly
- Pasting content from other sources
- Using custom components (Callout, Tabs, etc.)

Changes sync between modes instantly. Switch back and forth without losing work.

## Autosave

DocPlatform autosaves your work every few seconds. You'll see a status indicator in the toolbar:

| Status | Meaning |
|---|---|
| **Saved** | All changes persisted to disk |
| **Saving...** | Write in progress |
| **Unsaved changes** | Edits pending save (poor connection or error) |

If git sync is enabled, each save triggers an auto-commit. Commits are batched — rapid edits produce a single commit with the message format: `docs: update {page-title}`.

## Working with content

### Images

Drag and drop or paste images directly into the editor. Images are stored in the workspace's assets directory and referenced with relative paths.

Supported formats: PNG, JPG, GIF, SVG, WebP.

### Tables

Insert tables from the toolbar. Tables support:

- Add/remove rows and columns
- Header row toggle
- Text alignment (left, center, right)
- Markdown table syntax in raw mode

### Code blocks

Insert code blocks with the toolbar or by typing triple backticks (`` ``` ``). Select a language for syntax highlighting — Shiki supports 200+ languages.

```javascript
// Code blocks with syntax highlighting
function greet(name) {
  return `Hello, ${name}!`;
}
```

### Internal links

Link to other pages in your workspace using standard Markdown links:

```markdown
See the [API Authentication]({{< relref "/docs/reference/api" >}}) guide.
```

DocPlatform validates internal links and the `doctor` command reports broken references.

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Cmd+S` | Force save |
| `Cmd+K` | Open search dialog |
| `Cmd+Z` | Undo |
| `Cmd+Shift+Z` | Redo |
| `Cmd+/` | Toggle Markdown comment |
| `Tab` | Indent list item |
| `Shift+Tab` | Outdent list item |
| `Cmd+Enter` | Toggle task completion (in task lists) |
| `Escape` | Close dialogs / deselect |

> **Note:** On Windows and Linux, replace `Cmd` with `Ctrl`.

## Real-time collaboration

When multiple users edit the same workspace, presence indicators show who's online and which page they're viewing. The sidebar displays user avatars next to pages currently being edited.

DocPlatform does not support simultaneous editing of the same page by multiple users. If two users try to save conflicting changes to the same page, the Content Ledger detects the collision via content hashing and returns a 409 error with both versions available for manual resolution.

## Tips

- **Drag pages** in the sidebar to reorganize your documentation structure
- **Slash commands** — type `/` in the editor to quickly insert components (callout, code block, table, etc.)
- **Paste rich text** from Google Docs, Notion, or Confluence — the editor converts it to clean Markdown
- **Frontmatter defaults** — set workspace-level defaults for `published`, `access`, and `tags` to reduce repetitive entry
