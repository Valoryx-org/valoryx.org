---
title: Publicación de documentación
description: Publique su documentación como un sitio web público elegante con resaltado de sintaxis, soporte SEO y acceso opcional solo para el equipo.
weight: 5
---

# Publicación de documentación

DocPlatform puede servir su documentación como un sitio web público — completo con barra lateral de navegación, resaltado de sintaxis y metadatos SEO. No se requiere un generador de sitios estáticos adicional.

## Cómo funciona la publicación

La documentación publicada se sirve en `/p/{workspace-slug}/{page-path}`:

```
http://localhost:3000/p/my-docs/              → docs/index.md
http://localhost:3000/p/my-docs/quickstart    → docs/quickstart.md
http://localhost:3000/p/my-docs/api/auth      → docs/api/auth.md
```

Las páginas se renderizan de Markdown a HTML bajo demanda usando goldmark (compatible con CommonMark) con resaltado de sintaxis Chroma para bloques de código.

### Ciclo de vida del estado de página

Las páginas tienen un campo `status` que controla su visibilidad:

| Estado | En el editor | En el sitio publicado | En búsqueda |
|---|---|---|---|
| `draft` (predeterminado) | Visible | Oculto | Visible solo para miembros |
| `published` | Visible | Visible | Visible según reglas de acceso |
| `archived` | Visible (atenuado) | Oculto | Oculto |

Establezca el estado en el frontmatter:

```yaml
---
title: My Page
status: published    # draft, published, or archived
publish: true        # shorthand — equivalent to status: published
---
```

El atajo `publish: true` y `status: published` son equivalentes. Use el que prefiera.

## Habilitar la publicación

### Por página

Establezca `published: true` en el frontmatter de la página:

```yaml
---
title: API Authentication
description: How to authenticate with the API.
published: true
---
```

O active el interruptor **Published** en el formulario de frontmatter del editor web.

### Predeterminado a nivel de workspace

Establezca un valor predeterminado a nivel de workspace para que las nuevas páginas se publiquen automáticamente:

```yaml
# .docplatform/config.yaml
publishing:
  default_published: true
  require_explicit_unpublish: false
```

## Funcionalidades del sitio publicado

### Navegación

El sitio publicado genera una barra lateral de navegación a partir de la jerarquía de sus páginas. El orden coincide con la barra lateral del editor web.

Para personalizar el orden de navegación, ajuste la sección `navigation` en la configuración de su workspace:

```yaml
# .docplatform/config.yaml
navigation:
  - title: "Getting Started"
    path: "getting-started/index.md"
    children:
      - title: "Installation"
        path: "getting-started/installation.md"
      - title: "Quickstart"
        path: "getting-started/quickstart.md"
```

### Resaltado de sintaxis

Los bloques de código se resaltan usando **Chroma** (goldmark-highlighting, tema Dracula). Se soportan más de 200 lenguajes.

Especifique el lenguaje después de las triples comillas invertidas de apertura:

````markdown
```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```
````

### SEO

DocPlatform genera metadatos SEO automáticamente a partir del frontmatter de su página:

| Etiqueta | Origen |
|---|---|
| `<title>` | Frontmatter `title` |
| `<meta name="description">` | Frontmatter `description` |
| `<meta property="og:title">` | Frontmatter `title` |
| `<meta property="og:description">` | Frontmatter `description` |
| `<link rel="canonical">` | Generado a partir de la ruta de la página |
| `sitemap.xml` | Auto-generado a partir de todas las páginas publicadas |
| `robots.txt` | Auto-generado |

### Control de acceso

Por defecto, la documentación publicada es **pública** — no se requiere inicio de sesión. Cualquier persona con la URL puede verla.

Para restringir todo su sitio publicado solo a miembros del workspace, establezca `PUBLISH_REQUIRE_AUTH`:

```bash
# .env
PUBLISH_REQUIRE_AUTH=true
```

Cuando está habilitado:

