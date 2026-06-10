---
title: Installation
description: Install DocPlatform using a pre-built binary, Docker, or from source.
weight: 2
---

# Installation

DocPlatform ships as a single binary with zero runtime dependencies. Choose the installation method that fits your workflow.

## Option 1: Pre-built binary (recommended)

Download the latest release for your platform.

### Linux / macOS

```bash
# Recommended (auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh

# Or download manually
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Verify the installation
docplatform version
```

**Expected output:**

```
docplatform v0.10.0 (commit: 5738520, built: 2026-05-16T17:52:38Z)
```

### Windows

```powershell
# Download and run
Invoke-WebRequest https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-windows-amd64.exe -OutFile docplatform.exe

# Verify
.\docplatform.exe version

# Start the server
.\docplatform.exe serve
```

Open [http://localhost:3000](http://localhost:3000) to get started.

### Download manually

If you prefer to download manually, visit the [GitHub Releases](https://github.com/Valoryx-org/releases/releases) page. Binaries are available for:

| Platform | Architecture | Filename |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |
| Windows | amd64 | `docplatform-windows-amd64.exe` |

Each release includes SHA-256 checksums for verification.

## Option 2: Docker

Run DocPlatform as a container with persistent data stored in a volume.

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

The container auto-initializes on first run. Open [http://localhost:3000](http://localhost:3000) to get started.

### Docker Compose

For a more manageable setup, use Docker Compose:

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

For production Docker deployments, see the [Docker deployment guide](../deployment/docker.md).

## A note on source code

DocPlatform is proprietary software distributed as pre-built binaries and container images only. The source code is not publicly available, so there is no build-from-source installation path. Community Edition is free of charge and fully functional — see [Community Edition limits](../index.md#community-edition-limits).

## Next steps

With DocPlatform installed, continue to:

1. **[Quickstart](quickstart.md)** — initialize a workspace and start the server in 2 commands
2. **[Your First Workspace](first-workspace.md)** — set up git sync, invite users, and customize settings

## Uninstall

### Binary

```bash
# Remove the binary
sudo rm /usr/local/bin/docplatform

# Remove data (if you want a clean slate)
rm -rf .docplatform/
```

### Docker

```bash
docker stop docplatform && docker rm docplatform
docker volume rm docplatform-data  # removes all data
```
