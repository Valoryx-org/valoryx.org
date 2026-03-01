---
title: Authentifizierung
description: Konfigurieren Sie lokale Authentifizierung, Google- und GitHub-OIDC-Anmeldung, JWT-Einstellungen und Passwortrichtlinien.
weight: 2
---

# Authentifizierung

DocPlatform unterstützt lokale Authentifizierung (E-Mail + Passwort) direkt nach der Installation, mit optionaler Google- und GitHub-OIDC-Anmeldung für Teams, die diese Anbieter nutzen.

## Lokale Authentifizierung (Standard)

Lokale Authentifizierung funktioniert ohne jegliche Konfiguration. Benutzer registrieren sich mit E-Mail und Passwort und melden sich mit denselben Anmeldedaten an.

### Wie es funktioniert

1. **Registrierung** — Der Benutzer übermittelt E-Mail + Passwort. Das Passwort wird mit argon2id gehasht (von OWASP 2024 empfohlener Algorithmus).
2. **Anmeldung** — Der Benutzer übermittelt seine Anmeldedaten. Der Server verifiziert den Passwort-Hash und gibt JWT-Token zurück.
3. **Sitzung** — Der Access-Token (RS256, 15 Minuten Lebensdauer) wird mit jeder API-Anfrage gesendet. Der Refresh-Token (30 Tage Lebensdauer) wird verwendet, um neue Access-Token ohne erneute Authentifizierung zu erhalten.

### Passwort-Hashing

DocPlatform verwendet argon2id mit folgenden Parametern (OWASP 2024 Standard):

| Parameter | Wert |
|---|---|
| **Algorithmus** | argon2id |
| **Speicher** | 64 MB |
| **Iterationen** | 3 |
| **Parallelität** | 4 |
| **Salt-Länge** | 16 Bytes |
| **Schlüssellänge** | 32 Bytes |

Diese Parameter sind nicht konfigurierbar — sie folgen Best Practices für Sicherheit. Passwort-Hashes werden in der SQLite-Datenbank gespeichert und verlassen niemals den Server.

### Passwort-Zurücksetzung

Wenn ein Benutzer eine Passwort-Zurücksetzung anfordert:

- **Mit konfiguriertem SMTP** — ein Einmal-Reset-Link wird per E-Mail an den Benutzer gesendet
- **Ohne SMTP** — der Reset-Token wird auf stdout (Server-Logs) ausgegeben

```bash
# Server-Logs nach dem Reset-Token durchsuchen
docplatform serve 2>&1 | grep "password reset"
```

Der Token läuft nach 1 Stunde ab und kann nur einmal verwendet werden.

## JWT-Token

DocPlatform gibt RS256 (RSA-SHA256) JSON Web Token für die Authentifizierung aus.

### Token-Lebenszyklus

```
User logs in
    │
    ▼
┌─────────────────────────────────┐
│ Access Token (15 min)            │  ──►  Sent with every API request
│ Refresh Token (30 days)          │  ──►  Used to get new access tokens
└─────────────────────────────────┘
    │
    │  Access token expires
    ▼
┌─────────────────────────────────┐
│ POST /api/v1/auth/refresh        │
│ Body: { refresh_token: "..." }   │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ New Access Token (15 min)        │  ──►  Old refresh token rotated
│ New Refresh Token (30 days)      │  ──►  Old one invalidated
└─────────────────────────────────┘
```

### Refresh-Token-Rotation

Jedes Mal, wenn ein Refresh-Token verwendet wird, wird ein neuer Refresh-Token ausgegeben und der alte invalidiert. Dies begrenzt das Risikofenster, falls ein Token kompromittiert wird.

### Konfiguration

| Variable | Standard | Beschreibung |
|---|---|---|
| `JWT_SECRET_PATH` | `{DATA_DIR}/jwt-key.pem` | Pfad zum RS256-Privatschlüssel |
| `JWT_ACCESS_TTL` | `900` | Access-Token-Lebensdauer (Sekunden) |
| `JWT_REFRESH_TTL` | `2592000` | Refresh-Token-Lebensdauer (Sekunden) |

### Schlüsselverwaltung

Das RS256-Schlüsselpaar wird beim ersten Start automatisch generiert, wenn die Datei nicht existiert. Um Schlüssel zu rotieren:

1. Server stoppen
2. Schlüsseldatei löschen (`{DATA_DIR}/jwt-key.pem`)
3. Server starten — ein neuer Schlüssel wird generiert

Alle bestehenden Sitzungen werden bei Schlüsselrotation invalidiert. Benutzer müssen sich erneut anmelden.

## Google-OIDC-Anmeldung (optional)

Ermöglichen Sie Benutzern die Anmeldung mit ihrem Google-Konto.

### Einrichtung

