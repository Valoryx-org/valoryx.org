---
title: Roles y permisos
description: Configure la jerarquía de 5 roles de DocPlatform, el control de acceso a nivel de workspace, los permisos del editor y los límites de puestos por plan.
weight: 3
---

# Roles y permisos

DocPlatform usa control de acceso basado en roles (RBAC) impulsado por custom RBAC, un motor de autorización en proceso. Los permisos se evalúan en menos de 0.1ms por verificación sin servicio externo.

## Jerarquía de roles

DocPlatform define 5 roles públicos en una jerarquía estricta. Los roles superiores heredan todos los permisos de los roles inferiores.

```
Super Admin         ← Propietario de la org / creador de la cuenta (rol público más alto)
    │
Admin               ← Gestionar configuración del workspace, miembros, git, tema
    │
Editor              ← Crear y editar páginas (configurable por workspace)
    │
Commenter           ← Ver páginas, dejar comentarios
    │
Viewer              ← Solo ver páginas
```

> **Platform Owner** es un rol interno reservado para operadores auto-alojados para el mantenimiento de la plataforma (migraciones de base de datos, gestión de licencias, configuración del sistema). No aparece en la interfaz ni en la API y no forma parte de la jerarquía pública de roles.

### Matriz de permisos

| Permiso | Viewer | Commenter | Editor | Admin | Super Admin |
|---|---|---|---|---|---|
| Ver páginas | Sí | Sí | Sí | Sí | Sí |
| Buscar contenido | Sí | Sí | Sí | Sí | Sí |
| Dejar comentarios | | Sí | Sí | Sí | Sí |
| Editar páginas | | | Sí | Sí | Sí |
| Crear páginas | | | Configurable | Sí | Sí |
| Eliminar páginas | | | Configurable | Sí | Sí |
| Subir assets | | | Sí | Sí | Sí |
| Asignar miembros de la org al workspace | | | | Sí | Sí |
| Eliminar miembros del workspace | | | | Sí | Sí |
| Cambiar roles de miembros (dentro del workspace) | | | | Sí | Sí |
| Gestionar configuración del workspace | | | | Sí | Sí |
| Gestionar tema y navegación | | | | Sí | Sí |
| Invitar usuarios externos a la org | | | | | Sí |
| Crear/eliminar workspaces | | | | | Sí |
| Configurar repositorio git remoto | | | | | Sí |
| Gestionar facturación y suscripción | | | | | Sí |
| Acceder a todos los workspaces | | | | | Sí |
| Gestionar configuración a nivel de org | | | | | Sí |

### Permisos configurables del Editor

Las capacidades del Editor se pueden ajustar por workspace. Los Admins y Super Admins configuran estas opciones en la configuración del workspace:

| Configuración | Por defecto | Descripción |
|---|---|---|
| `editor_can_create_pages` | `true` | Los editores pueden crear nuevas páginas |
| `editor_can_delete_pages` | `false` | Los editores pueden eliminar páginas |

Cuando un permiso está desactivado, los editores ven la acción en gris en la interfaz y reciben `403 Forbidden` de la API.

## Asignación de roles

### Primer usuario (Super Admin)

El primer usuario en registrarse en una nueva instancia de DocPlatform recibe automáticamente el rol de **Super Admin**. Esto solo ocurre una vez — los registros posteriores no reciben rol de workspace hasta ser invitados.

El Super Admin es el propietario de la org y creador de la cuenta. Tiene control total sobre todos los workspaces, facturación, conexiones git e invitaciones de usuarios externos.

### Invitar usuarios externos

Solo el **Super Admin** puede invitar usuarios externos a la organización:

**Interfaz web:** Org Settings → Members → Invite External User

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/org/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "default_role": "editor"
  }'
