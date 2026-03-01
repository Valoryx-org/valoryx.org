---
title: Dokumentation veröffentlichen
description: Veröffentlichen Sie Ihre Dokumentation als ansprechende öffentliche Website mit Syntax-Highlighting, SEO-Unterstützung und optionalem Team-exklusiven Zugriff.
weight: 5
---

# Dokumentation veröffentlichen

DocPlatform kann Ihre Dokumentation als öffentliche Website bereitstellen — komplett mit Navigations-Seitenleiste, Syntax-Highlighting und SEO-Metadaten. Kein separater Static-Site-Generator erforderlich.

## Wie die Veröffentlichung funktioniert

Veröffentlichte Dokumentation wird unter `/p/{workspace-slug}/{page-path}` bereitgestellt:

```
http://localhost:3000/p/my-docs/              → docs/index.md
http://localhost:3000/p/my-docs/quickstart    → docs/quickstart.md
http://localhost:3000/p/my-docs/api/auth      → docs/api/auth.md
```

Seiten werden bei Anfrage von Markdown zu HTML gerendert, unter Verwendung von goldmark (CommonMark-konform) mit Chroma-Syntax-Highlighting für Codeblöcke.

### Seitenstatus-Lebenszyklus

Seiten haben ein `status`-Feld, das ihre Sichtbarkeit steuert:

| Status | Im Editor | In veröffentlichter Seite | In der Suche |
|---|---|---|---|
| `draft` (Standard) | Sichtbar | Verborgen | Nur für Mitglieder sichtbar |
| `published` | Sichtbar | Sichtbar | Sichtbar gemäß Zugriffsregeln |
| `archived` | Sichtbar (abgedimmt) | Verborgen | Verborgen |

Setzen Sie den Status im Frontmatter:

```yaml
---
title: My Page
status: published    # draft, published, or archived
publish: true        # Kurzform — entspricht status: published
---
```

Die Kurzform `publish: true` und `status: published` sind gleichwertig. Verwenden Sie, was Sie bevorzugen.

## Veröffentlichung aktivieren

### Pro Seite

Setzen Sie `published: true` im Frontmatter der Seite:

```yaml
---
title: API Authentication
description: How to authenticate with the API.
published: true
---
```

Oder schalten Sie den **Published**-Schalter im Frontmatter-Formular des Web-Editors um.

### Workspace-weiter Standard

Setzen Sie einen Workspace-weiten Standard, damit neue Seiten automatisch veröffentlicht werden:

```yaml
# .docplatform/config.yaml
publishing:
  default_published: true
  require_explicit_unpublish: false
```

## Funktionen der veröffentlichten Seite

### Navigation

Die veröffentlichte Seite generiert eine Seitenleisten-Navigation aus Ihrer Seitenhierarchie. Die Reihenfolge entspricht der Seitenleiste im Web-Editor.

Um die Navigationsreihenfolge anzupassen, passen Sie den `navigation`-Abschnitt in Ihrer Workspace-Konfiguration an:

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

### Syntax-Highlighting

Codeblöcke werden mit **Chroma** (goldmark-highlighting, Dracula-Theme) hervorgehoben. Über 200 Sprachen werden unterstützt.

Geben Sie die Sprache nach den öffnenden dreifachen Backticks an:

````markdown
```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```
````

### SEO

DocPlatform generiert SEO-Metadaten automatisch aus dem Frontmatter Ihrer Seite:

| Tag | Quelle |
|---|---|
| `<title>` | Frontmatter `title` |
| `<meta name="description">` | Frontmatter `description` |
| `<meta property="og:title">` | Frontmatter `title` |
| `<meta property="og:description">` | Frontmatter `description` |
| `<link rel="canonical">` | Generiert aus dem Seitenpfad |
| `sitemap.xml` | Automatisch generiert aus allen veröffentlichten Seiten |
| `robots.txt` | Automatisch generiert |

### Zugriffskontrolle

Standardmäßig sind veröffentlichte Dokumente **öffentlich** — keine Anmeldung erforderlich. Jeder mit der URL kann sie ansehen.

Um Ihre gesamte veröffentlichte Seite auf Workspace-Mitglieder zu beschränken, setzen Sie `PUBLISH_REQUIRE_AUTH`:

```bash
# .env
PUBLISH_REQUIRE_AUTH=true
```

Wenn aktiviert:

- Besucher, die nicht angemeldet sind, werden zu `/#/login?next=<url>` weitergeleitet
- Nach der Anmeldung werden sie zur angeforderten Seite zurückgeleitet
- Jedes Workspace-Mitglied (jede Rolle) kann ansehen — auch Viewer
- Nicht-Mitglieder, die sich anmelden, werden weiterhin abgewiesen

Starten Sie den Server neu, damit diese Änderung wirksam wird. Kein Rebuild erforderlich.

> **Zugriffskontrolle auf Seitenebene** (Beschränkung einzelner Seiten auf bestimmte Rollen) ist für eine zukünftige Version geplant. In v0.5 ist die Zugriffskontrolle alles-oder-nichts auf Seitenebene über `PUBLISH_REQUIRE_AUTH`.

## Integrierte Komponenten

Veröffentlichte Dokumentation unterstützt 7 benutzerdefinierte Komponenten, die als reichhaltige, interaktive Elemente gerendert werden:

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

**Typen:** `info`, `warning`, `danger`, `tip`, `note`

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

## Eigene Domain

Um veröffentlichte Dokumentation unter Ihrer eigenen Domain bereitzustellen:

1. Setzen Sie die Umgebungsvariable `BASE_DOMAIN`:

```bash
export BASE_DOMAIN=docs.yourcompany.com
```

2. Konfigurieren Sie DNS, sodass Ihre Domain auf den DocPlatform-Server zeigt
3. Richten Sie einen Reverse Proxy (nginx, Caddy oder Cloud-Load-Balancer) mit TLS-Terminierung ein

Beispiel-Caddy-Konfiguration:

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy stellt automatisch TLS-Zertifikate über Let's Encrypt bereit und erneuert sie.

## Caching

Veröffentlichte Seiten werden für die Leistung gecacht:

| Header | Wert | Beschreibung |
|---|---|---|
| `Cache-Control` | `public, max-age=300` | Browser und CDNs cachen für 5 Minuten |
| `ETag` | Content-Hash | Ermöglicht bedingte Anfragen (304 Not Modified) |

Der Cache-Key basiert auf dem Content-Hash der Seite. Wenn sich der Inhalt ändert, ändert sich der ETag automatisch und gecachte Versionen werden invalidiert.

### Asset-URL-Umschreibung

Im Web-Editor verwenden Assets relative Pfade (`assets/screenshot.png`). In veröffentlichten Dokumenten werden diese automatisch zu absoluten Pfaden umgeschrieben (`/p/{slug}/assets/screenshot.png`), damit Bilder und Dateien auf jeder URL-Tiefe korrekt geladen werden.

## Vorschau vor Veröffentlichung

Bevor Sie eine Seite öffentlich machen, können Sie sie unter der veröffentlichten URL anzeigen. Seiten mit `published: false` sind weiterhin für authentifizierte Workspace-Mitglieder unter dem `/p/`-Pfad zugänglich — sie werden nur aus der öffentlichen Navigation und Sitemap ausgeschlossen.
