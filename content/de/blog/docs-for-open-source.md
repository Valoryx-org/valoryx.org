---
title: "Dokumentation für Open-Source-Projekte"
description: "OSS-Maintainer brauchen Dokumentation, können sich aber keine kostenpflichtigen Tools leisten. So richten Sie kostenlose, selbstgehostete Dokumentation mit Git-Sync in unter 5 Minuten ein."
date: "2026-04-06"
author: "Valoryx Team"
tags: ["open-source", "documentation", "free", "tutorial"]
---

Open-Source-Projekte leben oder sterben mit ihrer Dokumentation. Eine Bibliothek mit guter Dokumentation wird adoptiert. Eine Bibliothek mit einem dürren README und einer „Lies den Code"-Einstellung wird von jemandem geforkt, der bessere Dokumentation schreibt — oder einfach ignoriert.

Aber die meisten Dokumentationstools sind für Unternehmen gebaut, nicht für OSS-Maintainer. Sie berechnen pro Benutzer, pro Seite oder pro Workspace. Für ein Projekt, das von Freiwilligen ohne Budget gepflegt wird, ist das ein Ausschlusskriterium.

Wir haben die Community Edition von DocPlatform so entwickelt, dass sie für immer kostenlos ist, ohne Limits. Unbegrenzte Benutzer, unbegrenzte Seiten, unbegrenzte Workspaces. Kein „Free Tier", das Sie zum Upgrade drängt — die Community Edition ist das vollständige Produkt ohne Cloud-Hosting. So richten Sie es für Ihr Open-Source-Projekt ein.

## Das typische OSS-Dokumentations-Setup

Die meisten Open-Source-Projekte landen bei einem dieser Ansätze:

