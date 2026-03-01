---
title: Workspace-Einstellungen
description: Konfigurieren Sie Workspace-spezifische Einstellungen — Git-Remote, Theme, Navigationsreihenfolge, Veröffentlichungsstandards und mehr.
weight: 4
---

# Workspace-Einstellungen

Jeder Workspace hat seine eigene Konfigurationsdatei unter `.docplatform/workspaces/{workspace-id}/.docplatform/config.yaml`. Bearbeiten Sie diese Datei direkt oder nutzen Sie die Web-Oberfläche (**Settings** → **Workspace**).

## Vollständige Konfigurationsreferenz

```yaml
# Workspace-Identität
workspace_id: 01KJJ10NTF31Z1QJTG4ZRQZ2Z2    # Automatisch generierte ULID
name: "Engineering Docs"                        # Anzeigename
slug: eng-docs                                  # URL-Slug für veröffentlichte Dokumentation
description: "Internal engineering documentation"

# Git-Synchronisation
git_remote: git@github.com:your-org/eng-docs.git
git_branch: main
git_auto_commit: true       # Editor-Speicherungen automatisch in Git committen
sync_interval: 300          # Polling-Intervall in Sekunden (0 = deaktiviert)

# Theme
theme:
  mode: auto                # light, dark, auto (folgt Systemeinstellung)
  accent: blue              # Akzentfarbe für veröffentlichte Seite

# Veröffentlichungsstandards
publishing:
  default_published: false  # Neue Seiten standardmäßig veröffentlicht?
  require_explicit_unpublish: false

# Berechtigungen
permissions:
  default_role: viewer      # Rolle, die neuen Workspace-Mitgliedern zugewiesen wird

# Navigation (für Seitenleiste der veröffentlichten Dokumentation)
navigation:
  - title: "Overview"
    path: "index.md"
  - title: "Getting Started"
    path: "getting-started/index.md"
    children:
      - title: "Installation"
        path: "getting-started/installation.md"
      - title: "Configuration"
        path: "getting-started/configuration.md"
```

## Einstellungsreferenz

### Identität

| Schlüssel | Typ | Beschreibung |
|---|---|---|
| `workspace_id` | string | ULID, automatisch bei Erstellung generiert. Nicht ändern. |
| `name` | string | Anzeigename, der in der Oberfläche und im Header der veröffentlichten Seite angezeigt wird |
| `slug` | string | URL-Segment für veröffentlichte Dokumentation: `/p/{slug}/`. Eine Änderung macht bestehende URLs ungültig. |
| `description` | string | Optionale Beschreibung als interne Referenz |

### Git

| Schlüssel | Typ | Standard | Beschreibung |
|---|---|---|---|
| `git_remote` | string | — | Remote-Repository-URL (SSH oder HTTPS) |
| `git_branch` | string | `main` | Branch zur Synchronisation |
| `git_auto_commit` | bool | `true` | Speicherungen aus dem Web-Editor automatisch committen |
| `sync_interval` | int | `300` | Sekunden zwischen dem Polling des Remotes. Setzen Sie auf `0`, um Polling zu deaktivieren (nur Webhook). |

### Theme

| Schlüssel | Typ | Standard | Beschreibung |
|---|---|---|---|
| `theme.mode` | string | `auto` | Farbschema für veröffentlichte Dokumentation: `light`, `dark`, `auto` |
| `theme.accent` | string | `blue` | Akzentfarbe für Links, Buttons und Hervorhebungen in veröffentlichten Dokumenten |

### Veröffentlichung

| Schlüssel | Typ | Standard | Beschreibung |
|---|---|---|---|
| `publishing.default_published` | bool | `false` | Ob neue Seiten standardmäßig veröffentlicht werden |
| `publishing.require_explicit_unpublish` | bool | `false` | Wenn true, müssen Seiten explizit unveröffentlicht werden (verhindert versehentlichen Ausschluss) |

### Berechtigungen

| Schlüssel | Typ | Standard | Beschreibung |
|---|---|---|---|
| `permissions.default_role` | string | `viewer` | Rolle, die Benutzern zugewiesen wird, die eine Workspace-Einladung annehmen |

### Navigation

Das `navigation`-Array steuert die Seitenleisten-Reihenfolge in veröffentlichten Dokumenten. Ohne dieses werden Seiten alphabetisch sortiert.

```yaml
navigation:
  - title: "Overview"       # Anzeigelabel
    path: "index.md"        # Dateipfad relativ zu docs/
  - title: "Guides"         # Abschnittsüberschrift (kein path = nicht anklickbare Gruppe)
    children:
      - title: "Editor"
        path: "guides/editor.md"
      - title: "Git Sync"
        path: "guides/git-integration.md"
```

**Regeln:**

- Jeder Eintrag benötigt einen `title`
- Einträge mit einem `path` sind Seitenlinks
- Einträge ohne `path` aber mit `children` sind Abschnittsüberschriften
- Die Verschachtelungstiefe ist unbegrenzt
- Seiten, die nicht in `navigation` aufgeführt sind, existieren weiterhin, erscheinen aber nicht in der Seitenleiste

## Einstellungen bearbeiten

### Über Web-Oberfläche

1. Öffnen Sie den Workspace im Web-Editor
2. Klicken Sie auf **Settings** (Zahnradsymbol)
3. Ändern Sie Einstellungen über die Formularoberfläche
4. Änderungen werden automatisch gespeichert

### Über Konfigurationsdatei

Bearbeiten Sie die YAML-Datei direkt:

```bash
# Workspace-Konfiguration finden
ls .docplatform/workspaces/*/. docplatform/config.yaml

# Bearbeiten
nano .docplatform/workspaces/01KJJ.../. docplatform/config.yaml
```

Starten Sie den Server neu, damit die Änderungen wirksam werden, oder lösen Sie einen Reload über die API aus:

```bash
curl -X POST http://localhost:3000/api/v1/admin/reload \
  -H "Authorization: Bearer {token}"
```

### Über Git

Wenn die Workspace-Konfigurationsdatei in Git verfolgt wird, pushen Sie Änderungen aus Ihrer IDE und sie werden im nächsten Synchronisationszyklus übernommen. Dies ist nützlich, um die Dokumentationskonfiguration als Code zu verwalten.

## Mehrere Workspaces

DocPlatform unterstützt mehrere Workspaces auf einer einzelnen Instanz. Jeder Workspace ist vollständig isoliert:

- Separate Inhaltsverzeichnisse
- Separate Git-Repositories
- Separate Mitgliederlisten und Rollen
- Separate Suchindizes
- Separate veröffentlichte Seiten (verschiedene Slugs)

Erstellen Sie zusätzliche Workspaces über CLI:

```bash
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git
```

Oder über den Workspace-Umschalter in der Web-Oberfläche.
