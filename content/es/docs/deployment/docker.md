---
title: Despliegue con Docker
description: Despliegue DocPlatform como un contenedor Docker con volúmenes persistentes y configuración de entorno.
weight: 2
---

# Despliegue con Docker

DocPlatform se distribuye como una imagen Docker multi-arquitectura (amd64/arm64) construida sobre Alpine Linux.

## Inicio rápido

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Abra [http://localhost:3000](http://localhost:3000) y registre su cuenta de administrador.

## Primera ejecución

En el primer arranque, DocPlatform automáticamente:

1. Crea la base de datos SQLite en `/data/data.db`
2. Genera una clave de firma RS256 en `/data/jwt-key.pem`
3. Inicializa el índice de búsqueda de texto completo
4. Comienza a escuchar en el puerto 3000

El primer usuario en registrarse se convierte en **SuperAdmin** con acceso completo a la plataforma. No se requiere un paso manual de `init` — el contenedor está listo para usar inmediatamente.

```bash
# Verify the container started correctly
docker logs docplatform
# → INFO  Server starting            port=3000 version=v0.5.0
# → INFO  Database initialized       path=/data/data.db
# → INFO  Search index ready         documents=0
# → INFO  Listening on               http://0.0.0.0:3000
```

## Docker Compose

Para una gestión más sencilla, use Docker Compose:

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

## Detalles de la imagen

| Propiedad | Valor |
|---|---|
| **Registry** | `ghcr.io/valoryx-org/docplatform` |
| **Imagen base** | Alpine Linux 3.19 |
| **Arquitecturas** | `linux/amd64`, `linux/arm64` |
| **Tamaño** | ~120 MB comprimido |
| **Usuario** | Non-root (`docplatform`, UID 1000) |
| **Puerto expuesto** | 3000 |
| **Directorio de datos** | `/data` |

### Tags

| Tag | Descripción |
|---|---|
| `latest` | Versión estable más reciente |
| `v0.5.0` | Versión específica |
| `v0.5` | Último parche de v0.5.x |

## Volúmenes

Monte un volumen persistente en `/data` para preservar los datos entre reinicios del contenedor:

```bash
-v docplatform-data:/data
```

El directorio `/data` contiene:

```
/data/
├── data.db              # SQLite database
├── jwt-key.pem          # Auto-generated RS256 signing key
├── backups/             # Daily backup files
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Markdown files
        ├── .git/        # Git repository (if connected)
        └── .docplatform/
            └── config.yaml
```

**No omita el montaje del volumen.** Sin él, todos los datos se pierden cuando se elimina el contenedor.

## Variables de entorno

Pase la configuración mediante flags `-e`, `--env-file` o `environment` de Docker Compose:

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

O use un archivo env:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

Consulte [Variables de entorno](../configuration/environment.md) para la referencia completa.

## Clave SSH para sincronización git

Monte su clave de deploy como un volumen de solo lectura:

```bash
-v /path/to/deploy_key:/etc/docplatform/deploy_key:ro
-e GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
```

Asegúrese de que el archivo de clave tenga los permisos correctos en el host:

```bash
chmod 600 /path/to/deploy_key
```

## Health checks

DocPlatform expone endpoints de salud:

| Endpoint | Propósito |
|---|---|
| `GET /health` | Verificación básica de actividad (el servidor está ejecutándose) |
| `GET /ready` | Verificación de preparación (la base de datos y la búsqueda están inicializadas) |

Use estos para healthchecks de Docker, sondas de balanceadores de carga o sondas de liveness/readiness del orquestador.

```bash
# Quick liveness check
curl -f http://localhost:3000/health
# → {"status":"ok"}

# Readiness check (database + search initialized)
curl -f http://localhost:3000/ready
# → {"status":"ok","database":"ok","search":"ok"}
```

## Con reverse proxy

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

Caddy gestiona TLS automáticamente mediante Let's Encrypt.

## Actualizaciones

```bash
# Pull the latest image
docker pull ghcr.io/valoryx-org/docplatform:latest

# Recreate the container
docker compose up -d
```

O con Docker simple:

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

Los datos en el volumen persisten entre recreaciones del contenedor.

## Compilar desde el código fuente

Compile su propia imagen desde el Dockerfile:

```bash
cd Phase05/src
docker build -t docplatform:custom .
```

El Dockerfile usa una compilación multi-etapa:

1. **Etapa de compilación** — Compilación Go con CGO deshabilitado
2. **Etapa de frontend** — Exportación estática de Next.js
3. **Etapa de runtime** — Alpine Linux con el binario compilado y assets estáticos

## Logs

```bash
# Follow container logs
docker logs -f docplatform

# Last 100 lines
docker logs --tail 100 docplatform
```

Los logs están estructurados en JSON con IDs de solicitud para observabilidad.

## Copia de seguridad y restauración

### Copia de seguridad manual

```bash
# Copy the database from the container
docker cp docplatform:/data/data.db ./backup-$(date +%Y%m%d).db
```

### Copias de seguridad automatizadas

Las copias de seguridad diarias se ejecutan automáticamente dentro del contenedor (habilitadas por defecto). Se almacenan en `/data/backups/` y se incluyen en el volumen.

### Restaurar

```bash
docker stop docplatform
docker cp ./backup-20250115.db docplatform:/data/data.db
docker start docplatform
```
