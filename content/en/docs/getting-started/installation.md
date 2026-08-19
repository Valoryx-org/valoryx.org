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
# Recommended (auto-detects platform, all OSes)
curl -fsSL https://valoryx.org/install.sh | sh
```

`install.sh` downloads via curl, which does not set the macOS quarantine attribute — so on macOS it also sidesteps the Gatekeeper prompt described below. It's the recommended path on every OS for that reason alone.

Or download manually for your specific platform (do not use the Linux binary on macOS — see the platform table below):

```bash
# Linux (amd64)
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# macOS (Apple Silicon)
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-darwin-arm64
chmod +x docplatform-darwin-arm64
sudo mv docplatform-darwin-arm64 /usr/local/bin/docplatform

# macOS (Intel)
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-darwin-amd64
chmod +x docplatform-darwin-amd64
sudo mv docplatform-darwin-amd64 /usr/local/bin/docplatform
```

```bash
# Verify the installation
docplatform version
```

**Expected output** (version/commit/date will match the release you downloaded):

```
docplatform <version> (commit: <sha>, built: <date>)
```

**macOS Gatekeeper:** a manually-downloaded binary is not notarized, so macOS will refuse to run it the first time ("Apple could not verify... is free of malware"). Either use `install.sh` above (recommended — it never triggers this), or clear it manually: on macOS Sequoia and later, open **System Settings → Privacy & Security**, scroll to the blocked-app notice, and choose **Open Anyway**; on older macOS versions, right-click the binary in Finder and choose **Open**, then confirm in the dialog. This is a one-time step per binary.

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
```

To also remove data (clean slate), find your data directory first — **`rm -rf .docplatform/` deletes nothing on a default install.** Unless you explicitly set `DATA_DIR` or already had a pre-v0.15 install in the current directory, your data lives in an OS-standard per-user location instead. Before removing the binary, run:

```bash
docplatform doctor
```

and read the data directory path from its output, then remove that path directly (for example `rm -rf ~/.local/share/docplatform` on Linux — but always use the path `doctor` actually reports, since it depends on your OS and setup).

### Docker

```bash
docker stop docplatform && docker rm docplatform
docker volume rm docplatform-data  # removes all data
```