**GitHub Pages + Static-Site-Generator.** Sie schreiben Markdown-Dateien, konfigurieren eine Build-Pipeline und deployen auf GitHub Pages. Der häufigste Stack ist [Docusaurus](https://docusaurus.io/) (React-basiert) oder MkDocs (Python-basiert).

**Vorteile:** Kostenloses Hosting, versionskontrollierte Inhalte, vertrauter Git-Workflow.

**Nachteile:** Kein Web-Editor (Mitwirkende müssen Git, Markdown und das Build-System kennen), keine Echtzeit-Vorschau, keine Suche ohne Drittanbieterdienste (Algolia DocSearch hat eine Warteliste und einen Genehmigungsprozess), keine Kollaborationsfunktionen.

**Gehostete Plattform mit Free Tier.** GitBook, ReadMe oder Notion mit einer öffentlichen Seite. Sie bekommen einen Web-Editor und gehostete Suche.

**Vorteile:** Einfach zu starten, Web-Editor senkt die Hürde für nicht-technische Mitwirkende.

**Nachteile:** Free Tiers sind eingeschränkt (GitBook: 1 Space, eingeschränkte Integrationen; ReadMe: eingeschränkte API-Referenzen). Ihre Inhalte liegen auf dem Server eines Dritten. Wenn sich die Preise ändern oder der Dienst eingestellt wird, migrieren Sie unter Druck.

**Rohes Markdown im Repository.** Ein `docs/`-Ordner mit Markdown-Dateien. Kein Build-Schritt, kein Hosting, keine Suche.

**Vorteile:** Kein Setup. Inhalte sind versionskontrolliert.

**Nachteile:** Keine Möglichkeit für Benutzer, Dokumentation zu durchsuchen, ohne zu GitHub zu gehen. Keine Suche. Keine Navigationsstruktur außer Dateinamen.

## Ein besserer Ansatz

DocPlatform bietet Ihnen das Beste aus allen dreien: Inhalte als Markdown in Ihrem Git-Repository gespeichert, einen Web-Editor für nicht-technische Mitwirkende, Volltextsuche und eine veröffentlichte Dokumentationsseite — alles aus einem einzelnen Binary, das Sie überall hosten können.

So funktioniert die Einrichtung.

### Schritt 1: DocPlatform installieren

Auf jedem Linux-, macOS- oder Windows-Rechner:

```bash
curl -fsSL https://get.valoryx.org | sh
```

Oder laden Sie das Binary direkt von der [Installationsseite](/install/) herunter. Es gibt nichts anderes zu installieren — keine Datenbank, kein Docker, keine Laufzeitumgebung.

### Schritt 2: Server starten

```bash
docplatform serve
```

Öffnen Sie `http://localhost:3000`. Erstellen Sie Ihr Admin-Konto. Ihr Server läuft.

Für eine dauerhafte Einrichtung verwenden Sie einen systemd-Dienst:

```ini
[Unit]
Description=DocPlatform
After=network.target

[Service]
ExecStart=/opt/docplatform/bin/docplatform serve
WorkingDirectory=/opt/docplatform
Restart=always

[Install]
WantedBy=multi-user.target
```

### Schritt 3: Workspace erstellen

Ein Workspace in DocPlatform ist ein Dokumentationsprojekt. Für ein Open-Source-Projekt haben Sie typischerweise einen Workspace für Ihre öffentliche Dokumentation.

1. Gehen Sie zu Einstellungen → Workspaces → Erstellen
2. Benennen Sie ihn nach Ihrem Projekt (z. B. „MyProject Docs")
3. Wählen Sie ein Theme — es gibt 5 eingebaute Themes, alle für technische Dokumentation konzipiert

### Schritt 4: GitHub-Repository verbinden

Hier wird es interessant. DocPlatform unterstützt bidirektionalen Git-Sync — Bearbeitungen in der Web-Oberfläche werden in Ihr Repository committed, und Änderungen, die zum Repository gepusht werden, erscheinen in der Oberfläche.

1. Gehen Sie zu Workspace-Einstellungen → Git Sync
2. Fügen Sie Ihre Repository-URL hinzu: `https://github.com/yourorg/yourproject.git`
3. Konfigurieren Sie den Docs-Pfad (z. B. `docs/`, falls Ihr Markdown in einem Unterordner liegt)
4. Fügen Sie einen Deploy Key oder Personal Access Token für Push-Zugriff hinzu

Sobald verbunden, pullt DocPlatform Ihre vorhandenen Markdown-Dateien und indiziert sie für die Suche. Jede `.md`-Datei im konfigurierten Pfad wird zu einer Seite.

### Schritt 5: Dokumentation veröffentlichen

Schalten Sie „Veröffentlichen" in den Workspace-Einstellungen ein. DocPlatform generiert eine durchsuchbare Dokumentationsseite mit:

- Navigationsbaum basierend auf Ihrer Ordnerstruktur
- Volltextsuche mit Tippfehlertoleranz
- Responsives Design für mobile Geräte
- Syntaxhervorhebung für Code-Blöcke
- Dark-Mode-Umschaltung

Ihre veröffentlichte Dokumentation ist unter `http://yourserver:3000/docs/workspace-slug/` erreichbar.

## Der Git-Workflow

So sieht der Workflow in der Praxis für ein Open-Source-Projekt mit mehreren Mitwirkenden aus:

**Maintainer** verwenden den Web-Editor für schnelle Korrekturen — Tippfehler korrigieren, Seiten umstrukturieren, Screenshots aktualisieren. Jedes Speichern erstellt automatisch einen Git-Commit.

**Externe Mitwirkende** reichen PRs zum Docs-Verzeichnis in Ihrem GitHub-Repository ein, genau wie sie es für Code tun würden. Wenn Sie den PR mergen, übernimmt DocPlatform die Änderungen über Git-Sync und aktualisiert die veröffentlichte Seite.

**Nicht-technische Mitwirkende** (Community-Manager, technische Redakteure) verwenden den WYSIWYG-Editor im Browser. Sie müssen kein Git oder Markdown-Syntax kennen. Ihre Bearbeitungen werden trotzdem in das Repository committed.

Das bedeutet, Ihre Dokumentation hat denselben Review-Prozess wie Ihr Code. Möchten Sie, dass jemand eine Dokumentationsänderung überprüft, bevor sie live geht? Lassen Sie einen PR einreichen. Möchten Sie vertrauenswürdigen Mitwirkenden direkte Bearbeitung erlauben? Geben Sie ihnen Editor-Zugriff in DocPlatform.

## Vergleich: DocPlatform vs. Docusaurus

Da Docusaurus das beliebteste OSS-Dokumentationstool ist, hier ein direkter Vergleich:

| Feature | Docusaurus | DocPlatform CE |
|---|---|---|
| Web-Editor | Nein — Markdown bearbeiten, committen, auf Build warten | Ja — WYSIWYG, Änderungen sofort live |
| Suche | Erfordert Algolia DocSearch (Warteliste) oder Lunr.js (clientseitig, eingeschränkt) | Eingebaute Volltextsuche (Bleve) |
| Build-Schritt | Ja — React-Build, kann 30+ Sekunden dauern | Nein — Seiten rendern beim Speichern |
| Git-Integration | Nativ (es ist ein Static-Site-Generator) | Bidirektionaler Sync (Web ↔ Git) |
| Mehrere Versionen | Ja (versionierte Docs) | Workspace-basiert (ein Workspace pro Version) |
| Setup-Zeit | 10–30 Minuten (Node.js, npm, Konfiguration) | 2 Minuten (Binary herunterladen, ausführen) |
| Hosting | GitHub Pages, Netlify, Vercel (kostenlos) | Selbstgehostet (Sie brauchen einen Server) |
| RBAC | Keines (es ist ein Build-Tool) | 5 Rollen (Admin, Manager, Editor, Reviewer, Viewer) |
| i18n | Plugin-basiert | Workspace-basiert |

Docusaurus gewinnt, wenn Sie kostenloses Hosting auf GitHub Pages wollen und alle Ihre Mitwirkenden mit Git und React vertraut sind. DocPlatform gewinnt, wenn Sie einen Web-Editor, eingebaute Suche, Zugriffskontrolle brauchen oder Ihre Mitwirkenden nicht alle Entwickler sind.

## Hosting mit kleinem Budget

Ein häufiger Einwand: „Docusaurus ist kostenlos, weil GitHub Pages es hostet. Selbstgehostet bedeutet, ich brauche einen Server."

Stimmt. Aber Server sind günstig:

- **Hetzner CX22:** 2 vCPU, 4 GB RAM, 40 GB Disk — 3,99 EUR/Monat
- **Oracle Cloud Free Tier:** ARM-Instanz, 24 GB RAM — für immer kostenlos
- **Alter Laptop im Schrank:** Kostenlos, falls Sie einen haben

DocPlatform verwendet etwa 50 MB RAM im Leerlauf und 100–200 MB unter Last. Jeder Server, der ein Go-Binary ausführen kann, kann es betreiben.

Wenn Sie bereits einen CI-Server, einen Discord-Bot oder einen anderen Dienst für Ihr Projekt betreiben, kann DocPlatform auf derselben Maschine laufen.

## Echtes Setup: Von Null zur veröffentlichten Dokumentation

Gehen wir ein konkretes Beispiel durch. Sie pflegen ein CLI-Tool namens `fastgrep` und möchten von einem README zu richtiger Dokumentation wechseln.

```bash
# DocPlatform installieren
curl -fsSL https://get.valoryx.org | sh

# Server starten
docplatform serve &

# Browser öffnen, Admin-Konto erstellen, Workspace erstellen
# Verbinden mit github.com/yourname/fastgrep, Docs-Pfad: docs/

# Erste Seiten im Web-Editor erstellen:
# - Erste Schritte
# - Installation
# - Konfiguration
# - CLI-Referenz
# - Mitwirken
```

Jede Seite, die Sie im Web-Editor erstellen, wird in `docs/` in Ihrem Repository committed. Ihre bestehenden `docs/`-Markdown-Dateien (falls vorhanden) werden automatisch importiert.

Veröffentlichen Sie den Workspace, richten Sie Ihre Domain auf den Server, und Ihr Projekt hat durchsuchbare Dokumentation mit Web-Editor — eingerichtet in unter 5 Minuten.

Die vollständige Veröffentlichungseinrichtung finden Sie im [Veröffentlichungsleitfaden](/docs/guides/publishing/).

## Kostenlos heißt kostenlos

Die [Community Edition](/open-source/) ist kein Trial. Es ist kein eingeschränktes Free Tier. Es ist das vollständige Produkt:

- Unbegrenzte Benutzer und Editoren
- Unbegrenzte Workspaces und Seiten
- Volltextsuche
- Git-Sync
- RBAC mit 5 Rollen
- Alle 5 Themes
- WebAuthn/Passkey-Authentifizierung
- MCP-Server mit 13 KI-Tools

Das Einzige, was die Community Edition nicht enthält, ist Cloud-Hosting — Sie betreiben es auf Ihrer eigenen Infrastruktur. Für Open-Source-Projekte, die bereits ihre eigene Infrastruktur verwalten, ist das keine Einschränkung; es ist ein Feature.

[Laden Sie DocPlatform herunter](/install/) und geben Sie Ihrem Projekt die Dokumentation, die es verdient.
