---
title: CLI-Referenz
description: Vollständige Referenz aller DocPlatform-CLI-Befehle — serve, init, rebuild, doctor und version.
weight: 2
---

# CLI-Referenz

DocPlatform bietet 5 CLI-Befehle für Serververwaltung, Workspace-Initialisierung, Diagnose und Wartung.

## Globale Optionen

Diese Optionen gelten für alle Befehle:

| Flag | Beschreibung |
|---|---|
| `--help`, `-h` | Hilfe für jeden Befehl anzeigen |
| `--version`, `-v` | Versionsinformationen ausgeben |

## `docplatform serve`

HTTP-Server starten.

```bash
docplatform serve [flags]
```

### Flags

| Flag | Standard | Beschreibung |
|---|---|---|
| `--port` | `3000` | HTTP-Listening-Port (überschreibt Umgebungsvariable `PORT`) |
| `--host` | `0.0.0.0` | HTTP-Listening-Adresse (überschreibt Umgebungsvariable `HOST`) |
| `--data-dir` | `.docplatform` | Datenverzeichnispfad (überschreibt Umgebungsvariable `DATA_DIR`) |

### Verhalten

- Lädt Umgebungsvariablen aus der `.env`-Datei (falls vorhanden)
- Initialisiert die SQLite-Datenbank im WAL-Modus
- Führt ausstehende Datenbankmigrationen aus
- Lädt Casbin-Berechtigungsrichtlinien in den Speicher
- Baut den Bleve-Suchindex auf oder öffnet ihn
- Startet die Git-Sync-Engine für alle konfigurierten Workspaces
- Startet den Backup-Scheduler (wenn aktiviert)
- Stellt den Web-Editor und die API auf dem konfigurierten Port bereit

### Startsequenz

Wenn `docplatform serve` ausgeführt wird, geschieht Folgendes der Reihe nach:

1. Konfiguration laden (Umgebungsvariablen + `.env`-Datei + Standardwerte)
2. SQLite-Datenbank öffnen (WAL-Modus) und ausstehende Migrationen ausführen
3. Standardorganisation erstellen, wenn dies der erste Start ist
4. Dienste initialisieren: Content Ledger, Git-Engine (Worker-Pool von 4), Suchmaschine, Berechtigungsdienst, Auth-Dienst, WebSocket-Hub
5. Hintergrund-Goroutines starten: WebSocket-Hub, Git-Sync-Polling, Backup-Scheduler, Telemetrie (wenn aktiviert)
6. Auf dem konfigurierten Host:Port lauschen

Leseanfragen werden sofort bedient. Wenn Workspaces bestehende Inhalte haben, läuft die Reconciliation im Hintergrund ohne Blockierung.

### Signale

| Signal | Wirkung |
|---|---|
| `SIGTERM` | Kontrolliertes Herunterfahren — keine neuen Anfragen annehmen, laufende Operationen abschließen, Datenbank flushen |
| `SIGINT` | Wie SIGTERM (Ctrl+C) |

**Herunterfahrsequenz** (15-Sekunden-Frist):

1. Anwendungskontext abbrechen (signalisiert allen Goroutines, zu stoppen)
2. WebSocket-Hub stoppen (alle Client-Verbindungen schließen)
3. Git-Sync-Manager stoppen (laufende Sync-Operationen abschließen)
4. Suchmaschine schließen (Bleve-Index auf Festplatte flushen)
5. Git-Worker-Pool leeren (auf laufende Git-Operationen warten)
6. HTTP-Server herunterfahren (10-Sekunden-Timeout für laufende Anfragen)

Wenn das Herunterfahren 15 Sekunden überschreitet, wird der Prozess zwangsweise beendet.

### Beispiel

```bash
# Auf Standardport starten
docplatform serve

# Auf benutzerdefiniertem Port starten
docplatform serve --port 8080

# Mit explizitem Datenverzeichnis starten
docplatform serve --data-dir /var/lib/docplatform
```

### Ausgabe

```
INFO  Server starting            port=3000 version=v0.5.0
INFO  Database initialized       path=.docplatform/data.db wal=true
INFO  Migrations applied         count=1
INFO  Search index ready         documents=42
INFO  Workspace loaded           name="Docs" slug=docs git_remote=git@github.com:...
INFO  Backup scheduler started   retention_days=7
INFO  Listening on               http://0.0.0.0:3000
```