```

El usuario invitado se une a la org y luego puede ser asignado a workspaces por cualquier Admin o Super Admin.

### Asignar miembros a workspaces

Los **Admins** asignan miembros existentes de la org a su workspace. Los Admins no pueden invitar usuarios externos — solo el Super Admin puede hacerlo.

**Interfaz web:** Workspace Settings → Members → Add Member → seleccionar de los miembros de la org → seleccionar rol

**API:**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/:id/members \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "01HY5K3M7Q8P",
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

Valores disponibles: `viewer`, `commenter`, `editor`, `admin`

## Control de acceso a nivel de página

Anule los permisos a nivel de workspace en páginas individuales usando frontmatter. Las reglas de acceso en el frontmatter **restringen** dentro del rol del usuario — nunca otorgan permisos más allá del rol.

### Sintaxis de control de acceso

Use reglas de acceso basadas en roles y usuarios para controlar quién puede acceder a una página:

```yaml
---
title: Internal Security Policy
access:
  roles: ["security-team", "engineering-leads"]
  users: ["@01HY5K3M7Q8P"]
---
```

| Campo | Tipo de valor | Descripción |
|---|---|---|
| `access.roles` | lista de nombres de rol | Roles que pueden acceder a esta página |
| `access.users` | lista de `@user_id` | Usuarios individuales que pueden acceder a esta página |

**Reglas:**
- Prefije los IDs de usuario con `@` para apuntar a usuarios individuales
- Super Admin y Admin siempre tienen acceso independientemente de las reglas del frontmatter
- El frontmatter solo puede **restringir** — una página no puede otorgar acceso más allá del rol del usuario en el workspace

### Ejemplos

**Página pública** (predeterminado — todos los miembros del workspace pueden ver):

```yaml
---
title: Getting Started
---
```

**Restringida a equipos específicos:**

```yaml
---
title: Infrastructure Runbook
access:
  roles: ["security-team", "sre-team"]
---
```

**Restringida con acceso de usuario individual:**

```yaml
---
title: Budget Proposal
access:
  roles: ["finance-team"]
  users: ["@01HY5K3M7Q8P"]
---
```

### Qué significa el acceso restringido

Cuando una página tiene reglas de `access`:

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

| Rol | Nivel | Ámbito | Acción mínima |
|---|---|---|---|
| Viewer | 10 | Workspace | `read` |
| Commenter | 20 | Workspace | `read`, `comment` |
| Editor | 30 | Workspace | `read`, `comment`, `edit` (+ `create`/`delete` si está habilitado) |
| Admin | 40 | Workspace | Todas las acciones del workspace |
| Super Admin | — | Org | Omite todas las verificaciones del workspace |

> Super Admin es un **rol a nivel de org** — omite las verificaciones de permisos del workspace por completo en lugar de tener un nivel numérico. Platform Owner es un flag booleano en el registro del usuario que omite todas las verificaciones globalmente.

Las acciones tienen niveles mínimos: `read` requiere nivel 10+, `comment` requiere 20+, `edit` requiere 30+, `write`/`delete` requiere 40+ (los Editores obtienen `edit` pero no `write`/`delete` a menos que los flags configurables estén habilitados), `admin` requiere 40+. El nivel del rol del usuario se compara contra el nivel mínimo de la acción.

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
(custom RBAC check: user + role + resource + action)
    │
    ├── Allowed → proceed to handler
    │
    └── Denied → 403 Forbidden
```

### Flujo de evaluación en 5 pasos

1. **¿Es el usuario Platform Owner?** → PERMITIR (bypass global)
2. **¿Es el usuario Org Super Admin de la organización de este workspace?** → PERMITIR (bypass a nivel org)
3. **Buscar el rol del usuario en el workspace** → si no es miembro, DENEGAR
4. **¿El nivel del rol alcanza el mínimo para la acción?** → comparar `role_level >= action_min_level`, más los flags de permisos del editor
5. **¿Tiene la página reglas de acceso en el frontmatter?** → verificar `access.roles`/`access.users`, RESTRINGIR dentro del rol

El frontmatter RESTRINGE dentro del rol, nunca OTORGA más allá de él. Un frontmatter malformado aplica **modo estricto** — página restringida solo a Admin.

### Rendimiento

| Métrica | Valor |
|---|---|
| **Motor** | custom RBAC (en proceso, en memoria) |
| **Tiempo de evaluación** | < 0.1ms por verificación |
| **Verificación por lote** | < 1ms por 100 páginas |
| **Caché** | Versionado (auto-invalidado en cambio de rol o permiso) |
| **Almacenamiento de políticas** | SQLite (cargado en memoria al iniciar) |

