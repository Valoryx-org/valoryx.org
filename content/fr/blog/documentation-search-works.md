---
title: "Comment fonctionne réellement la recherche documentaire"
description: "La plupart des outils de documentation utilisent une correspondance par mots-clés basique ou nécessitent Elasticsearch. DocPlatform embarque Bleve pour la recherche plein texte avec racinisation et correspondance floue — sans service supplémentaire."
date: "2026-04-02"
author: "Valoryx Team"
tags: ["search", "architecture", "documentation"]
---

Vous tapez une requête dans la barre de recherche de votre documentation. Des résultats apparaissent. Mais que s'est-il passé entre la frappe et les résultats ? Pour la plupart des plateformes de documentation, la réponse est soit « pas grand-chose » (correspondance basique par mots-clés qui manque des résultats évidents) soit « beaucoup d'infrastructure » (un cluster Elasticsearch que votre équipe ops doit maintenir).

Il existe un juste milieu que la plupart des équipes ignorent : la recherche plein texte embarquée. DocPlatform utilise [Bleve](https://blevesearch.com/), une bibliothèque de recherche écrite en Go, compilée directement dans le binaire. Pas de services externes, pas d'appels réseau, pas de cluster à gérer — mais avec les fonctionnalités dont vous avez réellement besoin : racinisation, correspondance floue, boosting par champ et classement par pertinence.

Voici comment cela fonctionne, de la base au sommet.

## Pourquoi la correspondance par mots-clés échoue

L'implémentation de recherche la plus simple est `LIKE '%query%'` en SQL. C'est ce que vous obtenez quand un développeur ajoute la recherche après coup. Cela fonctionne pour les correspondances exactes mais échoue dans tous les autres cas :

- Chercher « install » ne trouve pas les pages contenant « installation » ou « installing »
- Chercher « authn » ne trouve pas les pages sur « authentication »
- Une faute de frappe comme « deploymnet » ne renvoie rien
- Chaque résultat a le même classement — une page intitulée « Installation Guide » est classée comme une page qui mentionne « install » une seule fois dans le pied de page

Certaines plateformes améliorent cela avec l'extension FTS5 de SQLite, qui ajoute la tokenisation et un classement basique. C'est un progrès, mais il manque toujours la racinisation, la correspondance floue et la possibilité de booster certains champs (comme les titres) par rapport aux autres.

## Ce que fait réellement la recherche plein texte

Un moteur de recherche approprié traite le texte en deux phases : l'indexation (quand le contenu est écrit) et l'interrogation (quand quelqu'un cherche). Les deux phases font plus de travail que vous ne le pensez.

### Indexation : ce qui se passe quand vous sauvegardez une page

Quand vous créez ou mettez à jour une page dans DocPlatform, le contenu passe par un pipeline d'analyse avant d'être indexé :

**1. Tokenisation** — Le texte est découpé en termes individuels. « Getting started with DocPlatform » devient `["getting", "started", "with", "docplatform"]`.

**2. Mise en minuscules** — Tous les tokens sont normalisés en minuscules. « DocPlatform » et « docplatform » correspondent.

**3. Suppression des mots vides** — Les mots courants comme « the », « is », « with », « a » sont supprimés. Ils apparaissent dans presque tous les documents et n'aident pas à distinguer les résultats pertinents.

**4. Racinisation** — Les mots sont réduits à leur forme racine. « installing », « installation » et « installed » deviennent tous « instal ». Cela signifie qu'une recherche sur n'importe lequel de ces mots trouve tous les autres.

**5. Séparation par champ** — Différentes parties du document sont indexées séparément. Le titre, le corps, les tags et le chemin ont chacun leur propre champ dans l'index. Cela permet le boosting par champ au moment de la requête.

L'index résultant est une structure de données appelée index inversé — une correspondance de chaque terme vers la liste des documents qui le contiennent, avec des informations de position (où dans le document le terme apparaît et à quelle fréquence).

```
"instal"     → [doc_3 (title, pos:0), doc_7 (body, pos:45), doc_12 (body, pos:102)]
"deploy"     → [doc_3 (body, pos:23), doc_5 (title, pos:0)]
"kubernetes" → [doc_5 (body, pos:15), doc_5 (body, pos:89)]
```

### Interrogation : ce qui se passe quand vous cherchez

Quand un utilisateur tape une requête, le moteur de recherche exécute le même pipeline d'analyse sur le texte de la requête (tokeniser, mettre en minuscules, raciniser), puis recherche chaque terme dans l'index inversé.

Mais la vraie valeur réside dans le classement. Toutes les correspondances ne sont pas égales. Bleve utilise une variante de TF-IDF (fréquence du terme, fréquence inverse de document) combinée avec le boosting par champ pour produire un score de pertinence :

- **Fréquence du terme :** Une page qui mentionne « deployment » 10 fois est probablement plus pertinente qu'une qui le mentionne une seule fois.
- **Fréquence inverse de document :** Un terme qui apparaît dans seulement 3 documents sur 500 est plus distinctif (et plus utile pour le classement) qu'un terme qui apparaît dans 400 documents.
- **Boost par champ :** Une correspondance dans le titre vaut plus qu'une correspondance dans le corps. Dans DocPlatform, les correspondances de titre reçoivent un boost de 3x, les correspondances de tags 2x, et les correspondances de corps 1x.

La formule produit un score numérique pour chaque document correspondant, et les résultats sont renvoyés triés par score.

## Correspondance floue : gérer les fautes de frappe

Les vrais utilisateurs font des fautes de frappe. « Kuberntes » au lieu de « Kubernetes ». « Authentcation » au lieu de « Authentication ». La recherche basique ne renvoie rien pour ces requêtes.

Bleve prend en charge la correspondance floue en utilisant la distance d'édition (distance de Levenshtein). Un terme de requête correspond à un terme de document s'ils diffèrent de N opérations de caractères ou moins (insertions, suppressions, substitutions). DocPlatform utilise une distance d'édition de 1 par défaut — suffisant pour détecter les fautes de frappe d'un seul caractère sans produire trop de faux positifs.

```
Requête : "authentcation"
Distance d'édition 1 : correspond à "authentication" (un 'i' manquant)
Résultats : tous les documents contenant "authentication"
```

Cela se produit de manière transparente. Les utilisateurs n'ont pas besoin de connaître la correspondance floue ni de configurer quoi que ce soit. Ils cherchent et obtiennent des résultats même quand ils font des fautes.

## Comment DocPlatform maintient l'index synchronisé

La partie délicate de la recherche embarquée n'est pas la recherche elle-même — c'est de maintenir l'index cohérent avec le contenu. DocPlatform a deux sources de contenu : l'éditeur web et git. Les deux peuvent créer, mettre à jour et supprimer des pages.

Voici le flux d'indexation :

**Sauvegarde depuis l'éditeur web :** L'utilisateur clique sur sauvegarder → le contenu est écrit dans la base de données → l'indexeur de recherche met à jour l'index Bleve → le moteur de synchronisation git commite la modification.

**Push git reçu :** Le webhook git se déclenche → le moteur de synchronisation tire les modifications → les pages nouvelles/modifiées sont écrites dans la base de données → l'indexeur de recherche met à jour l'index Bleve.

**Opérations en masse :** Quand vous importez un dépôt avec des centaines de fichiers markdown, l'indexeur les traite par lots. Un import de 500 pages prend environ 3 secondes pour être entièrement indexé sur du matériel modeste.

**Suppressions :** Quand une page est supprimée (depuis l'interface web ou git), le document correspondant est retiré de l'index Bleve. Pas de résultats de recherche orphelins.

Le détail important : l'indexation est synchrone avec l'opération d'écriture. Quand la sauvegarde/synchronisation se termine, l'index de recherche est déjà mis à jour. Il n'y a pas de délai « en attente de réindexation ». Cela est possible parce que Bleve tourne dans le même processus — il n'y a pas de saut réseau vers un cluster Elasticsearch séparé.

Pour en savoir plus sur le fonctionnement du moteur de synchronisation, consultez notre article sur [pourquoi la synchronisation git casse](/blog/why-git-sync-breaks/) et le pattern Content Ledger qui résout le problème.

## Comparaison : recherche embarquée vs. externe

| Capacité | SQL LIKE | SQLite FTS5 | Bleve (embarqué) | Elasticsearch |
|---|---|---|---|---|
| Tokenisation | Non | Oui | Oui | Oui |
| Racinisation | Non | Limitée | Oui | Oui |
| Correspondance floue | Non | Non | Oui | Oui |
| Boosting par champ | Non | Non | Oui | Oui |
| Classement par pertinence | Non | Basique | TF-IDF | BM25 |
| Service supplémentaire | Non | Non | Non | Oui |
| Surcoût mémoire | Aucun | ~1 Mo | ~10 Mo | 1-4 Go (JVM) |
| Complexité opérationnelle | Aucune | Aucune | Aucune | Élevée |

Elasticsearch gagne sur les fonctionnalités avancées : agrégations, requêtes sur documents imbriqués, analyseurs personnalisés, recherche distribuée sur des clusters. Si vous construisez un produit de recherche, vous en avez probablement besoin.

Mais pour la recherche documentaire — où le corpus est de milliers de pages, pas de millions d'enregistrements — Bleve embarqué couvre les besoins avec zéro surcoût opérationnel. Vous n'avez pas besoin d'un cluster séparé pour rechercher dans votre documentation.

Comme nous l'avons couvert dans [l'article sur l'architecture du binaire unique](/blog/single-binary-architecture/), garder tout dans un seul processus élimine toute une classe de problèmes opérationnels.

## Ce que les utilisateurs recherchent réellement

Nous avons construit notre configuration de recherche autour de la façon dont les gens recherchent réellement dans la documentation :

**Noms de fonctionnalités exacts :** « RBAC », « WebAuthn », « git sync » — ceux-ci doivent correspondre précisément dans les titres et les tags.

**Requêtes conceptuelles :** « comment configurer les permissions » — celles-ci reposent sur la racinisation et la correspondance dans le corps du texte.

**Rappel partiel :** « cette page à propos du déploiement... » — la correspondance floue et le boosting des titres aident à faire remonter le bon résultat même avec des requêtes incomplètes.

**Messages d'erreur :** Les utilisateurs collent des messages d'erreur dans la recherche. Ceux-ci bénéficient de la correspondance exacte avec de longues séquences de tokens.

La configuration par défaut gère bien tous ces cas. Aucun réglage nécessaire.

## Essayez-le

Si vous voulez voir cela en action, [installez DocPlatform](/install/) et créez quelques pages. La barre de recherche du site de documentation publié utilise exactement le système décrit ici. Tapez une requête, faites une faute de frappe volontairement, et regardez la recherche trouver quand même ce dont vous avez besoin.

L'édition Community inclut toutes les capacités de recherche — pas de restrictions de fonctionnalités, pas de « passez à la version supérieure pour une meilleure recherche ». Le [guide de configuration de la recherche](/docs/guides/search/) couvre les détails de personnalisation du comportement de recherche si vous en avez besoin.
