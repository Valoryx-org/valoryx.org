---
title: DocPlatform Community Edition
description: Selbst gehostete, git-gestützte Dokumentationsplattform mit einem ansprechenden Web-Editor. Behalten Sie die Kontrolle über Ihre Dokumente und Ihren Workflow.
weight: 1
---

# DocPlatform Community Edition

DocPlatform ist eine selbst gehostete Dokumentationsplattform, die einen leistungsfähigen Web-Editor mit bidirektionaler Git-Synchronisation kombiniert — verpackt als einzelne Binärdatei ohne externe Abhängigkeiten.

Schreiben Sie im Browser. Pushen Sie aus Ihrer IDE. Alles bleibt synchron.

## Warum DocPlatform

Dokumentationsplattformen zwingen Sie zu einer Entscheidung: ein ausgefeilter Web-Editor mit Herstellerbindung oder Rohdateien in Git ohne Kollaborationsfunktionen. DocPlatform beseitigt diesen Kompromiss.

| Was Sie erhalten | Wie es funktioniert |
|---|---|
| **Einzelne Binärdatei, keine Abhängigkeiten** | Eine Go-Binärdatei bündelt den Editor, die Datenbank, die Suchmaschine und die Git-Engine. Kein Node.js-Runtime, kein Postgres, kein Elasticsearch. |
| **Jede Seite ist eine `.md`-Datei** | Ihre Inhalte liegen als Markdown-Dateien in einem echten Git-Repository. Keine proprietären Formate. Kein Export erforderlich. |
| **Bidirektionale Git-Synchronisation** | Bearbeiten Sie im Browser — Änderungen werden automatisch committet und gepusht. Pushen Sie aus Ihrer IDE — die Web-Oberfläche aktualisiert sich automatisch. |
| **Ansprechende veröffentlichte Dokumentation** | Ein Klick zum Veröffentlichen einer Dokumentationsseite mit Dark Mode, Syntax-Highlighting und 7 integrierten Komponenten. |
| **Teamzusammenarbeit** | 6-stufige Rollenhierarchie, Workspace-Einladungen, Echtzeit-Präsenzanzeigen und vollständiger Audit-Trail. |
| **Volltextsuche** | Eingebettete Suchmaschine mit sofortigen Ergebnissen. Kein externer Dienst zu konfigurieren. |

## Für wen es gedacht ist

DocPlatform Community Edition ist konzipiert für:

- **Open-Source-Maintainer**, die Projektdokumentation im Repository führen, aber eine bessere Bearbeitungserfahrung als rohes Markdown in GitHub wünschen
- **Interne Plattform- / DevEx-Teams**, die Docs-as-Code mit Zugriffskontrolle und Web-Editor benötigen — nicht das eine oder das andere
- **Kleine Entwicklungsagenturen**, die mehrere Kundendokumentations-Repositories mit Git-Backup verwalten und keine bezahlbare selbst gehostete Option haben
- **Technische Redakteure**, die eine ausgefeilte Autorenerfahrung mit Versionskontrolle benötigen
- **Einzelentwickler**, die eine persönliche Wissensdatenbank mit öffentlicher Veröffentlichung möchten — ohne Abonnement

**Nicht die Zielgruppe:** Compliance-intensive Unternehmen, die SAML/SCIM benötigen (siehe zukünftige Enterprise Edition), oder nicht-technische Content-Teams ohne Git-Erfahrung.

## Wie es funktioniert

```
┌──────────────────────────────────────────────────┐
│              DocPlatform (single binary)          │
│                                                  │
│   ┌────────────┐  ┌──────────┐  ┌────────────┐  │
│   │ Web Editor  │  │ SQLite   │  │ Bleve      │  │
│   │ (Next.js)   │  │ Database │  │ Search     │  │
│   └──────┬──────┘  └────┬─────┘  └──────┬─────┘  │
│          │              │               │        │
│          └──────┬───────┴───────┬───────┘        │
│                 │               │                │
│          ┌──────▼──────┐ ┌─────▼──────┐         │
│          │ Content     │ │ Git        │         │
│          │ Ledger      │ │ Engine     │         │
│          └──────┬──────┘ └─────┬──────┘         │
│                 │              │                 │
└─────────────────┼──────────────┼─────────────────┘
                  │              │
           ┌──────▼──────┐ ┌────▼──────┐
           │ Filesystem  │ │ Remote    │
           │ (.md files) │ │ Git Repo  │
           └─────────────┘ └───────────┘
```

