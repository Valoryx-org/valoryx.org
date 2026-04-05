---
title: Rollen & Berechtigungen
description: Konfigurieren Sie die 5-stufige Rollenhierarchie von DocPlatform, Zugriffskontrolle auf Workspace-Ebene, Editor-Berechtigungen und planbasierte Sitzplatzlimits.
weight: 3
---

# Rollen & Berechtigungen

DocPlatform verwendet rollenbasierte Zugriffskontrolle (RBAC), gestützt durch benutzerdefiniertes RBAC, eine In-Process-Autorisierungs-Engine. Berechtigungen werden in unter 0,1ms pro Prüfung ausgewertet, ohne externen Dienst.

## Rollenhierarchie

DocPlatform definiert 5 öffentlich sichtbare Rollen in einer strikten Hierarchie. Höhere Rollen erben alle Berechtigungen niedrigerer Rollen.

```
Super Admin         ← Org-Eigentümer / Kontoersteller (höchste öffentliche Rolle)
    │
Admin               ← Workspace-Einstellungen, Mitglieder, Git, Theme verwalten
    │
Editor              ← Seiten erstellen und bearbeiten (pro Workspace konfigurierbar)
    │
Commenter           ← Seiten ansehen, Kommentare hinterlassen
    │
Viewer              ← Nur Seiten ansehen
```

> **Platform Owner** ist eine interne Rolle für selbst-gehostete Betreiber zur Plattformwartung (Datenbankmigrationen, Lizenzverwaltung, Systemkonfiguration). Sie erscheint nicht in der Benutzeroberfläche oder API und ist nicht Teil der öffentlichen Rollenhierarchie.

### Berechtigungsmatrix

| Berechtigung | Viewer | Commenter | Editor | Admin | Super Admin |
|---|---|---|---|---|---|
| Seiten ansehen | Ja | Ja | Ja | Ja | Ja |
| Inhalte suchen | Ja | Ja | Ja | Ja | Ja |
| Kommentare hinterlassen | | Ja | Ja | Ja | Ja |
| Seiten bearbeiten | | | Ja | Ja | Ja |
| Seiten erstellen | | | Konfigurierbar | Ja | Ja |
| Seiten löschen | | | Konfigurierbar | Ja | Ja |
| Assets hochladen | | | Ja | Ja | Ja |
| Org-Mitglieder dem Workspace zuweisen | | | | Ja | Ja |
| Workspace-Mitglieder entfernen | | | | Ja | Ja |
| Mitgliederrollen ändern (im Workspace) | | | | Ja | Ja |
| Workspace-Einstellungen verwalten | | | | Ja | Ja |
| Theme & Navigation verwalten | | | | Ja | Ja |
| Externe Benutzer zur Org einladen | | | | | Ja |
| Workspaces erstellen/löschen | | | | | Ja |
| Git-Remote konfigurieren | | | | | Ja |
| Abrechnung & Abonnement verwalten | | | | | Ja |
| Zugriff auf alle Workspaces | | | | | Ja |
| Org-Einstellungen verwalten | | | | | Ja |

### Konfigurierbare Editor-Berechtigungen

Editor-Fähigkeiten können pro Workspace angepasst werden. Admins und Super Admins konfigurieren diese in den Workspace-Einstellungen:

| Einstellung | Standard | Beschreibung |
|---|---|---|
| `editor_can_create_pages` | `true` | Editoren können neue Seiten erstellen |
| `editor_can_delete_pages` | `false` | Editoren können Seiten löschen |

Wenn eine Berechtigung deaktiviert ist, sehen Editoren die Aktion ausgegraut in der Oberfläche und erhalten `403 Forbidden` von der API.

## Rollen zuweisen

### Erster Benutzer (Super Admin)

Der erste Benutzer, der sich auf einer neuen DocPlatform-Instanz registriert, erhält automatisch die **Super Admin**-Rolle. Dies geschieht nur einmal — nachfolgende Registrierungen erhalten keine Workspace-Rolle, bis sie eingeladen werden.

Der Super Admin ist der Org-Eigentümer und Kontoersteller. Er hat die volle Kontrolle über alle Workspaces, Abrechnung, Git-Verbindungen und externe Benutzereinladungen.

### Externe Benutzer einladen

Nur der **Super Admin** kann externe Benutzer zur Organisation einladen:

**Web-Oberfläche:** Org Settings → Members → Externen Benutzer einladen

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/org/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "default_role": "editor"
  }'
