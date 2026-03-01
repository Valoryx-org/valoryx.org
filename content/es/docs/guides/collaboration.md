---
title: Equipos y colaboración
description: Invite a su equipo, asigne roles y colabore en documentación con presencia en tiempo real y registros de auditoría.
weight: 4
---

# Equipos y colaboración

DocPlatform está diseñado para documentación en equipo. Invite miembros, asigne roles granulares y rastree cada cambio con un registro completo de auditoría.

## Membresía del workspace

Cada usuario pertenece a uno o más workspaces con un rol específico. Los roles determinan qué acciones puede realizar un usuario.

### Invitar miembros

**Mediante la interfaz web:**

1. Abra **Workspace Settings** → **Members**
2. Haga clic en **Invite Member**
3. Ingrese la dirección de correo electrónico de la persona
4. Seleccione un rol
5. Haga clic en **Send**

Si SMTP está configurado, se envía un correo electrónico de invitación con un enlace único. Sin SMTP, el enlace de invitación se muestra en pantalla — cópielo y compártalo manualmente.

**Mediante la API:**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{workspace-id}/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "colleague@example.com",
    "role": "editor"
  }'
```

### Eliminar miembros

Los administradores del workspace pueden eliminar miembros desde **Settings** → **Members** → clic en el usuario → **Remove**.

Eliminar un miembro revoca su acceso inmediatamente. Sus ediciones anteriores y entradas del registro de auditoría se conservan.

### Cambiar roles

Haga clic en el rol actual de un miembro para cambiarlo. Los cambios de rol surten efecto inmediatamente — las sesiones activas se actualizan en la siguiente llamada a la API.

## Roles

DocPlatform usa una jerarquía de roles de 6 niveles. Los roles superiores heredan todos los permisos de los roles inferiores.

```
SuperAdmin
    └── WorkspaceAdmin
            └── Admin
                  └── Editor
                        └── Commenter
                              └── Viewer
```

| Rol | Ámbito | Capacidades |
|---|---|---|
| **Viewer** | Workspace | Ver páginas y buscar |
| **Commenter** | Workspace | Ver + dejar comentarios en páginas |
| **Editor** | Workspace | Ver + comentar + crear, editar, eliminar páginas |
| **Admin** | Workspace | Editor + gestionar miembros y roles |
| **WorkspaceAdmin** | Workspace | Admin + gestionar configuración del workspace, configuración git, tema |
| **SuperAdmin** | Plataforma | Acceso completo a todos los workspaces + configuración de la plataforma |

### Rol predeterminado para nuevos miembros

Configure el rol predeterminado asignado cuando los usuarios aceptan una invitación:

```yaml
# .docplatform/config.yaml
permissions:
  default_role: viewer