Jede Inhaltsänderung — ob über den Web-Editor, einen Git-Push oder einen API-Aufruf — durchläuft das **Content Ledger**, eine zentrale Pipeline, die Dateisystem, Datenbank und Suchindex in perfekter Synchronisation hält.

## Schnellstart

DocPlatform in unter 5 Minuten zum Laufen bringen:

```bash
# Binary herunterladen (empfohlen — erkennt die Plattform automatisch)
curl -fsSL https://valoryx.org/install.sh | sh

# Einen Workspace initialisieren
docplatform init --workspace-name "My Docs" --slug my-docs

# Server starten
docplatform serve
```

Öffnen Sie [http://localhost:3000](http://localhost:3000) und registrieren Sie Ihren ersten Benutzer — dieser wird automatisch zum SuperAdmin.

Die vollständige Anleitung finden Sie im [Erste Schritte](getting-started/index.md)-Leitfaden.

## Funktionsübersicht

### Kernplattform

- **Leistungsfähiger Web-Editor** — Tiptap-basierter Editor mit Frontmatter-Formular, Raw-Markdown-Umschalter und automatischem Speichern
- **Bidirektionale Git-Synchronisation** — Web → Git-Commit → Push; CLI-Push → Polling → Web-Aktualisierung
- **Konflikterkennung** — Hash-basierte optimistische Nebenläufigkeit mit herunterladbarem Diff bei Kollisionen
- **Volltextsuche** — Eingebettete Bleve-Engine mit berechtigungsgefilterten Ergebnissen und Cmd+K-Tastenkürzel
- **RBAC-Berechtigungen** — 6 Rollen: SuperAdmin, WorkspaceAdmin, Admin, Editor, Commenter, Viewer
- **Authentifizierung** — Lokal (argon2id) + optionales Google/GitHub OIDC
- **Workspace-Modell** — Organisation → Workspace → Seitenhierarchie mit Team-Einladungen
- **Audit-Trail** — Jede Mutation wird mit Benutzer, Zeitstempel und Operationstyp protokolliert

### Veröffentlichte Dokumentation

- **Öffentliche Seite** — Dokumentation unter `/p/{workspace-slug}/{page-path}` bereitstellen
- **Dark Mode** — Automatisches helles/dunkles Farbschema mit manuellem Umschalter
- **7 integrierte Komponenten** — Callout, Code (200+ Sprachen), Tabs, Accordion, Cards, Steps, API Block
- **SEO-fähig** — OpenGraph-Tags, kanonische URLs, sitemap.xml, robots.txt

### Betrieb

- **Diagnosefunktionen** — 9-Punkte-`doctor`-Befehl prüft FS/DB-Konsistenz, Suchstatus, defekte Links
- **Tägliche Backups** — Automatisierte SQLite-Backups mit konfigurierbarer Aufbewahrungsdauer
- **Kontrolliertes Herunterfahren** — Saubere Signalbehandlung für Deployments ohne Ausfallzeit
- **Strukturiertes Logging** — JSON-Logs mit Request-IDs für Observability

## Systemanforderungen

| Anforderung | Minimum | Empfohlen |
|---|---|---|
| **Betriebssystem** | Linux (amd64/arm64), macOS (amd64/arm64) | Linux amd64 |
| **Arbeitsspeicher** | 128 MB | 512 MB |
| **Festplatte** | 200 MB (Binärdatei + Daten) | 1 GB |
| **Git** | Optional (für Remote-Synchronisation) | Git 2.30+ |
| **Netzwerk** | Keines (läuft offline) | Port 3000 geöffnet |

## Nächste Schritte

| Leitfaden | Beschreibung |
|---|---|
| [Erste Schritte](getting-started/index.md) | Installation, Konfiguration und Erstellung Ihres ersten Workspace |
| [Benutzerhandbücher](guides/editor.md) | Editor, Git-Synchronisation, Veröffentlichung und Suche kennenlernen |
| [Konfiguration](configuration/index.md) | Umgebungsvariablen, Authentifizierung, Berechtigungen und Workspace-Einstellungen |
| [Deployment](deployment/binary.md) | Produktions-Deployment mit Binärdatei, Docker oder Containern |
| [CLI-Referenz](reference/cli.md) | Vollständige Befehlsreferenz |
| [API-Referenz](reference/api.md) | REST-API-Endpunkte und Beispiele |
| [Fehlerbehebung](reference/troubleshooting.md) | Häufige Probleme und deren Lösung |

## Leistung

Gemessen auf Apple M2, NVMe SSD, 1.000-Seiten-Workspace:

| Operation | Latenz |
|---|---|
| Seite speichern (Sync-Kern) | < 30ms |
| Seite rendern (API-Antwort) | < 50ms p99 |
| Volltextsuche | < 8ms p99 |
| Berechtigungsprüfung | < 0,1ms |
| Berechtigungs-Batch (100 Seiten) | < 1ms |
| Server-Kaltstart | < 1 Sekunde |
| Vollständige Reconciliation (1.000 Dateien) | < 5 Sekunden |
| Git-Commit (einzelne Datei) | < 2 Sekunden |
| Speicher (Leerlauf) | < 80 MB |
| Speicher (10 gleichzeitige Benutzer) | < 200 MB |
| Binärgröße | ~120 MB |

## Wie DocPlatform im Vergleich abschneidet

| Fähigkeit | DocPlatform | GitBook | Notion | Docusaurus | Confluence | Wiki.js |
|---|---|---|---|---|---|---|
| Selbst gehostet | Ja | Nein | Nein | Ja | Nein | Ja |
| Git-gestützt | Ja | Teilweise | Nein | Ja | Nein | Nein |
| Web-Editor | Ja | Ja | Ja | Nein | Ja | Ja |
| Bidirektionale Git-Synchronisation | Ja | Nein | Nein | N/A | Nein | Nein |
| Einzelne Binärdatei (keine Abhängigkeiten) | Ja | N/A | N/A | Nein (Node.js) | N/A | Docker |
| Integriertes RBAC | Ja | Kostenpflichtig | Kostenpflichtig | Nein | Ja | Ja |
| Veröffentlichte Dokumentationsseite | Ja | Ja | Ja | Ja | Ja | Ja |
| Open Source | Ja | Nein | Nein | Ja | Nein | Ja |
| Offline-fähig | Ja | Nein | Nein | Ja | Nein | Nein |

## Community Edition Limits

Die Community Edition ist der voll funktionsfähige, selbst gehostete Kern von DocPlatform. Sie umfasst alles, was auf dieser Seite dokumentiert ist, mit folgenden Einschränkungen:

| Ressource | Community Edition |
|---|---|
| **Editoren** (Benutzer, die Seiten erstellen/bearbeiten können) | Bis zu 5 |
| **Workspaces** | Bis zu 3 |
| **Viewer und Commenter** | Unbegrenzt (werden nie gezählt) |
| **Seiten pro Workspace** | Unbegrenzt |
| **Veröffentlichte Dokumentation** | Unbegrenzt |

Diese Limits decken die Mehrheit kleiner bis mittlerer Teams ab. Die zukünftige Enterprise Edition wird unbegrenzte Editoren, unbegrenzte Workspaces, SAML/SSO, PostgreSQL-Unterstützung und erweiterte Suche über Meilisearch bieten — aber die Community Edition wird immer die vollständige, selbst hostbare Grundlage bleiben.
