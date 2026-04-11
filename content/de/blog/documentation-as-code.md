---
title: "Documentation as Code: Ein praktischer Leitfaden"
description: "Was Docs-as-Code wirklich bedeutet, warum es für Engineering-Teams wichtig ist, und wie Sie zwischen Static-Site-Generatoren, Wikis und Dokumentationsplattformen wählen."
date: "2026-03-05"
author: "Valoryx Team"
tags: ["documentation", "git", "docs-as-code"]
---

„Documentation as Code" wird häufig verwendet. Im einfachsten Sinne bedeutet es, Dokumentation genauso zu behandeln wie Quellcode: in der Versionskontrolle gespeichert, in Klartext geschrieben, über Pull Requests überprüft und durch CI/CD gebaut. Aber zwischen der Idee und der guten Umsetzung klafft eine Lücke. Dieser Leitfaden erklärt, was Docs-as-Code ist, welche Ansätze existieren und wo jeder an seine Grenzen stößt.

## Warum Docs-as-Code wichtig ist

Softwareteams haben bereits Workflows für das Änderungsmanagement. Code durchläuft Versionskontrolle, Review, Tests und Deployment. Dokumentation in der Regel nicht. Sie lebt in einem Wiki, einem Google Doc oder einem Confluence-Space — außerhalb des Entwicklungsworkflows, gepflegt von demjenigen, der sich daran erinnert, sie zu aktualisieren.

Das Ergebnis ist vorhersehbar: Die Dokumentation weicht von der Realität ab. Ein API-Endpoint wird umbenannt, aber die Wiki-Seite verweist noch auf den alten Pfad. Eine Konfigurationsoption wird als veraltet markiert, aber die Notion-Seite sagt, sie sei erforderlich. Niemand bemerkt es, bis ein Benutzer einen Fehlerbericht einreicht.

Docs-as-Code löst dieses Problem, indem Dokumentation in denselben Workflow eingebettet wird:

- **Versionskontrolle** — jede Änderung wird nachverfolgt, zugeordnet und ist rückgängig machbar
- **Pull Requests** — Dokumentationsänderungen werden zusammen mit Codeänderungen überprüft
- **CI/CD** — Dokumentation wird automatisch beim Merge gebaut und bereitgestellt
- **Branching** — Entwurfsdokumentation lebt auf Feature-Branches, bis sie fertig ist
- **Blame** — Sie können sehen, wer jede Zeile wann geschrieben hat

