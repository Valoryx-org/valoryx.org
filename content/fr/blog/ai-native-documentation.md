---
title: "L'avenir de la documentation est AI-native"
description: "La documentation va évoluer de pages statiques vers des systèmes maintenus par l'IA. DocPlatform intègre 26 outils MCP dès aujourd'hui qui permettent aux agents IA de lire et écrire votre documentation."
date: "2026-04-13"
author: "Valoryx Team"
tags: ["ai", "mcp", "documentation", "future"]
---

La documentation a un problème de maintenance. Vous écrivez un guide, le publiez, et en trois mois il est obsolète. L'API a changé. Le format de configuration a été remanié. Une dépendance a été remplacée. Les captures d'écran montrent une interface qui n'existe plus.

La solution n'est pas « écrire de meilleure documentation » ou « créer une culture de la documentation ». Les équipes essaient ça depuis des décennies. La solution est de rendre la documentation consciente du code qu'elle décrit — pour que quand le code change, la documentation le sache.

C'est ce que signifie une documentation AI-native. Non pas « l'IA écrit votre documentation » (cela produit du contenu générique et sans âme). Plutôt : l'IA surveille votre codebase, détecte quand la documentation dérive de la réalité, et soit le signale à un humain, soit propose des mises à jour spécifiques. L'humain reste dans la boucle pour le jugement ; la machine gère la surveillance.

## Le problème d'obsolescence, quantifié

Auditez la documentation de n'importe quel projet logiciel actif et vous constaterez qu'une grande partie des pages contient au moins une incohérence factuelle avec le codebase actuel. Les problèmes les plus courants :

- **Signatures API obsolètes** — paramètres ajoutés ou supprimés mais documentation non mise à jour
- **Exemples de configuration erronés** — valeurs par défaut changées, ancien format toujours documenté
- **Liens morts** — pages restructurées, références internes non mises à jour
- **Fonctionnalités manquantes** — nouvelles capacités ajoutées sans aucune documentation

La revue manuelle détecte ces problèmes lentement, si elle les détecte. Une équipe de 20 ingénieurs pourrait faire un « audit de documentation » une fois par trimestre, passant une semaine à corriger ce qu'ils trouvent. Le temps que l'audit soit terminé, de nouvelles dérives ont déjà commencé.

## Ce que AI-native signifie réellement

Une plateforme de documentation AI-native possède trois propriétés :

**1. Contenu lisible par machine.** La documentation est stockée dans un format que les outils IA peuvent lire, interroger et modifier programmatiquement. Du markdown dans un dépôt git convient. Du texte riche propriétaire dans une base de données SaaS, non.

**2. Lien code-documentation.** La plateforme sait (ou peut découvrir) quelles pages de documentation décrivent quelles parties du codebase. Quand `auth.go` change, la plateforme peut identifier que `docs/authentication.md` pourrait nécessiter une mise à jour.

**3. Accès structuré aux outils.** Les agents IA peuvent interagir avec la documentation via un protocole défini — pas en scrapant du HTML ou en rétro-ingéniérant des API, mais via des outils explicites et documentés.

DocPlatform livre aujourd'hui la première et la troisième — du markdown synchronisé avec git, plus un serveur MCP intégré. La deuxième, le lien code-documentation, se construit par-dessus avec des conventions : quand la documentation et le code vivent dans des dépôts connectés, un agent IA ayant accès aux deux peut faire le lien lui-même.

## MCP : le protocole

