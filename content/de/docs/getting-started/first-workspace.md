---
title: Ihr erster Workspace
description: Erstellen und konfigurieren Sie einen Dokumentations-Workspace — verbinden Sie Git, richten Sie die Inhaltsstruktur ein und laden Sie Ihr Team ein.
weight: 3
---

# Ihr erster Workspace

Ein Workspace ist der übergeordnete Container für ein Dokumentationsprojekt. Jeder Workspace wird einem Verzeichnis mit Markdown-Dateien zugeordnet und synchronisiert sich optional mit einem Git-Repository.

## Workspace-Konzepte

| Konzept | Beschreibung |
|---|---|
| **Workspace** | Ein Dokumentationsprojekt mit Seiten, Mitgliedern und Einstellungen |
| **Seite** | Eine Markdown-Datei mit YAML-Frontmatter (Titel, Beschreibung, Tags, Zugriff) |
| **Slug** | Die URL-sichere Kennung für Ihren Workspace (z. B. `my-docs` → `/p/my-docs/`) |
| **Mitglied** | Ein Benutzer mit einer Rolle im Workspace (Viewer bis WorkspaceAdmin) |

## Workspace erstellen

### Über CLI

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs
```

### Über Web-Oberfläche

1. Melden Sie sich als SuperAdmin oder WorkspaceAdmin an
2. Öffnen Sie den Workspace-Umschalter (Dropdown oben links)
3. Klicken Sie auf **Create Workspace**
4. Geben Sie einen Namen und Slug ein
5. Konfigurieren Sie optional ein Git-Remote

## Git-Repository verbinden

Bidirektionale Synchronisation hält Ihre Workspace-Dateien und ein Remote-Git-Repository synchron.

### Während der Initialisierung

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs \
  --git-url git@github.com:your-org/eng-docs.git \
  --branch main
```

### Nach der Erstellung

Aktualisieren Sie die Workspace-Konfiguration unter `.docplatform/workspaces/{id}/.docplatform/config.yaml`:

```yaml
git_remote: git@github.com:your-org/eng-docs.git
git_branch: main
git_auto_commit: true
sync_interval: 300  # Sekunden
```

Starten Sie dann den Server neu oder lösen Sie eine manuelle Synchronisation über die Web-Oberfläche aus.

### SSH-Schlüssel einrichten

Für private Repositories verwendet DocPlatform einen dedizierten SSH-Deploy-Key:

```bash
# Deploy-Key generieren (ohne Passphrase)
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""

# Öffentlichen Schlüssel zu den Deploy-Keys Ihres Repositories hinzufügen
cat ~/.ssh/docplatform_deploy_key.pub
# → Kopieren Sie dies nach GitHub/GitLab Einstellungen → Deploy Keys (Schreibzugriff aktivieren)
```

Setzen Sie die Umgebungsvariable:

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

### Wie die Synchronisation funktioniert

```
┌─────────────┐     auto-commit + push      ┌──────────────┐
│ Web Editor   │ ──────────────────────────► │ Remote Repo  │
│ (browser)    │                             │ (GitHub, etc)│
│              │ ◄────────────────────────── │              │
└─────────────┘     polling / webhook        └──────────────┘
```

**Web → Git:** Wenn Sie im Editor speichern, schreibt DocPlatform die `.md`-Datei, erstellt automatisch einen Commit mit einer beschreibenden Nachricht und pusht zum Remote.

**Git → Web:** DocPlatform pollt das Remote (Standard: alle 5 Minuten) oder lauscht auf Webhooks. Neue Commits werden gepullt und die Web-Oberfläche aktualisiert sich in Echtzeit über WebSocket.

**Konflikte:** Wenn beide Seiten dieselbe Datei zwischen Synchronisationen ändern, erkennt DocPlatform die Kollision anhand von Content-Hashes, gibt HTTP 409 zurück und stellt beide Versionen zum Download bereit, damit Sie den Konflikt manuell lösen können.

## Inhalte organisieren

