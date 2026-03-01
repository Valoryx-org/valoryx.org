---
title: Docker-Deployment
description: Deployen Sie DocPlatform als Docker-Container mit persistenten Volumes und Umgebungskonfiguration.
weight: 2
---

# Docker-Deployment

DocPlatform wird als Multi-Architektur-Docker-Image (amd64/arm64) ausgeliefert, basierend auf Alpine Linux.

## Schnellstart

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Öffnen Sie [http://localhost:3000](http://localhost:3000) und registrieren Sie Ihr Admin-Konto.

## Erster Start

Beim ersten Start führt DocPlatform automatisch folgende Schritte aus:

1. Erstellt die SQLite-Datenbank unter `/data/data.db`
2. Generiert einen RS256-Signaturschlüssel unter `/data/jwt-key.pem`
3. Initialisiert den Volltext-Suchindex
4. Beginnt auf Port 3000 zu lauschen

Der erste Benutzer, der sich registriert, wird zum **SuperAdmin** mit vollem Plattformzugriff. Kein manueller `init`-Schritt ist erforderlich — der Container ist sofort einsatzbereit.

```bash
# Überprüfen, ob der Container korrekt gestartet ist
docker logs docplatform
# → INFO  Server starting            port=3000 version=v0.5.0
# → INFO  Database initialized       path=/data/data.db
# → INFO  Search index ready         documents=0
# → INFO  Listening on               http://0.0.0.0:3000
```

## Docker Compose

Für einfachere Verwaltung nutzen Sie Docker Compose:

```yaml
# docker-compose.yml
services:
  docplatform:
    image: ghcr.io/valoryx-org/docplatform:latest
    container_name: docplatform
    ports:
      - "3000:3000"
    volumes:
      - docplatform-data:/data
      - ./deploy_key:/etc/docplatform/deploy_key:ro
    environment:
      - DATA_DIR=/data
      - PORT=3000
      - GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
      - BACKUP_RETENTION_DAYS=30
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  docplatform-data:
```

```bash
docker compose up -d
```

## Image-Details

| Eigenschaft | Wert |
|---|---|
| **Registry** | `ghcr.io/valoryx-org/docplatform` |
| **Basis-Image** | Alpine Linux 3.19 |
| **Architekturen** | `linux/amd64`, `linux/arm64` |
| **Größe** | ~120 MB komprimiert |
| **Benutzer** | Nicht-Root (`docplatform`, UID 1000) |
| **Freigegebener Port** | 3000 |
| **Datenverzeichnis** | `/data` |

### Tags

| Tag | Beschreibung |
|---|---|
| `latest` | Neuestes stabiles Release |
| `v0.5.0` | Spezifische Version |
| `v0.5` | Neuester Patch für v0.5.x |

## Volumes

Mounten Sie ein persistentes Volume unter `/data`, um Daten über Container-Neustarts hinweg zu bewahren:

```bash
-v docplatform-data:/data
```

Das `/data`-Verzeichnis enthält:

```
/data/
├── data.db              # SQLite-Datenbank
├── jwt-key.pem          # Automatisch generierter RS256-Signaturschlüssel
├── backups/             # Tägliche Backup-Dateien
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Markdown-Dateien
        ├── .git/        # Git-Repository (wenn verbunden)
        └── .docplatform/
            └── config.yaml
```

**Überspringen Sie das Volume-Mount nicht.** Ohne dieses gehen alle Daten verloren, wenn der Container entfernt wird.

## Umgebungsvariablen

Übergeben Sie die Konfiguration über `-e`-Flags, `--env-file` oder Docker Compose `environment`:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  -e DATA_DIR=/data \
  -e SMTP_HOST=smtp.example.com \
  -e SMTP_PORT=587 \
  -e SMTP_FROM=docs@example.com \
  -e SMTP_USERNAME=docs@example.com \
  -e SMTP_PASSWORD=app-password \
  -e OIDC_GOOGLE_CLIENT_ID=your-client-id \
  -e OIDC_GOOGLE_CLIENT_SECRET=your-client-secret \
  ghcr.io/valoryx-org/docplatform:latest
```

Oder verwenden Sie eine Env-Datei:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

Siehe [Umgebungsvariablen](../configuration/environment.md) für die vollständige Referenz.

## SSH-Schlüssel für Git-Synchronisation

Mounten Sie Ihren Deploy-Key als schreibgeschütztes Volume:

```bash
-v /path/to/deploy_key:/etc/docplatform/deploy_key:ro
-e GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
```

Stellen Sie sicher, dass die Schlüsseldatei korrekte Berechtigungen auf dem Host hat:

```bash
chmod 600 /path/to/deploy_key
```

## Health Checks

DocPlatform stellt Health-Endpunkte bereit:

| Endpunkt | Zweck |
|---|---|
| `GET /health` | Einfacher Liveness-Check (Server läuft) |
| `GET /ready` | Readiness-Check (Datenbank und Suche sind initialisiert) |

Verwenden Sie diese für Docker-Healthchecks, Load-Balancer-Probes oder Orchestrator-Liveness-/Readiness-Probes.

```bash
# Schneller Liveness-Check
curl -f http://localhost:3000/health
# → {"status":"ok"}

# Readiness-Check (Datenbank + Suche initialisiert)
curl -f http://localhost:3000/ready
# → {"status":"ok","database":"ok","search":"ok"}
```

## Mit Reverse Proxy

### Caddy + Docker Compose

```yaml
services:
  docplatform:
    image: ghcr.io/valoryx-org/docplatform:latest
    volumes:
      - docplatform-data:/data
    environment:
      - DATA_DIR=/data
      - HOST=0.0.0.0
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config
    restart: unless-stopped

volumes:
  docplatform-data:
  caddy-data:
  caddy-config:
```

```
# Caddyfile
docs.yourcompany.com {
    reverse_proxy docplatform:3000
}
```

Caddy kümmert sich automatisch über Let's Encrypt um TLS.

## Upgrades

```bash
# Neuestes Image pullen
docker pull ghcr.io/valoryx-org/docplatform:latest

# Container neu erstellen
docker compose up -d
```

Oder mit einfachem Docker:

```bash
docker pull ghcr.io/valoryx-org/docplatform:latest
docker stop docplatform
docker rm docplatform
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Daten im Volume bleiben über Container-Neuerstellungen hinweg erhalten.

## Aus dem Quellcode bauen

Erstellen Sie Ihr eigenes Image aus dem Dockerfile:

```bash
cd Phase05/src
docker build -t docplatform:custom .
```

Das Dockerfile verwendet einen mehrstufigen Build:

1. **Build-Phase** — Go-Kompilierung mit deaktiviertem CGO
2. **Frontend-Phase** — Next.js Static Export
3. **Runtime-Phase** — Alpine Linux mit kompilierter Binärdatei und statischen Assets

## Logs

```bash
# Container-Logs verfolgen
docker logs -f docplatform

# Letzte 100 Zeilen
docker logs --tail 100 docplatform
```

Logs sind JSON-strukturiert mit Request-IDs für Observability.

## Backup und Wiederherstellung

### Manuelles Backup

```bash
# Datenbank aus dem Container kopieren
docker cp docplatform:/data/data.db ./backup-$(date +%Y%m%d).db
```

### Automatische Backups

Tägliche Backups werden automatisch innerhalb des Containers ausgeführt (standardmäßig aktiviert). Sie werden in `/data/backups/` gespeichert und sind im Volume enthalten.

### Wiederherstellung

```bash
docker stop docplatform
docker cp ./backup-20250115.db docplatform:/data/data.db
docker start docplatform
```
