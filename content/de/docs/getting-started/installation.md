---
title: Installation
description: Installieren Sie DocPlatform mit einer vorkompilierten Binärdatei, Docker oder aus dem Quellcode.
weight: 2
---

# Installation

DocPlatform wird als einzelne Binärdatei ohne Runtime-Abhängigkeiten ausgeliefert. Wählen Sie die Installationsmethode, die zu Ihrem Workflow passt.

## Option 1: Vorkompilierte Binärdatei (empfohlen)

Laden Sie die neueste Version für Ihre Plattform herunter.

### Linux / macOS

```bash
# Empfohlen (erkennt die Plattform automatisch)
curl -fsSL https://valoryx.org/install.sh | sh

# Oder manuell herunterladen
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Installation überprüfen
docplatform version
```

**Erwartete Ausgabe:**

```
docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
```
### Windows```powershell# Download and runInvoke-WebRequest https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-windows-amd64.exe -OutFile docplatform.exe# Verify.docplatform.exe version# Start the server.docplatform.exe serve```Open [http://localhost:3000](http://localhost:3000) to get started.

### Manuell herunterladen

Wenn Sie lieber manuell herunterladen, besuchen Sie die [GitHub Releases](https://github.com/Valoryx-org/releases/releases)-Seite. Binärdateien sind verfügbar für:

| Plattform | Architektur | Dateiname |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |
| Windows | amd64 | `docplatform-windows-amd64.exe` |

Jedes Release enthält SHA-256-Prüfsummen zur Verifizierung.

## Option 2: Docker

Führen Sie DocPlatform als Container aus, wobei persistente Daten in einem Volume gespeichert werden.

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Der Container initialisiert sich beim ersten Start automatisch. Öffnen Sie [http://localhost:3000](http://localhost:3000), um zu beginnen.

### Docker Compose

Für eine komfortablere Einrichtung verwenden Sie Docker Compose:

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
    environment:
      - PORT=3000
      - DATA_DIR=/data
    restart: unless-stopped

volumes:
  docplatform-data:
```

```bash
docker compose up -d
```

Für Docker-Deployments in Produktionsumgebungen siehe den [Docker-Deployment-Leitfaden](../deployment/docker.md).

## Option 3: Aus dem Quellcode kompilieren

Kompilieren Sie aus dem Quellcode, wenn Sie beitragen oder eine Entwicklungsversion ausführen möchten.

**Voraussetzungen:**

- Go 1.24+
- Node.js 20+ und pnpm (für den Frontend-Build)
- Git
- Make

```bash
# Repository klonen
git clone https://github.com/Valoryx-org/docplatform.git
cd docplatform/Phase05/src

# Binärdatei kompilieren (kompiliert Go + bettet Next.js-Static-Export ein)
make build

# Überprüfen
./docplatform version
```

### Entwicklungsmodus

Für Hot-Reloading während der Entwicklung:

```bash
make dev
```

Dies startet den Go-Server mit Live-Reload und den Next.js-Entwicklungsserver mit HMR.

## Nächste Schritte

Mit installiertem DocPlatform fahren Sie fort mit:

1. **[Schnellstart](quickstart.md)** — Workspace initialisieren und den Server mit 2 Befehlen starten
2. **[Ihr erster Workspace](first-workspace.md)** — Git-Synchronisation einrichten, Benutzer einladen und Einstellungen anpassen

## Deinstallation

### Binärdatei

```bash
# Binärdatei entfernen
sudo rm /usr/local/bin/docplatform

# Daten entfernen (wenn Sie einen sauberen Neuanfang wünschen)
rm -rf .docplatform/
```

### Docker

```bash
docker stop docplatform && docker rm docplatform
docker volume rm docplatform-data  # entfernt alle Daten
```
