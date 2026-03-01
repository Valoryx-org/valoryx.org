---
title: Lista de verificación de producción
description: Todo lo que necesita verificar antes de ejecutar DocPlatform en un entorno de producción.
weight: 3
---

# Lista de verificación de producción

Use esta lista de verificación antes de desplegar DocPlatform en un entorno de producción. Cada elemento enlaza a la sección de documentación relevante.

## Obligatorio

Estos elementos son necesarios para un despliegue de producción seguro y confiable.

### Servidor

- [ ] **Almacenamiento persistente configurado** — Monte un volumen o use una ruta estable del sistema de archivos para `DATA_DIR`. La pérdida de este directorio significa la pérdida de todos los datos.
- [ ] **Gestor de procesos implementado** — Use systemd, Docker con `restart: unless-stopped` o un orquestador de contenedores para asegurar que el servidor se reinicie después de fallos o reinicios.
- [ ] **Puerto accesible** — Asegúrese de que el `PORT` configurado (predeterminado: 3000) sea accesible desde su red o reverse proxy.
- [ ] **Recursos suficientes** — Mínimo 128 MB RAM, 200 MB disco. Recomendado 512 MB RAM, 1 GB disco.

### Seguridad

- [ ] **TLS habilitado** — Ejecute detrás de un reverse proxy (Caddy, nginx, balanceador de carga en la nube) con HTTPS. DocPlatform no realiza terminación TLS por sí mismo.
- [ ] **Clave JWT protegida** — El archivo `jwt-key.pem` otorga la capacidad de falsificar tokens de autenticación. Restrinja los permisos del sistema de archivos: `chmod 600`.
- [ ] **Primer usuario registrado** — El primer usuario registrado se convierte en SuperAdmin. Registre su cuenta de administrador antes de abrir el servidor a otros.
- [ ] **Enlazar a localhost** — Si usa un reverse proxy en el mismo host, establezca `HOST=127.0.0.1` para que DocPlatform no sea directamente accesible.

### Copias de seguridad

- [ ] **Copias de seguridad habilitadas** — `BACKUP_ENABLED=true` (predeterminado). Verifique que las copias de seguridad se están creando en `{DATA_DIR}/backups/`.
- [ ] **Retención de copias de seguridad configurada** — `BACKUP_RETENTION_DAYS` configurado según su política (predeterminado: 7 días).
- [ ] **Copia de seguridad fuera del servidor** — Copie los archivos de copia de seguridad a una ubicación separada (S3, NFS, otro servidor). Las copias de seguridad en disco no protegen contra fallos de disco.

## Recomendado

Estos elementos mejoran la confiabilidad, seguridad y experiencia del equipo.

### Autenticación

- [ ] **OIDC configurado** — Si su equipo usa Google o GitHub, habilite el inicio de sesión OIDC para delegar la gestión de contraseñas. Consulte [Autenticación](../configuration/authentication.md).
- [ ] **SMTP configurado** — Habilite el correo electrónico para invitaciones al workspace y restablecimiento de contraseña. Sin SMTP, los tokens se imprimen en stdout. Consulte [Variables de entorno](../configuration/environment.md).

### Git

- [ ] **Clave SSH de deploy provisionada** — Para repositorios privados, genere una clave de deploy dedicada con acceso de escritura. Consulte [Integración con Git](../guides/git-integration.md).
- [ ] **Webhook configurado** — Para sincronización casi instantánea, configure un webhook de push en su proveedor de hosting git. El polling (predeterminado: 5 minutos) funciona pero añade retraso.
- [ ] **Git instalado en el host** — Aunque go-git maneja la mayoría de operaciones, se necesita el CLI nativo de git para repositorios grandes (>1 GB).

### Monitorización

- [ ] **Endpoint de salud monitorizado** — Consulte `GET /health` desde su sistema de monitorización (Uptime Robot, Prometheus blackbox exporter, etc.).
- [ ] **Logs recopilados** — DocPlatform produce logs estructurados en JSON a stdout. Reenvíelos a su agregador de logs (ELK, Datadog, CloudWatch).
- [ ] **Uso de disco monitorizado** — Las bases de datos SQLite y los índices de búsqueda crecen con el contenido. Genere alertas cuando el uso de disco supere el 80%.

### Operaciones

