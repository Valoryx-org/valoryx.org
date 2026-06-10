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

Une étude de 2023 par Zhi et al. a révélé que 68 % des pages de documentation dans les projets logiciels actifs contiennent au moins une incohérence factuelle avec le codebase actuel. Les problèmes les plus courants :

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

DocPlatform implémente les trois aujourd'hui, en utilisant le Model Context Protocol (MCP).

## MCP : le protocole

[MCP](https://modelcontextprotocol.io/) est un standard ouvert développé par Anthropic pour connecter les modèles IA aux outils externes et sources de données. Au lieu que chaque outil IA construise des intégrations personnalisées avec chaque plateforme, MCP définit une interface standard : des outils (actions que l'IA peut effectuer), des ressources (données que l'IA peut lire) et des prompts (templates pour les workflows courants).

DocPlatform intègre un serveur MCP — pas de plugins, pas de service séparé. Quand vous l'activez, tout client IA compatible MCP peut interagir avec votre documentation via 26 outils dédiés.

## Les 26 outils

Voici une sélection de ce que le serveur MCP de DocPlatform expose — la référence complète des 26 outils se trouve sur la [page MCP](/mcp/) :

### Opérations de lecture

- **`search_docs`** — Recherche plein texte dans toute la documentation. Renvoie les pages correspondantes avec des scores de pertinence et des extraits. Un agent IA l'utilise pour trouver la page décrivant une fonctionnalité spécifique avant de vérifier si elle est toujours exacte.

- **`get_page`** — Récupère le contenu complet d'une page spécifique par chemin. Renvoie le contenu markdown, les métadonnées (auteur, dernière modification, tags) et la position de la page dans l'arborescence de navigation.

- **`list_pages`** — Liste toutes les pages d'un workspace, avec filtrage optionnel par préfixe de chemin ou tag. Utile pour les agents IA effectuant des audits en masse.

- **`get_workspace_info`** — Métadonnées d'un workspace : nom, thème, connexion au dépôt git, statut de publication.

### Opérations d'écriture

- **`create_page`** — Crée une nouvelle page de documentation. Prend un chemin, un titre et du contenu markdown. La page est immédiatement indexée pour la recherche et commitée dans git.

- **`update_page`** — Modifie le contenu d'une page existante. L'agent IA fournit le nouveau markdown, et DocPlatform gère le versionnage, la réindexation de recherche et le commit git.

- **`move_page`** — Déplace une page dans l'arborescence de navigation. Gère les mises à jour de chemin et la création de redirections.

- **`delete_page`** — Supprime une page. La retire de l'index de recherche et commite la suppression dans git.

### Opérations d'analyse

- **`check_links`** — Vérifie tous les liens internes d'une page ou d'un workspace. Renvoie une liste des liens cassés avec la page source et le chemin cible. Un agent IA peut exécuter cela après une restructuration pour détecter les références mortes.

- **`check_freshness`** — Compare les dates de dernière modification des pages avec les horodatages des commits git pour les sections de code qu'elles décrivent. Signale les pages qui n'ont pas été mises à jour depuis que leur code correspondant a changé.

- **`suggest_updates`** — Étant donné un diff de code (par exemple d'une PR récente), identifie les pages de documentation susceptibles de nécessiter une mise à jour et suggère des modifications spécifiques.

### Opérations de workflow

- **`create_review`** — Soumet une modification de documentation pour revue humaine. Crée un brouillon qui apparaît dans la file d'attente de revue, pas sur le site publié.

- **`get_review_status`** — Vérifie le statut d'une revue en cours.

## Workflows pratiques

Ces outils ne sont pas théoriques. Voici comment les équipes les utilisent aujourd'hui.

### Détection de documentation obsolète

Une tâche planifiée s'exécute chaque nuit :

```
1. L'agent IA appelle list_pages pour obtenir toutes les pages de documentation
2. Pour chaque page, appelle check_freshness pour comparer avec les modifications
   de code récentes
3. Les pages signalées comme obsolètes sont rapportées à l'équipe
4. Pour les cas à haute confiance, l'agent appelle suggest_updates avec le diff
   de code pertinent
5. Les suggestions passent par create_review — un humain approuve ou rejette
```

Cela transforme la maintenance de la documentation d'un exercice trimestriel en un processus continu. Les pages obsolètes sont détectées dans les 24 heures suivant la modification de code qui les a rendues obsolètes.

### Mises à jour de documentation déclenchées par les PR

Quand une pull request modifie une API publique :

```
1. Le pipeline CI extrait le diff
2. L'agent IA appelle search_docs pour trouver les pages référençant l'API modifiée
3. L'agent appelle suggest_updates avec le diff et les pages correspondantes
4. Si les modifications sont simples (renommage de paramètre, nouvelle option),
   l'agent appelle create_review avec la mise à jour proposée
5. La mise à jour de documentation est livrée dans le même cycle de PR que
   la modification de code
```

Plus de « créer un ticket de suivi pour mettre à jour la doc ». La mise à jour de documentation fait partie du même workflow.

### Documentation de nouvelles fonctionnalités

Quand une fonctionnalité est mergée sans documentation (ça arrive) :

```
1. L'agent détecte de nouvelles fonctions/endpoints exportés sans page de doc
   correspondante
2. L'agent appelle create_page avec un squelette : signature de fonction,
   descriptions des paramètres, un exemple placeholder
3. Crée une revue pour qu'un humain étoffe l'explication et ajoute des exemples
   réels
```

L'humain écrit toujours le narratif. Mais le squelette — les signatures de fonctions exactes, les types de paramètres, les valeurs de retour — vient directement du code. Pas d'erreurs de copier-coller, pas d'oubli de mise à jour quand la signature change.

## Ce que ce n'est PAS

Soyons clairs sur les limites :

**Ce n'est pas « l'IA écrit votre documentation ».** La documentation générée par l'IA jamais révisée par un humain est pire que pas de documentation. Elle est faussement confiante, formulée de manière générique, et apprend aux gens à se méfier de votre documentation. Les outils MCP créent des brouillons et des suggestions — les humains révisent et approuvent.

**Ce n'est pas un remplacement des rédacteurs techniques.** Une bonne documentation nécessite du jugement : quoi expliquer, quoi omettre, dans quel ordre présenter les concepts, comment écrire un exemple qui aide réellement. L'IA n'a pas ce jugement. Elle a de la reconnaissance de patterns.

**Ce n'est pas de la magie.** L'outil `check_freshness` fonctionne parce que les pages de documentation et les fichiers de code peuvent être liés via des conventions de chemin et des métadonnées explicites. Si votre documentation et votre code n'ont aucune structure de relation, l'outil ne peut pas en déduire une.

Ce que c'EST : un système de surveillance de la qualité documentaire. Il observe, signale, suggère. Les humains décident.

## Pourquoi c'est important maintenant

Trois choses ont convergé pour rendre cela possible :

**La standardisation MCP.** Avant MCP, chaque outil IA avait besoin d'intégrations personnalisées. Maintenant il y a un protocole unique. Claude, Cursor, VS Code avec Copilot — ils parlent tous MCP. Construisez une intégration, elle fonctionne partout.

**Des modèles IA capables de raisonner sur le code.** Les modèles actuels peuvent lire un diff de code et comprendre ce qui a changé sémantiquement — pas seulement syntaxiquement. « Cette fonction accepte maintenant un paramètre optionnel `timeout` » est quelque chose qu'un modèle peut extraire de manière fiable d'un diff.

**Des plateformes de documentation qui stockent le contenu comme du code.** Du markdown dans des dépôts git signifie que les agents IA peuvent lire et écrire de la documentation en utilisant les mêmes outils qu'ils utilisent pour le code. Pas d'API propriétaires, pas de scraping d'écran.

DocPlatform se situe à l'intersection des trois. Contenu dans git (lisible par machine), serveur MCP intégré (accès structuré aux outils), et outillage conscient du code (lien entre documentation et codebase).

## Pour commencer

Le serveur MCP est inclus dans chaque installation DocPlatform — édition Community et Cloud.

Pour l'activer :

```bash
docplatform serve --mcp
```

Puis pointez votre client IA dessus. Dans Claude Desktop, ajoutez à votre configuration MCP :

```json
{
  "mcpServers": {
    "docplatform": {
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

Pour le guide de configuration complet, incluant l'authentification et le scoping par workspace, consultez la [documentation MCP](/mcp/).

Si vous voulez voir comment les outils MCP fonctionnent en pratique, notre article précédent sur [l'utilisation de MCP avec la documentation](/blog/mcp-documentation-guide/) détaille des exemples spécifiques.

L'avenir de la documentation n'est pas l'IA qui remplace les rédacteurs. C'est l'IA qui maintient les lumières allumées — détectant l'obsolescence, signalant la dérive, maintenant les liens — pour que les rédacteurs puissent se concentrer sur le travail qui nécessite réellement le jugement humain.

[Installez DocPlatform](/install/) et connectez votre premier agent IA à votre documentation.
