---
title: DocPlatform Community Edition
description: Plataforma de documentación autoalojada y respaldada por git con un editor web elegante. Sea dueño de su documentación. Controle su flujo de trabajo.
weight: 1
---

# DocPlatform Community Edition

DocPlatform es una plataforma de documentación autoalojada que combina un editor web enriquecido con sincronización bidireccional de git, empaquetada como un único binario sin dependencias externas.

Escriba en su navegador. Haga push desde su IDE. Todo se mantiene sincronizado.

## Por qué DocPlatform

Las plataformas de documentación le obligan a elegir: un editor web pulido con dependencia del proveedor, o archivos sin procesar en git sin funciones de colaboración. DocPlatform elimina esa disyuntiva.

| Lo que obtiene | Cómo funciona |
|---|---|
| **Un solo binario, cero dependencias** | Un único binario Go incluye el editor, la base de datos, el motor de búsqueda y el motor git. Sin runtime de Node.js, sin Postgres, sin Elasticsearch. |
| **Cada página es un archivo `.md`** | Su contenido vive como archivos Markdown en un repositorio git real. Sin formatos propietarios. Sin necesidad de exportar. |
| **Sincronización bidireccional de git** | Edite en el navegador: los cambios se auto-confirman y se envían. Haga push desde su IDE: la interfaz web se actualiza automáticamente. |
| **Documentación publicada elegante** | Un clic para publicar un sitio de documentación con modo oscuro, resaltado de sintaxis y 7 componentes integrados. |
| **Colaboración en equipo** | Jerarquía de roles de 6 niveles, invitaciones al workspace, indicadores de presencia en tiempo real y registro completo de auditoría. |
| **Búsqueda de texto completo** | Motor de búsqueda integrado con resultados instantáneos. Sin servicio externo que configurar. |

## Para quién es

DocPlatform Community Edition está diseñada para:

- **Mantenedores de código abierto** que guardan la documentación del proyecto en el repositorio pero desean una mejor experiencia de edición que Markdown sin procesar en GitHub
- **Equipos internos de plataforma / DevEx** que necesitan docs-as-code con control de acceso y un editor web, no uno u otro
- **Pequeñas agencias de desarrollo** que gestionan múltiples repositorios de documentación de clientes con respaldo git y sin opción autoalojada asequible
- **Redactores técnicos** que necesitan una experiencia de autoría pulida respaldada por control de versiones
- **Desarrolladores individuales** que desean una base de conocimiento personal con publicación pública, sin suscripción

**No está dirigido a:** empresas con requisitos estrictos de cumplimiento que necesitan SAML/SCIM (consulte la futura Enterprise Edition), ni a equipos de contenido no técnicos sin familiaridad con git.

## Cómo funciona

```
┌──────────────────────────────────────────────────┐
│              DocPlatform (single binary)          │
│                                                  │
│   ┌────────────┐  ┌──────────┐  ┌────────────┐  │
│   │ Web Editor  │  │ SQLite   │  │ Bleve      │  │
│   │ (Next.js)   │  │ Database │  │ Search     │  │
│   └──────┬──────┘  └────┬─────┘  └──────┬─────┘  │
│          │              │               │        │
│          └──────┬───────┴───────┬───────┘        │
│                 │               │                │
│          ┌──────▼──────┐ ┌─────▼──────┐         │
│          │ Content     │ │ Git        │         │
│          │ Ledger      │ │ Engine     │         │
│          └──────┬──────┘ └─────┬──────┘         │
│                 │              │                 │
└─────────────────┼──────────────┼─────────────────┘
                  │              │
           ┌──────▼──────┐ ┌────▼──────┐
           │ Filesystem  │ │ Remote    │
           │ (.md files) │ │ Git Repo  │
           └─────────────┘ └───────────┘
```

Cada cambio de contenido, ya sea desde el editor web, un git push o una llamada a la API, fluye a través del **Content Ledger**, un único pipeline que mantiene el sistema de archivos, la base de datos y el índice de búsqueda en perfecta sincronización.

## Inicio rápido

Ponga en marcha DocPlatform en menos de 5 minutos:

```bash
# Download the binary (recommended — auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh

# Initialize a workspace
docplatform init --workspace-name "My Docs" --slug my-docs

# Start the server
docplatform serve
```

