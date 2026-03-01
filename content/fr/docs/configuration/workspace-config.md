---
title: Paramètres de l'espace de travail
description: Configurez les paramètres au niveau de l'espace de travail — dépôt git distant, thème, ordre de navigation, valeurs par défaut de publication, et plus encore.
weight: 4
---

# Paramètres de l'espace de travail

Chaque espace de travail a son propre fichier de configuration dans `.docplatform/workspaces/{workspace-id}/.docplatform/config.yaml`. Modifiez ce fichier directement ou utilisez l'interface web (**Settings** → **Workspace**).

## Référence complète de la configuration

```yaml
# Workspace identity
workspace_id: 01KJJ10NTF31Z1QJTG4ZRQZ2Z2    # Auto-generated ULID
name: "Engineering Docs"                        # Display name
slug: eng-docs                                  # URL slug for published docs
description: "Internal engineering documentation"

# Git synchronization
git_remote: git@github.com:your-org/eng-docs.git
git_branch: main
git_auto_commit: true       # Auto-commit editor saves to git
sync_interval: 300          # Polling interval in seconds (0 = disabled)

# Theme
theme:
  mode: auto                # light, dark, auto (follows system preference)
  accent: blue              # Accent color for published site

# Publishing defaults
publishing:
  default_published: false  # New pages published by default?
  require_explicit_unpublish: false

# Permissions
permissions:
  default_role: viewer      # Role assigned to new workspace members

# Navigation (for published docs sidebar)
navigation:
  - title: "Overview"
    path: "index.md"
  - title: "Getting Started"
    path: "getting-started/index.md"
    children:
      - title: "Installation"
        path: "getting-started/installation.md"
      - title: "Configuration"
        path: "getting-started/configuration.md"
```

## Référence des paramètres

### Identité

| Clé | Type | Description |
|---|---|---|
| `workspace_id` | string | ULID généré automatiquement à la création. Ne pas modifier. |
| `name` | string | Nom affiché dans l'interface et l'en-tête du site publié |
| `slug` | string | Segment d'URL pour la documentation publiée : `/p/{slug}/`. Le modifier casse les URLs existantes. |
| `description` | string | Description optionnelle pour référence interne |

### Git

| Clé | Type | Par défaut | Description |
|---|---|---|---|
| `git_remote` | string | — | URL du dépôt distant (SSH ou HTTPS) |
| `git_branch` | string | `main` | Branche avec laquelle synchroniser |
| `git_auto_commit` | bool | `true` | Auto-commit des sauvegardes depuis l'éditeur web |
| `sync_interval` | int | `300` | Secondes entre chaque interrogation du dépôt distant. Définissez à `0` pour désactiver le polling (webhook uniquement). |

### Thème

| Clé | Type | Par défaut | Description |
|---|---|---|---|
| `theme.mode` | string | `auto` | Schéma de couleurs pour la documentation publiée : `light`, `dark`, `auto` |
| `theme.accent` | string | `blue` | Couleur d'accentuation utilisée dans la documentation publiée pour les liens, boutons et éléments mis en évidence |

### Publication

| Clé | Type | Par défaut | Description |
|---|---|---|---|
| `publishing.default_published` | bool | `false` | Les nouvelles pages sont-elles publiées par défaut |
| `publishing.require_explicit_unpublish` | bool | `false` | Lorsque true, les pages doivent être explicitement dépubliées (empêche l'exclusion accidentelle) |

### Permissions

| Clé | Type | Par défaut | Description |
|---|---|---|---|
| `permissions.default_role` | string | `viewer` | Rôle attribué aux utilisateurs qui acceptent une invitation à l'espace de travail |

### Navigation

Le tableau `navigation` contrôle l'ordre de la barre latérale dans la documentation publiée. Sans ce tableau, les pages sont ordonnées par ordre alphabétique.

```yaml
navigation:
  - title: "Overview"       # Display label
    path: "index.md"        # File path relative to docs/
  - title: "Guides"         # Section header (no path = non-clickable group)
    children:
      - title: "Editor"
        path: "guides/editor.md"
      - title: "Git Sync"
        path: "guides/git-integration.md"
```

**Règles :**

- Chaque entrée nécessite un `title`
- Les entrées avec un `path` sont des liens de page
- Les entrées sans `path` mais avec `children` sont des en-têtes de section
- La profondeur d'imbrication est illimitée
- Les pages non listées dans `navigation` existent toujours mais n'apparaissent pas dans la barre latérale

## Modifier les paramètres

### Via l'interface web

1. Ouvrez l'espace de travail dans l'éditeur web
2. Cliquez sur **Settings** (icône engrenage)
3. Modifiez les paramètres via l'interface de formulaire
4. Les modifications sont sauvegardées automatiquement

### Via le fichier de configuration

Modifiez le fichier YAML directement :

```bash
# Trouver la configuration de votre espace de travail
ls .docplatform/workspaces/*/. docplatform/config.yaml

# Modifier
nano .docplatform/workspaces/01KJJ.../. docplatform/config.yaml
```

Redémarrez le serveur pour que les modifications prennent effet, ou déclenchez un rechargement via l'API :

```bash
curl -X POST http://localhost:3000/api/v1/admin/reload \
  -H "Authorization: Bearer {token}"
```

### Via git

Si le fichier de configuration de l'espace de travail est suivi dans git, poussez les modifications depuis votre IDE et elles seront prises en compte lors du prochain cycle de synchronisation. Cela est utile pour gérer la configuration de la documentation en tant que code.

## Espaces de travail multiples

DocPlatform prend en charge plusieurs espaces de travail sur une seule instance. Chaque espace de travail est totalement isolé :

- Répertoires de contenu séparés
- Dépôts git séparés
- Listes de membres et rôles séparés
- Index de recherche séparés
- Sites publiés séparés (slugs différents)

Créez des espaces de travail supplémentaires via la CLI :

```bash
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git
```

Ou via le sélecteur d'espace de travail dans l'interface web.
