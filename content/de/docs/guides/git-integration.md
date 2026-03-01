---
title: Git-Integration
description: Bidirektionale Git-Synchronisation — bearbeiten Sie im Browser oder pushen Sie aus Ihrer IDE, alles bleibt synchron.
weight: 3
---

# Git-Integration

Die bidirektionale Git-Synchronisation von DocPlatform ermöglicht es Ihrem Team, so zu arbeiten, wie es bevorzugt wird. Technische Redakteure nutzen den Web-Editor. Entwickler pushen aus ihrer IDE. Alle sehen denselben Inhalt.

## Wie es funktioniert

```
        ┌─────────────┐
        │ Web Editor   │
        │ (browser)    │
        └──────┬───────┘
               │ save
               ▼
        ┌─────────────┐          ┌──────────────┐
        │ Content     │  commit  │ Local Git    │  push    ┌──────────────┐
        │ Ledger      │ ───────► │ Repository   │ ───────► │ Remote Repo  │
        │             │          │ (.git)       │          │ (GitHub etc) │
        └─────────────┘          └──────┬───────┘          └──────┬───────┘
               ▲                        │                         │
               │ reconcile              │ pull                    │
               │                 ┌──────▼───────┐                 │
               └──────────────── │ Sync Engine  │ ◄───────────────┘
                                 │ (polling /   │   webhook / poll
                                 │  webhook)    │
                                 └──────────────┘
```

### Web → Git (ausgehend)

1. Sie speichern eine Seite im Web-Editor
2. Das Content Ledger schreibt die `.md`-Datei auf die Festplatte
3. Die Git-Engine erstellt automatisch einen Commit: `docs: update {page-title}`
4. Commits werden zum Remote-Repository gepusht

### Git → Web (eingehend)

1. Jemand pusht einen Commit zum Remote (aus IDE, CI usw.)
2. Die Sync-Engine erkennt die Änderung (Polling oder Webhook)
3. Änderungen werden zum lokalen Repository gepullt
4. Das Content Ledger reconciliert: Dateisystem → Datenbank → Suchindex
5. WebSocket sendet die Aktualisierung an verbundene Browser

## Einrichtung

### Remote-Repository verbinden

**Während der Initialisierung:**

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

**Nach der Initialisierung** — bearbeiten Sie die Workspace-Konfiguration:

```yaml
# .docplatform/workspaces/{id}/.docplatform/config.yaml
git_remote: git@github.com:your-org/docs.git
git_branch: main
git_auto_commit: true
sync_interval: 300
```

Starten Sie den Server neu oder lösen Sie eine manuelle Synchronisation aus.

### Authentifizierung

#### SSH (empfohlen)

Generieren Sie einen Deploy-Key und fügen Sie ihn Ihrem Repository hinzu:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""
```

Setzen Sie die Umgebungsvariable:

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

Fügen Sie den öffentlichen Schlüssel (`~/.ssh/docplatform_deploy_key.pub`) zu den Deploy-Keys Ihres Repositories hinzu. **Aktivieren Sie den Schreibzugriff**, wenn DocPlatform Commits pushen soll.

#### HTTPS mit Token

Für HTTPS-Repositories betten Sie den Token in die URL ein:

```yaml
git_remote: https://x-access-token:ghp_xxxxxxxxxxxx@github.com/your-org/docs.git
```

Oder verwenden Sie einen Git-Credential-Helper, der auf dem Host konfiguriert ist.

## Synchronisationsverhalten

### Auto-Commit

Wenn `git_auto_commit: true` (Standard), erzeugt jede Speicherung im Web-Editor einen Git-Commit. Schnelle Bearbeitungen innerhalb eines kurzen Zeitfensters werden zu einem einzelnen Commit zusammengefasst.

Commit-Nachrichtenformat:

```
docs: update Getting Started