Abra [http://localhost:3000](http://localhost:3000) y registre su primer usuario; este se convierte automáticamente en SuperAdmin.

Para la guía completa, consulte la sección [Primeros pasos](getting-started/index.md).

## Descripción general de funcionalidades

### Plataforma principal

- **Editor web enriquecido** — Editor basado en Tiptap con formulario de frontmatter, alternancia a Markdown sin procesar y autoguardado
- **Sincronización bidireccional de git** — Web → git commit → push; CLI push → polling → actualización web
- **Detección de conflictos** — Concurrencia optimista basada en hash con diff descargable en caso de colisión
- **Búsqueda de texto completo** — Motor Bleve integrado con resultados filtrados por permisos y atajo Cmd+K
- **Permisos RBAC** — 6 roles: SuperAdmin, WorkspaceAdmin, Admin, Editor, Commenter, Viewer
- **Autenticación** — Local (argon2id) + OIDC opcional de Google/GitHub
- **Modelo de workspaces** — Org → Workspace → Páginas con jerarquía e invitaciones de equipo
- **Registro de auditoría** — Cada mutación registrada con usuario, marca de tiempo y tipo de operación

### Documentación publicada

- **Sitio público** — Sirva documentación en `/p/{workspace-slug}/{page-path}`
- **Modo oscuro** — Tema claro/oscuro automático con alternancia manual
- **7 componentes integrados** — Callout, Code (200+ lenguajes), Tabs, Accordion, Cards, Steps, API Block
- **Preparado para SEO** — Etiquetas OpenGraph, URLs canónicas, sitemap.xml, robots.txt

### Operaciones

- **Diagnósticos de salud** — Comando `doctor` de 9 puntos que verifica la consistencia FS/DB, la salud de búsqueda y los enlaces rotos
- **Copias de seguridad diarias** — Copias de seguridad automatizadas de SQLite con retención configurable
- **Apagado graceful** — Manejo limpio de señales para despliegues sin tiempo de inactividad
- **Registro estructurado** — Logs en formato JSON con IDs de solicitud para observabilidad

## Requisitos del sistema

| Requisito | Mínimo | Recomendado |
|---|---|---|
| **SO** | Linux (amd64/arm64), macOS (amd64/arm64) | Linux amd64 |
| **Memoria** | 128 MB | 512 MB |
| **Disco** | 200 MB (binario + datos) | 1 GB |
| **Git** | Opcional (para sincronización remota) | Git 2.30+ |
| **Red** | Ninguna (funciona sin conexión) | Puerto 3000 abierto |

## Próximos pasos

| Guía | Descripción |
|---|---|
| [Primeros pasos](getting-started/index.md) | Instale, configure y cree su primer workspace |
| [Guías del usuario](guides/editor.md) | Aprenda a usar el editor, la sincronización git, la publicación y la búsqueda |
| [Configuración](configuration/index.md) | Variables de entorno, autenticación, permisos y configuración del workspace |
| [Despliegue](deployment/binary.md) | Despliegue en producción con binario, Docker o contenedores |
| [Referencia CLI](reference/cli.md) | Referencia completa de comandos |
| [Referencia API](reference/api.md) | Endpoints de la API REST y ejemplos |
| [Solución de problemas](reference/troubleshooting.md) | Problemas comunes y cómo resolverlos |

## Rendimiento

Medido en Apple M2, SSD NVMe, workspace de 1.000 páginas:

| Operación | Latencia |
|---|---|
| Guardado de página (sync core) | < 30ms |
| Renderizado de página (respuesta API) | < 50ms p99 |
| Búsqueda de texto completo | < 8ms p99 |
| Verificación de permisos | < 0.1ms |
| Verificación de permisos en lote (100 páginas) | < 1ms |
| Arranque en frío del servidor | < 1 segundo |
| Reconciliación completa (1.000 archivos) | < 5 segundos |
| Git commit (un archivo) | < 2 segundos |
| Memoria (inactivo) | < 80 MB |
| Memoria (10 usuarios simultáneos) | < 200 MB |
| Tamaño del binario | ~120 MB |

## Cómo se compara DocPlatform

| Capacidad | DocPlatform | GitBook | Notion | Docusaurus | Confluence | Wiki.js |
|---|---|---|---|---|---|---|
| Autoalojado | Sí | No | No | Sí | No | Sí |
| Respaldado por git | Sí | Parcial | No | Sí | No | No |
| Editor web | Sí | Sí | Sí | No | Sí | Sí |
| Sincronización bidireccional de git | Sí | No | No | N/A | No | No |
| Binario único (cero deps) | Sí | N/A | N/A | No (Node.js) | N/A | Docker |
| RBAC integrado | Sí | De pago | De pago | No | Sí | Sí |
| Sitio de documentación publicado | Sí | Sí | Sí | Sí | Sí | Sí |
| Código abierto | Sí | No | No | Sí | No | Sí |
| Funciona sin conexión | Sí | No | No | Sí | No | No |

## Límites de Community Edition

Community Edition es el núcleo completamente funcional y autoalojado de DocPlatform. Incluye todo lo documentado en este sitio con los siguientes límites:

| Recurso | Community Edition |
|---|---|
| **Editores** (usuarios que pueden crear/editar páginas) | Hasta 5 |
| **Workspaces** | Hasta 3 |
| **Viewers y Commenters** | Ilimitados (nunca se contabilizan) |
| **Páginas por workspace** | Ilimitadas |
| **Documentación publicada** | Ilimitada |

Estos límites cubren la mayoría de equipos pequeños y medianos. La futura Enterprise Edition ofrecerá editores ilimitados, workspaces ilimitados, SAML/SSO, soporte para PostgreSQL y búsqueda avanzada mediante Meilisearch, pero Community Edition siempre seguirá siendo la base completa y autoalojable.
