---
title: Teams & Zusammenarbeit
description: Laden Sie Ihr Team ein, weisen Sie Rollen zu und arbeiten Sie an Dokumentation zusammen — mit Echtzeit-Präsenz und Audit-Trails.
weight: 4
---

# Teams & Zusammenarbeit

DocPlatform ist für Team-Dokumentation konzipiert. Laden Sie Mitglieder ein, weisen Sie granulare Rollen zu und verfolgen Sie jede Änderung mit einem vollständigen Audit-Trail.

## Workspace-Mitgliedschaft

Jeder Benutzer gehört einem oder mehreren Workspaces mit einer bestimmten Rolle an. Rollen bestimmen, welche Aktionen ein Benutzer ausführen kann.

### Mitglieder einladen

**Über Web-Oberfläche:**

1. Öffnen Sie **Workspace Settings** → **Members**
2. Klicken Sie auf **Invite Member**
3. Geben Sie die E-Mail-Adresse der Person ein
4. Wählen Sie eine Rolle
5. Klicken Sie auf **Send**

Wenn SMTP konfiguriert ist, wird eine Einladungs-E-Mail mit einem eindeutigen Link gesendet. Ohne SMTP wird der Einladungslink auf dem Bildschirm angezeigt — kopieren und teilen Sie ihn manuell.

**Über API:**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{workspace-id}/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "colleague@example.com",
    "role": "editor"
  }'
```

### Mitglieder entfernen

Workspace-Admins können Mitglieder unter **Settings** → **Members** → Benutzer anklicken → **Remove** entfernen.

Das Entfernen eines Mitglieds widerruft dessen Zugriff sofort. Vergangene Bearbeitungen und Audit-Log-Einträge bleiben erhalten.

### Rollen ändern

Klicken Sie auf die aktuelle Rolle eines Mitglieds, um sie zu ändern. Rollenänderungen werden sofort wirksam — aktive Sitzungen werden beim nächsten API-Aufruf aktualisiert.

## Rollen

DocPlatform verwendet eine 6-stufige Rollenhierarchie. Höhere Rollen erben alle Berechtigungen niedrigerer Rollen.

```
SuperAdmin
    └── WorkspaceAdmin
            └── Admin
                  └── Editor
                        └── Commenter
                              └── Viewer
```

| Rolle | Geltungsbereich | Fähigkeiten |
|---|---|---|
| **Viewer** | Workspace | Seiten ansehen und suchen |
| **Commenter** | Workspace | Ansehen + Kommentare auf Seiten hinterlassen |
| **Editor** | Workspace | Ansehen + kommentieren + Seiten erstellen, bearbeiten, löschen |
| **Admin** | Workspace | Editor + Mitglieder und Rollen verwalten |
| **WorkspaceAdmin** | Workspace | Admin + Workspace-Einstellungen, Git-Konfiguration, Theme verwalten |
| **SuperAdmin** | Plattform | Vollzugriff auf alle Workspaces + Plattformeinstellungen |

### Standardrolle für neue Mitglieder

Konfigurieren Sie die Standardrolle, die zugewiesen wird, wenn Benutzer eine Einladung annehmen:

```yaml
# .docplatform/config.yaml
permissions:
  default_role: viewer
