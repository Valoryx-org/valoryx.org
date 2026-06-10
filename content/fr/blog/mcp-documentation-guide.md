---
title: "MCP pour la documentation : guide technique"
description: "Comment le Model Context Protocol connecte les assistants IA à votre documentation. Configurez Claude Desktop, utilisez 26 outils intégrés et automatisez la maintenance documentaire."
date: "2026-03-16"
author: "Valoryx Team"
tags: ["mcp", "ai", "documentation", "tutorial"]
---

Le Model Context Protocol (MCP) est un standard ouvert qui permet aux assistants IA d'interagir avec des outils externes et des sources de données via une interface structurée. Au lieu de copier du texte dans une fenêtre de chat en espérant que le modèle comprenne le contexte, MCP donne à l'assistant un accès direct et typé à vos systèmes — lire des fichiers, lancer des recherches, créer du contenu, le tout via des appels d'outils bien définis.

Pour les équipes de documentation, cela change fondamentalement le workflow. Votre assistant IA cesse d'être un générateur de texte travaillant à partir d'un contexte obsolète et devient un participant qui lit votre documentation réelle, recherche dans votre base de connaissances et effectue des modifications que vous pouvez réviser avant leur mise en ligne.

Valoryx intègre un serveur MCP avec 26 outils. Aucun plugin à installer, aucune clé API à configurer. Si vous avez une instance en fonctionnement, le serveur MCP est déjà là.

## Ce que fait réellement MCP

MCP définit un protocole pour la découverte et l'invocation d'outils. Un client IA (comme Claude Desktop) se connecte à un serveur MCP, demande quels outils sont disponibles et les appelle avec des paramètres structurés. Le serveur exécute l'opération et renvoie des résultats structurés.

C'est différent des « fonctionnalités IA » greffées sur un produit. Il n'y a pas d'intégration propriétaire. Tout client compatible MCP fonctionne. La [spécification MCP](https://modelcontextprotocol.io) est ouverte, et plusieurs assistants IA la prennent déjà en charge.

Le résultat pratique : vous pouvez demander à Claude « trouve toutes les pages qui mentionnent l'authentification » et il effectuera réellement une recherche dans votre instance de documentation, au lieu d'halluciner des titres de pages à partir de données d'entraînement.

## Les 26 outils intégrés

Les outils MCP de Valoryx se répartissent en quatre catégories :

### Outils de lecture
Ceux-ci récupèrent du contenu sans rien modifier.

- **get_page** — Récupère une page unique par ID ou chemin. Renvoie le titre, le contenu markdown, les métadonnées et l'horodatage de dernière modification.
- **get_workspace** — Liste tous les workspaces avec leurs nombres de pages et paramètres.
- **get_page_tree** — Renvoie l'arborescence de navigation complète d'un workspace. Utile pour comprendre la structure de la documentation avant d'effectuer des modifications.

### Outils de recherche
Recherche plein texte propulsée par le même moteur Bleve que l'interface web.

- **search_pages** — Recherche dans toutes les pages d'un workspace. Prend en charge les requêtes par phrase, les recherches par champ spécifique et les opérateurs booléens.
- **search_by_tag** — Trouve les pages avec des tags spécifiques. Utile pour l'audit : « montre-moi tout ce qui est tagué `deprecated` ».
- **search_recent** — Trouve les pages modifiées au cours des N derniers jours. Pratique pour réviser les changements récents.

### Outils d'écriture
Ceux-ci créent ou modifient du contenu. Chaque opération d'écriture crée une entrée dans le ledger, garantissant que les modifications sont suivies et compatibles avec la synchronisation.

- **create_page** — Crée une nouvelle page avec titre, contenu, chemin parent et tags.
- **update_page** — Remplace le contenu d'une page existante. La version précédente est conservée dans l'historique.
- **move_page** — Modifie la position d'une page dans l'arborescence de navigation.
- **delete_page** — Suppression douce d'une page (récupérable depuis le panneau d'administration).

### Outils d'administration
Opérations de gestion des workspaces et utilisateurs.

- **list_users** — Obtient tous les utilisateurs avec leurs rôles. Utile pour auditer les accès.
- **get_activity_log** — Récupère l'activité récente (modifications, connexions, changements de permissions).
- **get_sync_status** — Vérifie l'état de la synchronisation git pour un workspace — dernière synchronisation, modifications en attente, éventuels conflits.

## Configuration de Claude Desktop

Pour connecter Claude Desktop à votre instance Valoryx, ajoutez une entrée de serveur MCP à votre fichier de configuration. Sur macOS, il se trouve à `~/Library/Application Support/Claude/claude_desktop_config.json`. Sur Windows, c'est `%APPDATA%\Claude\claude_desktop_config.json`.

