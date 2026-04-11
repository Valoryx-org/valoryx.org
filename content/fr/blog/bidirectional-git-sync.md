---
title: "Comment fonctionne la synchronisation bidirectionnelle Git"
description: "La plupart des outils de documentation prétendent intégrer git mais échouent sur les conflits. Voici comment le pattern Content Ledger rend la synchronisation bidirectionnelle fiable."
date: "2026-03-19"
author: "Valoryx Team"
tags: ["git-sync", "architecture", "documentation"]
---

Chaque plateforme de documentation avec une page d'intégration git fait la même promesse : votre documentation vit dans git, votre équipe édite dans le navigateur, et tout reste synchronisé. En pratique, la plupart de ces intégrations sont des miroirs unidirectionnels qui se cassent dès que deux personnes éditent depuis des directions différentes.

Nous avons écrit sur [pourquoi cela arrive](/blog/why-git-sync-breaks/) dans un article précédent. Celui-ci approfondit la solution : comment Valoryx implémente la synchronisation bidirectionnelle en utilisant le pattern Content Ledger, et pourquoi cette approche gère les scénarios qui cassent les autres outils.

## Le problème fondamental

Un éditeur web et un dépôt git ont des modèles de cohérence fondamentalement différents.

Dans un éditeur web, les sauvegardes sont immédiates et atomiques. Vous cliquez sur sauvegarder, le contenu est persisté, et quiconque charge la page voit votre version. Il n'y a pas de concept de « staging » ou de « commit » — l'écriture est la publication.

Dans git, les modifications sont regroupées en commits, les commits sont poussés vers un remote, et le remote doit être fetché et mergé par les autres participants. Il y a un délai inhérent entre « j'ai fait une modification » et « tout le monde voit ma modification ».

Quand vous combinez les deux modèles — un éditeur web et un dépôt git pointant vers le même contenu — vous créez une fenêtre où deux personnes peuvent faire des modifications conflictuelles sans le savoir. La personne A édite dans le navigateur. La personne B pousse un commit depuis VS Code. Ni l'une ni l'autre ne sait ce que fait l'autre jusqu'à ce que la synchronisation s'exécute, et alors quelque chose doit céder.

La plupart des plateformes gèrent cela en choisissant un gagnant : soit la base de données gagne toujours (Wiki.js), soit le dépôt git gagne toujours (la plupart des générateurs de sites statiques). Les deux approches perdent silencieusement des données.

## Le pattern Content Ledger

Le Content Ledger est un journal en ajout seul de chaque mutation de contenu, quelle que soit son origine. Pensez-y comme un write-ahead log dans une base de données, mais pour les modifications de documentation.

Chaque modification — qu'elle provienne de l'éditeur web, de l'API, d'un appel d'outil MCP ou d'un push git — est enregistrée comme une entrée de ledger avant d'être appliquée. Chaque entrée contient :

- **Horodatage** — quand la modification a été faite
- **Origine** — d'où elle provient (web, git, api, mcp)
- **Chemin de page** — quelle page est concernée
- **Opération** — création, mise à jour, déplacement, suppression
- **Hash du contenu** — SHA-256 du nouveau contenu
- **Hash parent** — SHA-256 du contenu sur lequel cette modification est basée

Le hash parent est l'innovation clé. Il crée une chaîne de causalité, similaire à la façon dont les [commits git référencent leurs commits parents](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects). Quand deux modifications ont le même hash parent mais des hash de contenu différents, vous avez un conflit — et vous le savez avant que l'une ou l'autre modification ne soit appliquée.

## Comment fonctionne la synchronisation : étape par étape

Voici ce qui se passe pendant un cycle de synchronisation. Valoryx exécute cela automatiquement sur un intervalle configurable (par défaut : 30 secondes) ou à la demande lorsqu'un utilisateur le déclenche.

### Étape 1 : Collecter les modifications en attente

Le moteur de synchronisation lit toutes les entrées de ledger depuis la dernière synchronisation réussie. Ce sont les modifications locales qui n'ont pas encore été poussées vers git.

### Étape 2 : Récupérer les modifications distantes

Le moteur exécute `git fetch` pour obtenir tout nouveau commit depuis le dépôt distant. Il compare ensuite le HEAD distant avec le pointeur de synchronisation local pour identifier les modifications entrantes.

### Étape 3 : Réconcilier

Pour chaque page qui a des modifications des deux côtés (entrées de ledger locales ET commits git distants), le moteur vérifie les hash parents :

- **Pas de chevauchement :** La modification locale est basée sur la même version que celle de git. Merge fast-forward — appliquer les deux modifications dans l'ordre.
- **Divergence, pas de conflit :** Les deux côtés ont modifié des pages différentes. Appliquer les deux ensembles de modifications indépendamment.
- **Divergence, même page :** Les deux côtés ont modifié la même page. C'est un vrai conflit.

### Étape 4 : Résolution des conflits

Quand un véritable conflit est détecté, Valoryx ne choisit pas silencieusement un gagnant. Au lieu de cela :

