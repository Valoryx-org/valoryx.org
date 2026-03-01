---
title: Roles y permisos
description: Configure la jerarquía de roles de 6 niveles de DocPlatform, el control de acceso a nivel de página y el almacenamiento en caché de permisos.
weight: 3
---

# Roles y permisos

DocPlatform usa control de acceso basado en roles (RBAC) impulsado por Casbin, un motor de autorización en proceso. Los permisos se evalúan en menos de 0.1ms por verificación sin servicio externo.

## Jerarquía de roles

DocPlatform define 6 roles en una jerarquía estricta. Los roles superiores heredan todos los permisos de los roles inferiores.

```
SuperAdmin          ← Full platform access (all workspaces)
    │
WorkspaceAdmin      ← Manage workspace settings, git config, theme
    │
Admin               ← Manage members, assign roles
    │
Editor              ← Create, edit, delete pages
    │
Commenter           ← View pages, leave comments
    │
Viewer              ← View pages only
```

### Matriz de permisos

| Permiso | Viewer | Commenter | Editor | Admin | WS Admin | Super Admin |
|---|---|---|---|---|---|---|
| Ver páginas | Sí | Sí | Sí | Sí | Sí | Sí |
| Buscar contenido | Sí | Sí | Sí | Sí | Sí | Sí |
| Dejar comentarios | | Sí | Sí | Sí | Sí | Sí |
| Crear páginas | | | Sí | Sí | Sí | Sí |
| Editar páginas | | | Sí | Sí | Sí | Sí |
| Eliminar páginas | | | Sí | Sí | Sí | Sí |
| Subir assets | | | Sí | Sí | Sí | Sí |
| Invitar miembros | | | | Sí | Sí | Sí |
| Eliminar miembros | | | | Sí | Sí | Sí |
| Cambiar roles de miembros | | | | Sí | Sí | Sí |
| Gestionar configuración del workspace | | | | | Sí | Sí |
| Configurar repositorio git remoto | | | | | Sí | Sí |
| Gestionar tema y navegación | | | | | Sí | Sí |
| Acceder a todos los workspaces | | | | | | Sí |
| Gestionar configuración de la plataforma | | | | | | Sí |
| Crear/eliminar workspaces | | | | | | Sí |

## Asignación de roles

### Primer usuario

El primer usuario en registrarse en una nueva instancia de DocPlatform recibe automáticamente el rol de **SuperAdmin**. Esto solo ocurre una vez — los registros posteriores no reciben rol de workspace hasta ser invitados.

### Miembros del workspace

Al invitar a un usuario a un workspace, especifique su rol:

**Interfaz web:** Workspace Settings → Members → Invite → seleccionar rol

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{id}/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "role": "editor"
  }'
```

### Rol predeterminado

Establezca el rol predeterminado para nuevos miembros que aceptan una invitación sin un rol específico asignado:

```yaml
# .docplatform/config.yaml
permissions:
  default_role: viewer
```

Valores disponibles: `viewer`, `commenter`, `editor`, `admin`, `workspace_admin`

## Control de acceso a nivel de página

Anule los permisos a nivel de workspace en páginas individuales usando frontmatter.

### Niveles de acceso (editor web — usuarios internos)

Para usuarios autenticados dentro del editor web, el acceso a nivel de página restringe la visibilidad por rol:

| Nivel | Comportamiento |
|---|---|
| `public` | Cualquier miembro del workspace puede ver |
| `workspace` | Cualquier miembro del workspace puede ver (igual que `public` para usuarios autenticados) |
| `restricted` | Solo los usuarios con roles listados en `allowed_roles` pueden ver |

### Ejemplos

**Página pública** (predeterminado):

```yaml
---
title: Getting Started
access: public
---
```

**Restringida solo a administradores:**

```yaml
---
title: Infrastructure Runbook
access: restricted
allowed_roles: [admin, workspace_admin]
---
```

### Qué significa "restricted"

Cuando una página tiene `access: restricted`:

- Los usuarios sin el rol requerido **no pueden ver** la página
- La página **no aparece** en los resultados de búsqueda para usuarios no autorizados
- El acceso directo por URL devuelve **403 Forbidden**

### Acceso a documentación publicada

Para el **sitio de documentación publicada** (`/p/{slug}/...`), el control de acceso funciona de manera diferente:

- Todas las páginas publicadas son **públicas por defecto** — no se requiere inicio de sesión
- Para requerir inicio de sesión para todo el sitio publicado, establezca [`PUBLISH_REQUIRE_AUTH=true`](environment.md) — esto aplica a todas las páginas en todos los workspaces
- El control de acceso por página en documentación publicada (por ejemplo, hacer una página solo para el workspace mientras otras son públicas) está planificado para una versión futura

> En v0.5, el campo de frontmatter `access` se almacena y está disponible para uso futuro, pero no se aplica en las rutas publicadas. Use `PUBLISH_REQUIRE_AUTH` para restricción de acceso a nivel de sitio.

## Niveles internos de roles

Como referencia, cada rol se asigna a un nivel numérico. Los niveles superiores heredan todos los permisos de los niveles inferiores:

| Rol | Nivel | Acción mínima |
|---|---|---|
| Viewer | 10 | `read` |
| Commenter | 20 | `read` |
| Editor | 30 | `read`, `write`, `delete` |
| Admin | 40 | `read`, `write`, `delete`, `admin` (gestión de miembros) |
| WorkspaceAdmin | 50 | Todas las acciones del workspace |
| SuperAdmin | 60 | Todas las acciones de la plataforma (omite todas las verificaciones) |

Las acciones tienen niveles mínimos: `read` requiere nivel 10+, `write` requiere 30+, `delete` requiere 30+, `admin` requiere 50+. El nivel del rol del usuario se compara contra el nivel mínimo de la acción.

## Cómo se evalúan los permisos

```
API Request
    │
    ▼
