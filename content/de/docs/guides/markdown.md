---
title: Markdown & Komponenten
description: Schreiben Sie Dokumentation mit CommonMark-Markdown, YAML-Frontmatter und 7 integrierten interaktiven Komponenten.
weight: 2
---

# Markdown & Komponenten

DocPlatform verwendet CommonMark-konformes Markdown mit YAML-Frontmatter und 7 benutzerdefinierten Komponenten für reichhaltige, interaktive Dokumentation.

## Markdown-Grundlagen

DocPlatform unterstützt die vollständige CommonMark-Spezifikation sowie gängige Erweiterungen.

### Überschriften

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```

Überschriften generieren automatisch Anker-IDs für Deep Linking: `## My Section` → `#my-section`.

### Textformatierung

```markdown
**Bold text**
*Italic text*
~~Strikethrough~~
`Inline code`
[Link text](https://example.com)
![Image alt text](./assets/screenshot.png)
```

### Listen

```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item

- [ ] Task item (unchecked)
- [x] Task item (checked)
```

### Blockzitate

```markdown
> This is a blockquote.
>
> It can span multiple paragraphs.
```

### Codeblöcke

Umzäunte Codeblöcke mit sprachspezifischem Syntax-Highlighting (über 200 Sprachen via Shiki):

````markdown
```go
func main() {
    fmt.Println("Hello, DocPlatform!")
}
```
````

### Tabellen

```markdown
| Feature | Status | Notes |
|---|---|---|
| Editor | Complete | Tiptap-based |
| Search | Complete | Bleve engine |
| Git sync | Complete | Bidirectional |
```

Tabellen unterstützen links-, zentrierte und rechtsbündige Ausrichtung:

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| A    |   B    |     C |
```

### Horizontale Linien

```markdown
---
```

### Links zwischen Seiten

Verlinken Sie auf andere Seiten in Ihrem Workspace mit relativen Pfaden:

```markdown
See the [Installation guide](../getting-started/installation.md).
Check the [API reference](../reference/api.md) for endpoint details.
```

DocPlatform validiert interne Links. Der `doctor`-Befehl meldet defekte Referenzen.

## Frontmatter

Jede Seite beginnt mit einem YAML-Frontmatter-Block, der durch `---` begrenzt wird:

```yaml
---
title: Page Title
description: A brief summary for search results and SEO.
tags: [guide, getting-started]
published: true
access: public
allowed_roles: []
---
```

### Frontmatter-Felder

| Feld | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `title` | string | Ja | — | Seitentitel, der in Navigation und Überschriften angezeigt wird |
| `description` | string | Nein | — | Zusammenfassung für Suchergebnisse und SEO-Meta-Tags |
| `tags` | string[] | Nein | `[]` | Kategorien für Filterung und Suche |
| `published` | boolean | Nein | `false` | In die veröffentlichte Dokumentationsseite aufnehmen |
| `access` | string | Nein | `public` | Sichtbarkeit: `public`, `workspace`, `restricted` |
| `allowed_roles` | string[] | Nein | `[]` | Rollen, die ansehen dürfen (wenn `access: restricted`) |

## Benutzerdefinierte Komponenten

DocPlatform enthält 7 integrierte Komponenten, die als reichhaltige, interaktive Elemente sowohl in der Web-Editor-Vorschau als auch in veröffentlichten Dokumenten gerendert werden.

Komponenten verwenden eine Direktiven-Syntax:

```
:::component-name{attributes}
Content goes here.
:::
```

### Callout

Heben Sie wichtige Informationen mit stilisierten Callout-Boxen hervor.

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

**Verfügbare Typen:** `info`, `warning`, `danger`, `tip`, `note`

### Codeblock (erweitert)

Standard-umzäunte Codeblöcke werden automatisch erweitert mit:

- **Syntax-Highlighting** — über 200 Sprachen via Shiki
- **Kopier-Button** — Ein-Klick-Kopie in die Zwischenablage
- **Sprachlabel** — wird in der oberen rechten Ecke angezeigt
- **Zeilennummern** — optional, aktiviert mit `showLineNumbers`

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

Gruppieren Sie verwandte Inhalte in umschaltbare Tab-Panels.

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

Die Tab-Auswahl bleibt über Seitennavigation hinweg bestehen — wenn ein Benutzer "Docker" auswählt, werden alle Tab-Gruppen auf nachfolgenden Seiten standardmäßig auf "Docker" gesetzt, wenn dieses Label vorhanden ist.

### Accordion

Einklappbare Abschnitte für ergänzende Inhalte.

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

Raster verlinkter Karten für Navigationsseiten oder Funktionsübersichten.

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

Nummerierte Schritt-für-Schritt-Anleitungen mit visuellen Fortschrittsanzeigen.

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

Dokumentieren Sie API-Endpunkte mit Methoden-Badges, Parametern und Antwortbeispielen.

```markdown
:::api{method="POST" path="/api/v1/auth/login"}
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
  "expires_in": 900
}
```

**Errors:**
- `401 Unauthorized` — Invalid credentials
- `429 Too Many Requests` — Rate limit exceeded
:::
```

## Komponentenverwendung im Editor

### Rich-Text-Modus

Im Rich-Editor werden Komponenten als interaktive Blöcke gerendert. Fügen Sie sie ein mit:

- **Slash-Befehle** — geben Sie `/` ein, gefolgt vom Komponentennamen (z. B. `/callout`, `/tabs`)
- **Symbolleiste** — klicken Sie auf den **+** Button → wählen Sie eine Komponente
- **Tastatur** — keine dedizierten Tastenkürzel (verwenden Sie Slash-Befehle)

### Raw-Markdown-Modus

Im Raw-Modus schreiben Sie die Direktiven-Syntax direkt. Der Editor bietet Syntax-Highlighting für Komponentenblöcke.

## Markdown-Erweiterungen

Über CommonMark hinaus unterstützt DocPlatform:

| Erweiterung | Syntax | Beschreibung |
|---|---|---|
| **Aufgabenlisten** | `- [ ] item` | Interaktive Checkboxen |
| **Durchgestrichen** | `~~text~~` | Durchgestrichener Text |
| **Tabellen** | GFM-Tabellen | Mit Ausrichtungsunterstützung |
| **Autolinks** | `https://...` | URLs werden automatisch verlinkt |
| **Fußnoten** | `[^1]` | Referenzstil-Fußnoten |
| **Überschriftenanker** | Automatisch generiert | Deep Linking zu Abschnitten |
