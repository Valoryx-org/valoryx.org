---
title: "MCP pour la documentation : guide technique"
description: "Comment le Model Context Protocol connecte les assistants IA à votre documentation. Configurez Claude Desktop, utilisez les 26 outils intégrés et automatisez la maintenance documentaire."
date: "2026-03-16"
author: "Valoryx Team"
tags: ["mcp", "ai", "documentation", "tutorial"]
---

Le Model Context Protocol (MCP) est un standard ouvert qui permet aux assistants IA d'interagir avec des outils externes et des sources de données via une interface structurée. Au lieu de copier du texte dans une fenêtre de chat en espérant que le modèle comprenne le contexte, MCP donne à l'assistant un accès direct et typé à vos systèmes — lire des fichiers, lancer des recherches, créer du contenu, le tout via des appels d'outils bien définis.

Pour les équipes de documentation, cela change fondamentalement le workflow. Votre assistant IA cesse d'être un générateur de texte travaillant à partir d'un contexte obsolète et devient un participant qui lit votre documentation réelle, recherche dans votre base de connaissances et effectue des modifications que vous pouvez réviser avant leur mise en ligne.

Valoryx intègre un serveur MCP avec 26 outils. Aucun plugin à installer, aucun service séparé à lancer — si vous avez une instance en fonctionnement, le serveur MCP est déjà là. Il ne vous faut qu'une clé API.

## Ce que fait réellement MCP

MCP définit un protocole pour la découverte et l'invocation d'outils. Un client IA (comme Claude Desktop) se connecte à un serveur MCP, demande quels outils sont disponibles et les appelle avec des paramètres structurés. Le serveur exécute l'opération et renvoie des résultats structurés.

C'est différent des « fonctionnalités IA » greffées sur un produit. Il n'y a pas d'intégration propriétaire. Tout client compatible MCP fonctionne. La [spécification MCP](https://modelcontextprotocol.io) est ouverte, et plusieurs assistants IA la prennent déjà en charge.

Le résultat pratique : vous pouvez demander à Claude « trouve toutes les pages qui mentionnent l'authentification » et il effectuera réellement une recherche dans votre instance de documentation, au lieu d'halluciner des titres de pages à partir de données d'entraînement.

## Les 26 outils intégrés

Chaque outil porte le préfixe `docplatform_*` afin de ne jamais entrer en collision avec d'autres serveurs MCP dans votre client. La référence complète, au niveau des paramètres, se trouve sur la [page MCP](/mcp/) ; voici le registre complet par catégorie :

### Contenu
Créer, lire et réorganiser des pages. Chaque écriture passe par le même service de contenu que l'éditeur web : les modifications sont donc suivies et compatibles avec la synchronisation.

- **docplatform_list_pages** — liste les pages de l'espace de travail connecté.
- **docplatform_read_page** — lit le contenu markdown et les métadonnées d'une page.
- **docplatform_write_page** — écrit une page : la crée si elle n'existe pas, la met à jour si elle existe. L'opération « écris-la, c'est tout » pour les agents IA.
- **docplatform_update_page** — met à jour une page existante (échoue plutôt que de créer — utile quand la page doit déjà exister).
- **docplatform_delete_page** — supprime une page.
- **docplatform_move_page** — déplace une page vers un nouveau chemin dans l'arborescence.

### Découverte et contexte
- **docplatform_search** — recherche plein texte dans l'espace de travail, avec correspondance approximative et résultats classés par pertinence — le même moteur Bleve que l'interface web.
- **docplatform_get_context** — le pilier du RAG : renvoie une page accompagnée de son parent, de ses pages sœurs et des cibles de ses wikilinks en un seul appel, pour que l'assistant dispose du contexte environnant sans cinq allers-retours.
- **docplatform_get_tree** — l'arborescence de navigation complète d'un espace de travail. Utile pour comprendre la structure de la documentation avant d'effectuer des modifications.
- **docplatform_list_workspaces** — liste les espaces de travail accessibles avec la clé API.
- **docplatform_get_manifest** — un manifeste de l'espace de travail lisible par machine.

### Qualité
- **docplatform_validate_links** — détecte les liens internes et les wikilinks cassés.
- **docplatform_quality_scan** — analyse le contenu pour repérer les problèmes de qualité.

### Versionnage
- **docplatform_list_versions** / **docplatform_create_version** — lister et créer des instantanés de version nommés.

### Commentaires et activité
- **docplatform_list_comments** / **docplatform_add_comment** — lire les discussions d'une page et y participer.
- **docplatform_get_activity** — le flux d'activité récente : qui a changé quoi, et quand.

### Gestion des espaces de travail
- **docplatform_create_workspace** / **docplatform_get_workspace** — créer et inspecter des espaces de travail.
- **docplatform_publish_workspace** — publier un espace de travail en tant que site public.

### Thèmes, export, IA et synchronisation git
- **docplatform_get_theme** / **docplatform_update_theme** — lire et modifier le thème de l'espace de travail.
- **docplatform_export** — exporter le contenu de l'espace de travail.
- **docplatform_writing_assist** — assistance à la rédaction côté serveur (améliorer, simplifier, développer, résumer, corriger la grammaire, traduire) lorsqu'un fournisseur IA est configuré.
- **docplatform_resolve_sync_conflict** — résoudre un conflit de synchronisation git en choisissant un côté ou en fournissant le contenu fusionné.

## Configuration de Claude Desktop

