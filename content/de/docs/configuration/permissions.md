---
title: Rollen & Berechtigungen
description: Konfigurieren Sie die 6-stufige Rollenhierarchie von DocPlatform, Zugriffskontrolle auf Seitenebene und Berechtigungs-Caching.
weight: 3
---

# Rollen & Berechtigungen

DocPlatform verwendet rollenbasierte Zugriffskontrolle (RBAC), gestützt durch Casbin, eine In-Process-Autorisierungs-Engine. Berechtigungen werden in unter 0,1ms pro Prüfung ausgewertet, ohne externen Dienst.

## Rollenhierarchie

DocPlatform definiert 6 Rollen in einer strikten Hierarchie. Höhere Rollen erben alle Berechtigungen niedrigerer Rollen.

```
SuperAdmin          ← Vollständiger Plattformzugriff (alle Workspaces)
    │
WorkspaceAdmin      ← Workspace-Einstellungen, Git-Konfiguration, Theme verwalten
    │
Admin               ← Mitglieder verwalten, Rollen zuweisen
    │
Editor              ← Seiten erstellen, bearbeiten, löschen
    │
Commenter           ← Seiten ansehen, Kommentare hinterlassen
    │
Viewer              ← Nur Seiten ansehen
```

### Berechtigungsmatrix

| Berechtigung | Viewer | Commenter | Editor | Admin | WS Admin | Super Admin |
|---|---|---|---|---|---|---|
| Seiten ansehen | Ja | Ja | Ja | Ja | Ja | Ja |
| Inhalte suchen | Ja | Ja | Ja | Ja | Ja | Ja |
| Kommentare hinterlassen | | Ja | Ja | Ja | Ja | Ja |
| Seiten erstellen | | | Ja | Ja | Ja | Ja |
| Seiten bearbeiten | | | Ja | Ja | Ja | Ja |
| Seiten löschen | | | Ja | Ja | Ja | Ja |
| Assets hochladen | | | Ja | Ja | Ja | Ja |
| Mitglieder einladen | | | | Ja | Ja | Ja |
| Mitglieder entfernen | | | | Ja | Ja | Ja |
| Mitgliederrollen ändern | | | | Ja | Ja | Ja |
| Workspace-Einstellungen verwalten | | | | | Ja | Ja |
| Git-Remote konfigurieren | | | | | Ja | Ja |
| Theme & Navigation verwalten | | | | | Ja | Ja |
| Zugriff auf alle Workspaces | | | | | | Ja |
| Plattformeinstellungen verwalten | | | | | | Ja |
| Workspaces erstellen/löschen | | | | | | Ja |

## Rollen zuweisen

### Erster Benutzer

Der erste Benutzer, der sich auf einer neuen DocPlatform-Instanz registriert, erhält automatisch die **SuperAdmin**-Rolle. Dies geschieht nur einmal — nachfolgende Registrierungen erhalten keine Workspace-Rolle, bis sie eingeladen werden.

### Workspace-Mitglieder

Beim Einladen eines Benutzers in einen Workspace geben Sie dessen Rolle an:

**Web-Oberfläche:** Workspace Settings → Members → Invite → Rolle auswählen

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{id}/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "role": "editor"
  }'
```

### Standardrolle

Setzen Sie die Standardrolle für neue Mitglieder, die eine Einladung ohne spezifisch zugewiesene Rolle annehmen:

```yaml
# .docplatform/config.yaml
permissions:
  default_role: viewer
