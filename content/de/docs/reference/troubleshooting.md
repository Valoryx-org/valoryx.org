---
title: Fehlerbehebung
description: Häufige Probleme und Lösungen für DocPlatform — Serverstart, Git-Synchronisation, Authentifizierung, Suche und Datenwiederherstellung.
weight: 3
---

# Fehlerbehebung

Dieser Leitfaden behandelt häufige Probleme und deren Lösungen. Für Diagnoseinformationen starten Sie immer mit:

```bash
docplatform doctor
```

## Serverstart

### Server startet nicht: „address already in use"

**Ursache:** Ein anderer Prozess belegt den konfigurierten Port.

**Lösung:**

```bash
# Herausfinden, was Port 3000 belegt
lsof -i :3000  # macOS/Linux
ss -tlnp | grep 3000  # Linux

# Option 1: Den anderen Prozess stoppen
# Option 2: Einen anderen Port verwenden
docplatform serve --port 8080
```

### Server startet nicht: „permission denied"

**Ursache:** Der Prozess hat keine Lese-/Schreibrechte für das Datenverzeichnis.

**Lösung:**

```bash
# Eigentümer prüfen
ls -la .docplatform/

# Eigentümer korrigieren (wenn als docplatform-Benutzer ausgeführt)
sudo chown -R docplatform:docplatform .docplatform/

# Berechtigungen korrigieren
chmod 700 .docplatform/
```

### Server startet nicht: „database is locked"

**Ursache:** Ein anderer DocPlatform-Prozess läuft, oder ein vorheriger Prozess wurde nicht sauber heruntergefahren.

**Lösung:**

```bash
# Auf andere docplatform-Prozesse prüfen
ps aux | grep docplatform

# Wenn ein Prozess hängt, beenden
kill -SIGTERM <pid>

# Wenn die Lock-Datei nach dem Ende aller Prozesse bestehen bleibt
# SQLite WAL-Modus handhabt dies automatisch beim Neustart
docplatform serve
```

## Git-Synchronisation

### „Permission denied (publickey)" bei Git-Synchronisation

**Ursache:** Der SSH-Schlüssel ist nicht konfiguriert oder hat keinen Zugriff auf das Repository.

**Lösung:**

1. Überprüfen Sie, ob der Schlüssel existiert:
   ```bash
   ls -la $GIT_SSH_KEY_PATH
   ```

2. Überprüfen Sie, ob der Schlüssel zu den Deploy-Keys des Repositories hinzugefügt wurde:
   ```bash
   ssh -T -i $GIT_SSH_KEY_PATH git@github.com
   ```

3. Stellen Sie sicher, dass der Schreibzugriff auf dem Deploy-Key aktiviert ist (erforderlich zum Pushen)

### Git-Synchronisation zeigt „no changes", aber Dateien wurden aktualisiert

**Ursache:** Änderungen wurden an Dateien außerhalb des `docs/`-Verzeichnisses vorgenommen, das DocPlatform nicht indiziert.

**Lösung:** Stellen Sie sicher, dass Ihre Markdown-Dateien im `docs/`-Verzeichnis des Workspace liegen. Dateien in anderen Verzeichnissen werden in Git beibehalten, aber nicht von DocPlatform verfolgt.

### Konflikt: HTTP 409 beim Speichern

**Ursache:** Die Seite wurde von einem anderen Benutzer oder über einen Git-Push zwischen Ihrem Laden und Speichern geändert.

**Lösung:**

1. Die Web-Oberfläche zeigt ein Konflikt-Banner mit beiden Versionen
2. Klicken Sie auf **Download both**, um beide Dateien herunterzuladen
3. Führen Sie die Änderungen manuell zusammen
4. Speichern Sie die zusammengeführte Version

**Vorbeugung:**

- Aktivieren Sie Webhooks für schnellere Synchronisation (verkleinertes Konfliktfenster)
- Verwenden Sie Präsenzindikatoren, um zu sehen, wer was bearbeitet
- Weisen Sie Seitenverantwortung zu, um gleichzeitige Bearbeitungen zu vermeiden

### Git-Push schlägt fehl: „remote rejected"

**Ursache:** Der Deploy-Key hat keinen Schreibzugriff, oder Branch-Schutzregeln verhindern direkte Pushes.

**Lösung:**

1. Überprüfen Sie, ob der Deploy-Key Schreibzugriff in Ihren Repository-Einstellungen hat
2. Prüfen Sie Branch-Schutzregeln — DocPlatform pusht direkt auf den konfigurierten Branch
3. Wenn Branch-Schutz erforderlich ist, konfigurieren Sie DocPlatform so, dass es auf einen ungeschützten Branch pusht

## Authentifizierung

### „401 Unauthorized" bei jeder Anfrage

**Ursache:** Der JWT-Access-Token ist abgelaufen (standardmäßig 15 Minuten Lebensdauer).