### Seitenhierarchie

Seiten können beliebig tief verschachtelt werden. Die Dateistruktur in `docs/` wird direkt auf die URL-Struktur abgebildet:

```
docs/
├── index.md                → /p/eng-docs/
├── getting-started.md      → /p/eng-docs/getting-started
├── api/
│   ├── index.md            → /p/eng-docs/api/
│   ├── authentication.md   → /p/eng-docs/api/authentication
│   └── endpoints.md        → /p/eng-docs/api/endpoints
└── guides/
    ├── deployment.md       → /p/eng-docs/guides/deployment
    └── contributing.md     → /p/eng-docs/guides/contributing
```

### Frontmatter

Jede Seite beginnt mit YAML-Frontmatter:

```yaml
---
title: Authentication
description: How to authenticate with the API using JWT tokens.
tags: [api, auth, jwt]
published: true
access: public        # public, workspace, restricted
allowed_roles: []     # nur verwendet wenn access: restricted
---
```

Das Feld `title` ist erforderlich. Alle anderen Felder sind optional und haben sinnvolle Standardwerte.

## Ihr Team einladen

### Über Web-Oberfläche

1. Öffnen Sie **Workspace Settings** → **Members**
2. Klicken Sie auf **Invite**
3. Geben Sie die E-Mail-Adresse der Person ein
4. Wählen Sie eine Rolle (Viewer, Commenter, Editor, Admin)
5. Klicken Sie auf **Send Invitation**

Wenn SMTP konfiguriert ist, wird die Einladung per E-Mail gesendet. Andernfalls wird ein teilbarer Einladungslink angezeigt.

### Rollen

| Rolle | Kann ansehen | Kann kommentieren | Kann bearbeiten | Kann Mitglieder verwalten | Kann Workspace verwalten |
|---|---|---|---|---|---|
| **Viewer** | Ja | | | | |
| **Commenter** | Ja | Ja | | | |
| **Editor** | Ja | Ja | Ja | | |
| **Admin** | Ja | Ja | Ja | Ja | |
| **WorkspaceAdmin** | Ja | Ja | Ja | Ja | Ja |
| **SuperAdmin** | Vollständiger Plattformzugriff über alle Workspaces |

Für detaillierte Berechtigungskonfiguration siehe [Rollen & Berechtigungen](../configuration/permissions.md).

## Workspace-Einstellungen

Greifen Sie auf Workspace-Einstellungen über die Web-Oberfläche (**Settings**-Zahnradsymbol) oder direkt durch Bearbeiten der Konfigurationsdatei zu.

Wichtige Einstellungen:

| Einstellung | Beschreibung | Standard |
|---|---|---|
| `name` | Anzeigename des Workspace | — |
| `slug` | URL-Slug für veröffentlichte Dokumentation | — |
| `git_remote` | Remote-Git-Repository-URL | (keine) |
| `git_branch` | Branch zur Synchronisation | `main` |
| `git_auto_commit` | Automatisches Committen von Editor-Speicherungen | `true` |
| `sync_interval` | Git-Polling-Intervall (Sekunden) | `300` |
| `theme.mode` | Farbschema: `light`, `dark`, `auto` | `auto` |
| `theme.accent` | Akzentfarbe | `blue` |
| `permissions.default_role` | Rolle für neue Mitglieder | `viewer` |

Für die vollständige Konfigurationsreferenz siehe [Workspace-Einstellungen](../configuration/workspace-config.md).

## Nächste Schritte

Ihr Workspace ist bereit. Hier geht es weiter:

| Ziel | Leitfaden |
|---|---|
| Den Web-Editor kennenlernen | [Der Web-Editor](../guides/editor.md) |
| Veröffentlichte Dokumentation einrichten | [Veröffentlichung](../guides/publishing.md) |
| Authentifizierung konfigurieren | [Authentifizierung](../configuration/authentication.md) |
| In Produktion deployen | [Produktions-Checkliste](../deployment/production.md) |
