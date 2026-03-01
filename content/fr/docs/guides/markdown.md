---
title: Markdown et composants
description: Rédigez de la documentation avec du Markdown CommonMark, un frontmatter YAML et 7 composants interactifs intégrés.
weight: 2
---

# Markdown et composants

DocPlatform utilise du Markdown conforme à CommonMark avec un frontmatter YAML et 7 composants personnalisés pour une documentation riche et interactive.

## Bases du Markdown

DocPlatform prend en charge la spécification CommonMark complète ainsi que des extensions courantes.

### Titres

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```

Les titres génèrent automatiquement des identifiants d'ancrage pour les liens profonds : `## My Section` → `#my-section`.

### Mise en forme du texte

```markdown
**Bold text**
*Italic text*
~~Strikethrough~~
`Inline code`
[Link text](https://example.com)
![Image alt text](./assets/screenshot.png)
```

### Listes

```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item

- [ ] Task item (unchecked)
- [x] Task item (checked)
```

### Citations

```markdown
> This is a blockquote.
>
> It can span multiple paragraphs.
```

### Blocs de code

Blocs de code clôturés avec coloration syntaxique spécifique au langage (200+ langages via Shiki) :

````markdown
```go
func main() {
    fmt.Println("Hello, DocPlatform!")
}
```
````

### Tableaux

```markdown
| Feature | Status | Notes |
|---|---|---|
| Editor | Complete | Tiptap-based |
| Search | Complete | Bleve engine |
| Git sync | Complete | Bidirectional |
```

Les tableaux prennent en charge l'alignement gauche, centre et droite :

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| A    |   B    |     C |
```

### Lignes horizontales

```markdown
---
```

### Liens entre pages

Créez des liens vers d'autres pages de votre espace de travail en utilisant des chemins relatifs :

```markdown
See the [Installation guide](../getting-started/installation.md).
Check the [API reference](../reference/api.md) for endpoint details.
```

DocPlatform valide les liens internes. La commande `doctor` signale toute référence cassée.

## Frontmatter

Chaque page commence par un bloc de frontmatter YAML délimité par `---` :

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

### Champs du frontmatter

| Champ | Type | Obligatoire | Par défaut | Description |
|---|---|---|---|---|
| `title` | string | Oui | — | Titre de la page affiché dans la navigation et les en-têtes |
| `description` | string | Non | — | Résumé pour les résultats de recherche, balises méta SEO |
| `tags` | string[] | Non | `[]` | Catégories pour le filtrage et la recherche |
| `published` | boolean | Non | `false` | Inclure dans le site de documentation publié |
| `access` | string | Non | `public` | Visibilité : `public`, `workspace`, `restricted` |
| `allowed_roles` | string[] | Non | `[]` | Rôles autorisés à consulter (quand `access: restricted`) |

## Composants personnalisés

DocPlatform inclut 7 composants intégrés qui s'affichent comme des éléments riches et interactifs dans l'aperçu de l'éditeur web et la documentation publiée.

Les composants utilisent une syntaxe de directive :

```
:::component-name{attributes}
Content goes here.
:::
```

### Callout

Mettez en valeur des informations importantes avec des encadrés stylisés.

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

**Types disponibles :** `info`, `warning`, `danger`, `tip`, `note`

### Bloc de code (amélioré)

Les blocs de code clôturés standard sont automatiquement enrichis avec :

- **Coloration syntaxique** — 200+ langages via Shiki
- **Bouton de copie** — copie en un clic vers le presse-papiers
- **Étiquette de langage** — affichée dans le coin supérieur droit
- **Numéros de ligne** — optionnel, activé avec `showLineNumbers`

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

Regroupez du contenu connexe en panneaux d'onglets commutables.

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

La sélection d'onglet persiste entre les navigations de page — si un utilisateur sélectionne « Docker », tous les groupes d'onglets des pages suivantes s'ouvrent par défaut sur « Docker » quand ce libellé existe.

### Accordion

Sections repliables pour du contenu complémentaire.

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

Grille de cartes cliquables pour les pages de navigation ou les aperçus de fonctionnalités.

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

Instructions pas à pas numérotées avec indicateurs visuels de progression.

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

Documentez les endpoints API avec des badges de méthode, des paramètres et des exemples de réponse.

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

## Utilisation des composants dans l'éditeur

### Mode texte riche

Dans l'éditeur riche, les composants s'affichent comme des blocs interactifs. Insérez-les en utilisant :

- **Commandes slash** — tapez `/` puis le nom du composant (par ex. `/callout`, `/tabs`)
- **Barre d'outils** — cliquez sur le bouton **+** → sélectionnez un composant
- **Clavier** — pas de raccourcis dédiés (utilisez les commandes slash)

### Mode Markdown brut

En mode brut, écrivez la syntaxe de directive directement. L'éditeur fournit la coloration syntaxique pour les blocs de composants.

## Extensions Markdown

Au-delà de CommonMark, DocPlatform prend en charge :

| Extension | Syntaxe | Description |
|---|---|---|
| **Listes de tâches** | `- [ ] item` | Cases à cocher interactives |
| **Texte barré** | `~~text~~` | Texte barré |
| **Tableaux** | Tableaux GFM | Avec support de l'alignement |
| **Liens automatiques** | `https://...` | URLs automatiquement transformées en liens |
| **Notes de bas de page** | `[^1]` | Notes de bas de page par référence |
| **Ancres de titres** | Générées automatiquement | Liens profonds vers les sections |