**Lösung:** Der Web-Editor handhabt die Token-Aktualisierung automatisch. Wenn Sie die API direkt verwenden, rufen Sie den Refresh-Endpunkt auf:

```bash
curl -X POST http://localhost:3000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

### Anmeldung nach JWT-Schlüsselrotation nicht möglich

**Ursache:** Alle Token wurden invalidiert, als der JWT-Schlüssel gelöscht und neu generiert wurde.

**Lösung:** Dies ist das erwartete Verhalten. Alle Benutzer müssen sich nach einer Schlüsselrotation erneut anmelden. Löschen Sie Ihre Browser-Cookies/Speicher und melden Sie sich mit Ihrem Passwort an.

### OIDC-Anmeldung leitet zu einer Fehlerseite weiter

**Ursache:** Die OAuth-Callback-URL stimmt nicht mit der in Google/GitHub konfigurierten überein.

**Lösung:**

1. Prüfen Sie die Callback-URL in den Einstellungen Ihres OAuth-Anbieters
2. Sie sollte lauten: `https://your-domain.com/api/v1/auth/callback/google` (oder `/github`)
3. Stellen Sie sicher, dass die Umgebungsvariablen `OIDC_*_CLIENT_ID` und `OIDC_*_CLIENT_SECRET` korrekt gesetzt sind
4. Starten Sie den Server nach dem Ändern von OIDC-Umgebungsvariablen neu

### Erster Benutzer ist nicht SuperAdmin

**Ursache:** Die Datenbank enthielt bereits Benutzerdatensätze aus einer vorherigen Installation.

**Lösung:**

```bash
# WARNUNG: Dies löscht alle Daten
docplatform serve  # zuerst stoppen
rm .docplatform/data.db
docplatform serve
# Registrieren Sie Ihr Admin-Konto
```

Tun Sie dies nur bei einer Neuinstallation. Für bestehende Installationen verwenden Sie die Datenbank, um Benutzerrollen direkt zu aktualisieren (fortgeschritten).

## Suche

### Suche gibt keine Ergebnisse zurück

**Ursache:** Der Suchindex ist möglicherweise leer oder nicht synchron.

**Lösung:**

```bash
# Suchstatus prüfen
docplatform doctor

# Wenn der Index nicht synchron ist, neu aufbauen
docplatform rebuild
```

### Suchergebnisse sind veraltet (spiegeln aktuelle Bearbeitungen nicht wider)

**Ursache:** Der asynchrone Indizierungsjob wurde noch nicht verarbeitet (typischerweise < 1 Sekunde Verzögerung).

**Lösung:** Warten Sie einen Moment und versuchen Sie es erneut. Wenn das Problem weiterhin besteht:

1. Prüfen Sie die Server-Logs auf Indizierungsfehler
2. Führen Sie `docplatform rebuild` aus, um eine vollständige Neuindizierung zu erzwingen

### Suche ist langsam

**Ursache:** Sehr große Workspaces (1000+ Seiten) mit komplexen Abfragen.

**Lösung:**

- Verwenden Sie spezifischere Suchbegriffe
- Verwenden Sie Tag-Filter, um den Bereich einzugrenzen
- Zukünftige Releases werden Meilisearch für Hochleistungssuche unterstützen

## Datenwiederherstellung

### Seite versehentlich gelöscht

**Option 1: Git-Historie** (wenn Git-Synchronisation aktiviert ist)

```bash
cd .docplatform/workspaces/{id}/docs/
git log --all -- path/to/deleted-page.md
git checkout <commit-hash> -- path/to/deleted-page.md
```

Führen Sie dann `docplatform rebuild` aus, um neu zu indizieren.

**Option 2: Datenbank-Backup**

```bash
# Backups auflisten
ls .docplatform/backups/

# Aus Backup wiederherstellen (Server vorher stoppen)
cp .docplatform/backups/{latest}.db .docplatform/data.db
docplatform serve
```

### Datenbank ist beschädigt

**Lösung:**

1. Server stoppen
2. Nach einem aktuellen Backup suchen:
   ```bash
   ls -la .docplatform/backups/
   ```
3. Aus Backup wiederherstellen:
   ```bash
   cp .docplatform/backups/{latest}.db .docplatform/data.db
   ```
4. Wenn kein Backup verfügbar ist, aus dem Dateisystem neu aufbauen:
   ```bash
   rm .docplatform/data.db
   docplatform rebuild
   ```
5. Server starten

Das Dateisystem (`.md`-Dateien) ist die Quelle der Wahrheit. Selbst wenn die Datenbank verloren geht, erstellt `rebuild` sie aus Ihren Dateien neu.

### JWT-Schlüssel verloren

**Ursache:** Die `jwt-key.pem`-Datei wurde gelöscht.

**Auswirkung:** Alle Benutzersitzungen werden invalidiert. Benutzer müssen sich erneut anmelden.

**Lösung:** Starten Sie den Server — ein neuer Schlüssel wird automatisch generiert. Keine Daten gehen verloren, aber alle Benutzer müssen sich erneut authentifizieren.

