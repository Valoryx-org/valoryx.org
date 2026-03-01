---
title: El editor web
description: Escriba y edite documentación usando el editor web enriquecido de DocPlatform con alternancia a Markdown, formulario de frontmatter y autoguardado.
weight: 1
---

# El editor web

DocPlatform incluye un editor de texto enriquecido construido sobre Tiptap (basado en ProseMirror) que renderiza Markdown en tiempo real manteniendo plena compatibilidad con el código fuente Markdown. Cada cambio que realice produce un archivo `.md` limpio — sin formato propietario, sin dependencia del proveedor.

## Diseño del editor

```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar          │  Editor                                 │
│                   │                                         │
│  📁 Getting       │  ┌──────────────────────────────────┐   │
│     Started       │  │ Frontmatter (collapsible)        │   │
│  📁 Guides        │  │ Title: ___________________       │   │
│  📁 API           │  │ Description: ______________      │   │
│    > auth.md      │  │ Tags: [api] [auth]               │   │
│    > endpoints    │  └──────────────────────────────────┘   │
│  📄 changelog     │                                         │
│                   │  Start writing here...                  │
│  ┌────────────┐   │                                         │
│  │ + New Page │   │                                         │
│  └────────────┘   │  ┌──────────────────────────────────┐   │
│                   │  │ Toolbar: B I Link Image Code ... │   │
└───────────────────┴──┴──────────────────────────────────┘   │
```

### Barra lateral

- **Árbol de páginas** — Lista anidada de todas las páginas del workspace. Arrastre para reordenar.
- **Nueva página** — Cree una nueva página en el nivel raíz o anidada bajo una página existente.
- **Atajo de búsqueda** — Haga clic o presione `Cmd+K` / `Ctrl+K` para abrir la búsqueda de texto completo.

### Formulario de frontmatter

La sección plegable de frontmatter en la parte superior del editor proporciona campos de formulario para los metadatos de la página:

| Campo | Descripción | Obligatorio |
|---|---|---|
| **Title** | Encabezado de la página y etiqueta de navegación | Sí |
| **Description** | Resumen mostrado en resultados de búsqueda y etiquetas meta SEO | No |
| **Tags** | Etiquetas de categorización para filtrado y descubrimiento | No |
| **Published** | Alternancia para incluir/excluir del sitio público | No |
| **Access** | Nivel de visibilidad: `public`, `workspace`, `restricted` | No |

Los cambios en los campos de frontmatter actualizan el bloque YAML en el archivo `.md` automáticamente.

### Barra de herramientas

La barra de herramientas de formato proporciona acceso rápido a:

| Acción | Atajo | Descripción |
|---|---|---|
| **Negrita** | `Cmd+B` | Texto en negrita |
| **Cursiva** | `Cmd+I` | Texto en cursiva |
| **Código** | `Cmd+E` | Código en línea |
| **Enlace** | `Cmd+K` | Insertar o editar hipervínculo |
| **Encabezado 1-3** | `Cmd+Shift+1/2/3` | Encabezados de sección |
| **Lista con viñetas** | `Cmd+Shift+8` | Lista desordenada |
| **Lista numerada** | `Cmd+Shift+7` | Lista ordenada |
| **Lista de tareas** | `Cmd+Shift+9` | Lista con casillas de verificación |
| **Cita** | `Cmd+Shift+>` | Bloque de cita |
| **Bloque de código** | `Cmd+Alt+C` | Bloque de código con selector de lenguaje |
| **Imagen** | — | Subir o pegar una imagen |
| **Tabla** | — | Insertar una tabla |
| **Línea horizontal** | `---` | Línea divisoria |

## Modos de escritura

### Modo de texto enriquecido (predeterminado)

El editor renderiza Markdown como contenido formateado. Los encabezados aparecen como encabezados, los enlaces son clicables, los bloques de código tienen resaltado de sintaxis.

### Modo Markdown sin procesar

