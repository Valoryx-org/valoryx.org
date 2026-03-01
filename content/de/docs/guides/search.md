---
title: Suche
description: Sofortige Volltextsuche über Ihre gesamte Dokumentation mit berechtigungsgefilterten Ergebnissen.
weight: 6
---

# Suche

DocPlatform enthält eine eingebettete Volltextsuche (Bleve), die alle Inhalte automatisch indiziert. Kein externer Dienst zu konfigurieren — die Suche funktioniert sofort nach der Installation.

## Suche verwenden

### Cmd+K-Dialog

Drücken Sie `Cmd+K` (macOS) oder `Ctrl+K` (Windows/Linux) an beliebiger Stelle im Web-Editor, um den Suchdialog zu öffnen.

```
┌──────────────────────────────────────────┐
│  🔍  Search documentation...             │
├──────────────────────────────────────────┤
│                                          │
│  📄 Getting Started                      │
│     Install and configure DocPlatform... │
│                                          │
│  📄 API Authentication                   │
│     JWT tokens, OAuth2, and session...   │
│                                          │
│  📄 Docker Deployment                    │
│     Run DocPlatform as a container...    │
│                                          │
│  ↑↓ Navigate   ↵ Open   Esc Close       │
└──────────────────────────────────────────┘
```

### Was indiziert wird

Die Suchmaschine indiziert:

- **Seitentitel** (erhöhte Gewichtung für Ranking)
- **Seitenbeschreibung** (erhöhte Gewichtung)
- **Vollständiger Seiteninhalt** (Fließtext, Codeblöcke, Listen usw.)
- **Tags** (exakte Übereinstimmungs-Boosting)
- **Frontmatter-Metadaten**

### Suchsyntax

| Syntax | Beispiel | Beschreibung |
|---|---|---|
| Schlüsselwörter | `git sync` | Seiten, die sowohl "git" als auch "sync" enthalten |
| Exakte Phrase | `"bidirectional sync"` | Seiten mit der exakten Phrase |
| Präfix | `auth*` | Seiten mit Wörtern, die mit "auth" beginnen |
| Tag-Filter | `tag:api` | Seiten, die mit "api" getaggt sind |

## Berechtigungsfilterung

Suchergebnisse werden automatisch basierend auf den Berechtigungen des aktuellen Benutzers gefiltert:

- **Öffentliche Seiten** — in Suchergebnissen für alle authentifizierten Benutzer sichtbar
- **Workspace-Seiten** — nur für Workspace-Mitglieder sichtbar
- **Eingeschränkte Seiten** — nur für Benutzer mit der erforderlichen Rolle sichtbar

Ein Viewer kann eingeschränkte Admin-only-Seiten nicht über die Suche finden, selbst wenn der Inhalt der Abfrage entspricht. Diese Filterung erfolgt auf der Suchmaschinen-Ebene, nicht nach der Abfrage.

## Indizierung

### Automatische Indizierung

Inhalte werden inkrementell über eine asynchrone Job-Queue indiziert:

1. Eine Seite wird erstellt oder aktualisiert (über Editor oder Git-Synchronisation)
2. Das Content Ledger löst ein Event aus
3. Ein Such-Indizierungsjob wird in die Queue gestellt
4. Der Bleve-Indexer verarbeitet den Job und aktualisiert den Index

Es gibt eine kurze Verzögerung (typischerweise unter 1 Sekunde) zwischen dem Speichern einer Seite und dem Erscheinen des aktualisierten Inhalts in den Suchergebnissen.

### Suchindex neu aufbauen

Wenn der Suchindex nicht mehr synchron ist (selten — normalerweise nach einem Absturz oder manueller Dateimanipulation), bauen Sie ihn neu auf:

```bash
docplatform rebuild
```

Dies löscht den bestehenden Suchindex und indiziert alle Seiten aus dem Dateisystem neu. Der Prozess läuft im Hintergrund — der Server bleibt während des Neuaufbaus verfügbar.

### Indexzustand

Überprüfen Sie den Zustand des Suchindex mit dem Doctor-Befehl:

```bash
docplatform doctor
```

Der Doctor meldet:

- Anzahl der indizierten Dokumente im Vergleich zur Datenbankseiten-Anzahl
- Verwaiste Index-Einträge (indiziert, aber keine passende Seite)
- Fehlende Index-Einträge (Seite existiert, aber nicht indiziert)
- Index-Dateigröße und Zeitstempel der letzten Aktualisierung

## Suche in veröffentlichten Dokumenten

Veröffentlichte Dokumentationsseiten enthalten eine Suchoberfläche für Besucher. Die Sucheingabe erscheint im Seitenkopf und verwendet dieselbe Bleve-Engine.

Die Suche auf der öffentlichen Seite ist auf veröffentlichte Seiten beschränkt — unveröffentlichte oder eingeschränkte Inhalte erscheinen niemals in öffentlichen Suchergebnissen.

## Suchmaschinen-Interna

Für Benutzer, die verstehen möchten, wie die Suche unter der Haube funktioniert:

### Analyzer

Bleve verwendet standardmäßig den **englischen Analyzer**, der Folgendes umfasst:

- **Tokenisierung** — teilt Text an Leerzeichen und Satzzeichen
- **Kleinschreibung** — Groß-/Kleinschreibung wird nicht unterschieden
- **Stoppwort-Entfernung** — filtert häufige Wörter (the, is, at usw.)
- **Stemming** — erkennt Wortvarianten (running → run, documented → document)

### Feldgewichtung

Nicht alle Felder werden bei der Relevanzbewertung gleich gewichtet:

| Feld | Gewichtung | Beschreibung |
|---|---|---|
| `title` | Hoch | Seitentitel (relevantstes Signal) |
| `description` | Hoch | Seitenbeschreibung / Zusammenfassung |
| `tags` | Exakte Übereinstimmung | Schlüsselwortfeld — exakte Tag-Übereinstimmungen werden geboostet |
| `body` | Normal | Vollständiger Seiteninhalt |
| `path` | Schlüsselwort | Dateipfad — nur exakte Übereinstimmung |

Das bedeutet, dass eine Abfrage, die den Titel einer Seite trifft, höher rangiert als dieselbe Abfrage, die tief im Fließtext trifft.

### Speicherung

Der Bleve-Index wird unter `{DATA_DIR}/search-index/` gespeichert, unter Verwendung von bbolt (eine reine Go-B+-Baum-Datenbank). Der Index ist von der SQLite-Datenbank getrennt und kann sicher gelöscht und mit `docplatform rebuild` neu aufgebaut werden.

## Leistung

| Metrik | Wert |
|---|---|
| **Abfragelatenz** | < 8ms (p99) |
| **Indexgröße** | ~1 KB pro Seite (ungefähr) |
| **Maximal getesteter Korpus** | 1.000 Seiten |
| **Gleichzeitige Abfragen** | Unterstützt (thread-sicher) |
| **Indizierungslatenz** | < 1 Sekunde nach dem Speichern (asynchron) |

Die Suchleistung skaliert linear mit dem Inhaltsvolumen. Für Workspaces mit mehr als 10.000 Seiten wird eine zukünftige Version eine optionale Meilisearch-Integration bieten.