---

## `docplatform init`

Einen neuen Workspace initialisieren.

```bash
docplatform init [flags]
```

### Flags

| Flag | Erforderlich | Standard | Beschreibung |
|---|---|---|---|
| `--workspace-name` | Ja | — | Anzeigename für den Workspace |
| `--slug` | Ja | — | URL-sicherer Bezeichner (verwendet in der URL veröffentlichter Dokumentation) |
| `--git-url` | Nein | — | Remote-Git-Repository-URL (SSH oder HTTPS) |
| `--branch` | Nein | `main` | Git-Branch zur Synchronisation |
| `--data-dir` | Nein | `.docplatform` | Datenverzeichnispfad |

### Verhalten

1. Erstellt die Datenverzeichnisstruktur (`{DATA_DIR}/`)
2. Initialisiert die SQLite-Datenbank (wenn noch nicht vorhanden)
3. Generiert einen RS256-JWT-Signaturschlüssel (wenn noch nicht vorhanden)
4. Erstellt das Workspace-Verzeichnis (`{DATA_DIR}/workspaces/{ulid}/`)
5. Wenn `--git-url` angegeben, wird das Repository geklont
6. Erstellt die Workspace-Konfigurationsdatei
7. Indiziert vorhandene `.md`-Dateien

### Beispiel

```bash
# Lokaler Workspace (ohne Git)
docplatform init \
  --workspace-name "Internal Wiki" \
  --slug wiki

# Mit Git
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git \
  --branch main
```

### Ausgabe

```
INFO  Data directory created     path=.docplatform
INFO  Database initialized       path=.docplatform/data.db
INFO  JWT key generated          path=.docplatform/jwt-key.pem
INFO  Workspace created          id=01KJJ10NTF... name="API Docs" slug=api-docs
INFO  Repository cloned          url=git@github.com:your-org/api-docs.git branch=main
INFO  Pages indexed              count=15
INFO  Ready. Run 'docplatform serve' to start.
```

---

## `docplatform rebuild`

Datenbank und Suchindex aus dem Dateisystem neu aufbauen. Verwenden Sie diesen Befehl, wenn die Datenbank nicht mehr mit den tatsächlichen Dateien auf der Festplatte synchron ist.

```bash
docplatform rebuild [flags]
```

### Flags

| Flag | Erforderlich | Standard | Beschreibung |
|---|---|---|---|
| `--workspace-id` | Nein | alle | ULID eines spezifischen Workspace zum Neuaufbau. Ohne dieses Flag werden alle Workspaces neu aufgebaut. |
| `--search` | Nein | `false` | Auch den Bleve-Suchindex löschen und neu aufbauen |
| `--data-dir` | Nein | `.docplatform` | Datenverzeichnispfad |

### Verhalten

1. Erstellt ein Backup der aktuellen Datenbank
2. Löscht die `pages`-Tabelle
3. Durchsucht das Dateisystem nach allen `.md`-Dateien in Workspace-`docs/`-Verzeichnissen
4. Parst Frontmatter und Inhalt jeder Datei
5. Fügt Seitendatensätze in die Datenbank ein
6. Baut den Bleve-Suchindex neu auf
7. Meldet Reconciliation-Ergebnisse

### Wann zu verwenden

- Nach manuellem Hinzufügen, Verschieben oder Löschen von `.md`-Dateien außerhalb von DocPlatform
- Nach einem Absturz, der möglicherweise die Datenbank inkonsistent hinterlassen hat
- Nach dem Wiederherstellen von Dateien aus einem Git-Backup
- Wenn `docplatform doctor` FS/DB-Abweichungen meldet

### Beispiel

```bash
# Alle Workspaces neu aufbauen
docplatform rebuild

# Einen spezifischen Workspace neu aufbauen
docplatform rebuild --workspace-id 01KJJ10NTF31Z1QJTG4ZRQZ2Z2
```

### Ausgabe

```
INFO  Backup created             path=.docplatform/backups/pre-rebuild-20250115.db
INFO  Rebuilding workspace       id=01KJJ10NTF... name="API Docs"
INFO  Scanning filesystem        path=.docplatform/workspaces/01KJJ.../docs/
INFO  Pages found                count=42
INFO  Database rebuilt            inserted=42 updated=0 orphaned=3
INFO  Search index rebuilt        documents=42
INFO  Ghost recovery             matched=2 unmatched=1
INFO  Rebuild complete
```

