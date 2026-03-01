---
title: Der Web-Editor
description: Schreiben und bearbeiten Sie Dokumentation mit dem leistungsfähigen Web-Editor von DocPlatform — mit Markdown-Umschalter, Frontmatter-Formular und automatischem Speichern.
weight: 1
---

# Der Web-Editor

DocPlatform enthält einen Rich-Text-Editor, der auf Tiptap (ProseMirror-basiert) aufbaut und Markdown in Echtzeit rendert, während die volle Markdown-Quelldatei-Kompatibilität erhalten bleibt. Jede Änderung, die Sie vornehmen, erzeugt eine saubere `.md`-Datei — kein proprietäres Format, keine Herstellerbindung.

## Editor-Layout

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

### Seitenleiste

- **Seitenbaum** — Verschachtelte Liste aller Seiten im Workspace. Per Drag-and-Drop neu anordnen.
- **Neue Seite** — Erstellen Sie eine neue Seite auf der obersten Ebene oder verschachtelt unter einer bestehenden Seite.
- **Such-Shortcut** — Klicken Sie oder drücken Sie `Cmd+K` / `Ctrl+K`, um die Volltextsuche zu öffnen.

### Frontmatter-Formular

Der einklappbare Frontmatter-Bereich am oberen Rand des Editors bietet Formularfelder für Seiten-Metadaten:

| Feld | Beschreibung | Erforderlich |
|---|---|---|
| **Title** | Seitenüberschrift und Navigationsbeschriftung | Ja |
| **Description** | Zusammenfassung, die in Suchergebnissen und SEO-Meta-Tags angezeigt wird | Nein |
| **Tags** | Kategorisierungslabels für Filterung und Auffindbarkeit | Nein |
| **Published** | Umschalter zum Ein-/Ausschließen von der öffentlichen Seite | Nein |
| **Access** | Sichtbarkeitsstufe: `public`, `workspace`, `restricted` | Nein |

Änderungen an Frontmatter-Feldern aktualisieren den YAML-Block in der `.md`-Datei automatisch.

### Symbolleiste

Die Formatierungssymbolleiste bietet schnellen Zugriff auf:

| Aktion | Tastenkürzel | Beschreibung |
|---|---|---|
| **Fett** | `Cmd+B` | Fetter Text |
| **Kursiv** | `Cmd+I` | Kursiver Text |
| **Code** | `Cmd+E` | Inline-Code |
| **Link** | `Cmd+K` | Hyperlink einfügen oder bearbeiten |
| **Überschrift 1-3** | `Cmd+Shift+1/2/3` | Abschnittsüberschriften |
| **Aufzählung** | `Cmd+Shift+8` | Ungeordnete Liste |
| **Nummerierte Liste** | `Cmd+Shift+7` | Nummerierte Liste |
| **Aufgabenliste** | `Cmd+Shift+9` | Checkbox-Liste |
| **Blockzitat** | `Cmd+Shift+>` | Blockzitat |
| **Codeblock** | `Cmd+Alt+C` | Umzäunter Codeblock mit Sprachauswahl |
| **Bild** | — | Bild hochladen oder einfügen |
| **Tabelle** | — | Tabelle einfügen |
| **Horizontale Linie** | `---` | Trennlinie |

## Schreibmodi

### Rich-Text-Modus (Standard)

Der Editor rendert Markdown als formatierten Inhalt. Überschriften erscheinen als Überschriften, Links sind anklickbar, Codeblöcke haben Syntax-Highlighting.

### Raw-Markdown-Modus

Klicken Sie auf den `</>` Umschalter in der Symbolleiste, um zum Raw-Markdown-Bearbeitungsmodus zu wechseln. Dies bietet eine Klartextansicht der Datei mit Syntax-Highlighting.

Der Raw-Modus ist nützlich für:

- Feinabstimmung der Markdown-Formatierung
- Direkte Bearbeitung des Frontmatter-YAML
- Einfügen von Inhalten aus anderen Quellen
- Verwendung von benutzerdefinierten Komponenten (Callout, Tabs usw.)

Änderungen werden sofort zwischen den Modi synchronisiert. Wechseln Sie hin und her, ohne Arbeit zu verlieren.

