---
title: "Dokumentation in 5 Minuten selbst hosten"
description: "Schritt-für-Schritt-Anleitung: DocPlatform herunterladen, ein einzelnes Binary starten, den ersten Workspace erstellen und Dokumentation veröffentlichen. Kein Docker, keine Datenbank."
date: "2026-03-02"
author: "Valoryx Team"
tags: ["self-hosted", "tutorial", "documentation"]
---

Die meisten selbstgehosteten Dokumentationstools erfordern eine Datenbank, einen Reverse-Proxy und einen halben Nachmittag YAML-Bearbeitung, bevor Sie einen Willkommensbildschirm sehen. DocPlatform ist ein einzelnes Go-Binary ohne externe Abhängigkeiten. Diese Anleitung bringt Sie in etwa fünf Minuten von Null zur veröffentlichten Dokumentation.

## Voraussetzungen

Sie benötigen einen Linux-, macOS- oder Windows-Rechner. Das war's. Kein Docker, kein PostgreSQL, keine Node.js-Laufzeitumgebung. DocPlatform kompiliert zu einem einzelnen statischen Binary — die Go-Laufzeitumgebung ist eingebettet. Falls Sie sich für die Implementierungssprache interessieren: [Go](https://go.dev/) erzeugt eigenständige ausführbare Dateien, die ohne Installation auf dem Host laufen.

## Schritt 1: Herunterladen und Installieren

Unter Linux oder macOS übernimmt das Installationsskript alles:

```bash
curl -fsSL https://valoryx.org/install.sh | bash
```

Dies lädt das neueste Release-Binary nach `/usr/local/bin/docplatform` herunter (oder `~/.local/bin/`, falls Sie keinen Root-Zugriff haben). Unter macOS mit Homebrew können Sie auch Folgendes ausführen:

```bash
brew install valoryx/tap/docplatform
```

Unter Windows laden Sie die `.exe` von der [Releases-Seite](/install/) herunter und fügen sie Ihrem PATH hinzu.

Überprüfen Sie die Installation:

```bash
docplatform version
# DocPlatform v1.x.x (linux/amd64)
```

## Schritt 2: Server starten

Starten Sie den Server mit Standardeinstellungen:

```bash
docplatform serve
```

Sie sehen eine Ausgabe wie diese:

```
INFO  Starting DocPlatform server
INFO  Data directory: ./data
INFO  Listening on http://localhost:3000
INFO  Full-text search index: ready
INFO  Admin setup required — visit http://localhost:3000 to create your account
```

Öffnen Sie `http://localhost:3000` in Ihrem Browser. DocPlatform stellt sowohl den Editor als auch die veröffentlichte Seite vom selben Binary auf dem selben Port bereit. Kein separater Frontend-Build-Schritt.

Beim ersten Start sehen Sie den Admin-Setup-Bildschirm. Wählen Sie einen Benutzernamen und ein Passwort. Dies erstellt das Super-Admin-Konto — dasjenige, das alles verwalten kann. Weitere Benutzer können Sie später über das Admin-Panel hinzufügen.

## Schritt 3: Ersten Workspace erstellen

Nach der Anmeldung zeigt das Dashboard eine leere Workspace-Liste. Klicken Sie auf **Neuer Workspace** und füllen Sie aus:

- **Name:** `engineering-handbook` (oder was auch immer Sie dokumentieren)
- **Slug:** `engineering-handbook` (wird zum URL-Pfad)
- **Theme:** Wählen Sie eines der 5 eingebauten Themes — Sie können es später ändern

Klicken Sie auf **Erstellen**. Sie haben jetzt einen Workspace mit einer Startseite, die bearbeitet werden kann.

## Schritt 4: Dokumentation schreiben

Klicken Sie in Ihren neuen Workspace und Sie landen im [WYSIWYG-Editor](/docs/getting-started/first-workspace/). Er unterstützt Markdown-Shortcuts — tippen Sie `##` gefolgt von einem Leerzeichen, um eine H2-Überschrift zu erstellen, verwenden Sie Backticks für Inline-Code und dreifache Backticks für Code-Blöcke. Alles, was Sie von einem modernen Editor erwarten, aber als Rich Text gerendert, während Sie tippen.

Erstellen Sie ein paar Seiten, um ein Gefühl dafür zu bekommen:

1. Klicken Sie auf **Neue Seite** in der Seitenleiste
2. Geben Sie ihr einen Titel: „Erste Schritte"
3. Schreiben Sie Inhalt — fügen Sie vorhandenes Markdown ein, falls vorhanden
4. Drücken Sie **Strg+S** (oder Cmd+S auf macOS) zum Speichern

Die Seite wird in DocPlatforms lokaler SQLite-Datenbank gespeichert (eingebettet im Binary — keine externe Datenbank zu verwalten). Jedes Speichern erstellt eine Version, zu der Sie zurückkehren können.

Versuchen Sie, eine Unterseite zu erstellen: Fahren Sie mit der Maus über „Erste Schritte" in der Seitenleiste und klicken Sie auf das **+**-Symbol. Jetzt haben Sie eine Seitenhierarchie.

