---
title: Variables de entorno
description: Referencia completa de todas las variables de entorno de DocPlatform — servidor, base de datos, git, autenticación, correo electrónico y operaciones.
weight: 1
---

# Variables de entorno

DocPlatform lee la configuración de variables de entorno. Establézcalas en su shell, un archivo `.env` en el directorio de trabajo o su orquestador de contenedores.

## Servidor

| Variable | Predeterminado | Descripción |
|---|---|---|
| `PORT` | `3000` | Puerto de escucha HTTP |
| `HOST` | `0.0.0.0` | Dirección de escucha HTTP. Establezca `127.0.0.1` para restringir a localhost. |
| `DATA_DIR` | `.docplatform` | Directorio raíz para todos los datos de DocPlatform (base de datos, copias de seguridad, workspaces, claves) |
| `BASE_DOMAIN` | — | Dominio personalizado para documentación publicada (por ejemplo, `docs.yourcompany.com`). Cuando se establece, la documentación publicada usa este dominio para URLs canónicas y entradas del sitemap. |
| `PUBLISH_REQUIRE_AUTH` | `false` | Cuando es `true`, todos los sitios de documentación publicada requieren que el visitante haya iniciado sesión como miembro del workspace. Los visitantes no autenticados son redirigidos a la página de inicio de sesión y devueltos a la página original después de iniciar sesión. |

## Autenticación

| Variable | Predeterminado | Descripción |
|---|---|---|
| `JWT_SECRET_PATH` | `{DATA_DIR}/jwt-key.pem` | Ruta a la clave privada RS256 para firma JWT. Se auto-genera en la primera ejecución si no existe. |
| `JWT_ACCESS_TTL` | `900` | Tiempo de vida del token de acceso en segundos (predeterminado: 15 minutos) |
| `JWT_REFRESH_TTL` | `2592000` | Tiempo de vida del token de actualización en segundos (predeterminado: 30 días) |

## Proveedores OIDC (opcional)

Habilite el inicio de sesión con Google y/o GitHub configurando estas variables. Cuando no están configuradas, solo está disponible la autenticación local (correo electrónico + contraseña).

| Variable | Predeterminado | Descripción |
|---|---|---|
| `OIDC_GOOGLE_CLIENT_ID` | — | ID de cliente OAuth 2.0 de Google |
| `OIDC_GOOGLE_CLIENT_SECRET` | — | Secreto de cliente OAuth 2.0 de Google |
| `OIDC_GITHUB_CLIENT_ID` | — | ID de cliente OAuth de GitHub |
| `OIDC_GITHUB_CLIENT_SECRET` | — | Secreto de cliente OAuth de GitHub |

Consulte [Autenticación](authentication.md) para instrucciones de configuración.

## Git

| Variable | Predeterminado | Descripción |
|---|---|---|
| `GIT_SSH_KEY_PATH` | `~/.ssh/docplatform_deploy_key` | Ruta a la clave privada SSH para operaciones git. Requerida para repositorios privados a través de SSH. |
| `GIT_SYNC_INTERVAL` | `300` | Intervalo de polling predeterminado en segundos para sincronización remota (mínimo: 10). Anulado por `sync_interval` del workspace. Establezca `0` para sincronización solo por webhook (sin polling). |
| `GIT_AUTO_COMMIT` | `true` | Comportamiento predeterminado de auto-commit. Anulado por `git_auto_commit` del workspace. |
| `GIT_WEBHOOK_SECRET` | — | Secreto compartido para verificar payloads de webhook (HMAC-SHA256) de GitHub, GitLab o Bitbucket. |
| `GIT_COMMIT_NAME` | `DocPlatform` | Nombre del committer git para auto-commits |
| `GIT_COMMIT_EMAIL` | `docplatform@local` | Correo electrónico del committer git para auto-commits |

## Correo electrónico (opcional)

Configure SMTP para invitaciones al workspace y correos electrónicos de restablecimiento de contraseña. Sin SMTP, los tokens se imprimen en stdout (logs del servidor).

| Variable | Predeterminado | Descripción |
|---|---|---|
| `SMTP_HOST` | — | Nombre de host del servidor SMTP (por ejemplo, `smtp.gmail.com`) |
| `SMTP_PORT` | `587` | Puerto SMTP (587 para STARTTLS, 465 para SSL) |
| `SMTP_FROM` | — | Dirección de correo electrónico del remitente (por ejemplo, `docs@yourcompany.com`) |
| `SMTP_USERNAME` | — | Nombre de usuario de autenticación SMTP |
| `SMTP_PASSWORD` | — | Contraseña de autenticación SMTP |

## Copias de seguridad

| Variable | Predeterminado | Descripción |
|---|---|---|
| `BACKUP_ENABLED` | `true` | Habilitar copias de seguridad diarias automatizadas de SQLite |
| `BACKUP_RETENTION_DAYS` | `7` | Número de días para retener archivos de copia de seguridad. Las copias de seguridad más antiguas se eliminan automáticamente. |
| `BACKUP_DIR` | `{DATA_DIR}/backups` | Directorio para archivos de copia de seguridad |

## Telemetría

| Variable | Predeterminado | Descripción |
|---|---|---|
| `DOCPLATFORM_TELEMETRY` | `off` | Establezca `on` para habilitar métricas de uso anónimas y opcionales. Cuando está habilitado, se envía semanalmente un ID de instalación SHA-256 (sin información personal identificable). |
| `DOCPLATFORM_TELEMETRY_ENDPOINT` | — | Endpoint personalizado para datos de telemetría (avanzado — para entornos aislados con analíticas internas) |

### Qué envía la telemetría (cuando está habilitada)

- ID de instalación SHA-256 (derivado del directorio de datos, no reversible)
- Conteo de workspaces y conteo total de páginas
- Versión de DocPlatform
- SO y arquitectura

La telemetría **nunca** envía: contenido de páginas, correos electrónicos de usuarios, direcciones IP, nombres de archivos ni información personal identificable. Frecuencia: semanal.

## Manejo de frontmatter

| Variable | Predeterminado | Descripción |
|---|---|---|
| `FRONTMATTER_ERROR_MODE` | `strict` | Cómo manejar frontmatter YAML inválido: `strict` restringe la página a acceso solo para administradores (previene exposición accidental); `lenient` mantiene el último frontmatter válido conocido y muestra una advertencia. |

## Uso de un archivo `.env`

Cree un archivo `.env` en el directorio donde ejecuta `docplatform serve`:

```bash
# .env
PORT=8080
DATA_DIR=/var/lib/docplatform
GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_FROM=docs@example.com
SMTP_USERNAME=docs@example.com
SMTP_PASSWORD=app-specific-password
BACKUP_RETENTION_DAYS=30
```

DocPlatform carga el archivo `.env` automáticamente. Las variables de entorno configuradas en el shell tienen precedencia sobre los valores del `.env`.

## Entorno Docker

Pase variables de entorno a Docker con flags `-e` o un archivo env:

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  -e DATA_DIR=/data \
  -e SMTP_HOST=smtp.example.com \
  -e SMTP_FROM=docs@example.com \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

## Notas de seguridad

- **Nunca haga commit de archivos `.env`** al control de versiones. Agregue `.env` a su `.gitignore`.
- **Las claves JWT** se auto-generan. Si necesita rotarlas, elimine el archivo de clave y reinicie — se genera una nueva clave y todas las sesiones existentes se invalidan.
- **Contraseñas SMTP** — use contraseñas específicas de la aplicación o claves API, no la contraseña de su cuenta principal.
- **Tokens de git** — use tokens con alcance de repositorio con permisos mínimos (lectura + escritura para sincronización).