## Automatisches Speichern

DocPlatform speichert Ihre Arbeit automatisch alle paar Sekunden. Sie sehen einen Statusindikator in der Symbolleiste:

| Status | Bedeutung |
|---|---|
| **Saved** | Alle Änderungen auf Festplatte gespeichert |
| **Saving...** | Schreibvorgang läuft |
| **Unsaved changes** | Bearbeitungen warten auf Speicherung (schlechte Verbindung oder Fehler) |

Wenn Git-Synchronisation aktiviert ist, löst jede Speicherung einen automatischen Commit aus. Commits werden gebündelt — schnelle Bearbeitungen erzeugen einen einzelnen Commit im Format: `docs: update {page-title}`.

## Arbeiten mit Inhalten

### Bilder

Ziehen Sie Bilder per Drag-and-Drop in den Editor oder fügen Sie sie ein. Bilder werden im Assets-Verzeichnis des Workspace gespeichert und mit relativen Pfaden referenziert.

Unterstützte Formate: PNG, JPG, GIF, SVG, WebP.

### Tabellen

Fügen Sie Tabellen über die Symbolleiste ein. Tabellen unterstützen:

- Zeilen und Spalten hinzufügen/entfernen
- Kopfzeile ein-/ausschalten
- Textausrichtung (links, zentriert, rechts)
- Markdown-Tabellensyntax im Raw-Modus

### Codeblöcke

Fügen Sie Codeblöcke über die Symbolleiste oder durch Eingabe dreier Backticks (`` ``` ``) ein. Wählen Sie eine Sprache für Syntax-Highlighting — Shiki unterstützt über 200 Sprachen.

```javascript
// Codeblöcke mit Syntax-Highlighting
function greet(name) {
  return `Hello, ${name}!`;
}
```

### Interne Links

Verlinken Sie auf andere Seiten in Ihrem Workspace mit Standard-Markdown-Links:

```markdown
See the [API Authentication]({{< relref "/docs/reference/api" >}}) guide.
```

DocPlatform validiert interne Links und der `doctor`-Befehl meldet defekte Referenzen.

## Tastenkürzel

| Tastenkürzel | Aktion |
|---|---|
| `Cmd+S` | Speichern erzwingen |
| `Cmd+K` | Suchdialog öffnen |
| `Cmd+Z` | Rückgängig |
| `Cmd+Shift+Z` | Wiederholen |
| `Cmd+/` | Markdown-Kommentar umschalten |
| `Tab` | Listenelement einrücken |
| `Shift+Tab` | Listenelement ausrücken |
| `Cmd+Enter` | Aufgabenabschluss umschalten (in Aufgabenlisten) |
| `Escape` | Dialoge schließen / Auswahl aufheben |

> **Hinweis:** Unter Windows und Linux ersetzen Sie `Cmd` durch `Ctrl`.

## Echtzeit-Zusammenarbeit

Wenn mehrere Benutzer denselben Workspace bearbeiten, zeigen Präsenzindikatoren an, wer online ist und welche Seite angesehen wird. Die Seitenleiste zeigt Benutzer-Avatare neben Seiten an, die gerade bearbeitet werden.

DocPlatform unterstützt keine gleichzeitige Bearbeitung derselben Seite durch mehrere Benutzer. Wenn zwei Benutzer versuchen, widersprüchliche Änderungen an derselben Seite zu speichern, erkennt das Content Ledger die Kollision über Content-Hashing und gibt einen 409-Fehler mit beiden verfügbaren Versionen zur manuellen Auflösung zurück.

## Tipps

- **Seiten verschieben** — ziehen Sie Seiten in der Seitenleiste, um Ihre Dokumentationsstruktur neu zu organisieren
- **Slash-Befehle** — geben Sie `/` im Editor ein, um schnell Komponenten einzufügen (Callout, Codeblock, Tabelle usw.)
- **Rich-Text einfügen** — aus Google Docs, Notion oder Confluence — der Editor konvertiert es in sauberes Markdown
- **Frontmatter-Standards** — setzen Sie Workspace-weite Standards für `published`, `access` und `tags`, um repetitive Eingaben zu reduzieren