Edited via DocPlatform web editor
Author: jane@example.com
```

Setzen Sie `git_auto_commit: false`, um Auto-Commit zu deaktivieren. In diesem Modus schreibt der Web-Editor auf das Dateisystem, erstellt aber keine Git-Commits — nützlich, wenn Sie manuell oder nach Zeitplan committen möchten.

### Polling

DocPlatform pollt das Remote-Repository im konfigurierten Intervall (Standard: 300 Sekunden / 5 Minuten). Anpassen mit:

```yaml
sync_interval: 60  # jede Minute prüfen
```

Kürzere Intervalle bedeuten schnellere Synchronisation, aber mehr Netzwerkverkehr.

### Webhooks

Für sofortige Synchronisation konfigurieren Sie einen Webhook in Ihrem Repository:

**GitHub:**

1. Gehen Sie zu **Settings** → **Webhooks** → **Add webhook**
2. Payload URL: `https://your-domain.com/api/v1/webhooks/github`
3. Content type: `application/json`
4. Secret: Setzen Sie die Umgebungsvariable `GIT_WEBHOOK_SECRET` auf denselben Wert
5. Events: Wählen Sie **Push events**

**GitLab:**

1. Gehen Sie zu **Settings** → **Webhooks**
2. URL: `https://your-domain.com/api/v1/webhooks/gitlab`
3. Secret token: Muss mit `GIT_WEBHOOK_SECRET` übereinstimmen
4. Trigger: **Push events**

**Bitbucket:**

1. Gehen Sie zu **Repository settings** → **Webhooks** → **Add webhook**
2. URL: `https://your-domain.com/api/v1/webhooks/bitbucket`
3. Triggers: **Repository push**

### Manuelle Synchronisation

Lösen Sie eine Synchronisation über die Web-Oberfläche aus (**Settings** → **Git** → **Sync Now**) oder über die API:

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{id}/sync \
  -H "Authorization: Bearer {token}"
```

## Konfliktauflösung

Konflikte treten auf, wenn dieselbe Datei sowohl im Web-Editor als auch über einen Git-Push zwischen Synchronisationsintervallen geändert wird.

### Wie Konflikte erkannt werden

DocPlatform verfolgt Content-Hashes (SHA-256) für jede Seite. Beim Pullen von Remote-Änderungen wird der eingehende Hash mit dem lokalen Hash verglichen. Wenn beide vom gemeinsamen Vorfahren abweichen, wird ein Konflikt deklariert.

### Was bei einem Konflikt passiert

1. Die Speicher- oder Synchronisationsoperation gibt **HTTP 409 Conflict** zurück
2. Beide Versionen (lokal und remote) werden aufbewahrt
3. Die Web-Oberfläche zeigt ein Konflikt-Banner mit Optionen:
   - **Keep local** — die Remote-Version verwerfen
   - **Keep remote** — die lokale Version verwerfen
   - **Download both** — beide Dateien für manuelles Zusammenführen herunterladen
4. Ein Konflikt-Branch (`conflict/{page-slug}-{timestamp}`) wird mit der lokalen Version erstellt

### Konflikte vermeiden

- **Verwenden Sie Webhooks** statt Polling — schnellere Synchronisation bedeutet kleinere Konfliktfenster
- **Weisen Sie Seitenverantwortung zu** — ein Autor pro Seite reduziert das Kollisionsrisiko
- **Nutzen Sie den Web-Editor für Inhalte**, die IDE für Code — natürliche Trennung
- **Kurze Synchronisationsintervalle** — `sync_interval: 30` in Umgebungen mit hoher Zusammenarbeit

## Batch-Synchronisation

Wenn ein Remote-Push mehr als 20 geänderte Dateien enthält, wechselt DocPlatform in den Batch-Modus:

1. Ruft alle geänderten Dateien in einem einzelnen Diff ab
2. Erwirbt pfadspezifische Mutexe für alle betroffenen Pfade (sortiert zur Vermeidung von Deadlocks)
3. Verarbeitet alle Dateien in einer einzelnen Datenbanktransaktion
4. Invalidiert den Berechtigungs-Cache einmal (nicht pro Datei)
5. Sendet eine einzelne `bulk-sync` WebSocket-Nachricht mit der Gesamtanzahl der Änderungen

Dies verhindert Benachrichtigungsstürme und Datenbanküberlastung, wenn große Änderungen gepusht werden (z. B. initialer Repository-Import oder umfangreiche Umstrukturierung).

## Konfliktspeicherung

Wenn ein Konflikt erkannt wird, werden beide Versionen auf der Festplatte gespeichert:

```
.docplatform/conflicts/
└── {page-id}/
    └── 20250115T103045Z/
        ├── ours.md      # Lokale Version (Web-Editor)
        └── theirs.md    # Remote-Version (Git-Push)