- [ ] **`docplatform doctor` ejecutado** — Ejecute `docplatform doctor` después de la configuración inicial para verificar la consistencia FS/DB, la salud de búsqueda y los enlaces rotos.
- [ ] **Proceso de actualización documentado** — Documente cómo su equipo actualiza DocPlatform (reemplazo de binario + reinicio, o Docker pull + recreación).
- [ ] **Plan de reversión implementado** — Conserve la versión anterior del binario y sepa cómo restaurar desde una copia de seguridad de base de datos.

## Límites de recursos de Community Edition

Community Edition incluye los siguientes límites codificados:

| Recurso | Límite |
|---|---|
| Usuarios con rol de Editor o superior | 5 |
| Workspaces | 3 |
| Viewers y Commenters | Ilimitados |
| Páginas por workspace | Ilimitadas |

Estos límites se verifican al asignar el rol de editor y al crear workspaces. Si necesita más editores o workspaces, la futura Enterprise Edition ofrecerá límites configurables mediante clave de licencia.

## Consideraciones de escalabilidad

DocPlatform Community Edition se ejecuta como una instancia única con una base de datos SQLite de escritor único. Esta es la arquitectura correcta para la escala objetivo:

| Métrica | Límite probado |
|---|---|
| **Páginas** | 1.000 |
| **Usuarios concurrentes** | 50 |
| **Workspaces** | 10 |
| **Latencia de renderizado de página** | < 50ms (p99) |
| **Latencia de búsqueda** | < 50ms (p99) |
| **Uso de memoria** | < 200 MB bajo carga |

Si necesita escalar más allá de estos límites, las ediciones futuras soportarán despliegue multi-instancia, bases de datos externas y Meilisearch.

## Endurecimiento de seguridad

### Red

- Ejecute detrás de un reverse proxy con TLS
- Establezca `HOST=127.0.0.1` para bloquear el acceso directo
- Use reglas de firewall para restringir el acceso al servidor
- **Proxy WebSocket** — asegúrese de que su reverse proxy soporte la actualización WebSocket. Sin esto, la presencia en tiempo real y las actualizaciones en vivo no funcionarán. Tanto Caddy como nginx (con `proxy_http_version 1.1` y headers `Upgrade`) lo soportan.

### Headers de respuesta

DocPlatform establece headers de seguridad automáticamente en todas las respuestas:

| Header | Valor |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| `X-Request-ID` | ULID (único por solicitud) |

### Sistema de archivos

- Ejecute como un usuario dedicado no-root (systemd: `User=docplatform`)
- Restrinja los permisos del directorio de datos: `chmod 700 {DATA_DIR}`
- Restrinja los permisos de la clave JWT: `chmod 600 {DATA_DIR}/jwt-key.pem`

### Autenticación

- Habilite OIDC para reducir las credenciales almacenadas localmente
- Use contraseñas fuertes (DocPlatform usa argon2id — resistente a fuerza bruta)
- Revise las sesiones activas periódicamente (panel de administración → Users → Sessions)

### Actualizaciones

- Suscríbase a las releases de GitHub para actualizaciones de seguridad
- Actualice puntualmente cuando se publiquen parches de seguridad
- Ejecute `docplatform doctor` después de cada actualización

## Ejemplo: configuración mínima de producción

```bash
# 1. Install
sudo mv docplatform /usr/local/bin/

# 2. Create service user and data directory
sudo useradd -r -s /sbin/nologin docplatform
sudo mkdir -p /var/lib/docplatform
sudo chown docplatform:docplatform /var/lib/docplatform

# 3. Initialize workspace
cd /var/lib/docplatform
sudo -u docplatform docplatform init \
  --workspace-name "Docs" \
  --slug docs

# 4. Configure environment
sudo mkdir -p /etc/docplatform
sudo tee /etc/docplatform/.env <<EOF
PORT=3000
HOST=127.0.0.1
DATA_DIR=/var/lib/docplatform
BACKUP_RETENTION_DAYS=30
EOF

# 5. Create systemd service (see Binary Deployment guide)
# 6. Set up reverse proxy with TLS (see Binary Deployment guide)

# 7. Start and verify
sudo systemctl enable --now docplatform
docplatform doctor

# 8. Register admin account at https://docs.yourcompany.com
```
