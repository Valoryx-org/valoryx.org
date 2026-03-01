---
title: Umgebungsvariablen
description: Vollständige Referenz aller DocPlatform-Umgebungsvariablen — Server, Datenbank, Git, Authentifizierung, E-Mail und Betrieb.
weight: 1
---

# Umgebungsvariablen

DocPlatform liest die Konfiguration aus Umgebungsvariablen. Setzen Sie diese in Ihrer Shell, einer `.env`-Datei im Arbeitsverzeichnis oder in Ihrem Container-Orchestrator.

## Server

| Variable | Standard | Beschreibung |
|---|---|---|
| `PORT` | `3000` | HTTP-Listening-Port |
| `HOST` | `0.0.0.0` | HTTP-Listening-Adresse. Setzen Sie auf `127.0.0.1`, um auf localhost zu beschränken. |
| `DATA_DIR` | `.docplatform` | Stammverzeichnis für alle DocPlatform-Daten (Datenbank, Backups, Workspaces, Schlüssel) |
| `BASE_DOMAIN` | — | Eigene Domain für veröffentlichte Dokumentation (z. B. `docs.yourcompany.com`). Wenn gesetzt, verwendet die veröffentlichte Dokumentation diese Domain für kanonische URLs und Sitemap-Einträge. |
| `PUBLISH_REQUIRE_AUTH` | `false` | Wenn `true`, erfordern alle veröffentlichten Dokumentationsseiten, dass der Besucher als Workspace-Mitglied angemeldet ist. Nicht authentifizierte Besucher werden zur Anmeldeseite weitergeleitet und nach der Anmeldung zur Originalseite zurückgeführt. |

## Authentifizierung

| Variable | Standard | Beschreibung |
|---|---|---|
| `JWT_SECRET_PATH` | `{DATA_DIR}/jwt-key.pem` | Pfad zum RS256-Privatschlüssel für JWT-Signierung. Wird beim ersten Start automatisch generiert, wenn nicht vorhanden. |
| `JWT_ACCESS_TTL` | `900` | Access-Token-Lebensdauer in Sekunden (Standard: 15 Minuten) |
| `JWT_REFRESH_TTL` | `2592000` | Refresh-Token-Lebensdauer in Sekunden (Standard: 30 Tage) |

## OIDC-Anbieter (optional)

Aktivieren Sie Google- und/oder GitHub-Anmeldung durch Setzen dieser Variablen. Wenn nicht gesetzt, steht nur die lokale Authentifizierung (E-Mail + Passwort) zur Verfügung.

| Variable | Standard | Beschreibung |
|---|---|---|
| `OIDC_GOOGLE_CLIENT_ID` | — | Google OAuth 2.0 Client-ID |
| `OIDC_GOOGLE_CLIENT_SECRET` | — | Google OAuth 2.0 Client-Secret |
| `OIDC_GITHUB_CLIENT_ID` | — | GitHub OAuth Client-ID |
| `OIDC_GITHUB_CLIENT_SECRET` | — | GitHub OAuth Client-Secret |

Siehe [Authentifizierung](authentication.md) für Einrichtungsanleitungen.

## Git

| Variable | Standard | Beschreibung |
|---|---|---|
| `GIT_SSH_KEY_PATH` | `~/.ssh/docplatform_deploy_key` | Pfad zum privaten SSH-Schlüssel für Git-Operationen. Erforderlich für private Repositories über SSH. |
| `GIT_SYNC_INTERVAL` | `300` | Standard-Polling-Intervall in Sekunden für Remote-Synchronisation (Minimum: 10). Wird durch workspace-spezifisches `sync_interval` überschrieben. Setzen Sie auf `0` für Webhook-only-Synchronisation (kein Polling). |
| `GIT_AUTO_COMMIT` | `true` | Standard-Auto-Commit-Verhalten. Wird durch workspace-spezifisches `git_auto_commit` überschrieben. |
| `GIT_WEBHOOK_SECRET` | — | Gemeinsames Secret zur Verifizierung von Webhook-Payloads (HMAC-SHA256) von GitHub, GitLab oder Bitbucket. |
| `GIT_COMMIT_NAME` | `DocPlatform` | Git-Committer-Name für Auto-Commits |
| `GIT_COMMIT_EMAIL` | `docplatform@local` | Git-Committer-E-Mail für Auto-Commits |

## E-Mail (optional)