```

Konflikte bestehen, bis sie explizit über die Web-Oberfläche oder API aufgelöst werden. Der `docplatform doctor`-Befehl meldet ungelöste Konflikte.

## Git-Engine-Details

DocPlatform verwendet eine hybride Git-Engine, die automatisch das beste Backend auswählt:

| Bedingung | Engine | Warum |
|---|---|---|
| Unter 5.000 Dateien | **go-git** (In-Process) | Schnell, keine externe Abhängigkeit, reines Go |
| Über 5.000 Dateien | **Native Git-CLI** (Subprozess) | Bessere Handhabung großer Repositories, Shallow Clones |
| go-git RSS > 512 MB | **Native Git-CLI** (Fallback) | Speichersicherheit — verhindert OOM bei großen Repositories |

Ein Worker-Pool von **4 gleichzeitigen Workern** bearbeitet Git-Operationen über alle Workspaces hinweg. Jeder Workspace hat seinen eigenen Mutex — Operationen auf verschiedenen Workspaces laufen parallel, während Operationen auf demselben Workspace serialisiert werden.

Auto-Commit-Nachrichten verwenden dieses Format:

```
docs: update {page-title}

Edited via DocPlatform web editor
Author: user@example.com
Committer: DocPlatform <docplatform@local>
```

## Arbeiten mit bestehenden Repositories

DocPlatform funktioniert mit bestehenden Dokumentations-Repositories. Wenn Sie ein Repository verbinden:

1. Das Repository wird geklont (oder gepullt, wenn es bereits lokal existiert)
2. Alle `.md`-Dateien im `docs/`-Verzeichnis werden indiziert
3. Frontmatter wird geparst und Seiten-Metadaten in SQLite gespeichert
4. Der Suchindex wird inkrementell aufgebaut

Dateien außerhalb von `docs/` werden nicht indiziert oder im Editor angezeigt, verbleiben aber unberührt im Git-Repository.

### Import von anderen Plattformen

DocPlatform funktioniert mit jedem Markdown-Inhalt. So migrieren Sie von gängigen Plattformen:

| Quelle | Export-Methode | Hinweise |
|---|---|---|
| **Docusaurus** | Direkte Kopie | Bereits `.md`-basiert — kopieren Sie das `docs/`-Verzeichnis unverändert, fügen Sie bei Bedarf Frontmatter hinzu |
| **GitBook** | JSON-Export → konvertieren | Export über GitBook API, Konvertierung zu Markdown |
| **Notion** | Markdown-Export | Workspace als Markdown exportieren, in `docs/`-Hierarchie umstrukturieren |
| **Confluence** | HTML-Export → konvertieren | Bereiche als HTML exportieren, mit pandoc oder ähnlichem zu Markdown konvertieren |
| **Wiki.js** | Datenbank-Export | Seiten als Markdown aus dem Admin-Panel exportieren |

**Allgemeine Migrationsschritte:**

1. Exportieren Sie Ihre Inhalte als Markdown-Dateien
2. Platzieren Sie sie in einem Git-Repository unter `docs/`
3. Fügen Sie YAML-Frontmatter (mindestens `title`) zu jeder Datei hinzu
4. Verbinden Sie das Repository mit DocPlatform
5. Führen Sie `docplatform rebuild` aus, um eine vollständige Reconciliation zu erzwingen

Der Reconciler von DocPlatform entdeckt automatisch alle `.md`-Dateien, parst deren Frontmatter, weist Seiten ohne `id`-Feld ULIDs zu und erstellt den Suchindex.
