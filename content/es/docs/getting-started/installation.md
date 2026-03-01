---
title: Instalación
description: Instale DocPlatform usando un binario precompilado, Docker o desde el código fuente.
weight: 2
---

# Instalación

DocPlatform se distribuye como un único binario sin dependencias de runtime. Elija el método de instalación que se adapte a su flujo de trabajo.

## Opción 1: Binario precompilado (recomendado)

Descargue la última versión para su plataforma.

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

**Salida esperada:**

```
docplatform v0.5.0 (commit: abc1234, built: 2025-01-15T10:00:00Z)
```

### Descarga manual

Si prefiere descargar manualmente, visite la página de [GitHub Releases](https://github.com/Valoryx-org/releases/releases). Los binarios están disponibles para:

| Plataforma | Arquitectura | Nombre del archivo |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |

Cada versión incluye sumas de verificación SHA-256.

## Opción 2: Docker

Ejecute DocPlatform como un contenedor con datos persistentes almacenados en un volumen.

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

El contenedor se auto-inicializa en la primera ejecución. Abra [http://localhost:3000](http://localhost:3000) para comenzar.

### Docker Compose

Para una configuración más manejable, use Docker Compose:

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

Para despliegues Docker en producción, consulte la [guía de despliegue con Docker](../deployment/docker.md).

## Opción 3: Compilar desde el código fuente

Compile desde el código fuente si desea contribuir o ejecutar una versión de desarrollo.

**Requisitos previos:**

- Go 1.24+
- Node.js 20+ y pnpm (para la compilación del frontend)
- Git
- Make

```bash
# Clone the repository
git clone https://github.com/Valoryx-org/docplatform.git
cd docplatform/Phase05/src

# Build the binary (compiles Go + embeds Next.js static export)
make build

# Verify
./docplatform version
```

### Modo de desarrollo

Para recarga en caliente durante el desarrollo:

```bash
make dev
```

Esto inicia el servidor Go con recarga en vivo y el servidor de desarrollo Next.js con HMR.

## Próximos pasos

Con DocPlatform instalado, continúe con:

1. **[Inicio rápido](quickstart.md)** — inicialice un workspace e inicie el servidor en 2 comandos
2. **[Su primer workspace](first-workspace.md)** — configure la sincronización git, invite usuarios y personalice la configuración

## Desinstalar

### Binario

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
