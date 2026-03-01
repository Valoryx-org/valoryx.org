---
title: L'éditeur web
description: Rédigez et modifiez de la documentation à l'aide de l'éditeur web riche de DocPlatform avec bascule Markdown, formulaire de frontmatter et sauvegarde automatique.
weight: 1
---

# L'éditeur web

DocPlatform inclut un éditeur de texte riche basé sur Tiptap (fondé sur ProseMirror) qui affiche le Markdown en temps réel tout en préservant une compatibilité totale avec le format Markdown source. Chaque modification que vous effectuez produit un fichier `.md` propre — pas de format propriétaire, pas de verrouillage.

## Disposition de l'éditeur

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

### Barre latérale

- **Arborescence des pages** — Liste imbriquée de toutes les pages de l'espace de travail. Glissez pour réorganiser.
- **Nouvelle page** — Créez une nouvelle page au niveau racine ou imbriquée sous une page existante.
- **Raccourci de recherche** — Cliquez ou appuyez sur `Cmd+K` / `Ctrl+K` pour ouvrir la recherche plein texte.

### Formulaire de frontmatter

La section de frontmatter repliable en haut de l'éditeur fournit des champs de formulaire pour les métadonnées de la page :

| Champ | Description | Obligatoire |
|---|---|---|
| **Title** | Titre de la page et libellé de navigation | Oui |
| **Description** | Résumé affiché dans les résultats de recherche et les balises méta SEO | Non |
| **Tags** | Étiquettes de catégorisation pour le filtrage et la découverte | Non |
| **Published** | Bascule pour inclure/exclure du site public | Non |
| **Access** | Niveau de visibilité : `public`, `workspace`, `restricted` | Non |

Les modifications des champs de frontmatter mettent automatiquement à jour le bloc YAML dans le fichier `.md`.

### Barre d'outils

La barre d'outils de mise en forme offre un accès rapide à :

| Action | Raccourci | Description |
|---|---|---|
| **Gras** | `Cmd+B` | Texte en gras |
| **Italique** | `Cmd+I` | Texte en italique |
| **Code** | `Cmd+E` | Code en ligne |
| **Lien** | `Cmd+K` | Insérer ou modifier un lien hypertexte |
| **Titre 1-3** | `Cmd+Shift+1/2/3` | Titres de section |
| **Liste à puces** | `Cmd+Shift+8` | Liste non ordonnée |
| **Liste numérotée** | `Cmd+Shift+7` | Liste ordonnée |
| **Liste de tâches** | `Cmd+Shift+9` | Liste à cases à cocher |
| **Citation** | `Cmd+Shift+>` | Bloc de citation |
| **Bloc de code** | `Cmd+Alt+C` | Bloc de code clôturé avec sélecteur de langage |
| **Image** | — | Télécharger ou coller une image |
| **Tableau** | — | Insérer un tableau |
| **Ligne horizontale** | `---` | Ligne de séparation |

## Modes d'écriture

### Mode texte riche (par défaut)

L'éditeur affiche le Markdown sous forme de contenu mis en forme. Les titres apparaissent comme des titres, les liens sont cliquables, les blocs de code ont la coloration syntaxique.

### Mode Markdown brut

Cliquez sur le bouton `</>` dans la barre d'outils pour basculer vers l'édition Markdown brute. Cela vous donne une vue en texte brut du fichier avec coloration syntaxique.

Le mode brut est utile pour :

- Ajuster finement la mise en forme Markdown
- Modifier directement le frontmatter YAML
- Coller du contenu provenant d'autres sources
- Utiliser des composants personnalisés (Callout, Tabs, etc.)

Les modifications se synchronisent instantanément entre les modes. Basculez librement sans perdre votre travail.

## Sauvegarde automatique

DocPlatform sauvegarde automatiquement votre travail toutes les quelques secondes. Vous verrez un indicateur d'état dans la barre d'outils :

| État | Signification |
|---|---|
| **Saved** | Toutes les modifications sont enregistrées sur le disque |
| **Saving...** | Écriture en cours |
| **Unsaved changes** | Modifications en attente de sauvegarde (connexion instable ou erreur) |

Si la synchronisation git est activée, chaque sauvegarde déclenche un auto-commit. Les commits sont regroupés — des modifications rapides produisent un seul commit avec le format de message : `docs: update {page-title}`.

## Travailler avec le contenu

### Images

Glissez-déposez ou collez des images directement dans l'éditeur. Les images sont stockées dans le répertoire d'assets de l'espace de travail et référencées avec des chemins relatifs.

Formats supportés : PNG, JPG, GIF, SVG, WebP.

### Tableaux

Insérez des tableaux depuis la barre d'outils. Les tableaux supportent :

- Ajout/suppression de lignes et colonnes
- Bascule de la ligne d'en-tête
- Alignement du texte (gauche, centre, droite)
- Syntaxe de tableau Markdown en mode brut

### Blocs de code

Insérez des blocs de code avec la barre d'outils ou en tapant trois backticks (`` ``` ``). Sélectionnez un langage pour la coloration syntaxique — Shiki prend en charge plus de 200 langages.

```javascript
// Code blocks with syntax highlighting
function greet(name) {
  return `Hello, ${name}!`;
}
```

### Liens internes

Créez des liens vers d'autres pages de votre espace de travail en utilisant des liens Markdown standard :

```markdown
See the [API Authentication]({{< relref "/docs/reference/api" >}}) guide.
```

DocPlatform valide les liens internes et la commande `doctor` signale les références cassées.

## Raccourcis clavier

| Raccourci | Action |
|---|---|
| `Cmd+S` | Forcer la sauvegarde |
| `Cmd+K` | Ouvrir la boîte de recherche |
| `Cmd+Z` | Annuler |
| `Cmd+Shift+Z` | Rétablir |
| `Cmd+/` | Basculer le commentaire Markdown |
| `Tab` | Indenter un élément de liste |
| `Shift+Tab` | Désindenter un élément de liste |
| `Cmd+Enter` | Basculer l'état d'une tâche (dans les listes de tâches) |
| `Escape` | Fermer les dialogues / désélectionner |

> **Note :** Sous Windows et Linux, remplacez `Cmd` par `Ctrl`.

## Collaboration en temps réel

Lorsque plusieurs utilisateurs sont actifs dans le même espace de travail, des indicateurs de présence montrent qui est en ligne et quelle page ils consultent. La barre latérale affiche les avatars des utilisateurs à côté des pages en cours d'édition.

DocPlatform ne prend pas en charge l'édition simultanée de la même page par plusieurs utilisateurs. Si deux utilisateurs tentent de sauvegarder des modifications conflictuelles sur la même page, le Content Ledger détecte la collision via le hash de contenu et renvoie une erreur 409 avec les deux versions disponibles pour résolution manuelle.

## Astuces

- **Glissez les pages** dans la barre latérale pour réorganiser la structure de votre documentation
- **Commandes slash** — tapez `/` dans l'éditeur pour insérer rapidement des composants (callout, bloc de code, tableau, etc.)
- **Collez du texte riche** depuis Google Docs, Notion ou Confluence — l'éditeur le convertit en Markdown propre
- **Valeurs par défaut du frontmatter** — définissez des valeurs par défaut au niveau de l'espace de travail pour `published`, `access` et `tags` afin de réduire la saisie répétitive