Die [Write the Docs Community](https://www.writethedocs.org/guide/docs-as-code/) setzt sich seit Jahren für diesen Ansatz ein, und das Argument ist weitgehend gewonnen. Der schwierige Teil ist die Wahl des richtigen Werkzeugs.

## Drei Ansätze für Docs-as-Code

### 1. Static-Site-Generatoren

Tools wie Docusaurus, MkDocs, Hugo und Jekyll nehmen Markdown-Dateien aus einem Git-Repository und bauen eine statische HTML-Seite. Sie bearbeiten `.md`-Dateien in Ihrer IDE, committen, pushen, und CI baut und deployt die Seite.

**Vorteile:**
- Echter Git-nativer Workflow — Dateien sind einfach Markdown in einem Repository
- Schnelle Builds, günstiges Hosting (Netlify, Vercel, GitHub Pages)
- Volle Kontrolle über Templates, Styling und Struktur
- Keine Laufzeitabhängigkeiten — Output ist statisches HTML

**Nachteile:**
- Kein Web-Editor — jeder muss einen Texteditor und Git verwenden
- Keine eingebaute Zugriffskontrolle (es ist eine statische Seite)
- Keine Suche ohne Drittanbieter-Dienst (Algolia, Pagefind)
- Nicht-technische Mitwirkende sind ausgesperrt
- Frontmatter-Verwaltung wird im großen Maßstab mühsam

**Beispiel-Workflow:**

```bash
# Docs-Repository klonen
git clone git@github.com:yourorg/docs.git
cd docs

# Neue Seite erstellen
cat > docs/guides/deployment.md << 'EOF'
---
title: Deployment Guide
sidebar_position: 3
---

# Deploying to Production

Follow these steps to deploy...
EOF

# Lokal vorschauen
mkdocs serve  # oder docusaurus start, hugo serve

# Committen und pushen — CI erledigt den Rest
git add docs/guides/deployment.md
git commit -m "docs: add deployment guide"
git push
```

Das funktioniert gut für entwicklerorientierte Dokumentation, bei der jeder Mitwirkende mit Git vertraut ist. Es scheitert, wenn Produktmanager, Support-Ingenieure oder technische Redakteure beitragen müssen.

### 2. Wikis und Wissensbasen

Confluence, Notion, Outline, Wiki.js und BookStack bieten webbasierte Editoren mit WYSIWYG-Oberflächen. Inhalte werden in einer Datenbank gespeichert, und Benutzer bearbeiten über einen Browser.

**Vorteile:**
- Niedrige Einstiegshürde — jeder kann schreiben
- Reichhaltige Editoren mit Einbettungen, Tabellen und Medien
- Echtzeit-Zusammenarbeit (bei einigen Tools)
- Eingebaute Suche

**Nachteile:**
- Inhalte sind NICHT in Git (oder nur als Einweg-Export)
- Keine Pull-Request-Überprüfung für Dokumentationsänderungen
- Kein Branching oder Staging — Bearbeitungen sind sofort live
- Vendor Lock-in — der Export von Confluence zu etwas anderem ist schmerzhaft
- Versionshistorie ist im Vergleich zu Git rudimentär

Diese Tools optimieren den Schreibkomfort auf Kosten all dessen, was Docs-as-Code wertvoll macht. Sie können leicht Dokumentation schreiben, verlieren aber Versionskontrolle, Review und die Verbindung zu Ihrer Codebasis.

### 3. Dokumentationsplattformen mit Git-Sync

Eine neuere Kategorie: Plattformen, die einen Web-Editor mit echter Git-Integration kombinieren. Die Idee ist, nicht-technischen Mitwirkenden eine WYSIWYG-Oberfläche zu bieten und gleichzeitig die Inhalte in einem Git-Repository als Source of Truth zu halten.

Dies ist der Ansatz, den DocPlatform verfolgt. Bearbeitungen in der Web-Oberfläche erstellen Git-Commits. Änderungen, die von einer IDE nach Git gepusht werden, erscheinen im Web-Editor. Beide Richtungen funktionieren — es ist kein Einweg-Spiegel.

**Vorteile:**
- Web-Editor für nicht-technische Mitwirkende
- Inhalte leben in Git — Pull Requests, Branching, Blame funktionieren
- Suche, Zugriffskontrolle und Veröffentlichung sind eingebaut
- Kein Build-Schritt — veröffentlichte Dokumentation wird beim Speichern aktualisiert

**Nachteile:**
- Bidirektionaler Sync ist schwierig korrekt umzusetzen (siehe [Warum Git-Docs-Tools den Sync nicht hinbekommen](/blog/why-git-sync-breaks/))
- Weniger Template-Optionen als Static-Site-Generatoren
- Erfordert das Betreiben eines Servers (vs. statisches Hosting)

## Vergleichstabelle

| Fähigkeit | Static-Site-Generatoren | Wikis | Plattformen + Git |
|---|---|---|---|
| Inhalt in Git | Ja | Nein | Ja |
| PR-basiertes Review | Ja | Nein | Ja |
| Web-Editor | Nein | Ja | Ja |
| Nicht-technische Mitwirkende | Schwierig | Einfach | Einfach |
| Eingebaute Suche | Nein (Drittanbieter) | Ja | Ja |
| Zugriffskontrolle | Nein (statische Seite) | Ja | Ja |
| Build-/Deploy-Schritt | Erforderlich | Keiner | Keiner |
| Hosting-Komplexität | Niedrig (statisch) | Mittel (App + DB) | Niedrig-Mittel (einzelnes Binary) |

## Praktische Muster für den Erfolg

Unabhängig vom gewählten Ansatz machen diese Muster Docs-as-Code effektiver:

### Dokumentation neben dem Code platzieren

Platzieren Sie Ihre Dokumentation im selben Repository wie den Code, den sie beschreibt, oder zumindest in der selben GitHub-Organisation mit Querverweisen. Wenn ein Entwickler einen API-Endpoint ändert, sollte die Dokumentation für diesen Endpoint im selben PR sichtbar sein.

### Frontmatter konsistent verwenden

Jede Dokumentationsseite sollte strukturiertes Frontmatter haben:

```yaml
---
title: "API Authentication"
description: "How to authenticate with the DocPlatform API using JWT tokens"
last_reviewed: 2026-02-15
owner: "@backend-team"
---
```

Die Felder `last_reviewed` und `owner` sind keine Standard-Hugo-Felder — sie sind benutzerdefinierte Metadaten. Aber sie machen es trivial einfach, veraltete Dokumentation zu finden und zu wissen, wen man fragen kann.

### Aktualitätsprüfungen automatisieren

Richten Sie einen CI-Job ein, der Dokumentation markiert, die seit 90 Tagen nicht überprüft wurde:

```bash
#!/bin/bash
find docs/ -name "*.md" -exec grep -l "last_reviewed" {} \; | while read f; do
  reviewed=$(grep "last_reviewed" "$f" | cut -d'"' -f2)
  if [[ $(date -d "$reviewed" +%s) -lt $(date -d "-90 days" +%s) ]]; then
    echo "VERALTET: $f (zuletzt überprüft $reviewed)"
  fi
done
```

### Nicht auf Perfektion bestehen

Der häufigste Fehlermodus bei Docs-as-Code ist, das Beitragen zu schwierig zu machen. Wenn Ihr PR-Template eine Style-Guide-Prüfung, eine Link-Prüfung, eine Rechtschreibprüfung und zwei Genehmigungen erfordert — werden die Leute aufhören, Dokumentation zu schreiben. Halten Sie die Hürde für Inhaltsänderungen niedrig. Reservieren Sie strenge Reviews für strukturelle Änderungen.

## Wo DocPlatform passt

DocPlatform ist für Teams gebaut, die Docs-as-Code wollen, ohne jeden auf die Kommandozeile zu zwingen. Der [WYSIWYG-Editor](/docs/) übernimmt das Schreiben. Git übernimmt die Versionskontrolle. Das Content-Ledger-Muster übernimmt den bidirektionalen Sync, sodass keine Seite die andere überschreibt.

Die Community Edition ist kostenlos und selbstgehostet — [installieren Sie sie in fünf Minuten](/install/) mit einem einzelnen Binary-Download. Wenn Sie gehostetes Hosting wünschen, beginnen [Cloud-Pläne](/pricing/) bei 0 $ für kleine Teams.

Der schwierige Teil von Docs-as-Code war nie die Philosophie. Es waren die Werkzeuge. Static-Site-Generatoren funktionieren für Entwickler, schließen aber alle anderen aus. Wikis schließen alle ein, geben aber die Versionskontrolle auf. Die richtige Antwort ist beides: eine Schreiboberfläche, die nicht-technische Personen nutzen können, unterstützt durch einen Git-Workflow, dem Entwickler vertrauen.