```

### Acceso a nivel de página

Restrinja páginas individuales a roles específicos usando frontmatter:

```yaml
---
title: Internal Runbook
access: restricted
allowed_roles: [admin, editor]
---
```

Las páginas con `access: restricted` son invisibles para los usuarios sin el rol requerido — no aparecerán en los resultados de búsqueda, la navegación ni la documentación publicada.

## Presencia en tiempo real

Cuando múltiples usuarios están activos en el mismo workspace, el editor web muestra quién está en línea:

- **Indicadores en la barra lateral** — puntos de colores junto a las páginas que están siendo vistas o editadas por otros usuarios
- **Pila de avatares** — avatares de usuarios en el encabezado de la página mostrando quién más está viendo la página actual

La presencia funciona mediante conexiones WebSocket y se actualiza en tiempo real.

### Cómo funciona la presencia

| Parámetro | Valor |
|---|---|
| **Protocolo** | WebSocket (autenticado mediante ticket de un solo uso) |
| **Intervalo de heartbeat** | Cada 30 segundos |
| **Tiempo de desconexión** | 90 segundos sin heartbeat |
| **Eventos** | `presence-join` (primera conexión), `presence-leave` (timeout o desconexión) |
| **Buffer** | 256 eventos por workspace (previene contrapresión) |

La conexión WebSocket también entrega eventos de contenido en tiempo real:

| Evento | Cuándo |
|---|---|
| `page-created` | Se crea una nueva página (cualquier origen) |
| `page-updated` | Se modifica una página (cualquier origen) |
| `page-deleted` | Se elimina una página |
| `sync-status` | Cambia el estado de sincronización git (synced, ahead, behind, conflict) |
| `conflict-detected` | Se encuentra un conflicto de merge en git |
| `bulk-sync` | Se sincronizan más de 20 archivos en una operación (notificación única, no por archivo) |

### Edición concurrente

DocPlatform no soporta edición colaborativa en tiempo real (estilo Google Docs). Si dos usuarios editan la misma página simultáneamente:

1. El primer guardado tiene éxito
2. El segundo guardado activa una **detección de conflicto** (HTTP 409)
3. Ambas versiones se preservan para resolución manual

Para evitar conflictos:

- Use convenciones de propiedad a nivel de página (un escritor por página a la vez)
- Los indicadores de presencia ayudan a su equipo a coordinar quién está editando qué
- Para equipos con alta concurrencia, considere intervalos de sincronización git más cortos

## Registro de auditoría

Cada mutación de contenido se registra con:

| Campo | Descripción |
|---|---|
| **Timestamp** | Cuándo ocurrió la acción (UTC) |
| **User** | Quién realizó la acción (correo electrónico, ID de usuario) |
| **Operation** | Qué sucedió: `create`, `update`, `delete`, `publish`, `unpublish` |
| **Page** | Qué página se vio afectada (ID, título, ruta) |
| **Source** | De dónde vino el cambio: `web_editor`, `git_sync`, `api` |
| **Content hash** | SHA-256 del nuevo contenido (para verificación) |

### Ver el registro de auditoría

Acceda al registro de auditoría desde **Workspace Settings** → **Activity**.

Filtre por:

- **Usuario** — vea todos los cambios de un miembro específico del equipo
- **Página** — vea el historial completo de una página específica
- **Rango de fechas** — reduzca a una ventana de tiempo
- **Tipo de operación** — filtre por creaciones, actualizaciones, eliminaciones, etc.

### Tipos de acciones de auditoría

El campo `action` en el registro de auditoría usa notación con puntos para filtrado preciso:

| Acción | Descripción |
|---|---|
| `page.create` | Nueva página creada |
| `page.update` | Contenido o frontmatter de página modificado |
| `page.delete` | Página eliminada |
| `page.publish` | Página publicada (hecha pública) |
| `page.unpublish` | Página despublicada |
| `auth.login` | Usuario inició sesión |
| `auth.register` | Nuevo usuario registrado |
| `auth.password_reset` | Restablecimiento de contraseña completado |
| `workspace.create` | Nuevo workspace creado |
| `workspace.member_add` | Usuario agregado al workspace |
| `workspace.member_remove` | Usuario eliminado del workspace |
| `workspace.role_change` | Rol del usuario cambiado |

### Retención

Los registros de auditoría se almacenan en SQLite junto con sus datos regulares. Se incluyen en las copias de seguridad diarias. La retención predeterminada es de 1 año (configurable). Un trabajo de limpieza semanal elimina las entradas más antiguas que el período de retención.

## Notificaciones por correo electrónico

Con SMTP configurado, DocPlatform envía correos electrónicos transaccionales para:

| Evento | Destinatario | Contenido |
|---|---|---|
| **Invitación al workspace** | Usuario invitado | Enlace para unirse + nombre del workspace |
| **Restablecimiento de contraseña** | Usuario solicitante | Token de restablecimiento de un solo uso |

DocPlatform no envía correos electrónicos de notificación por cambios de contenido. Las actualizaciones en tiempo real vía WebSocket cumplen esa función para usuarios activos, y el registro de auditoría cubre la revisión histórica.

### Configuración SMTP

```bash
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_FROM=docs@yourcompany.com
export SMTP_USERNAME=docs@yourcompany.com
export SMTP_PASSWORD=your-app-password
```

Sin SMTP, los enlaces de invitación y los tokens de restablecimiento de contraseña se imprimen en stdout (logs del servidor).

## Consejos para flujos de trabajo en equipo

- **Un escritor por página** — use los indicadores de presencia para evitar conflictos
- **Editores escriben, Admins publican** — separe las responsabilidades con roles
- **Use etiquetas para propiedad** — etiquete páginas con `owner:jane` para clarificar la responsabilidad
- **Git para flujos de revisión** — envíe cambios a una rama, abra un PR, haga merge después de la revisión
- **Audite antes de publicar** — revise el registro de auditoría en busca de cambios inesperados antes de hacer público el contenido
