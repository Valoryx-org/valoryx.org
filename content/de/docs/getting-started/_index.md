---
title: Erste Schritte
description: Installieren Sie DocPlatform, erstellen Sie Ihren ersten Workspace und beginnen Sie in unter 10 Minuten mit dem Schreiben von Dokumentation.
weight: 1
---

# Erste Schritte

Dieser Abschnitt führt Sie durch die Installation von DocPlatform, den ersten Start und die Erstellung eines Workspace, in dem Ihr Team mit dem Schreiben beginnen kann.

## Wählen Sie Ihren Weg

| Weg | Zeit | Am besten geeignet für |
|---|---|---|
| [Schnellstart](quickstart.md) | 5 Minuten | Das Produkt schnell evaluieren — ein Befehl, und es läuft |
| [Installation](installation.md) | 10 Minuten | Vollständige Einrichtung — wählen Sie Ihre Methode (Binärdatei, Docker, Quellcode), verstehen Sie, was passiert |
| [Ihr erster Workspace](first-workspace.md) | 10 Minuten | Bereits gestartet — lernen Sie, Workspaces zu erstellen, Git zu verbinden, Ihr Team einzuladen |

## Bevor Sie beginnen

DocPlatform hat keine externen Abhängigkeiten. Sie müssen keine Datenbank, keine Suchmaschine und kein Node.js-Runtime installieren. Die einzelne Binärdatei enthält alles.

**Optionale Abhängigkeiten:**

- **Git 2.30+** — nur erforderlich, wenn Sie mit einem Remote-Git-Repository synchronisieren möchten
- **SSH-Schlüssel** — nur erforderlich für private Git-Repositories über SSH
- **SMTP-Server** — nur erforderlich für E-Mail-Einladungen und Passwort-Zurücksetzung (ohne SMTP werden Reset-Token auf stdout ausgegeben)

## Architektur auf einen Blick

Wenn Sie `docplatform serve` ausführen, startet ein einzelner Prozess, der Folgendes umfasst:

- **HTTP-Server** — stellt den Web-Editor und die API auf Port 3000 bereit
- **SQLite-Datenbank** — speichert Benutzer, Workspaces, Seiten-Metadaten und Audit-Logs
- **Bleve-Suchmaschine** — indiziert alle Inhalte für sofortige Volltextsuche
- **Git-Engine** — synchronisiert Inhalte bidirektional mit Remote-Repositories
- **Statisches Frontend** — der Next.js-Web-Editor, eingebettet in die Binärdatei

Alle Daten liegen in einem einzigen Verzeichnis (Standard: `.docplatform/`), was Backups und Migrationen unkompliziert macht — kopieren Sie einfach das Verzeichnis.