```

Verfügbare Werte: `viewer`, `commenter`, `editor`, `admin`, `workspace_admin`

## Zugriffskontrolle auf Seitenebene

Überschreiben Sie Workspace-weite Berechtigungen auf einzelnen Seiten über Frontmatter.

### Zugriffsebenen (Web-Editor — interne Benutzer)

Für authentifizierte Benutzer innerhalb des Web-Editors beschränkt die seitenbezogene Zugriffskontrolle die Sichtbarkeit nach Rolle:

| Ebene | Verhalten |
|---|---|
| `public` | Jedes Workspace-Mitglied kann ansehen |
| `workspace` | Jedes Workspace-Mitglied kann ansehen (identisch mit `public` für authentifizierte Benutzer) |
| `restricted` | Nur Benutzer mit in `allowed_roles` aufgeführten Rollen können ansehen |

### Beispiele

**Öffentliche Seite** (Standard):

```yaml
---
title: Getting Started
access: public
---
```

**Nur für Admins eingeschränkt:**

```yaml
---
title: Infrastructure Runbook
access: restricted
allowed_roles: [admin, workspace_admin]
---
```

### Was "restricted" bedeutet

Wenn eine Seite `access: restricted` hat:

- Benutzer ohne die erforderliche Rolle **können die Seite nicht ansehen**
- Die Seite **erscheint nicht** in Suchergebnissen für nicht autorisierte Benutzer
- Direkter URL-Zugriff gibt **403 Forbidden** zurück

### Zugriff auf veröffentlichte Dokumentation

Für die **veröffentlichte Dokumentationsseite** (`/p/{slug}/...`) funktioniert die Zugriffskontrolle anders:

- Alle veröffentlichten Seiten sind **standardmäßig öffentlich** — keine Anmeldung erforderlich
- Um eine Anmeldung für die gesamte veröffentlichte Seite zu erzwingen, setzen Sie [`PUBLISH_REQUIRE_AUTH=true`](environment.md) — dies gilt für alle Seiten in allen Workspaces
- Zugriffskontrolle auf Seitenebene in veröffentlichten Dokumenten (z. B. eine Seite workspace-only machen, während andere öffentlich sind) ist für eine zukünftige Version geplant

> In v0.5 wird das `access`-Frontmatter-Feld gespeichert und steht für zukünftige Verwendung bereit, wird aber auf veröffentlichten Routen nicht erzwungen. Verwenden Sie `PUBLISH_REQUIRE_AUTH` für seitenweite Zugriffsbeschränkung.

## Interne Rollenstufen

Als Referenz: Jede Rolle wird einer numerischen Stufe zugeordnet. Höhere Stufen erben alle Berechtigungen niedrigerer Stufen:

| Rolle | Stufe | Mindest-Aktion |
|---|---|---|
| Viewer | 10 | `read` |
| Commenter | 20 | `read` |
| Editor | 30 | `read`, `write`, `delete` |
| Admin | 40 | `read`, `write`, `delete`, `admin` (Mitgliederverwaltung) |
| WorkspaceAdmin | 50 | Alle Workspace-Aktionen |
| SuperAdmin | 60 | Alle Plattform-Aktionen (umgeht alle Prüfungen) |

Aktionen haben Mindeststufen: `read` erfordert Stufe 10+, `write` erfordert 30+, `delete` erfordert 30+, `admin` erfordert 50+. Die Rollenstufe eines Benutzers wird mit der Mindeststufe der Aktion verglichen.

## Wie Berechtigungen ausgewertet werden

```
API Request
    │
    ▼
Auth Middleware
(extract JWT, identify user)
    │
    ▼
Permission Middleware
(Casbin check: user + role + resource + action)
    │
    ├── Allowed → proceed to handler
    │
    └── Denied → 403 Forbidden