## Frontmatter-Fehler

### Seite wird nach Frontmatter-Bearbeitung unzugänglich

**Ursache:** Ungültiges YAML im Frontmatter-Block. DocPlatform verwendet standardmäßig den **Strict-Modus** — wenn das Frontmatter-Parsing fehlschlägt, wird die Seite auf WorkspaceAdmin-only-Zugriff beschränkt, um zu verhindern, dass ein YAML-Tippfehler versehentlich eine private Seite öffentlich macht.

**Symptome:**

- Seite verschwindet aus Suchergebnissen
- Seite wird aus veröffentlichter Dokumentation ausgeschlossen
- Nicht-Admin-Benutzer erhalten 403 Forbidden
- Admin sieht ein Warnbanner auf der Seite

**Lösung:**

1. Melden Sie sich als WorkspaceAdmin oder SuperAdmin an
2. Öffnen Sie die betroffene Seite im Web-Editor
3. Wechseln Sie zum Raw-Markdown-Modus (`</>` Umschalter)
4. Korrigieren Sie das YAML-Frontmatter (häufige Probleme: fehlende Anführungszeichen bei Werten mit Doppelpunkten, falsche Einrückung, nicht geschlossene Klammern)
5. Speichern — die Seite wird neu indiziert und der Zugriff wiederhergestellt

**Wenn Sie keinen Zugriff auf den Web-Editor haben**, korrigieren Sie die Datei direkt auf der Festplatte:

```bash
# Markdown-Datei bearbeiten
nano .docplatform/workspaces/{id}/docs/{path-to-page}.md

# Neu aufbauen, um zu reindizieren
docplatform rebuild
```

### Frontmatter-Fehlermodi verstehen

| Modus | Verhalten bei ungültigem YAML | Wann zu verwenden |
|---|---|---|
| **Strict** (Standard) | Seite auf WorkspaceAdmin beschränkt, aus Suche und veröffentlichter Dokumentation ausgeschlossen | Produktion — verhindert versehentliche Freigabe |
| **Lenient** | Zuletzt bekanntes gültiges Frontmatter aus der Datenbank beibehalten, Warnung anzeigen | Entwicklung — weniger Unterbrechung beim Bearbeiten |

Der Strict-Modus stellt sicher, dass ein YAML-Tippfehler niemals versehentlich eine eingeschränkte Seite öffentlich macht. Dies ist ein bewusstes Sicherheitsdesign.

## Speicherplatz

### „Low disk space"-Warnung von Doctor

**Ursache:** DocPlatform warnt, wenn der freie Speicherplatz unter 1 GB fällt.

**Auswirkung:** SQLite benötigt freien Speicherplatz für WAL (Write-Ahead-Log)-Operationen. Wenn die Festplatte vollständig gefüllt ist, schlagen Schreibvorgänge fehl und Daten können beschädigt werden.

**Lösung:**

1. Festplattennutzung prüfen: `df -h`
2. Alte Backups bereinigen: `BACKUP_RETENTION_DAYS` reduzieren oder alte Dateien in `{DATA_DIR}/backups/` manuell löschen
3. Datenverzeichnis auf eine größere Festplatte verschieben: `DATA_DIR` aktualisieren und das Verzeichnis verschieben
4. Bei Docker die Volume-Größe erhöhen

## Leistung

### Hoher Speicherverbrauch

**Erwartet:** < 80 MB im Leerlauf, < 200 MB unter Last.

Wenn der Speicherverbrauch 200 MB überschreitet:

1. Prüfen Sie die Anzahl aktiver WebSocket-Verbindungen
2. Prüfen Sie die Workspace-Anzahl und Gesamtseitenanzahl
3. Große Git-Repositories (>5.000 Dateien) verbrauchen mehr Speicher — die hybride Engine wechselt automatisch zur nativen Git-CLI, wenn go-git 512 MB RSS überschreitet

### Langsame Seiten-Renders

**Erwartet:** < 50ms p99.

Wenn Seiten-Renders langsam sind:

1. Prüfen Sie die Festplatten-I/O — SQLite-Leistung hängt von der Festplattengeschwindigkeit ab
2. Verwenden Sie eine SSD für das Datenverzeichnis
3. Prüfen Sie, ob die Datenbankdatei auf einem Netzwerk-Dateisystem (NFS/CIFS) liegt — auf lokale Festplatte verschieben

## Hilfe erhalten

Wenn Sie ein Problem nicht lösen können:

1. Führen Sie `docplatform doctor --bundle` aus, um ein Diagnose-Bundle zu generieren
2. Prüfen Sie die Server-Logs auf Fehlermeldungen
3. Erstellen Sie ein Issue auf GitHub mit dem Diagnose-Bundle und relevanten Log-Einträgen

Das Diagnose-Bundle enthält **keine** Seiteninhalte, Passwörter oder API-Token — nur strukturelle Metadaten und Konfiguration (mit geschwärzten Secrets).