Auth Middleware
(extract JWT, identify user)
    │
    ▼
Permission Middleware
(Casbin check: user + role + resource + action)
    │
    ├── Allowed → proceed to handler
    │
    └── Denied → 403 Forbidden
```

### Flujo de evaluación

1. **Extraer identidad del usuario** del token de acceso JWT
2. **Buscar el rol del usuario** para el workspace destino
3. **Verificar permiso a nivel de workspace** — ¿el rol permite la acción?
4. **Verificar acceso a nivel de página** — si la página tiene `access: restricted`, ¿el rol del usuario está en `allowed_roles`?
5. **Devolver resultado** — permitido o denegado

### Rendimiento

| Métrica | Valor |
|---|---|
| **Motor** | Casbin (en proceso, en memoria) |
| **Tiempo de evaluación** | < 0.1ms por verificación |
| **Caché** | Versionado (auto-invalidado en cambio de rol o permiso) |
| **Almacenamiento de políticas** | SQLite (cargado en memoria al iniciar) |

## Caché de permisos

Las políticas de Casbin se cargan desde SQLite a memoria al iniciar el servidor. Los cambios en roles o declaraciones de acceso en frontmatter activan una invalidación de caché:

1. El administrador cambia el rol de un usuario → se incrementa la versión de la caché de permisos
2. Un editor actualiza el frontmatter de una página con nuevo `access` o `allowed_roles` → se invalida la caché para esa página
3. La siguiente verificación de permisos carga la política fresca desde SQLite

La caché es versionada, no basada en tiempo — no hay ventana de permisos obsoletos.

## Patrones comunes

### Documentación pública de solo lectura con páginas internas restringidas

```yaml
# Most pages: default
access: public

# Internal pages: restricted
---
title: Incident Response Playbook
access: restricted
allowed_roles: [admin, workspace_admin]
---
```

### El Editor crea, el Admin publica

1. Establezca `publishing.default_published: false` en la configuración del workspace
2. Los Editores crean y editan páginas (no publicadas por defecto)
3. Los Admins revisan y activan `published: true`

### Workspaces específicos por equipo

Cree workspaces separados por equipo con listas de miembros independientes:

- Workspace `eng-docs` → equipo de ingeniería
- Workspace `product-docs` → equipo de producto
- Workspace `internal-wiki` → todos

SuperAdmin tiene acceso a todos los workspaces para visibilidad entre equipos.

## Límites de Community Edition

Community Edition aplica los siguientes límites de recursos:

| Recurso | Límite |
|---|---|
| Usuarios con rol de Editor o superior | 5 |
| Workspaces | 3 |
| Viewers y Commenters | Ilimitados |
| Páginas | Ilimitadas |

Estos límites están codificados de forma permanente (no se requiere clave de licencia). Los Viewers y Commenters nunca se contabilizan contra el límite de editores. Cuando se alcanza el límite de editores, los nuevos usuarios aún pueden ser invitados como Viewers o Commenters.

## Solución de problemas

### "403 Forbidden" en una página a la que debería tener acceso

1. Verifique su rol: Profile → Workspace Membership
2. Verifique el frontmatter de la página: ¿`access: restricted` + `allowed_roles` incluye su rol?
3. Pida a un administrador del workspace que verifique su asignación de rol

### Los cambios de permisos no surten efecto

Los cambios de permisos deberían ser instantáneos (la invalidación de caché es síncrona). Si no lo son:

1. Cierre sesión e inicie sesión nuevamente (actualice sus tokens JWT)
2. Verifique los logs del servidor en busca de errores de invalidación de caché
3. Ejecute `docplatform doctor` para verificar la salud del sistema de permisos

### El primer usuario no es SuperAdmin

Esto sucede si el primer usuario se registra mientras la base de datos ya contiene registros de usuarios (por ejemplo, de una instalación anterior). Para solucionarlo:

1. Detenga el servidor
2. Elimine la base de datos: `rm {DATA_DIR}/data.db`
3. Inicie el servidor y regístrese nuevamente

Esto restablece todos los datos. Use solo en instalaciones nuevas.