1. Gehen Sie zur [Google Cloud Console](https://console.cloud.google.com/)
2. Erstellen Sie ein neues Projekt (oder verwenden Sie ein bestehendes)
3. Navigieren Sie zu **APIs & Services** → **Credentials**
4. Klicken Sie auf **Create Credentials** → **OAuth 2.0 Client ID**
5. Anwendungstyp: **Web application**
6. Fügen Sie die autorisierte Redirect-URI hinzu: `https://your-domain.com/api/v1/auth/callback/google`
7. Kopieren Sie Client-ID und Client-Secret

Setzen Sie die Umgebungsvariablen:

```bash
export OIDC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
export OIDC_GOOGLE_CLIENT_SECRET=your-client-secret
```

Starten Sie den Server neu. Ein **Sign in with Google**-Button erscheint auf der Anmeldeseite.

### Benutzerbereitstellung

Wenn sich ein Benutzer zum ersten Mal über Google anmeldet:

- Ein DocPlatform-Konto wird mit seiner Google-E-Mail erstellt
- Ihm wird die Standardrolle (`permissions.default_role`) in jedem Workspace zugewiesen, zu dem er eingeladen wird
- Kein Passwort wird gesetzt (er kann später eines über sein Profil hinzufügen)

## GitHub-OIDC-Anmeldung (optional)

Ermöglichen Sie Benutzern die Anmeldung mit ihrem GitHub-Konto.

### Einrichtung

1. Gehen Sie zu [GitHub Developer Settings](https://github.com/settings/developers)
2. Klicken Sie auf **New OAuth App**
3. Setzen Sie die Authorization-Callback-URL: `https://your-domain.com/api/v1/auth/callback/github`
4. Kopieren Sie die Client-ID und generieren Sie ein Client-Secret

Setzen Sie die Umgebungsvariablen:

```bash
export OIDC_GITHUB_CLIENT_ID=your-client-id
export OIDC_GITHUB_CLIENT_SECRET=your-client-secret
```

Starten Sie den Server neu. Ein **Sign in with GitHub**-Button erscheint auf der Anmeldeseite.

### Benutzerbereitstellung

Wie bei Google — ein DocPlatform-Konto wird mit der primären GitHub-E-Mail erstellt. Wenn das GitHub-Konto keine öffentliche E-Mail hat, wird der Benutzer aufgefordert, eine einzugeben.

## Sitzungsverwaltung

DocPlatform verfolgt aktive Sitzungen pro Benutzer:

| Feld | Beschreibung |
|---|---|
| **Gerät** | User-Agent-String |
| **IP-Adresse** | Client-IP (für Auditzwecke) |
| **Erstellt** | Wann die Sitzung aufgebaut wurde |
| **Zuletzt aktiv** | Letzte API-Anfrage |

Benutzer können Sitzungen auf ihrer Profilseite einsehen und widerrufen. Admins können alle Sitzungen über das Admin-Panel einsehen.

### Sitzungen widerrufen

- **Vom Benutzer initiiert** — Profil → Sessions → Revoke
- **Vom Admin initiiert** — Admin → Users → Benutzer auswählen → Revoke All Sessions
- **Schlüsselrotation** — Das Löschen des JWT-Schlüssels invalidiert alle Sitzungen global

## Passwortrichtlinie

| Einschränkung | Wert |
|---|---|
| Mindestlänge | 8 Zeichen |
| Maximale Länge | 128 Zeichen |
| Hashing | argon2id (64 MB Speicher, 3 Iterationen, Parallelität 4) |

Passwörter werden bei Registrierung und Passwort-Zurücksetzung validiert. DocPlatform erzwingt keine Zeichenklassen-Anforderungen (Großbuchstaben, Sonderzeichen) — die Länge ist gemäß den aktuellen NIST-Richtlinien die primäre Sicherheitsmaßnahme.

## WebSocket-Authentifizierung

WebSocket-Verbindungen verwenden ein Einmal-Ticket-Verfahren, um zu vermeiden, dass JWT-Token in URLs offengelegt werden (die in Server-Logs und Browser-Verlauf erscheinen würden).

**Ablauf:**

1. Client ruft `POST /api/v1/auth/ws-ticket` mit einem gültigen JWT auf
2. Server gibt ein zufälliges Ticket zurück (gültig für **30 Sekunden**, einmalige Verwendung)
3. Client verbindet sich mit `ws://host/ws?ticket={ticket}`
4. Server validiert das Ticket, baut die WebSocket-Verbindung auf und verwirft das Ticket

Dies ist für Benutzer transparent — der Web-Editor übernimmt die Ticket-Beschaffung automatisch.

## Sicherheitsempfehlungen

- **Aktivieren Sie OIDC** für Teams mit Google- oder GitHub-Konten — delegiert die Passwortverwaltung an etablierte Anbieter
- **Verwenden Sie HTTPS** in der Produktion — JWT-Token sind Bearer-Token; abgefangene Token gewähren vollen Zugriff
- **Halten Sie Token-Lebensdauern kurz** — 15-Minuten-Access-Token begrenzen das Risiko
- **Überwachen Sie Sitzungen** — überprüfen Sie aktive Sitzungen regelmäßig auf unerwartete Geräte oder IPs
- **Rotieren Sie Schlüssel** jährlich oder nach jedem Verdacht auf Kompromittierung
- **Verwenden Sie HttpOnly-Cookies** — DocPlatform speichert Token in HttpOnly + Secure + SameSite=Strict Cookies, was XSS-Token-Diebstahl verhindert