Haga clic en el botón `</>` en la barra de herramientas para cambiar a edición Markdown sin procesar. Esto le ofrece una vista de texto plano del archivo con resaltado de sintaxis.

El modo sin procesar es útil para:

- Ajustar con precisión el formato Markdown
- Editar el frontmatter YAML directamente
- Pegar contenido de otras fuentes
- Usar componentes personalizados (Callout, Tabs, etc.)

Los cambios se sincronizan entre modos instantáneamente. Alterne entre uno y otro sin perder trabajo.

## Autoguardado

DocPlatform guarda automáticamente su trabajo cada pocos segundos. Verá un indicador de estado en la barra de herramientas:

| Estado | Significado |
|---|---|
| **Saved** | Todos los cambios guardados en disco |
| **Saving...** | Escritura en progreso |
| **Unsaved changes** | Ediciones pendientes de guardar (mala conexión o error) |

Si la sincronización git está habilitada, cada guardado activa un auto-commit. Los commits se agrupan — ediciones rápidas producen un solo commit con el formato de mensaje: `docs: update {page-title}`.

## Trabajar con contenido

### Imágenes

Arrastre y suelte o pegue imágenes directamente en el editor. Las imágenes se almacenan en el directorio de assets del workspace y se referencian con rutas relativas.

Formatos compatibles: PNG, JPG, GIF, SVG, WebP.

### Tablas

Inserte tablas desde la barra de herramientas. Las tablas soportan:

- Agregar/eliminar filas y columnas
- Alternancia de fila de encabezado
- Alineación de texto (izquierda, centro, derecha)
- Sintaxis de tabla Markdown en modo sin procesar

### Bloques de código

Inserte bloques de código con la barra de herramientas o escribiendo tres acentos graves (`` ``` ``). Seleccione un lenguaje para resaltado de sintaxis — Shiki soporta más de 200 lenguajes.

```javascript
// Code blocks with syntax highlighting
function greet(name) {
  return `Hello, ${name}!`;
}
```

### Enlaces internos

Enlace a otras páginas en su workspace usando enlaces Markdown estándar:

```markdown
See the [API Authentication]({{< relref "/docs/reference/api" >}}) guide.
```

DocPlatform valida los enlaces internos y el comando `doctor` reporta referencias rotas.

## Atajos de teclado

| Atajo | Acción |
|---|---|
| `Cmd+S` | Forzar guardado |
| `Cmd+K` | Abrir diálogo de búsqueda |
| `Cmd+Z` | Deshacer |
| `Cmd+Shift+Z` | Rehacer |
| `Cmd+/` | Alternar comentario Markdown |
| `Tab` | Indentar elemento de lista |
| `Shift+Tab` | Des-indentar elemento de lista |
| `Cmd+Enter` | Alternar completado de tarea (en listas de tareas) |
| `Escape` | Cerrar diálogos / deseleccionar |

> **Nota:** En Windows y Linux, reemplace `Cmd` por `Ctrl`.

## Colaboración en tiempo real

Cuando varios usuarios editan el mismo workspace, los indicadores de presencia muestran quién está en línea y qué página están viendo. La barra lateral muestra avatares de usuarios junto a las páginas que se están editando actualmente.

DocPlatform no soporta la edición simultánea de la misma página por múltiples usuarios. Si dos usuarios intentan guardar cambios en conflicto en la misma página, el Content Ledger detecta la colisión mediante hash de contenido y devuelve un error 409 con ambas versiones disponibles para resolución manual.

## Consejos

- **Arrastre páginas** en la barra lateral para reorganizar la estructura de su documentación
- **Comandos slash** — escriba `/` en el editor para insertar rápidamente componentes (callout, bloque de código, tabla, etc.)
- **Pegue texto enriquecido** desde Google Docs, Notion o Confluence — el editor lo convierte a Markdown limpio
- **Valores predeterminados de frontmatter** — establezca valores predeterminados a nivel de workspace para `published`, `access` y `tags` para reducir la entrada repetitiva
