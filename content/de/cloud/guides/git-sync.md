---
title: GitHub Sync
description: Verbinden Sie Ihren Workspace mit GitHub für Backup, IDE-Bearbeitung und Versionskontrolle.
weight: 4
---

# GitHub Sync

Valoryx Cloud kann Ihre Dokumentation mit einem GitHub-Repository synchronisieren. So erhalten Sie das Beste aus beiden Welten: einen ansprechenden Web-Editor UND die volle Leistungsfähigkeit von Git.

## Warum GitHub verbinden?

- **Backup** — Ihre Dokumentation ist immer sicher auf GitHub, selbst wenn Sie Ihr Konto kündigen
- **IDE-Bearbeitung** — Entwickler in Ihrem Team können Dokumentation in VS Code, Vim oder jedem anderen Editor bearbeiten
- **Pull Requests** — nutzen Sie den GitHub-PR-Workflow für Dokumentations-Reviews vor der Veröffentlichung
- **Versionshistorie** — vollständiges Git Blame, Diff und Rollback für jede Änderung
- **CI/CD-Integration** — lösen Sie Builds oder Tests aus, wenn sich die Dokumentation ändert

## So funktioniert es

```
Sie bearbeiten im Browser → Auto-Save → Auto-Commit → Push zu GitHub
                                                           ↕
Teammitglied pusht aus IDE → GitHub → Webhook → Pull zu Valoryx
```

Änderungen fließen automatisch in beide Richtungen. Sie müssen nie über die Synchronisierung nachdenken.

## Einrichtung

1. Gehen Sie zu **Workspace Settings** → **Git Sync**
2. Klicken Sie auf **Connect GitHub**
3. Autorisieren Sie Valoryx für den Zugriff auf Ihre Repositories
4. Wählen Sie das Repository und den Branch zur Synchronisierung aus
5. Fertig — Ihr Workspace ist jetzt verbunden

## Was wird synchronisiert

Jede Seite in Ihrem Workspace entspricht einer `.md`-Datei im Repository:

```
your-repo/
├── getting-started.md
├── api/
│   ├── authentication.md
│   └── endpoints.md
├── guides/
│   ├── deployment.md
│   └── troubleshooting.md
└── .docplatform.yaml     ← Workspace-Metadaten
```

## Brauche ich GitHub?

**Nein.** GitHub Sync ist vollständig optional. Valoryx Cloud funktioniert auch ohne GitHub einwandfrei. Ihre Dokumentation wird sicher auf unseren Servern gespeichert. GitHub bietet zusätzlich Backup und IDE-Zugriff — ist aber für keine Funktion erforderlich.