```json
{
  "mcpServers": {
    "valoryx-docs": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-client",
        "--server-url",
        "https://docs.yourcompany.com/api/mcp"
      ],
      "env": {
        "MCP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Générez une clé API depuis le panneau d'administration Valoryx sous **Settings > API Keys**. La clé hérite des permissions de l'utilisateur qui l'a créée, utilisez donc un compte de service dédié avec un rôle RBAC approprié si vous souhaitez limiter ce que l'IA peut faire.

Pour l'édition Community en local, l'URL est typiquement `http://localhost:3000/api/mcp`.

## Exemples pratiques

Une fois connecté, voici des actions concrètes que vous pouvez réaliser :

### Trouver le contenu obsolète

```
"Trouve toutes les pages dans le workspace Engineering qui n'ont pas
été mises à jour au cours des 90 derniers jours"
```

L'assistant appelle `search_recent` avec une fenêtre de 90 jours, inverse le résultat par rapport à `get_page_tree` et renvoie une liste de pages potentiellement obsolètes. Vous obtenez les chemins des pages, les dates de dernière modification et les derniers éditeurs — suffisamment pour attribuer des tâches de révision.

### Auditer la cohérence

```
"Recherche dans toutes les pages les références à notre ancien
endpoint API api.example.com/v1 et liste-les"
```

Cela appelle `search_pages` avec la chaîne de l'ancien endpoint. Vous obtenez une liste de chaque page qui référence encore l'URL dépréciée, avec le contexte environnant. Pas de grep manuel dans un dépôt de documentation.

### Rédiger et mettre à jour du contenu

```
"Lis le guide d'authentification actuel, puis mets-le à jour pour
inclure le nouveau flux de connexion par passkey. Garde la structure
existante."
```

L'assistant appelle `get_page` pour lire le contenu actuel, rédige la mise à jour et appelle `update_page` pour l'appliquer. La version précédente reste dans l'historique. Si la [synchronisation git](/docs/guides/git-integration/) est configurée, la modification apparaît comme un commit dans votre dépôt.

### Réviser les changements récents

```
"Montre-moi tout ce qui a changé la semaine dernière dans tous
les workspaces"
```

Appelle `search_recent` avec une fenêtre de 7 jours. Renvoie un résumé de ce qui a changé, qui l'a changé et quand. Utile pour les revues hebdomadaires de documentation sans se connecter à l'interface web.

## Ce que cela signifie pour la maintenance documentaire

Le workflow traditionnel de maintenance de la documentation est : quelqu'un remarque que la doc est fausse, crée un ticket, quelqu'un d'autre finit par mettre à jour la page. L'écart entre « remarqué » et « corrigé » est généralement de plusieurs semaines.

Avec MCP, le workflow devient : demander à l'IA d'auditer une section, réviser les conclusions, approuver les modifications. L'écart se réduit à quelques minutes. Non pas parce que l'IA écrit de la meilleure documentation — ce n'est pas le cas, pas de manière fiable — mais parce que le goulot d'étranglement a toujours été de trouver ce qui est faux et de faire la modification, pas de composer le texte.

Cela fonctionne particulièrement bien pour les mises à jour mécaniques : changements d'URL, renommages de terminologie, mises à jour de numéros de version, avis de dépréciation. Le type de modifications fastidieuses pour les humains et simples pour une IA avec un accès structuré au contenu.

Pour en savoir plus sur l'utilisation de MCP pour maintenir la documentation à jour, consultez [Comment garder la documentation à jour](/blog/keep-docs-up-to-date/).

## Limitations à connaître

Les outils MCP opèrent sur des pages individuelles. Il n'y a pas d'outil « réécrire tout le site de documentation » — c'est intentionnel. Les restructurations à grande échelle nécessitent toujours le jugement humain sur l'architecture de l'information.

Les outils d'écriture créent de vrais changements. Si vous configurez Claude Desktop avec une clé API de niveau admin, l'IA peut supprimer des pages. Utilisez le RBAC pour limiter les permissions de la clé API de manière appropriée. Un rôle « Editor » peut lire et écrire du contenu mais ne peut pas supprimer des workspaces ni gérer les utilisateurs.

La qualité de la recherche dépend de votre contenu. Si votre documentation utilise une terminologie incohérente, l'IA trouvera des résultats incohérents. MCP rend la recherche rapide, mais ne corrige pas les problèmes de contenu sous-jacents.

## Pour commencer

1. [Installez Valoryx](/install/) — binaire unique, pas de dépendances, opérationnel en moins de 2 minutes
2. Générez une clé API depuis le panneau d'administration
3. Ajoutez la configuration du serveur MCP à Claude Desktop
4. Commencez par un workflow en lecture seule : recherchez et auditez avant d'activer l'écriture

La [documentation MCP](/mcp/) couvre la référence API complète des 26 outils, y compris les types de paramètres et les schémas de réponse.

La maintenance de la documentation n'a pas à être un processus manuel. Avec un protocole structuré entre votre assistant IA et votre plateforme de documentation, les parties fastidieuses — trouver le contenu obsolète, vérifier la cohérence, effectuer des mises à jour mécaniques — deviennent quelque chose que vous pouvez déléguer en toute confiance.
