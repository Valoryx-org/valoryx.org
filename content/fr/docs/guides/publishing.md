---
title: Publier la documentation
description: Publiez votre documentation sous forme de site public élégant avec coloration syntaxique, support SEO et accès optionnel réservé à l'équipe.
weight: 5
---

# Publier la documentation

DocPlatform peut servir votre documentation sous forme de site web public — avec une barre de navigation latérale, la coloration syntaxique et les métadonnées SEO. Aucun générateur de site statique séparé n'est nécessaire.

## Fonctionnement de la publication

La documentation publiée est servie à `/p/{workspace-slug}/{page-path}` :

```
http://localhost:3000/p/my-docs/              → docs/index.md
http://localhost:3000/p/my-docs/quickstart    → docs/quickstart.md
http://localhost:3000/p/my-docs/api/auth      → docs/api/auth.md
```

Les pages sont rendues du Markdown vers le HTML à la demande en utilisant goldmark (conforme à CommonMark) avec la coloration syntaxique Chroma pour les blocs de code.

### Cycle de vie du statut de page

Les pages ont un champ `status` qui contrôle leur visibilité :

| Statut | Dans l'éditeur | Dans le site publié | Dans la recherche |
|---|---|---|---|
| `draft` (par défaut) | Visible | Masqué | Visible uniquement pour les membres |
| `published` | Visible | Visible | Visible selon les règles d'accès |
| `archived` | Visible (estompé) | Masqué | Masqué |

Définissez le statut dans le frontmatter :

```yaml
---
title: My Page
status: published    # draft, published, or archived
publish: true        # shorthand — equivalent to status: published
---
```

Le raccourci `publish: true` et `status: published` sont équivalents. Utilisez celui que vous préférez.

## Activer la publication

### Par page

Définissez `published: true` dans le frontmatter de la page :

```yaml
---
title: API Authentication
description: How to authenticate with the API.
published: true
---
```

Ou basculez l'interrupteur **Published** dans le formulaire de frontmatter de l'éditeur web.

### Valeur par défaut au niveau de l'espace de travail

Définissez une valeur par défaut au niveau de l'espace de travail pour que les nouvelles pages soient publiées automatiquement :

```yaml
# .docplatform/config.yaml
publishing:
  default_published: true
  require_explicit_unpublish: false
```

## Fonctionnalités du site publié

### Navigation

Le site publié génère une navigation latérale à partir de la hiérarchie de vos pages. L'ordre correspond à la barre latérale de l'éditeur web.

Pour personnaliser l'ordre de navigation, ajustez la section `navigation` dans la configuration de votre espace de travail :

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

### Coloration syntaxique

Les blocs de code sont colorés en utilisant **Chroma** (goldmark-highlighting, thème Dracula). Plus de 200 langages sont supportés.

Spécifiez le langage après les trois backticks d'ouverture :

````markdown
```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```
````

### SEO

DocPlatform génère automatiquement les métadonnées SEO à partir du frontmatter de vos pages :

| Balise | Source |
|---|---|
| `<title>` | Frontmatter `title` |
| `<meta name="description">` | Frontmatter `description` |
| `<meta property="og:title">` | Frontmatter `title` |
| `<meta property="og:description">` | Frontmatter `description` |
| `<link rel="canonical">` | Généré à partir du chemin de la page |
| `sitemap.xml` | Généré automatiquement à partir de toutes les pages publiées |
| `robots.txt` | Généré automatiquement |

### Contrôle d'accès

Par défaut, la documentation publiée est **publique** — aucune connexion requise. Toute personne disposant de l'URL peut la consulter.

Pour restreindre l'ensemble de votre site publié aux membres de l'espace de travail uniquement, définissez `PUBLISH_REQUIRE_AUTH` :

```bash
# .env
PUBLISH_REQUIRE_AUTH=true
```

Lorsque cette option est activée :

- Les visiteurs non connectés sont redirigés vers `/#/login?next=<url>`
- Après connexion, ils sont renvoyés vers la page demandée
- Tout membre de l'espace de travail (quel que soit son rôle) peut consulter — même les Viewers
- Les non-membres qui se connectent sont tout de même redirigés

Redémarrez le serveur pour que ce changement prenne effet. Aucune reconstruction n'est nécessaire.

> **Contrôle d'accès par page** (restreindre des pages individuelles à des rôles spécifiques) est prévu pour une future version. Dans la v0.5, le contrôle d'accès est tout ou rien au niveau du site via `PUBLISH_REQUIRE_AUTH`.

## Composants intégrés

La documentation publiée prend en charge 7 composants personnalisés qui s'affichent comme des éléments riches et interactifs :

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

**Types :** `info`, `warning`, `danger`, `tip`, `note`

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

## Domaine personnalisé

Pour servir la documentation publiée sur votre propre domaine :

1. Définissez la variable d'environnement `BASE_DOMAIN` :

```bash
export BASE_DOMAIN=docs.yourcompany.com
```

2. Configurez le DNS pour pointer votre domaine vers le serveur DocPlatform
3. Mettez en place un reverse proxy (nginx, Caddy ou un load balancer cloud) avec terminaison TLS

Exemple de configuration Caddy :

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy provisionne et renouvelle automatiquement les certificats TLS via Let's Encrypt.

## Mise en cache

Les pages publiées sont mises en cache pour la performance :

| En-tête | Valeur | Description |
|---|---|---|
| `Cache-Control` | `public, max-age=300` | Les navigateurs et CDN mettent en cache pendant 5 minutes |
| `ETag` | Hash du contenu | Active les requêtes conditionnelles (304 Not Modified) |

La clé de cache est basée sur le hash du contenu de la page. Lorsque le contenu change, l'ETag change automatiquement et les versions en cache sont invalidées.

### Réécriture des URLs d'assets

Dans l'éditeur web, les assets utilisent des chemins relatifs (`assets/screenshot.png`). Dans la documentation publiée, ceux-ci sont automatiquement réécrits en chemins absolus (`/p/{slug}/assets/screenshot.png`) afin que les images et fichiers se chargent correctement quelle que soit la profondeur de l'URL.

## Prévisualiser avant publication

Avant de rendre une page publique, prévisualisez-la à l'URL publiée. Les pages avec `published: false` sont toujours accessibles aux membres authentifiés de l'espace de travail au chemin `/p/` — elles sont simplement exclues de la navigation publique et du sitemap.