Konfigurieren Sie SMTP für Workspace-Einladungen und Passwort-Zurücksetzungs-E-Mails. Ohne SMTP werden Token auf stdout (Server-Logs) ausgegeben.

| Variable | Standard | Beschreibung |
|---|---|---|
| `SMTP_HOST` | — | SMTP-Server-Hostname (z. B. `smtp.gmail.com`) |
| `SMTP_PORT` | `587` | SMTP-Port (587 für STARTTLS, 465 für SSL) |
| `SMTP_FROM` | — | Absender-E-Mail-Adresse (z. B. `docs@yourcompany.com`) |
| `SMTP_USERNAME` | — | SMTP-Authentifizierungs-Benutzername |
| `SMTP_PASSWORD` | — | SMTP-Authentifizierungs-Passwort |

## Backups

| Variable | Standard | Beschreibung |
|---|---|---|
| `BACKUP_ENABLED` | `true` | Tägliche automatisierte SQLite-Backups aktivieren |
| `BACKUP_RETENTION_DAYS` | `7` | Anzahl der Tage, die Backup-Dateien aufbewahrt werden. Ältere Backups werden automatisch gelöscht. |
| `BACKUP_DIR` | `{DATA_DIR}/backups` | Verzeichnis für Backup-Dateien |

## Telemetrie

| Variable | Standard | Beschreibung |
|---|---|---|
| `DOCPLATFORM_TELEMETRY` | `off` | Setzen Sie auf `on`, um anonyme, opt-in Nutzungsmetriken zu aktivieren. Wenn aktiviert, wird wöchentlich eine SHA-256-Installations-ID (keine personenbezogenen Daten) gesendet. |
| `DOCPLATFORM_TELEMETRY_ENDPOINT` | — | Benutzerdefinierter Endpunkt für Telemetriedaten (fortgeschritten — für Air-Gapped-Umgebungen mit interner Analyse) |

### Was die Telemetrie sendet (wenn aktiviert)

- SHA-256-Installations-ID (abgeleitet vom Datenverzeichnis, nicht umkehrbar)
- Workspace-Anzahl und Gesamtseitenanzahl
- DocPlatform-Version
- Betriebssystem und Architektur

Telemetrie sendet **niemals**: Seiteninhalte, Benutzer-E-Mails, IP-Adressen, Dateinamen oder personenbezogene Daten. Frequenz: wöchentlich.

## Frontmatter-Behandlung

| Variable | Standard | Beschreibung |
|---|---|---|
| `FRONTMATTER_ERROR_MODE` | `strict` | Umgang mit ungültigem YAML-Frontmatter: `strict` beschränkt die Seite auf Admin-only-Zugriff (verhindert versehentliche Freigabe); `lenient` behält das zuletzt bekannte gültige Frontmatter bei und zeigt eine Warnung an. |

## Verwendung einer `.env`-Datei

Erstellen Sie eine `.env`-Datei in dem Verzeichnis, in dem Sie `docplatform serve` ausführen:

```bash
# .env
PORT=8080
DATA_DIR=/var/lib/docplatform
GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_FROM=docs@example.com
SMTP_USERNAME=docs@example.com
SMTP_PASSWORD=app-specific-password
BACKUP_RETENTION_DAYS=30
```

DocPlatform lädt die `.env`-Datei automatisch. Umgebungsvariablen, die in der Shell gesetzt sind, haben Vorrang vor `.env`-Werten.

## Docker-Umgebung

Übergeben Sie Umgebungsvariablen an Docker mit `-e`-Flags oder einer Env-Datei:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  -e DATA_DIR=/data \
  -e SMTP_HOST=smtp.example.com \
  -e SMTP_FROM=docs@example.com \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

## Sicherheitshinweise

- **Committen Sie niemals `.env`-Dateien** in die Versionskontrolle. Fügen Sie `.env` zu Ihrer `.gitignore` hinzu.
- **JWT-Schlüssel** werden automatisch generiert. Wenn Sie rotieren müssen, löschen Sie die Schlüsseldatei und starten Sie neu — ein neuer Schlüssel wird generiert und alle bestehenden Sitzungen werden invalidiert.
- **SMTP-Passwörter** — verwenden Sie App-spezifische Passwörter oder API-Keys, nicht Ihr primäres Kontopasswort.
- **Git-Token** — verwenden Sie Repository-spezifische Token mit minimalen Berechtigungen (Lese- + Schreibzugriff für die Synchronisation).
