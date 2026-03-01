---
title: Markdown y componentes
description: Escriba documentación con Markdown CommonMark, frontmatter YAML y 7 componentes interactivos integrados.
weight: 2
---

# Markdown y componentes

DocPlatform usa Markdown compatible con CommonMark con frontmatter YAML y 7 componentes personalizados para documentación rica e interactiva.

## Fundamentos de Markdown

DocPlatform soporta la especificación completa de CommonMark más extensiones comunes.

### Encabezados

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```

Los encabezados generan automáticamente IDs de ancla para enlaces profundos: `## My Section` → `#my-section`.

### Formato de texto

```markdown
**Bold text**
*Italic text*
~~Strikethrough~~
`Inline code`
[Link text](https://example.com)
![Image alt text](./assets/screenshot.png)
```

### Listas

```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item

- [ ] Task item (unchecked)
- [x] Task item (checked)
```

### Citas

```markdown
> This is a blockquote.
>
> It can span multiple paragraphs.
```

### Bloques de código

Bloques de código delimitados con resaltado de sintaxis específico del lenguaje (más de 200 lenguajes mediante Shiki):

````markdown
```go
func main() {
    fmt.Println("Hello, DocPlatform!")
}
```
````

### Tablas

```markdown
| Feature | Status | Notes |
|---|---|---|
| Editor | Complete | Tiptap-based |
| Search | Complete | Bleve engine |
| Git sync | Complete | Bidirectional |
```

Las tablas soportan alineación izquierda, centro y derecha:

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| A    |   B    |     C |
```

### Líneas horizontales

```markdown
---
```

### Enlaces entre páginas

Enlace a otras páginas en su workspace usando rutas relativas:

```markdown
See the [Installation guide](../getting-started/installation.md).
Check the [API reference](../reference/api.md) for endpoint details.
```

DocPlatform valida los enlaces internos. El comando `doctor` reporta cualquier referencia rota.

## Frontmatter

Cada página comienza con un bloque de frontmatter YAML delimitado por `---`:

```yaml
---
title: Page Title
description: A brief summary for search results and SEO.
tags: [guide, getting-started]
published: true
access: public
allowed_roles: []
---
```

### Campos de frontmatter

| Campo | Tipo | Obligatorio | Predeterminado | Descripción |
|---|---|---|---|---|
| `title` | string | Sí | — | Título de la página mostrado en navegación y encabezados |
| `description` | string | No | — | Resumen para resultados de búsqueda, etiquetas meta SEO |
| `tags` | string[] | No | `[]` | Categorías para filtrado y búsqueda |
| `published` | boolean | No | `false` | Incluir en el sitio de documentación publicada |
| `access` | string | No | `public` | Visibilidad: `public`, `workspace`, `restricted` |
| `allowed_roles` | string[] | No | `[]` | Roles autorizados a ver (cuando `access: restricted`) |

## Componentes personalizados

DocPlatform incluye 7 componentes integrados que se renderizan como elementos ricos e interactivos tanto en la vista previa del editor web como en la documentación publicada.

Los componentes usan una sintaxis de directiva:

```
:::component-name{attributes}
Content goes here.
:::
```

### Callout

Resalte información importante con cuadros de llamada estilizados.

```markdown
:::callout{type="info"}
DocPlatform automatically indexes all content for search.
:::

:::callout{type="warning"}
Changing the workspace slug will break existing published URLs.
:::

:::callout{type="danger"}
Running `rebuild` drops the pages table and re-indexes from the filesystem.
This is irreversible.
:::

:::callout{type="tip"}
Press Cmd+K to open search from anywhere in the editor.
:::