[MCP](https://modelcontextprotocol.io/) est un standard ouvert développé par Anthropic pour connecter les modèles IA aux outils externes et sources de données. Au lieu que chaque outil IA construise des intégrations personnalisées avec chaque plateforme, MCP définit une interface standard : des outils (actions que l'IA peut effectuer), des ressources (données que l'IA peut lire) et des prompts (templates pour les workflows courants).

DocPlatform intègre un serveur MCP — pas de plugins, pas de service séparé. Quand vous l'activez, tout client IA compatible MCP peut interagir avec votre documentation via 26 outils dédiés.

## Les 26 outils

Voici une sélection de ce que le serveur MCP de DocPlatform expose — la référence complète des 26 outils se trouve sur la [page MCP](/mcp/). Chaque outil porte l'espace de noms `docplatform_*`, de sorte qu'il n'entre jamais en collision avec d'autres serveurs MCP dans votre client.

### Opérations de lecture

- **`docplatform_search`** — Recherche plein texte dans le workspace, avec correspondance floue et résultats classés par pertinence. Un agent IA l'utilise pour trouver la page décrivant une fonctionnalité spécifique avant de vérifier si elle est toujours exacte.

- **`docplatform_read_page`** — Récupère le contenu complet d'une page spécifique par chemin : contenu markdown plus métadonnées.

- **`docplatform_get_context`** — Le cheval de bataille du RAG : renvoie une page avec son parent, ses pages sœurs et les cibles de ses wikilinks en un seul appel — l'agent obtient le contexte environnant sans cinq allers-retours.

- **`docplatform_list_pages`** / **`docplatform_get_tree`** — Énumèrent les pages d'un workspace et son arborescence de navigation. Utile pour les agents IA effectuant des audits en masse.

### Opérations d'écriture

- **`docplatform_write_page`** — Écrit une page : la crée si elle n'existe pas, la met à jour sinon. La page est indexée pour la recherche et, avec la synchronisation git configurée, commitée dans git.

- **`docplatform_update_page`** — Modifie le contenu d'une page existante (échoue plutôt que de créer — pour les cas où la page doit déjà exister).

- **`docplatform_move_page`** — Déplace une page vers un nouveau chemin dans l'arborescence.

- **`docplatform_delete_page`** — Supprime une page.

### Opérations d'analyse

- **`docplatform_validate_links`** — Vérifie les liens internes et les wikilinks. Renvoie les cibles cassées avec leurs pages sources. Un agent IA peut exécuter cela après une restructuration pour détecter les références mortes.

- **`docplatform_quality_scan`** — Analyse le contenu à la recherche de problèmes de qualité — la matière première d'un rapport d'audit généré par un agent.

### Opérations de collaboration

- **`docplatform_get_activity`** — Le fil d'activité récente : qui a changé quoi, et quand. Le point de départ de l'analyse d'obsolescence.

- **`docplatform_list_comments`** / **`docplatform_add_comment`** — Lire et rejoindre les discussions de page, pour qu'un agent puisse signaler une trouvaille directement sur la page concernée.

## Workflows pratiques

Ces outils ne sont pas théoriques. Voici comment les équipes les utilisent aujourd'hui.

### Détection de documentation obsolète

Une exécution planifiée de l'agent (un cron job pilotant un assistant connecté via MCP) :

```
1. L'agent appelle docplatform_get_tree pour énumérer toutes les pages de documentation
2. Appelle docplatform_get_activity pour voir ce qui a changé récemment — les pages
   sans activité dont le domaine a continué d'évoluer sont des candidates
3. Pour chaque candidate, appelle docplatform_read_page et compare le contenu
   au code actuel (l'agent a aussi accès au dépôt)
4. Les trouvailles sont signalées avec docplatform_add_comment sur la page
   concernée — un humain examine et décide
```

Cela transforme la maintenance de la documentation d'un exercice trimestriel en un processus continu.

### Mises à jour de documentation déclenchées par les PR

Quand une pull request modifie une API publique :

```
1. Le pipeline CI extrait le diff
2. L'agent IA appelle docplatform_search pour trouver les pages référençant l'API modifiée
3. L'agent lit chaque correspondance avec docplatform_read_page et rédige la mise à jour
4. Avec la synchronisation git configurée, la modification de l'agent via
   docplatform_write_page devient un commit — révisable dans le même cycle de PR
   que la modification de code
```

Plus de « créer un ticket de suivi pour mettre à jour la doc ». La mise à jour de documentation fait partie du même workflow.

### Documentation de nouvelles fonctionnalités

Quand une fonctionnalité est mergée sans documentation (ça arrive) :

```
1. L'agent détecte de nouvelles fonctions/endpoints exportés sans page de doc
   correspondante (docplatform_search ne renvoie rien pour les nouveaux noms)
2. L'agent appelle docplatform_write_page avec un squelette : signature de fonction,
   descriptions des paramètres, un exemple placeholder
3. Vient ensuite l'étoffement humain — le brouillon est suivi dans l'historique
   de la page et, via la synchronisation git, révisable comme commit
```

L'humain écrit toujours le narratif. Mais le squelette — les signatures de fonctions exactes, les types de paramètres, les valeurs de retour — vient directement du code. Pas d'erreurs de copier-coller, pas d'oubli de mise à jour quand la signature change.

## Ce que ce n'est PAS

Soyons clairs sur les limites :

**Ce n'est pas « l'IA écrit votre documentation ».** La documentation générée par l'IA jamais révisée par un humain est pire que pas de documentation. Elle est faussement confiante, formulée de manière générique, et apprend aux gens à se méfier de votre documentation. Les outils MCP créent des brouillons et des suggestions — les humains révisent et approuvent.

**Ce n'est pas un remplacement des rédacteurs techniques.** Une bonne documentation nécessite du jugement : quoi expliquer, quoi omettre, dans quel ordre présenter les concepts, comment écrire un exemple qui aide réellement. L'IA n'a pas ce jugement. Elle a de la reconnaissance de patterns.

**Ce n'est pas de la magie.** La détection d'obsolescence fonctionne parce que les pages de documentation et les fichiers de code peuvent être liés via des conventions de chemin et la structure des dépôts. Si votre documentation et votre code n'ont aucune structure de relation, l'agent ne peut pas en déduire une.

Ce que c'EST : un système de surveillance de la qualité documentaire. Il observe, signale, suggère. Les humains décident.

## Pourquoi c'est important maintenant

Trois choses ont convergé pour rendre cela possible :

**La standardisation MCP.** Avant MCP, chaque outil IA avait besoin d'intégrations personnalisées. Maintenant il y a un protocole unique. Claude, Cursor, VS Code avec Copilot — ils parlent tous MCP. Construisez une intégration, elle fonctionne partout.

**Des modèles IA capables de raisonner sur le code.** Les modèles actuels peuvent lire un diff de code et comprendre ce qui a changé sémantiquement — pas seulement syntaxiquement. « Cette fonction accepte maintenant un paramètre optionnel `timeout` » est quelque chose qu'un modèle peut extraire de manière fiable d'un diff.

**Des plateformes de documentation qui stockent le contenu comme du code.** Du markdown dans des dépôts git signifie que les agents IA peuvent lire et écrire de la documentation en utilisant les mêmes outils qu'ils utilisent pour le code. Pas d'API propriétaires, pas de scraping d'écran.

DocPlatform se situe à l'intersection des trois. Contenu dans git (lisible par machine), serveur MCP intégré (accès structuré aux outils), et outillage conscient du code (lien entre documentation et codebase).

## Pour commencer

Le serveur MCP est inclus dans chaque installation DocPlatform. Créez une clé API (**Workspace Settings → API Keys**), puis pointez votre client IA vers le binaire `docplatform`. Dans Claude Desktop, ajoutez à `claude_desktop_config.json` :

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

Pour les installations distantes, il existe aussi un transport Streamable HTTP (`docplatform mcp-server`, servant `/mcp` sur le port 8081 par défaut). Pour le guide de configuration complet, incluant l'authentification et le scoping par workspace, consultez la [documentation MCP](/mcp/).

Si vous voulez voir comment les outils MCP fonctionnent en pratique, notre article précédent sur [l'utilisation de MCP avec la documentation](/blog/mcp-documentation-guide/) détaille des exemples spécifiques.

L'avenir de la documentation n'est pas l'IA qui remplace les rédacteurs. C'est l'IA qui maintient les lumières allumées — détectant l'obsolescence, signalant la dérive, maintenant les liens — pour que les rédacteurs puissent se concentrer sur le travail qui nécessite réellement le jugement humain.

[Installez DocPlatform](/install/) et connectez votre premier agent IA à votre documentation.