1. Les deux versions sont conservées dans le ledger
2. La page est marquée comme « en conflit » dans l'interface
3. Un diff entre les deux versions est affiché
4. Un humain choisit quelle version conserver, ou les merge manuellement

C'est le même modèle que `git merge` avec conflits — sauf que cela fonctionne via l'interface web, permettant aux éditeurs non techniques de résoudre les conflits sans apprendre les commandes git.

### Étape 5 : Commit et push

Après la réconciliation, les modifications locales sont commitées dans le dépôt git et poussées. Le message de commit inclut l'origine de chaque modification (édition web, appel API, etc.) afin que votre historique git vous indique non seulement ce qui a changé, mais comment.

## Ce que ça donne en pratique

Considérez ce scénario réel. Un développeur met à jour la documentation d'authentification API depuis VS Code et pousse vers le dépôt. Pendant ce temps, un rédacteur technique modifie l'introduction de la même page dans l'éditeur web Valoryx.

Avec un outil de synchronisation unidirectionnel, une modification écrase l'autre. Avec le Content Ledger :

1. Le push du développeur crée une modification distante (nouveau commit côté git)
2. La sauvegarde du rédacteur crée une entrée de ledger locale (nouvelle mutation côté web)
3. La synchronisation s'exécute, détecte que les deux modifications touchent la même page
4. Les hash parents divergent — c'est un vrai conflit
5. La page est signalée, les deux versions sont conservées
6. Le rédacteur voit une notification : « Cette page a un conflit de synchronisation » avec une vue diff
7. Le rédacteur merge les modifications (le développeur a corrigé un bloc de code, le rédacteur a réécrit l'introduction — les deux modifications sont valides)
8. La version mergée est commitée et poussée

Aucune perte de données. Aucun écrasement silencieux. Le merge s'est fait via une interface web, pas un terminal.

## Comparaison avec les approches unidirectionnelles

| Scénario | Unidirectionnel (BDD gagne) | Unidirectionnel (Git gagne) | Content Ledger |
|----------|-------------------|---------------------|---------------|
| Édition web + push git (même page) | Modification git perdue | Modification web perdue | Conflit surfacé, les deux conservées |
| Édition web + push git (pages différentes) | Fonctionne | Fonctionne | Fonctionne |
| Éditions web rapides | Fonctionne | Fonctionne | Fonctionne (regroupées en un seul commit) |
| Éditions git hors ligne, push en masse | Certaines modifications perdues | Fonctionne | Fonctionne |
| Merge de branche git dans main | Imprévisible | Fonctionne | Fonctionne (traite le commit de merge comme les autres) |
| Renommage/déplacement web + édition git | Incohérence de chemin, sync cassée | Incohérence de chemin, sync cassée | Le ledger suit les déplacements, réconcilie les chemins |

La dernière ligne est plus importante qu'il n'y paraît. Renommer ou déplacer une page dans une interface web pendant que quelqu'un édite l'ancien chemin dans git est l'un des cas limites les plus difficiles. La plupart des outils abandonnent à ce stade. Le Content Ledger suit explicitement les opérations de déplacement, il sait donc que `/docs/auth.md` est devenu `/docs/authentication.md` et peut appliquer la modification git entrante au bon nouveau chemin.

## Pourquoi ne pas utiliser Git directement ?

Si git est si central dans cette conception, pourquoi ne pas ignorer l'éditeur web et utiliser git directement ? Deux raisons :

Premièrement, tout le monde dans une équipe de documentation n'utilise pas git. Les product managers, les ingénieurs support et les rédacteurs techniques préfèrent souvent un éditeur web. Les forcer dans un workflow git crée de la friction et réduit les contributions.

Deuxièmement, git seul ne vous donne pas de documentation publiée. Vous avez toujours besoin d'une couche de rendu, d'indexation de recherche, de contrôle d'accès et d'une structure de navigation. Valoryx fournit tout cela tout en gardant git comme couche de stockage canonique.

Le Content Ledger fait le pont entre ces deux mondes. Les utilisateurs git travaillent dans git. Les utilisateurs web travaillent dans le navigateur. Les deux workflows sont de première classe, et le ledger les maintient cohérents.

## Configurer la synchronisation Git

Si vous souhaitez essayer avec votre propre dépôt :

1. [Installez Valoryx](/install/) — binaire unique, aucune dépendance externe
2. Créez un workspace et connectez-le à un dépôt git dans les paramètres du workspace
3. Configurez l'URL distante, la branche et l'intervalle de synchronisation
4. Commencez à éditer des deux côtés

Le [guide d'intégration git](/docs/guides/git-integration/) couvre la configuration complète, y compris la configuration des clés SSH, les stratégies de branches et le réglage de l'intervalle de synchronisation.

Pour les équipes qui gèrent déjà de la documentation dans des dépôts git, cela signifie que vous n'avez pas à choisir entre une bonne expérience d'édition et un workflow natif git. Le Content Ledger rend les deux possibles sans les compromis qui affligent toutes les autres approches que nous avons testées.
