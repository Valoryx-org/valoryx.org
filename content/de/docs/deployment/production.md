---
title: Produktions-Checkliste
description: Alles, was Sie überprüfen müssen, bevor Sie DocPlatform in einer Produktionsumgebung betreiben.
weight: 3
---

# Produktions-Checkliste

Verwenden Sie diese Checkliste, bevor Sie DocPlatform in einer Produktionsumgebung deployen. Jeder Punkt verlinkt zum relevanten Dokumentationsabschnitt.

## Erforderlich

Diese Punkte sind für ein sicheres, zuverlässiges Produktions-Deployment notwendig.

### Server

- [ ] **Persistenter Speicher konfiguriert** — Mounten Sie ein Volume oder verwenden Sie einen stabilen Dateisystempfad für `DATA_DIR`. Der Verlust dieses Verzeichnisses bedeutet Verlust aller Daten.
- [ ] **Prozessmanager vorhanden** — Verwenden Sie systemd, Docker mit `restart: unless-stopped` oder einen Container-Orchestrator, um sicherzustellen, dass der Server nach Abstürzen oder Neustarts wieder hochfährt.
- [ ] **Port erreichbar** — Stellen Sie sicher, dass der konfigurierte `PORT` (Standard: 3000) von Ihrem Netzwerk oder Reverse Proxy erreichbar ist.
- [ ] **Ausreichende Ressourcen** — Minimum 128 MB RAM, 200 MB Festplatte. Empfohlen 512 MB RAM, 1 GB Festplatte.

### Sicherheit

- [ ] **TLS aktiviert** — Betreiben Sie DocPlatform hinter einem Reverse Proxy (Caddy, nginx, Cloud-Load-Balancer) mit HTTPS. DocPlatform terminiert TLS nicht selbst.
- [ ] **JWT-Schlüssel gesichert** — Die `jwt-key.pem`-Datei ermöglicht das Fälschen von Authentifizierungs-Token. Schränken Sie die Dateisystemberechtigungen ein: `chmod 600`.
- [ ] **Erster Benutzer registriert** — Der erste registrierte Benutzer wird zum SuperAdmin. Registrieren Sie Ihr Admin-Konto, bevor Sie den Server für andere öffnen.
- [ ] **An localhost binden** — Wenn Sie einen Reverse Proxy auf demselben Host verwenden, setzen Sie `HOST=127.0.0.1`, damit DocPlatform nicht direkt zugänglich ist.

### Backups

- [ ] **Backups aktiviert** — `BACKUP_ENABLED=true` (Standard). Überprüfen Sie, dass Backups in `{DATA_DIR}/backups/` erstellt werden.
- [ ] **Backup-Aufbewahrung eingestellt** — `BACKUP_RETENTION_DAYS` gemäß Ihrer Richtlinie konfiguriert (Standard: 7 Tage).
- [ ] **Off-Server-Backup** — Kopieren Sie Backup-Dateien an einen separaten Ort (S3, NFS, ein anderer Server). On-Disk-Backups schützen nicht vor Festplattenausfällen.

## Empfohlen

Diese Punkte verbessern Zuverlässigkeit, Sicherheit und Teamzufriedenheit.

### Authentifizierung

- [ ] **OIDC konfiguriert** — Wenn Ihr Team Google oder GitHub nutzt, aktivieren Sie OIDC-Anmeldung, um die Passwortverwaltung zu delegieren. Siehe [Authentifizierung](../configuration/authentication.md).
- [ ] **SMTP konfiguriert** — Aktivieren Sie E-Mail für Workspace-Einladungen und Passwort-Zurücksetzung. Ohne SMTP werden Token auf stdout ausgegeben. Siehe [Umgebungsvariablen](../configuration/environment.md).

### Git

- [ ] **SSH-Deploy-Key bereitgestellt** — Für private Repositories generieren Sie einen dedizierten Deploy-Key mit Schreibzugriff. Siehe [Git-Integration](../guides/git-integration.md).
- [ ] **Webhook konfiguriert** — Für nahezu sofortige Synchronisation richten Sie einen Push-Webhook bei Ihrem Git-Hosting-Anbieter ein. Polling (Standard: 5 Minuten) funktioniert, verursacht aber Verzögerungen.
- [ ] **Git auf dem Host installiert** — Während go-git die meisten Operationen übernimmt, wird die native Git-CLI für große Repositories (>1 GB) benötigt.

### Monitoring

- [ ] **Health-Endpunkt überwacht** — Pollen Sie `GET /health` von Ihrem Monitoring-System (Uptime Robot, Prometheus Blackbox Exporter usw.).
- [ ] **Logs gesammelt** — DocPlatform gibt JSON-strukturierte Logs auf stdout aus. Leiten Sie sie an Ihren Log-Aggregator weiter (ELK, Datadog, CloudWatch).
- [ ] **Festplattennutzung überwacht** — SQLite-Datenbanken und Suchindizes wachsen mit dem Inhalt. Alarmieren Sie, wenn die Festplattennutzung 80% überschreitet.

### Betrieb

