---
title: Recherche
description: Recherche plein texte instantanée dans toute votre documentation avec des résultats filtrés par permissions.
weight: 6
---

# Recherche

DocPlatform inclut un moteur de recherche plein texte intégré (Bleve) qui indexe automatiquement tout le contenu. Aucun service externe à configurer — la recherche fonctionne directement.

## Utiliser la recherche

### Boîte de dialogue Cmd+K

Appuyez sur `Cmd+K` (macOS) ou `Ctrl+K` (Windows/Linux) n'importe où dans l'éditeur web pour ouvrir la boîte de recherche.

```
┌──────────────────────────────────────────┐
│  🔍  Search documentation...             │
├──────────────────────────────────────────┤
│                                          │
│  📄 Getting Started                      │
│     Install and configure DocPlatform... │
│                                          │
│  📄 API Authentication                   │
│     JWT tokens, OAuth2, and session...   │
│                                          │
│  📄 Docker Deployment                    │
│     Run DocPlatform as a container...    │
│                                          │
│  ↑↓ Navigate   ↵ Open   Esc Close       │
└──────────────────────────────────────────┘
```

### Ce qui est indexé

Le moteur de recherche indexe :

- **Titre de la page** (poids augmenté pour le classement)
- **Description de la page** (poids augmenté)
- **Contenu complet de la page** (texte, blocs de code, listes, etc.)
- **Tags** (boost sur correspondance exacte)
- **Métadonnées du frontmatter**

### Syntaxe de recherche

| Syntaxe | Exemple | Description |
|---|---|---|
| Mots-clés | `git sync` | Pages contenant à la fois « git » et « sync » |
| Expression exacte | `"bidirectional sync"` | Pages avec l'expression exacte |
| Préfixe | `auth*` | Pages avec des mots commençant par « auth » |
| Filtre par tag | `tag:api` | Pages taguées avec « api » |

## Filtrage par permissions

Les résultats de recherche sont automatiquement filtrés en fonction des permissions de l'utilisateur courant :

- **Pages publiques** — visibles dans les résultats de recherche pour tous les utilisateurs authentifiés
- **Pages d'espace de travail** — visibles uniquement pour les membres de l'espace de travail
- **Pages restreintes** — visibles uniquement pour les utilisateurs avec le rôle requis

Un Viewer ne peut pas trouver les pages restreintes réservées aux admins via la recherche, même si le contenu correspond à sa requête. Ce filtrage se fait au niveau du moteur de recherche, pas après la requête.

## Indexation

### Indexation automatique

Le contenu est indexé de manière incrémentale via une file d'attente de tâches asynchrone :

1. Une page est créée ou mise à jour (via l'éditeur ou la synchronisation git)
2. Le Content Ledger émet un événement
3. Une tâche d'indexation de recherche est mise en file d'attente
4. L'indexeur Bleve traite la tâche et met à jour l'index

Il y a un bref délai (typiquement moins d'une seconde) entre la sauvegarde d'une page et l'apparition du contenu mis à jour dans les résultats de recherche.

### Reconstruire l'index de recherche

Si l'index de recherche se désynchronise (rare — généralement après un crash ou une manipulation manuelle de fichiers), reconstruisez-le :

```bash
docplatform rebuild
```

Cela supprime l'index de recherche existant et ré-indexe toutes les pages depuis le système de fichiers. Le processus s'exécute en arrière-plan — le serveur reste disponible pendant la reconstruction.

### Santé de l'index

Vérifiez la santé de l'index de recherche avec la commande doctor :

```bash
docplatform doctor
```

Le diagnostic rapporte :

- Le nombre de documents indexés par rapport au nombre de pages en base de données
- Les entrées d'index orphelines (indexées mais sans page correspondante)
- Les entrées d'index manquantes (page existante mais non indexée)
- La taille du fichier d'index et l'horodatage de la dernière mise à jour

## Recherche dans la documentation publiée

Les sites de documentation publiée incluent une interface de recherche pour les visiteurs. Le champ de recherche apparaît dans l'en-tête du site et utilise le même moteur Bleve.

La recherche du site public est limitée aux pages publiées uniquement — le contenu non publié ou restreint n'apparaît jamais dans les résultats de recherche publics.

## Détails du moteur de recherche

Pour les utilisateurs souhaitant comprendre le fonctionnement interne de la recherche :

### Analyseur

Bleve utilise l'**analyseur anglais** par défaut, qui inclut :

- **Tokenisation** — découpe le texte sur les espaces et la ponctuation
- **Mise en minuscules** — correspondance insensible à la casse
- **Suppression des mots vides** — filtre les mots courants (the, is, at, etc.)
- **Racinisation** — correspond aux variantes de mots (running → run, documented → document)

### Pondération des champs

Tous les champs n'ont pas le même poids dans le score de pertinence :

| Champ | Poids | Description |
|---|---|---|
| `title` | Élevé | Titre de la page (signal le plus pertinent) |
| `description` | Élevé | Description / résumé de la page |
| `tags` | Correspondance exacte | Champ mot-clé — correspondance exacte des tags avec boost |
| `body` | Normal | Contenu complet de la page |
| `path` | Mot-clé | Chemin du fichier — correspondance exacte uniquement |

Cela signifie qu'une requête correspondant au titre d'une page est classée plus haut que la même requête correspondant à un passage du corps du texte.

### Stockage

L'index Bleve est stocké dans `{DATA_DIR}/search-index/` en utilisant bbolt (une base de données B+ tree en Go pur). L'index est séparé de la base de données SQLite et peut être supprimé et reconstruit en toute sécurité avec `docplatform rebuild`.

## Performances

| Métrique | Valeur |
|---|---|
| **Latence des requêtes** | < 8 ms (p99) |
| **Taille de l'index** | ~1 Ko par page (approximatif) |
| **Corpus maximum testé** | 1 000 pages |
| **Requêtes concurrentes** | Supportées (thread-safe) |
| **Latence d'indexation** | < 1 seconde après sauvegarde (asynchrone) |

Les performances de recherche évoluent linéairement avec le volume de contenu. Pour les espaces de travail dépassant 10 000 pages, une future version proposera une intégration optionnelle avec Meilisearch.