- Los visitantes que no han iniciado sesión son redirigidos a `/#/login?next=<url>`
- Después de iniciar sesión, son devueltos a la página que solicitaron
- Cualquier miembro del workspace (cualquier rol) puede ver — incluso Viewers
- Los no-miembros que inician sesión son redirigidos fuera

Reinicie el servidor para que este cambio surta efecto. No se requiere reconstrucción.

> **Control de acceso por página** (restringir páginas individuales a roles específicos) está planificado para una versión futura. En v0.5, el control de acceso es todo o nada a nivel de sitio mediante `PUBLISH_REQUIRE_AUTH`.

## Componentes integrados

La documentación publicada soporta 7 componentes personalizados que se renderizan como elementos ricos e interactivos:

### Callout

```markdown
:::callout{type="info"}
This is an informational callout.
:::

:::callout{type="warning"}
Be careful with this operation.
:::

:::callout{type="danger"}
This action is irreversible.
:::

:::callout{type="tip"}
Pro tip: use keyboard shortcuts for faster editing.
:::
```

**Tipos:** `info`, `warning`, `danger`, `tip`, `note`

### Tabs

```markdown
:::tabs
::tab{label="npm"}
npm install docplatform
::
::tab{label="yarn"}
yarn add docplatform
::
::tab{label="pnpm"}
pnpm add docplatform
::
:::
```

### Accordion

```markdown
:::accordion{title="How does sync work?"}
DocPlatform uses a hybrid git engine that combines go-git for small repositories
with native git CLI for large ones. Changes are synced via polling or webhooks.
:::
```

### Cards

```markdown
:::cards
::card{title="Getting Started" link="/getting-started"}
Install and configure DocPlatform in under 10 minutes.
::
::card{title="User Guide" link="/guides/editor"}
Learn the web editor, git sync, and publishing features.
::
:::
```

### Steps

```markdown
:::steps
::step{title="Install"}
Download the binary or pull the Docker image.
::
::step{title="Initialize"}
Run `docplatform init` to create your workspace.
::
::step{title="Start"}
Run `docplatform serve` and open the browser.
::
:::
```

### API Block

```markdown
:::api{method="GET" path="/api/v1/pages/{id}"}
Retrieve a single page by ID.

**Parameters:**
- `id` (path, required) — Page ULID

**Response:** `200 OK`
```json
{
  "id": "01HJKL...",
  "title": "Getting Started",
  "content": "..."
}
```
:::
```

## Dominio personalizado

Para servir documentación publicada en su propio dominio:

1. Establezca la variable de entorno `BASE_DOMAIN`:

```bash
export BASE_DOMAIN=docs.yourcompany.com
```

2. Configure DNS para apuntar su dominio al servidor DocPlatform
3. Configure un reverse proxy (nginx, Caddy o balanceador de carga en la nube) con terminación TLS

Ejemplo de configuración con Caddy:

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy aprovisiona y renueva certificados TLS automáticamente mediante Let's Encrypt.

## Caché

Las páginas publicadas se almacenan en caché para mejorar el rendimiento:

| Header | Valor | Descripción |
|---|---|---|
| `Cache-Control` | `public, max-age=300` | Navegadores y CDNs almacenan en caché durante 5 minutos |
| `ETag` | Hash del contenido | Habilita solicitudes condicionales (304 Not Modified) |

La clave de caché se basa en el hash del contenido de la página. Cuando el contenido cambia, el ETag cambia automáticamente y las versiones en caché se invalidan.

### Reescritura de URLs de assets

En el editor web, los assets usan rutas relativas (`assets/screenshot.png`). En la documentación publicada, estas se reescriben automáticamente a rutas absolutas (`/p/{slug}/assets/screenshot.png`) para que las imágenes y archivos se carguen correctamente a cualquier profundidad de URL.

## Vista previa antes de publicar

Antes de hacer una página pública, previsualícela en la URL publicada. Las páginas con `published: false` siguen siendo accesibles para miembros autenticados del workspace en la ruta `/p/` — simplemente se excluyen de la navegación pública y del sitemap.