```

Der eingeladene Benutzer tritt der Organisation bei und kann dann von jedem Admin oder Super Admin einem Workspace zugewiesen werden.

### Mitglieder zu Workspaces zuweisen

**Admins** weisen bestehende Org-Mitglieder ihrem Workspace zu. Admins können keine externen Benutzer einladen — das kann nur der Super Admin.

**Web-Oberfläche:** Workspace Settings → Members → Mitglied hinzufügen → aus Org-Mitgliedern auswählen → Rolle auswählen

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/:id/members \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "01HY5K3M7Q8P",
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

Verfügbare Werte: `viewer`, `commenter`, `editor`, `admin`

## Zugriffskontrolle auf Seitenebene

Überschreiben Sie Workspace-weite Berechtigungen auf einzelnen Seiten über Frontmatter. Frontmatter-Zugriffsregeln **beschränken** innerhalb der Rolle eines Benutzers — sie gewähren niemals Berechtigungen über die Rolle hinaus.

### Syntax der Zugriffskontrolle

Verwenden Sie rollen- und benutzerbasierte Zugriffsregeln, um zu steuern, wer auf eine Seite zugreifen kann:

```yaml
---
title: Internal Security Policy
access:
  roles: ["security-team", "engineering-leads"]
  users: ["@01HY5K3M7Q8P"]
---
```

| Feld | Werttyp | Beschreibung |
|---|---|---|
| `access.roles` | Liste von Rollennamen | Rollen, die auf diese Seite zugreifen können |
| `access.users` | Liste von `@user_id` | Einzelne Benutzer, die auf diese Seite zugreifen können |

**Regeln:**
- Benutzer-IDs mit `@` voranstellen, um einzelne Benutzer anzusprechen
- Super Admin und Admin haben immer Zugriff, unabhängig von Frontmatter-Regeln
- Frontmatter kann nur **einschränken** — eine Seite kann keinen Zugriff über die Workspace-Rolle des Benutzers hinaus gewähren

### Beispiele

**Öffentliche Seite** (Standard — alle Workspace-Mitglieder können ansehen):

```yaml
---
title: Getting Started
---
```

**Auf bestimmte Teams eingeschränkt:**

```yaml
---
title: Infrastructure Runbook
access:
  roles: ["security-team", "sre-team"]
---
```

**Eingeschränkt mit individuellem Benutzerzugriff:**

```yaml
---
title: Budget Proposal
access:
  roles: ["finance-team"]
  users: ["@01HY5K3M7Q8P"]
---
```

### Was eingeschränkter Zugriff bedeutet

Wenn eine Seite `access`-Regeln hat:

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

| Rolle | Stufe | Bereich | Minimale Aktion |
|---|---|---|---|
| Viewer | 10 | Workspace | `read` |
| Commenter | 20 | Workspace | `read`, `comment` |
| Editor | 30 | Workspace | `read`, `comment`, `edit` (+ `create`/`delete` wenn aktiviert) |
| Admin | 40 | Workspace | Alle Workspace-Aktionen |
| Super Admin | — | Org | Umgeht alle Workspace-Prüfungen |

> Super Admin ist eine **Org-Ebene-Rolle** — sie umgeht Workspace-Berechtigungsprüfungen vollständig, anstatt eine numerische Stufe zu haben. Platform Owner ist ein boolesches Flag auf dem Benutzerdatensatz, das alle Prüfungen global umgeht.

Aktionen haben Mindeststufen: `read` erfordert Stufe 10+, `comment` erfordert 20+, `edit` erfordert 30+, `write`/`delete` erfordert 40+ (Editoren erhalten `edit`, aber nicht `write`/`delete`, es sei denn, die konfigurierbaren Flags sind aktiviert), `admin` erfordert 40+. Die Rollenstufe eines Benutzers wird mit der Mindeststufe der Aktion verglichen.

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
(benutzerdefiniertes RBAC: user + role + resource + action)
    │
    ├── Allowed → proceed to handler
    │
    └── Denied → 403 Forbidden
```

### 5-Schritte-Auswertungsablauf

1. **Ist der Benutzer Platform Owner?** → ERLAUBEN (globaler Bypass)
2. **Ist der Benutzer Org Super Admin für die Organisation dieses Workspaces?** → ERLAUBEN (Org-Bypass)
3. **Workspace-Rolle des Benutzers nachschlagen** → wenn kein Mitglied, VERWEIGERN
4. **Erreicht die Rollenstufe das Minimum für die Aktion?** → vergleiche `role_level >= action_min_level`, plus Editor-Berechtigungsflags
5. **Hat die Seite Zugriffsregeln im Frontmatter?** → prüfe `access.roles`/`access.users`, EINSCHRÄNKEN innerhalb der Rolle

Frontmatter SCHRÄNKT innerhalb der Rolle EIN, es GEWÄHRT niemals darüber hinaus. Ein fehlerhaftes Frontmatter fällt standardmäßig in den **strikten Modus** — Seite nur für Admins zugänglich.

### Leistung

| Metrik | Wert |
|---|---|
| **Engine** | Benutzerdefiniertes RBAC (In-Process, In-Memory) |
| **Auswertungszeit** | < 0,1ms pro Prüfung |
| **Batch-Prüfung** | < 1ms pro 100 Seiten |
| **Cache** | Versioniert (automatische Invalidierung bei Rollen- oder Berechtigungsänderung) |
| **Policy-Speicherung** | SQLite (beim Start in den Speicher geladen) |