- [ ] **`docplatform doctor` ausgeführt** — Führen Sie `docplatform doctor` nach der Ersteinrichtung aus, um FS/DB-Konsistenz, Suchstatus und defekte Links zu verifizieren.
- [ ] **Upgrade-Prozess dokumentiert** — Dokumentieren Sie, wie Ihr Team DocPlatform upgradet (Binary-Austausch + Neustart oder Docker-Pull + Neuerstellung).
- [ ] **Rollback-Plan vorhanden** — Bewahren Sie die vorherige Binary-Version auf und wissen Sie, wie Sie aus einem Datenbank-Backup wiederherstellen.

## Community Edition Ressourcenlimits

Die Community Edition enthält folgende fest codierte Limits:

| Ressource | Limit |
|---|---|
| Benutzer mit Editor-Rolle oder höher | 5 |
| Workspaces | 3 |
| Viewer und Commenter | Unbegrenzt |
| Seiten pro Workspace | Unbegrenzt |

Diese Limits werden bei der Editor-Rollenzuweisung und Workspace-Erstellung geprüft. Wenn Sie mehr Editoren oder Workspaces benötigen, wird die zukünftige Enterprise Edition konfigurierbare Limits per Lizenzschlüssel bieten.

## Skalierungsüberlegungen

DocPlatform Community Edition läuft als einzelne Instanz mit einer Single-Writer-SQLite-Datenbank. Dies ist die richtige Architektur für die Zielgröße:

| Metrik | Getestetes Limit |
|---|---|
| **Seiten** | 1.000 |
| **Gleichzeitige Benutzer** | 50 |
| **Workspaces** | 10 |
| **Seiten-Render-Latenz** | < 50ms (p99) |
| **Suchlatenz** | < 50ms (p99) |
| **Speicherverbrauch** | < 200 MB unter Last |

Wenn Sie über diese Limits hinaus skalieren müssen, werden zukünftige Editionen Multi-Instanz-Deployment, externe Datenbanken und Meilisearch unterstützen.

## Sicherheitshärtung

### Netzwerk

- Betreiben Sie DocPlatform hinter einem Reverse Proxy mit TLS
- Setzen Sie `HOST=127.0.0.1`, um direkten Zugriff zu blockieren
- Verwenden Sie Firewall-Regeln, um den Zugriff auf den Server zu beschränken
- **WebSocket-Proxy** — stellen Sie sicher, dass Ihr Reverse Proxy WebSocket-Upgrade unterstützt. Ohne dies funktionieren Echtzeit-Präsenz und Live-Updates nicht. Sowohl Caddy als auch nginx (mit `proxy_http_version 1.1` und `Upgrade`-Headern) unterstützen dies.

### Antwort-Header

DocPlatform setzt Sicherheits-Header automatisch auf allen Antworten:

| Header | Wert |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| `X-Request-ID` | ULID (eindeutig pro Anfrage) |

### Dateisystem

- Als dedizierter Nicht-Root-Benutzer ausführen (systemd: `User=docplatform`)
- Datenverzeichnis-Berechtigungen einschränken: `chmod 700 {DATA_DIR}`
- JWT-Schlüssel-Berechtigungen einschränken: `chmod 600 {DATA_DIR}/jwt-key.pem`

### Authentifizierung

- Aktivieren Sie OIDC, um lokal gespeicherte Anmeldedaten zu reduzieren
- Verwenden Sie starke Passwörter (DocPlatform verwendet argon2id — widerstandsfähig gegen Brute-Force)
- Überprüfen Sie aktive Sitzungen regelmäßig (Admin-Panel → Users → Sessions)

### Updates

- Abonnieren Sie GitHub-Releases für Sicherheitsupdates
- Aktualisieren Sie zeitnah, wenn Sicherheitspatches veröffentlicht werden
- Führen Sie `docplatform doctor` nach jedem Upgrade aus

## Beispiel: Minimales Produktions-Setup

```bash
# 1. Installieren
sudo mv docplatform /usr/local/bin/

# 2. Dienstbenutzer und Datenverzeichnis erstellen
sudo useradd -r -s /sbin/nologin docplatform
sudo mkdir -p /var/lib/docplatform
sudo chown docplatform:docplatform /var/lib/docplatform

# 3. Workspace initialisieren
cd /var/lib/docplatform
sudo -u docplatform docplatform init \
  --workspace-name "Docs" \
  --slug docs

# 4. Umgebung konfigurieren
sudo mkdir -p /etc/docplatform
sudo tee /etc/docplatform/.env <<EOF
PORT=3000
HOST=127.0.0.1
DATA_DIR=/var/lib/docplatform
BACKUP_RETENTION_DAYS=30
EOF

# 5. systemd-Dienst erstellen (siehe Binary-Deployment-Leitfaden)
# 6. Reverse Proxy mit TLS einrichten (siehe Binary-Deployment-Leitfaden)

# 7. Starten und verifizieren
sudo systemctl enable --now docplatform
docplatform doctor

# 8. Admin-Konto registrieren unter https://docs.yourcompany.com
```
