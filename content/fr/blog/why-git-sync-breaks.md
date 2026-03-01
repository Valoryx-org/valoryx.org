---
title: "Pourquoi Tous les Outils de Docs Git Cassent la Synchronisation (Et Comment Nous l'Avons Résolu)"
description: "Chaque plateforme de documentation prétend offrir une intégration git. La plupart mentent. Voici ce qui se passe vraiment — et le pattern Content Ledger qui règle enfin le problème."
date: "2026-02-22"
author: "Équipe Valoryx"
tags: ["git-sync", "documentation", "architecture"]
---

Si vous maintenez de la documentation technique, vous avez probablement été brûlé par cette promesse : « Intégration git complète. » Vous connectez votre dépôt, faites quelques modifications dans l'interface web, poussez un commit depuis votre IDE — et tout s'effondre. Conflits de fusion. Modifications perdues. Pages qui reviennent silencieusement à leur état précédent. Un statut de synchronisation qui indique « à jour » pendant que votre contenu diverge.

Ce n'est pas un bug propre à un produit particulier. C'est un défaut de conception fondamental dans la façon dont la plupart des plateformes de documentation pensent git.

## Les Trois Façons dont la Sync Git Échoue

Après avoir étudié toutes les grandes plateformes de docs qui prétendent offrir une intégration git — GitBook, Wiki.js, Notion (via des tiers), Outline, BookStack — nous avons identifié trois patterns d'échec qui reviennent sans cesse.

### 1. Miroir Unidirectionnel, Pas une Vraie Sync

La plupart des plateformes traitent git comme une cible de sauvegarde, pas comme une source de vérité. Les modifications circulent de l'interface web vers git (sous forme de commits), mais les changements poussés vers git depuis un IDE ou un pipeline CI sont soit ignorés, soit génèrent des conflits.

La « Git Sync » de GitBook est l'exemple le plus visible. Elle fonctionne bien dans les cas simples — modifier dans le navigateur, voir le commit dans GitHub. Mais poussez une modification markdown depuis VS Code, et vous obtiendrez une notification de conflit de fusion qui nécessite une résolution manuelle dans leur interface. Pour les équipes où les développeurs éditent les docs en parallèle du code, cela casse entièrement le workflow.

### 2. La Base de Données en Premier, Git en Second

Wiki.js stocke tout le contenu dans une base de données (PostgreSQL, MySQL ou SQLite). Il propose la « synchronisation » git comme fonctionnalité optionnelle, mais la base de données est toujours la source canonique. Si la base de données et git divergent — ce qui arrive quand quelqu'un édite directement dans git — la base de données l'emporte.

Cela signifie que git n'est pas votre source de vérité. C'est un export en lecture seule. Vous ne pouvez pas faire `git clone` du dépôt, faire des modifications, pousser, et voir les résultats reflétés dans l'interface sans passer d'abord par la couche base de données. Pour les développeurs qui pensent en workflows natifs git, c'est rédhibitoire.

### 3. Résolution Destructrice des Conflits

Quand la sync se casse, la plupart des plateformes gèrent mal les conflits. Les approches courantes incluent l'écrasement silencieux d'une version (c'est généralement la version git qui perd), la création de pages dupliquées avec des horodatages ajoutés, ou simplement marquer la sync comme « échouée » en laissant l'utilisateur se débrouiller pour comprendre ce qui s'est passé.

Aucune de ces approches n'est acceptable pour de la documentation dont les équipes dépendent.

## Pourquoi C'est Difficile

La synchronisation bidirectionnelle entre une application web et un dépôt git est genuinement complexe. Le défi fondamental est qu'une interface web attend des écritures immédiates et atomiques (cliquer sur sauvegarder, le contenu est persisté), tandis que git opère sur des instantanés (commit, push, merge). Ces deux modèles créent une fenêtre temporelle où des modifications simultanées peuvent diverger.

Considérez ce scénario :

1. Alice modifie `getting-started.md` dans l'éditeur web
2. Bob modifie le même fichier dans VS Code et pousse vers main
3. Alice clique sur « Sauvegarder » — sa modification crée un commit
4. Il y a maintenant deux commits divergents sur la même branche

Dans un workflow git pur, cela produit un conflit de fusion. Mais une interface web ne peut pas afficher une boîte de dialogue de conflit de fusion — les utilisateurs s'attendent à ce que leur sauvegarde fonctionne simplement.

## Le Pattern Content Ledger

C'est le problème que nous avons entrepris de résoudre avec Valoryx. Notre approche s'appelle le **Content Ledger** — un moteur de synchronisation qui traite à la fois l'interface web et git comme des pairs égaux, avec un journal d'événements partagé qui empêche les conflits avant qu'ils se produisent.

Voici comment ça fonctionne :

**Chaque mutation est un événement.** Quand vous modifiez une page dans l'interface web, Valoryx n'écrit pas directement dans la base de données ni directement dans git. Il crée une entrée dans le ledger — un événement structuré qui indique « la page X a été modifiée, voici le diff. » Le ledger est en ajout uniquement et totalement ordonné.

**Les événements sont appliqués aux deux cibles.** Un worker en arrière-plan lit le ledger et applique chaque événement à la fois à la base de données (pour l'interface web) et au dépôt git (pour les utilisateurs en IDE). Comme les événements sont ordonnés, les deux cibles convergent vers le même état.

**Les git push deviennent des entrées dans le ledger.** Quand quelqu'un pousse vers le dépôt git distant, un webhook déclenche Valoryx pour lire les nouveaux commits, convertir chaque modification de fichier en une entrée dans le ledger, et l'appliquer. L'interface web se met à jour en quelques secondes.

**Les conflits sont impossibles par conception.** Comme toute mutation passe par le ledger, et que le ledger est strictement ordonné, il n'existe pas de fenêtre où deux écritures peuvent diverger. Si Alice et Bob modifient la même page simultanément, leurs modifications sont sérialisées dans le ledger — la seconde est appliquée par-dessus la première, comme des commits git séquentiels.

## Ce que Cela Signifie en Pratique

Avec le Content Ledger, vous pouvez :

- Modifier dans le navigateur, et le commit apparaît dans `git log` en quelques secondes
- Pousser depuis VS Code, et la modification apparaît dans l'interface web sans sync manuelle
- Exécuter des pipelines CI qui modifient les docs (références API auto-générées, par exemple) et voir les résultats dans l'éditeur web
- Annuler n'importe quelle modification avec `git revert` — l'interface web reflète le revert immédiatement

Il n'y a pas de « statut de synchronisation » à vérifier. Il n'y a pas d'interface de résolution de conflits. Il n'y a pas de divergence. Le dépôt git et l'interface web sont toujours en accord parce qu'ils partagent une seule source de vérité : le ledger.

## Essayez par Vous-Même

Valoryx est un binaire Go unique sans dépendance externe. Téléchargez-le, pointez-le vers un dépôt git, et constatez une synchronisation bidirectionnelle qui fonctionne vraiment. Pas de Docker requis, pas de base de données à configurer, pas de YAML à écrire.

Nous avons construit ceci parce que nous en avions assez des outils de documentation qui traitent git comme une réflexion après coup. Si vous ressentez la même chose, nous serions ravis d'avoir de vos nouvelles.