## Caché de permisos

Las políticas de custom RBAC se cargan desde SQLite a memoria al iniciar el servidor. Los cambios en roles o declaraciones de acceso en frontmatter activan una invalidación de caché:

1. El administrador cambia el rol de un usuario → se incrementa la versión de la caché de permisos
2. Un editor actualiza el frontmatter de una página con nuevas reglas de `access` → se invalida la caché para esa página
3. La siguiente verificación de permisos carga la política fresca desde SQLite

La caché es versionada, no basada en tiempo — no hay ventana de permisos obsoletos.

## Patrones comunes

### Documentación pública de solo lectura con páginas internas restringidas

```yaml
# Most pages: no access rules (open to all workspace members)

# Internal pages: restricted
---
title: Incident Response Playbook
access:
  roles: ["sre-team", "admin"]
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

Super Admin tiene acceso a todos los workspaces para visibilidad entre equipos.

## Planes y límites de puestos

### Conteo de puestos

Los roles **Super Admin**, **Admin** y **Editor** cuentan para el límite de puestos `max_editors` del plan. Los roles Commenter y Viewer son **ilimitados en todos los planes** y nunca cuentan para ningún límite de puestos.

Cuando se alcanza el límite de puestos, los nuevos miembros de la org aún pueden ser invitados — pero solo se les puede asignar los roles Commenter o Viewer hasta que se libere un puesto.

### Community Edition

Community Edition es gratuita y auto-alojada sin necesidad de clave de licencia:

| Recurso | Límite |
|---|---|
| Workspaces | Ilimitados |
| Editores (Super Admin + Admin + Editor) | Ilimitados |
| Viewers y Commenters | Ilimitados |
| Páginas | Ilimitadas |

### Planes Cloud

| | Free | Team | Business |
|---|---|---|---|
| **Workspaces** | 1 | 3 | 10 |
| **Puestos** (Super Admin + Admin + Editor) | 3 | 15 | 50 |
| **Viewers y Commenters** | Ilimitados | Ilimitados | Ilimitados |
| **Páginas** | 50 | 150 | 500 |

> ¿Necesita más? [Contacte a ventas](https://valoryx.org/contact) para planes Enterprise con límites personalizados, SSO y SLA.

Para detalles completos de facturación, consulte [Facturación y planes](../guides/billing.md).

## Solución de problemas

### "403 Forbidden" en una página a la que debería tener acceso

1. Verifique su rol: Profile → Workspace Membership
2. Verifique el frontmatter de la página: ¿`access.roles` incluye su rol?
3. Pida a un administrador del workspace que verifique su asignación de rol
4. Si es Editor, verifique si la acción requiere que `editor_can_create_pages` o `editor_can_delete_pages` estén habilitados

### Los cambios de permisos no surten efecto

Los cambios de permisos deberían ser instantáneos (la invalidación de caché es síncrona). Si no lo son:

1. Cierre sesión e inicie sesión nuevamente (actualice sus tokens JWT)
2. Verifique los logs del servidor en busca de errores de invalidación de caché
3. Ejecute `docplatform doctor` para verificar la salud del sistema de permisos

### El primer usuario no es Super Admin

Esto sucede si el primer usuario se registra mientras la base de datos ya contiene registros de usuarios (por ejemplo, de una instalación anterior). Para solucionarlo:

1. Detenga el servidor
2. Elimine la base de datos: `rm {DATA_DIR}/data.db`
3. Inicie el servidor y regístrese nuevamente

Esto restablece todos los datos. Use solo en instalaciones nuevas.

### "Límite de puestos alcanzado" al invitar a un miembro

Se ha alcanzado el límite `max_editors` del plan. Opciones:

1. Degradar un Admin o Editor existente a Commenter o Viewer para liberar un puesto
2. Invitar al nuevo usuario como Commenter o Viewer (estos son ilimitados)
3. Actualizar su plan para obtener más puestos