Le serveur MCP parle stdio via le binaire `docplatform` lui-même — pas de paquet intermédiaire. Ajoutez une entrée à votre fichier de configuration (sur macOS, `~/Library/Application Support/Claude/claude_desktop_config.json` ; sur Windows, `%APPDATA%\Claude\claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "docplatform": {
      "command": "docplatform",
      "args": ["mcp", "--workspace", "my-docs", "--api-key", "dp_live_abc123"]
    }
  }
}
```

Créez la clé API dans **Workspace Settings → API Keys**. Elle commence par `dp_live_` et n'est affichée qu'une seule fois. Les clés portent des scopes (`read`, `write`, `delete` — `admin` est opt-in), et chaque appel MCP est en outre vérifié contre le rôle de l'utilisateur agissant dans l'espace de travail : la clé d'un Editor ne peut donc pas effectuer d'opérations admin, quels que soient les scopes qu'elle revendique.

Pour les instances distantes ou cloud, il existe aussi un transport Streamable HTTP (endpoint `/mcp`) — voir la [page MCP](/mcp/) pour la matrice des transports et la configuration par client (Claude Code, Cursor, VS Code).

## Exemples pratiques

Une fois connecté, voici des actions concrètes que vous pouvez réaliser :

### Auditer la cohérence

```
"Search all pages for references to our old API endpoint
api.example.com/v1 and list them"
```

Cela appelle `docplatform_search` avec la chaîne de l'ancien endpoint. Vous obtenez la liste de toutes les pages qui référencent encore l'URL dépréciée. Aucun grep manuel dans un dépôt de documentation n'est nécessaire.

### Rédiger et mettre à jour du contenu

```
"Read the current authentication guide, then update it to include
the new passkey login flow. Keep the existing structure."
```

L'assistant appelle `docplatform_read_page` pour lire le contenu actuel, rédige la mise à jour et appelle `docplatform_update_page` pour l'appliquer. Si la [synchronisation git](/docs/guides/git-integration/) est configurée, la modification apparaît comme un commit dans votre dépôt, attribué à l'utilisateur agissant.

### Réviser les changements récents

```
"Show me everything that changed this week in this workspace"
```

Appelle `docplatform_get_activity`. Renvoie ce qui a changé, qui l'a changé et quand. Utile pour les revues hebdomadaires de documentation sans se connecter à l'interface web.

### Vérifier la qualité avant une release

```
"Validate all internal links in this workspace and list anything broken"
```

Appelle `docplatform_validate_links` et renvoie les cibles cassées avec leurs pages sources — le genre de passage en revue fastidieux à la main et instantané avec un accès structuré.

## Ce que cela signifie pour la maintenance documentaire

Le workflow traditionnel de maintenance de la documentation est : quelqu'un remarque que la doc est fausse, crée un ticket, quelqu'un d'autre finit par mettre à jour la page. L'écart entre « remarqué » et « corrigé » est généralement de plusieurs semaines.

Avec MCP, le workflow devient : demander à l'IA d'auditer une section, réviser les conclusions, approuver les modifications. L'écart se réduit à quelques minutes. Non pas parce que l'IA écrit de la meilleure documentation — ce n'est pas le cas, pas de manière fiable — mais parce que le goulot d'étranglement a toujours été de trouver ce qui est faux et de faire la modification, pas de composer le texte.

Cela fonctionne particulièrement bien pour les mises à jour mécaniques : changements d'URL, renommages de terminologie, mises à jour de numéros de version, avis de dépréciation. Le type de modifications fastidieuses pour les humains et simples pour une IA avec un accès structuré au contenu.

Pour en savoir plus sur l'utilisation de MCP pour maintenir la documentation à jour, consultez [Comment garder la documentation à jour](/blog/keep-docs-up-to-date/).

## Limitations à connaître

Les outils MCP opèrent sur des pages individuelles. Il n'y a pas d'outil « réécrire tout le site de documentation » — c'est intentionnel. Les restructurations à grande échelle nécessitent toujours le jugement humain sur l'architecture de l'information.

Les outils d'écriture créent de vrais changements. Si vous confiez à l'assistant une clé avec les scopes `write` et `delete`, il peut modifier et supprimer des pages. Commencez en lecture seule : créez une clé avec le seul scope `read` pour les workflows d'audit, puis accordez les scopes d'écriture une fois que vous faites confiance à la boucle de révision. Les scopes sont appliqués côté serveur, en plus du rôle de l'utilisateur agissant dans l'espace de travail.

La qualité de la recherche dépend de votre contenu. Si votre documentation utilise une terminologie incohérente, l'IA trouvera des résultats incohérents. MCP rend la recherche rapide, mais ne corrige pas les problèmes de contenu sous-jacents.

## Pour commencer

1. [Installez Valoryx](/install/) — binaire unique, sans dépendances, opérationnel en moins de 2 minutes
2. Créez une clé API dans **Workspace Settings → API Keys**
3. Ajoutez la configuration du serveur MCP à Claude Desktop
4. Commencez par un workflow en lecture seule : recherchez et auditez avant d'activer l'écriture

La [documentation MCP](/mcp/) couvre la référence complète des 26 outils, y compris les types de paramètres et les schémas de réponse.

La maintenance de la documentation n'a pas à être un processus manuel. Avec un protocole structuré entre votre assistant IA et votre plateforme de documentation, les parties fastidieuses — trouver le contenu obsolète, vérifier la cohérence, effectuer des mises à jour mécaniques — deviennent quelque chose que vous pouvez déléguer en toute confiance.