**Ghost Recovery:** Wenn verwaiste Datenbankdatensätze (keine passende Datei) gefunden werden, versucht DocPlatform, sie anhand des Content-Hash mit nicht-indizierten Dateien abzugleichen. Dies stellt Seiten wieder her, die außerhalb von DocPlatform verschoben oder umbenannt wurden.

---

## `docplatform doctor`

9 Diagnoseprüfungen zum Plattformzustand ausführen.

```bash
docplatform doctor [flags]
```

### Flags

| Flag | Erforderlich | Standard | Beschreibung |
|---|---|---|---|
| `--bundle` | Nein | `false` | ZIP-Datei mit Diagnoseausgabe für Support erstellen |
| `--data-dir` | Nein | `.docplatform` | Datenverzeichnispfad |

### Prüfungen

| # | Prüfung | Beschreibung |
|---|---|---|
| 1 | **Datenbankverbindung** | SQLite-Datei existiert, ist lesbar, WAL-Modus aktiviert |
| 2 | **Schema-Version** | Migrationen sind aktuell |
| 3 | **FS/DB-Konsistenz** | Jede Datei in `docs/` hat einen Datenbankdatensatz und umgekehrt |
| 4 | **Verwaiste Dateien** | Dateien auf der Festplatte ohne Datenbankdatensatz |
| 5 | **Verwaiste Datensätze** | Datenbankdatensätze ohne Datei auf der Festplatte |
| 6 | **Suchindex-Zustand** | Bleve-Index-Dokumentanzahl stimmt mit Seitenanzahl überein |
| 7 | **Defekte interne Links** | Markdown-Links, die auf nicht existierende Seiten zeigen |
| 8 | **Frontmatter-Gültigkeit** | Alle Seiten haben gültiges YAML-Frontmatter mit einem Titel |
| 9 | **Git-Remote-Erreichbarkeit** | Wenn Git konfiguriert ist, kann das Remote erreicht werden? |

### Exit-Codes

| Code | Bedeutung |
|---|---|
| `0` | Alle Prüfungen bestanden (gesund) |
| `1` | Eine oder mehrere Prüfungen fehlgeschlagen oder mit Warnungen |

Verwenden Sie den Exit-Code in Skripten und Monitoring:

```bash
docplatform doctor || echo "Health check failed"
```

### Beispiel

```bash
docplatform doctor
```

### Ausgabe

```
DocPlatform Health Check
========================

✓ Database connection          OK (WAL mode, 42 pages, 3 users)
✓ Schema version               OK (v1, up to date)
✓ FS/DB consistency            OK (42 files, 42 records)
✓ Orphaned files               OK (0 found)
✓ Orphaned records             OK (0 found)
✓ Search index health          OK (42 indexed, 42 expected)
⚠ Broken internal links        WARNING (2 broken links found)
  → guides/editor.md:15 → "old-page.md" (file not found)
  → api/endpoints.md:42 → "deprecated.md" (file not found)
✓ Frontmatter validity         OK (42/42 valid)
✓ Git remote connectivity      OK (git@github.com:your-org/docs.git)

Result: 8/9 passed, 1 warning
```

### Bundle-Modus

```bash
docplatform doctor --bundle
# Erstellt: docplatform-doctor-20250115.zip
```

Das Bundle wird unter `{DATA_DIR}/diagnostics/docplatform-diagnostics-{timestamp}.zip` gespeichert und enthält:

- `report.json` — strukturierte Diagnoseergebnisse
- Schema-Informationen (Tabellendefinitionen, keine Zeilendaten)
- Dateiliste (Pfade und Größen, keine Inhalte)
- Systeminformationen (Betriebssystem, Architektur, Go-Version)
- Letzte 1.000 Zeilen der Fehler-Logs
- Serverversion und Konfiguration (mit geschwärzten Secrets)

Das Bundle enthält **niemals** Seiteninhalte, Passwörter, Token oder private Schlüssel.

---

## `docplatform version`

Version, Commit-Hash und Build-Datum ausgeben.

```bash
docplatform version
```

### Ausgabe

```
docplatform v0.5.0 (commit: abc1234, built: 2025-01-15T10:00:00Z)
```

Die Versionsinformationen werden beim Build über Linker-Flags eingebettet. Nützlich zur Verifizierung, welches Release deployt ist, und für Support-Anfragen.