```

### Auswertungsablauf

1. **Benutzeridentität extrahieren** aus dem JWT-Access-Token
2. **Benutzerrolle nachschlagen** für den Ziel-Workspace
3. **Workspace-weite Berechtigung prüfen** — erlaubt die Rolle die Aktion?
4. **Seitenbezogenen Zugriff prüfen** — wenn die Seite `access: restricted` hat, ist die Rolle des Benutzers in `allowed_roles`?
5. **Ergebnis zurückgeben** — erlaubt oder verweigert

### Leistung

| Metrik | Wert |
|---|---|
| **Engine** | Casbin (In-Process, In-Memory) |
| **Auswertungszeit** | < 0,1ms pro Prüfung |
| **Cache** | Versioniert (automatische Invalidierung bei Rollen- oder Berechtigungsänderung) |
| **Policy-Speicherung** | SQLite (beim Start in den Speicher geladen) |

## Berechtigungs-Caching

Casbin-Policies werden beim Serverstart aus SQLite in den Speicher geladen. Änderungen an Rollen oder Frontmatter-Zugriffsdeklarationen lösen eine Cache-Invalidierung aus:

1. Admin ändert die Rolle eines Benutzers → Berechtigungs-Cache-Version wird inkrementiert
2. Editor aktualisiert Seiten-Frontmatter mit neuem `access` oder `allowed_roles` → Cache für diese Seite invalidiert
3. Nächste Berechtigungsprüfung lädt aktuelle Policy aus SQLite

Der Cache ist versioniert, nicht zeitbasiert — es gibt kein Fenster mit veralteten Berechtigungen.

## Gängige Muster

### Schreibgeschützte öffentliche Dokumentation mit eingeschränkten internen Seiten

```yaml
# Die meisten Seiten: Standard
access: public

# Interne Seiten: eingeschränkt
---
title: Incident Response Playbook
access: restricted
allowed_roles: [admin, workspace_admin]
---
```

### Editor erstellt, Admin veröffentlicht

1. Setzen Sie `publishing.default_published: false` in der Workspace-Konfiguration
2. Editoren erstellen und bearbeiten Seiten (standardmäßig unveröffentlicht)
3. Admins überprüfen und schalten `published: true` um

### Team-spezifische Workspaces

Erstellen Sie separate Workspaces pro Team mit unabhängigen Mitgliederlisten:

- `eng-docs` Workspace → Engineering-Team
- `product-docs` Workspace → Produktteam
- `internal-wiki` Workspace → alle

SuperAdmin hat Zugriff auf alle Workspaces für teamübergreifende Sichtbarkeit.

## Community Edition Limits

Die Community Edition erzwingt folgende Ressourcenlimits:

| Ressource | Limit |
|---|---|
| Benutzer mit Editor-Rolle oder höher | 5 |
| Workspaces | 3 |
| Viewer und Commenter | Unbegrenzt |
| Seiten | Unbegrenzt |

Diese Limits sind fest codiert (kein Lizenzschlüssel erforderlich). Viewer und Commenter werden nie gegen das Editor-Limit gezählt. Wenn das Editor-Limit erreicht ist, können neue Benutzer weiterhin als Viewer oder Commenter eingeladen werden.

## Fehlerbehebung

### „403 Forbidden" auf einer Seite, auf die ich Zugriff haben sollte

1. Prüfen Sie Ihre Rolle: Profil → Workspace Membership
2. Prüfen Sie das Frontmatter der Seite: enthält `access: restricted` + `allowed_roles` Ihre Rolle?
3. Bitten Sie einen Workspace-Admin, Ihre Rollenzuweisung zu verifizieren

### Berechtigungsänderungen werden nicht wirksam

Berechtigungsänderungen sollten sofort wirksam sein (Cache-Invalidierung ist synchron). Wenn nicht:

1. Melden Sie sich ab und wieder an (aktualisieren Sie Ihre JWT-Token)
2. Prüfen Sie die Server-Logs auf Cache-Invalidierungsfehler
3. Führen Sie `docplatform doctor` aus, um den Zustand des Berechtigungssystems zu verifizieren

### Erster Benutzer ist nicht SuperAdmin

Dies tritt auf, wenn der erste Benutzer sich registriert, während die Datenbank bereits Benutzerdatensätze enthält (z. B. aus einer vorherigen Installation). Lösung:

1. Server stoppen
2. Datenbank löschen: `rm {DATA_DIR}/data.db`
3. Server starten und erneut registrieren

Dies setzt alle Daten zurück. Verwenden Sie dies nur bei Neuinstallationen.