:::callout{type="note"}
This feature is available in Community Edition.
:::
```

**Tipos disponibles:** `info`, `warning`, `danger`, `tip`, `note`

### Bloque de código (mejorado)

Los bloques de código delimitados estándar se mejoran automáticamente con:

- **Resaltado de sintaxis** — más de 200 lenguajes mediante Shiki
- **Botón de copiar** — copia con un clic al portapapeles
- **Etiqueta de lenguaje** — mostrada en la esquina superior derecha
- **Números de línea** — opcional, habilitado con `showLineNumbers`

````markdown
```typescript {showLineNumbers}
interface Page {
  id: string;
  title: string;
  content: string;
  published: boolean;
}
```
````

### Tabs

Agrupe contenido relacionado en paneles de pestañas intercambiables.

```markdown
:::tabs
::tab{label="macOS"}
```bash
brew install docplatform
```
::
::tab{label="Linux"}
```bash
curl -fsSL https://valoryx.org/install.sh | sh
```
::
::tab{label="Docker"}
```bash
docker pull ghcr.io/valoryx-org/docplatform:latest
```
::
:::
```

La selección de pestaña persiste durante la navegación entre páginas — si un usuario selecciona "Docker", todos los grupos de pestañas en páginas posteriores usan "Docker" como predeterminado cuando esa etiqueta existe.

### Accordion

Secciones plegables para contenido complementario.

```markdown
:::accordion{title="What happens during initialization?"}
The `init` command creates a `.docplatform` directory, initializes the SQLite
database, generates an RS256 signing key, and optionally clones a git repository.
:::

:::accordion{title="Can I use an existing database?"}
No. DocPlatform manages its own SQLite database and does not support connecting
to external database servers in Community Edition.
:::
```

### Cards

Cuadrícula de tarjetas enlazadas para páginas de navegación o resúmenes de funcionalidades.

```markdown
:::cards
::card{title="Getting Started" link="/getting-started"}
Install and configure DocPlatform in under 10 minutes.
::
::card{title="Git Integration" link="/guides/git-integration"}
Bidirectional sync between the web editor and your git repository.
::
::card{title="Publishing" link="/guides/publishing"}
Publish beautiful documentation sites with dark mode and SEO.
::
::card{title="Search" link="/guides/search"}
Instant full-text search with permission filtering.
::
:::
```

### Steps

Instrucciones paso a paso numeradas con indicadores de progreso visual.

```markdown
:::steps
::step{title="Download"}
Get the latest binary from GitHub Releases.
::
::step{title="Initialize"}
Run `docplatform init` to create your workspace.
::
::step{title="Start the server"}
Run `docplatform serve` and open http://localhost:3000.
::
::step{title="Register"}
Create your admin account — the first user becomes SuperAdmin.
::
:::
```

### API Block

Documente endpoints de API con badges de método, parámetros y ejemplos de respuesta.

```markdown
:::api{method="POST" path="/api/v1/auth/login"}
Authenticate a user and receive JWT tokens.

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

**Errors:**
- `401 Unauthorized` — Invalid credentials
- `429 Too Many Requests` — Rate limit exceeded
:::
```

## Uso de componentes en el editor

### Modo de texto enriquecido

En el editor enriquecido, los componentes se renderizan como bloques interactivos. Insértelos usando:

- **Comandos slash** — escriba `/` y luego el nombre del componente (por ejemplo, `/callout`, `/tabs`)
- **Barra de herramientas** — haga clic en el botón **+** → seleccione un componente
- **Teclado** — sin atajos dedicados (use comandos slash)

### Modo Markdown sin procesar

En modo sin procesar, escriba la sintaxis de directiva directamente. El editor proporciona resaltado de sintaxis para los bloques de componentes.

## Extensiones de Markdown

Más allá de CommonMark, DocPlatform soporta:

| Extensión | Sintaxis | Descripción |
|---|---|---|
| **Listas de tareas** | `- [ ] item` | Casillas de verificación interactivas |
| **Tachado** | `~~text~~` | Texto tachado |
| **Tablas** | Tablas GFM | Con soporte de alineación |
| **Enlaces automáticos** | `https://...` | URLs auto-enlazadas |
| **Notas al pie** | `[^1]` | Notas al pie con estilo de referencia |
| **Anclas de encabezado** | Auto-generadas | Enlaces profundos a secciones |