## Schritt 5: Dokumentation veröffentlichen

Um Ihre Dokumentation öffentlich zugänglich zu machen, gehen Sie zu **Workspace-Einstellungen > Veröffentlichung** und schalten Sie den Veröffentlichungsstatus auf **Ein**. Ihre Dokumentation ist jetzt live unter:

```
http://localhost:3000/s/engineering-handbook
```

Das `/s/`-Präfix liefert die veröffentlichte, schreibgeschützte Ansicht. Sie verwendet das von Ihnen gewählte Theme, hat Volltextsuche basierend auf Bleve und enthält eine Seitenleisten-Navigation, die aus Ihrer Seitenhierarchie aufgebaut ist.

Das war's. Fünf Befehle, keine Konfigurationsdateien, und Sie haben eine laufende Dokumentationsseite.

## Was im Hintergrund läuft

Als Sie `docplatform serve` ausgeführt haben, haben Sie einen einzelnen Prozess gestartet, der Folgendes übernimmt:

- **HTTP-Server** — stellt die Editor-Oberfläche, die API und die veröffentlichte Dokumentationsseite bereit
- **SQLite-Datenbank** — speichert Benutzer, Workspaces, Seiten und Versionen
- **Bleve-Suchindex** — Volltextsuche mit Tippfehlertoleranz und Relevanz-Ranking
- **WebAuthn/Passkey-Authentifizierung** — moderne passwortlose Authentifizierung neben traditionellem Benutzername/Passwort
- **RBAC** — 5 Rollen (Super-Admin, Admin, Editor, Betrachter, Gast) mit granularen Berechtigungen

All das läuft in einem einzelnen Prozess mit etwa 50–80 MB RAM. Keine Hintergrund-Worker, keine Message Queues, keine Microservices.

## Schritt 6: Git verbinden (Optional)

Wenn Sie Ihre Dokumentation in einem Git-Repository speichern möchten — versionskontrolliert, überprüfbar, bearbeitbar in Ihrer IDE — unterstützt DocPlatform bidirektionalen Git-Sync. Lesen Sie die [Schnellstartanleitung](/docs/getting-started/quickstart/) für die vollständige Einrichtung, aber die Kurzversion ist:

1. Gehen Sie zu **Workspace-Einstellungen > Git Sync**
2. Fügen Sie Ihre Repository-URL und den Deploy Key ein
3. Wählen Sie einen Branch
4. Klicken Sie auf **Sync aktivieren**

Ab diesem Zeitpunkt erstellt jedes Speichern im Editor einen Git-Commit, und jeder Push zum Repository von einer IDE oder CI-Pipeline wird im Editor widergespiegelt. Dies ist kein Einweg-Spiegel — es ist echter bidirektionaler Sync unter Verwendung des Content-Ledger-Musters (siehe [Warum Git-Docs-Tools den Sync nicht hinbekommen](/blog/why-git-sync-breaks/) für die technische Erklärung).

## Betrieb in der Produktion

Für eine Produktionsumgebung sollten Sie einige Umgebungsvariablen setzen:

```bash
export DOCPLATFORM_PORT=3000
export DOCPLATFORM_DATA_DIR=/var/lib/docplatform
export DOCPLATFORM_BASE_URL=https://docs.yourcompany.com

docplatform serve
```

Setzen Sie es hinter einen Reverse-Proxy (Nginx, Caddy oder Cloudflare Tunnel) für HTTPS-Terminierung. Verwenden Sie eine systemd-Unit oder Ähnliches, um es am Laufen zu halten:

```ini
[Unit]
Description=DocPlatform Documentation Server
After=network.target

[Service]
ExecStart=/usr/local/bin/docplatform serve
WorkingDirectory=/var/lib/docplatform
Restart=always
User=docplatform

[Install]
WantedBy=multi-user.target
```

Sichern Sie das Datenverzeichnis regelmäßig — es enthält die SQLite-Datenbank und den Suchindex. Ein einfaches `cp` oder `rsync` während der Server läuft funktioniert einwandfrei (SQLite verarbeitet gleichzeitige Lesezugriffe).

## Nächste Schritte

Sie haben jetzt eine funktionierende Dokumentationsplattform. Hier geht es weiter:

- [Vollständige Schnellstartanleitung](/docs/getting-started/quickstart/) — deckt Git-Sync, Themes und Benutzerverwaltung ab
- [Ersten Workspace erstellen](/docs/getting-started/first-workspace/) — detaillierte Workspace-Konfiguration
- [Installationsoptionen](/install/) — alle Download-Methoden, einschließlich ARM-Builds

Die Community Edition von DocPlatform ist kostenlos, ohne Benutzerlimits, ohne Seitenlimits und ohne Feature-Einschränkungen. Laden Sie das Binary herunter und fangen Sie an zu schreiben. Alles, was Sie brauchen, ist in dieser einen Datei enthalten.