## Berechtigungs-Caching

Benutzerdefinierte RBAC-Policies werden beim Serverstart aus SQLite in den Speicher geladen. Änderungen an Rollen oder Frontmatter-Zugriffsdeklarationen lösen eine Cache-Invalidierung aus:

1. Admin ändert die Rolle eines Benutzers → Berechtigungs-Cache-Version wird inkrementiert
2. Editor aktualisiert Seiten-Frontmatter mit neuen `access`-Regeln → Cache für diese Seite invalidiert
3. Nächste Berechtigungsprüfung lädt aktuelle Policy aus SQLite

Der Cache ist versioniert, nicht zeitbasiert — es gibt kein Fenster mit veralteten Berechtigungen.

## Gängige Muster

### Schreibgeschützte öffentliche Dokumentation mit eingeschränkten internen Seiten

```yaml
# Die meisten Seiten: keine Zugriffsregeln (offen für alle Workspace-Mitglieder)

# Interne Seiten: eingeschränkt
---
title: Incident Response Playbook
access:
  roles: ["sre-team", "admin"]
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

Super Admin hat Zugriff auf alle Workspaces für teamübergreifende Sichtbarkeit.

## Pläne und Sitzplatzlimits

### Sitzplatzzählung

**Super Admin**, **Admin** und **Editor** zählen alle zum `max_editors`-Sitzplatzlimit des Plans. Commenter- und Viewer-Rollen sind **bei allen Plänen unbegrenzt** und zählen nie zu einem Sitzplatzlimit.

Wenn das Sitzplatzlimit erreicht ist, können neue Org-Mitglieder weiterhin eingeladen werden — sie können aber nur als Commenter oder Viewer zugewiesen werden, bis ein Platz frei wird.

### Community Edition

Die Community Edition ist kostenlos und selbst-gehostet, kein Lizenzschlüssel erforderlich:

| Ressource | Limit |
|---|---|
| Workspaces | Unbegrenzt |
| Editoren (Super Admin + Admin + Editor) | Unbegrenzt |
| Viewer und Commenter | Unbegrenzt |
| Seiten | Unbegrenzt |

### Cloud-Pläne

| | Free | Team | Business |
|---|---|---|---|
| **Workspaces** | 1 | 5 | 15 |
| **Sitzplätze** (Super Admin + Admin + Editor) | 3 | 15 | 50 |
| **Viewer & Commenter** | Unbegrenzt | Unbegrenzt | Unbegrenzt |
| **Seiten** | Unbegrenzt | Unbegrenzt | Unbegrenzt |

> Mehr benötigt? [Vertrieb kontaktieren](https://valoryx.org/contact) für Enterprise-Pläne mit individuellen Limits, SSO und SLA.

Für vollständige Abrechnungsdetails siehe [Abrechnung & Pläne](../guides/billing.md).

## Fehlerbehebung

### „403 Forbidden" auf einer Seite, auf die ich Zugriff haben sollte

1. Prüfen Sie Ihre Rolle: Profil → Workspace Membership
2. Prüfen Sie das Frontmatter der Seite: enthält `access.roles` Ihre Rolle?
3. Bitten Sie einen Workspace-Admin, Ihre Rollenzuweisung zu verifizieren
4. Wenn Sie Editor sind, prüfen Sie, ob die Aktion `editor_can_create_pages` oder `editor_can_delete_pages` als aktiviert erfordert

### Berechtigungsänderungen werden nicht wirksam

Berechtigungsänderungen sollten sofort wirksam sein (Cache-Invalidierung ist synchron). Wenn nicht:

1. Melden Sie sich ab und wieder an (aktualisieren Sie Ihre JWT-Token)
2. Prüfen Sie die Server-Logs auf Cache-Invalidierungsfehler
3. Führen Sie `docplatform doctor` aus, um den Zustand des Berechtigungssystems zu verifizieren

### Erster Benutzer ist nicht Super Admin

Dies tritt auf, wenn der erste Benutzer sich registriert, während die Datenbank bereits Benutzerdatensätze enthält (z. B. aus einer vorherigen Installation). Lösung:

1. Server stoppen
2. Datenbank löschen: `rm {DATA_DIR}/data.db`
3. Server starten und erneut registrieren

Dies setzt alle Daten zurück. Verwenden Sie dies nur bei Neuinstallationen.

### „Sitzplatzlimit erreicht" beim Einladen eines Mitglieds

Das `max_editors`-Limit des Plans wurde erreicht. Optionen:

1. Einen bestehenden Admin oder Editor zu Commenter oder Viewer herabstufen, um einen Platz freizugeben
2. Den neuen Benutzer als Commenter oder Viewer einladen (diese sind unbegrenzt)
3. Ihren Plan für mehr Sitzplätze upgraden