```

### Zugriff auf Seitenebene

Beschränken Sie einzelne Seiten auf bestimmte Rollen über Frontmatter:

```yaml
---
title: Internal Runbook
access: restricted
allowed_roles: [admin, editor]
---
```

Seiten mit `access: restricted` sind für Benutzer ohne die erforderliche Rolle unsichtbar — sie erscheinen nicht in Suchergebnissen, der Navigation oder in veröffentlichten Dokumenten.

## Echtzeit-Präsenz

Wenn mehrere Benutzer gleichzeitig im selben Workspace aktiv sind, zeigt der Web-Editor an, wer online ist:

- **Seitenleisten-Indikatoren** — farbige Punkte neben Seiten, die von anderen Benutzern angesehen oder bearbeitet werden
- **Avatar-Stapel** — Benutzer-Avatare im Seitenkopf zeigen, wer sonst die aktuelle Seite ansieht

Die Präsenz wird über WebSocket-Verbindungen gesteuert und in Echtzeit aktualisiert.

### Wie Präsenz funktioniert

| Parameter | Wert |
|---|---|
| **Protokoll** | WebSocket (authentifiziert über Einmal-Ticket) |
| **Heartbeat-Intervall** | Alle 30 Sekunden |
| **Eviction-Timeout** | 90 Sekunden ohne Heartbeat |
| **Events** | `presence-join` (erste Verbindung), `presence-leave` (Timeout oder Verbindungsabbruch) |
| **Puffer** | 256 Events pro Workspace (verhindert Backpressure) |

Die WebSocket-Verbindung liefert auch Echtzeit-Inhalts-Events:

| Event | Wann |
|---|---|
| `page-created` | Eine neue Seite wird erstellt (beliebige Quelle) |
| `page-updated` | Eine Seite wird geändert (beliebige Quelle) |
| `page-deleted` | Eine Seite wird gelöscht |
| `sync-status` | Git-Synchronisationsstatus ändert sich (synced, ahead, behind, conflict) |
| `conflict-detected` | Ein Git-Merge-Konflikt wird gefunden |
| `bulk-sync` | 20+ Dateien in einer Operation synchronisiert (einzelne Benachrichtigung, nicht pro Datei) |

### Gleichzeitige Bearbeitung

DocPlatform unterstützt keine gleichzeitige Echtzeit-Bearbeitung (Google-Docs-Stil). Wenn zwei Benutzer dieselbe Seite gleichzeitig bearbeiten:

1. Die erste Speicherung ist erfolgreich
2. Die zweite Speicherung löst eine **Konflikterkennung** aus (HTTP 409)
3. Beide Versionen werden zur manuellen Auflösung aufbewahrt

Um Konflikte zu vermeiden:

- Verwenden Sie Konventionen zur Seitenverantwortung (ein Autor pro Seite gleichzeitig)
- Präsenzindikatoren helfen Ihrem Team zu koordinieren, wer was bearbeitet
- Für Teams mit hoher Parallelität sollten Sie kürzere Git-Synchronisationsintervalle in Betracht ziehen

## Audit-Trail

Jede Inhaltsmutation wird protokolliert mit:

| Feld | Beschreibung |
|---|---|
| **Zeitstempel** | Wann die Aktion stattfand (UTC) |
| **Benutzer** | Wer die Aktion ausgeführt hat (E-Mail, Benutzer-ID) |
| **Operation** | Was passiert ist: `create`, `update`, `delete`, `publish`, `unpublish` |
| **Seite** | Welche Seite betroffen war (ID, Titel, Pfad) |
| **Quelle** | Woher die Änderung kam: `web_editor`, `git_sync`, `api` |
| **Content-Hash** | SHA-256 des neuen Inhalts (zur Verifizierung) |

### Audit-Log anzeigen

Greifen Sie auf das Audit-Log unter **Workspace Settings** → **Activity** zu.

Filtern nach:

- **Benutzer** — alle Änderungen eines bestimmten Teammitglieds anzeigen
- **Seite** — die vollständige Historie einer bestimmten Seite anzeigen
- **Zeitraum** — auf ein Zeitfenster eingrenzen
- **Operationstyp** — nach Erstellungen, Aktualisierungen, Löschungen usw. filtern

### Audit-Aktionstypen

Das `action`-Feld im Audit-Log verwendet Punkt-Notation für präzise Filterung:

| Aktion | Beschreibung |
|---|---|
| `page.create` | Neue Seite erstellt |
| `page.update` | Seiteninhalt oder Frontmatter geändert |
| `page.delete` | Seite gelöscht |
| `page.publish` | Seite veröffentlicht (öffentlich gemacht) |
| `page.unpublish` | Seite unveröffentlicht |
| `auth.login` | Benutzer hat sich angemeldet |
| `auth.register` | Neuer Benutzer registriert |
| `auth.password_reset` | Passwort-Zurücksetzung abgeschlossen |
| `workspace.create` | Neuer Workspace erstellt |
| `workspace.member_add` | Benutzer zum Workspace hinzugefügt |
| `workspace.member_remove` | Benutzer aus dem Workspace entfernt |
| `workspace.role_change` | Benutzerrolle geändert |

### Aufbewahrung

Audit-Logs werden in SQLite zusammen mit Ihren regulären Daten gespeichert. Sie sind in den täglichen Backups enthalten. Die Standardaufbewahrung beträgt 1 Jahr (konfigurierbar). Ein wöchentlicher Bereinigungsjob entfernt Einträge, die älter als die Aufbewahrungsfrist sind.

## E-Mail-Benachrichtigungen

Mit konfiguriertem SMTP sendet DocPlatform transaktionale E-Mails für:

| Event | Empfänger | Inhalt |
|---|---|---|
| **Workspace-Einladung** | Eingeladener Benutzer | Beitrittslink + Workspace-Name |
| **Passwort-Zurücksetzung** | Anfragender Benutzer | Einmal-Reset-Token |

DocPlatform sendet keine Benachrichtigungs-E-Mails für Inhaltsänderungen. Echtzeit-WebSocket-Updates dienen diesem Zweck für aktive Benutzer, und das Audit-Log deckt die historische Überprüfung ab.

### SMTP-Konfiguration

```bash
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_FROM=docs@yourcompany.com
export SMTP_USERNAME=docs@yourcompany.com
export SMTP_PASSWORD=your-app-password
```

Ohne SMTP werden Einladungslinks und Passwort-Reset-Token auf stdout (Server-Logs) ausgegeben.

## Tipps für Team-Workflows

- **Ein Autor pro Seite** — verwenden Sie Präsenzindikatoren, um Konflikte zu vermeiden
- **Editoren schreiben, Admins veröffentlichen** — trennen Sie Verantwortlichkeiten durch Rollen
- **Verwenden Sie Tags für Verantwortlichkeiten** — taggen Sie Seiten mit `owner:jane`, um die Zuständigkeit zu klären
- **Git für Review-Workflows** — pushen Sie Änderungen auf einen Branch, öffnen Sie einen Pull Request, mergen Sie nach Review
- **Audit vor Veröffentlichung** — überprüfen Sie das Audit-Log auf unerwartete Änderungen, bevor Sie Inhalte öffentlich machen
