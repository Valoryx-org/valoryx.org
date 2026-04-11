---
title: "Le vrai coût des plateformes de documentation"
description: "La tarification par utilisateur pénalise l'adoption de la documentation. Voici une comparaison du coût total de possession à 5, 15, 50 et 100 utilisateurs — avec des chiffres réels."
date: "2026-04-09"
author: "Valoryx Team"
tags: ["pricing", "comparison", "documentation"]
---

La tarification par utilisateur semble raisonnable à première vue. Cinq utilisateurs à 8 $/mois ? C'est 40 $. Votre équipe peut se permettre 40 $.

Mais la documentation est l'un de ces outils où le nombre de personnes qui *devraient* avoir accès ne cesse de croître. Les ingénieurs doivent écrire. Les product managers doivent relire. Le support doit consulter. Les nouveaux arrivants doivent lire et annoter. Soudain vous n'êtes plus à 5 postes — vous êtes à 50, et ces 8 $/poste « abordables » représentent 400 $/mois pour un outil qui stocke des fichiers texte.

La tarification par utilisateur pour la documentation crée un incitatif pervers : elle pénalise les entreprises qui laissent plus de personnes contribuer à la documentation. Les managers commencent à restreindre l'accès. Les gens partagent les mots de passe. La documentation devient le problème de quelqu'un d'autre. Et ensuite on se demande pourquoi la documentation est toujours obsolète.

## Les chiffres

Comparons le coût mensuel réel de quatre plateformes de documentation à différentes tailles d'équipe. Ce sont les prix catalogue début 2026.

| Utilisateurs | [GitBook](https://www.gitbook.com/pricing) (8 $/user) | Notion (10 $/user) | Confluence (6 $/user) | Valoryx Cloud | Valoryx CE |
|------:|------:|------:|------:|------:|------:|
| 5 | 40 $ | 50 $ | 30 $ | 29 $ | 0 $ |
| 15 | 120 $ | 150 $ | 90 $ | 29 $ | 0 $ |
| 50 | 400 $ | 500 $ | 300 $ | 29 $ | 0 $ |
| 100 | 800 $ | 1 000 $ | 600 $ | 29 $ | 0 $ |

Quelques précisions sur ces chiffres :

**GitBook** facture 8 $/utilisateur/mois sur le plan Plus. Le tier gratuit est limité à 1 espace avec des fonctionnalités basiques. La documentation publiée n'est disponible que sur les plans payants.

**Notion** facture 10 $/utilisateur/mois pour le plan Plus. Notion est un outil de workspace généraliste, pas une plateforme de documentation — il manque la documentation publiée, la synchronisation git et les fonctionnalités dédiées à la documentation. Mais beaucoup d'équipes l'utilisent pour la documentation, la comparaison de prix est donc pertinente.

**Confluence** facture 6,05 $/utilisateur/mois (Standard) pour le cloud. C'est le tarif actuel d'Atlassian pour 1-100 utilisateurs. La version Data Center (auto-hébergée) démarre à 27 000 $/an pour 500 utilisateurs.

**Valoryx Cloud** est à 29 $/mois forfaitaire pour le plan Team — 3 workspaces, 15 éditeurs, 150 pages. Pas par utilisateur. Le [plan Free](/pricing/) vous donne 1 workspace, 3 éditeurs, 50 pages à 0 $.

**Valoryx Community Edition** est à 0 $. Pour toujours. Tout est illimité. Vous l'hébergez vous-même.

## Le problème de la mise à l'échelle

Regardez la colonne à 5 utilisateurs. Chaque plateforme est abordable. GitBook à 40 $/mois, c'est moins qu'un déjeuner d'équipe. Personne ne va se battre pour 40 $.

Maintenant regardez la colonne à 100 utilisateurs. GitBook est à 800 $/mois — 9 600 $/an pour un outil qui stocke et affiche du markdown. À ce stade, vous êtes en revue budgétaire, quelqu'un demande « on a vraiment besoin de ça ? », et la réponse est généralement « limitons l'accès aux personnes qui écrivent vraiment de la doc ».

Cette décision — limiter l'accès — est le point où la qualité de la documentation meurt.

Une bonne documentation se produit quand tout le monde peut contribuer. L'ingénieur qui vient de debugger un problème de déploiement devrait pouvoir mettre à jour le guide de déploiement. L'agent support qui a trouvé un contournement devrait pouvoir l'ajouter à la page de dépannage. Le nouveau qui a galéré avec l'onboarding devrait pouvoir améliorer la documentation d'onboarding.

La tarification par utilisateur fait que chacune de ces contributions coûte 6-10 $/mois. Alors à la place, vous obtenez : « Envoyez un email à l'équipe documentation et demandez-leur de mettre à jour. » L'équipe documentation a un backlog. La mise à jour ne se fait jamais. La connaissance reste dans la tête de quelqu'un jusqu'à ce qu'il quitte l'entreprise.

## Coût total de possession

Le prix de l'abonnement mensuel n'est qu'une partie du coût. Le vrai TCO inclut :

### Coût d'infrastructure (auto-hébergé uniquement)

Si vous choisissez l'édition Community de Valoryx, vous avez besoin d'un serveur. Un Hetzner CX22 (2 vCPU, 4 Go RAM) coûte 3,99 EUR/mois. DocPlatform utilise ~100 Mo de RAM en charge normale. Ce serveur peut aussi faire tourner d'autres choses.

Coût annuel d'infrastructure pour l'auto-hébergement : **~50 $/an.**

### Temps d'administration

**Les plateformes SaaS** ne nécessitent presque pas de temps d'administration pour un usage basique, mais consomment des heures pour la configuration SSO, le provisionnement/déprovisionnement des utilisateurs, et la lutte avec des modèles de permissions qui ne correspondent pas à votre structure organisationnelle.

**DocPlatform auto-hébergé** nécessite une configuration initiale (30 minutes), des mises à jour occasionnelles (télécharger le nouveau binaire, redémarrer — 5 minutes), et une vérification des sauvegardes (automatisée, mais à vérifier mensuellement).

### Coût de migration

Le coût caché de toute plateforme est ce qui se passe quand vous voulez partir. L'export de Confluence est notoirement pénible — des années de contenu verrouillées dans un format de stockage propriétaire. GitBook exporte en markdown mais perd les métadonnées.

DocPlatform stocke tout en markdown dans un dépôt git. Votre contenu est toujours accessible en dehors de la plateforme, dans un format standard, avec l'historique complet des versions. Le coût de migration est zéro parce qu'il n'y a rien à migrer — votre contenu vit déjà dans git.

## L'argument du tarif forfaitaire

Valoryx Cloud utilise une tarification forfaitaire au lieu du par-utilisateur :

| Plan | Prix | Workspaces | Éditeurs | Pages |
|------|------:|------:|------:|------:|
| Free | 0 $/mois | 1 | 3 | 50 |
| Team | 29 $/mois | 3 | 15 | 150 |
| Business | Bientôt disponible | Plus | Plus | Plus |

Les limites portent sur les workspaces et les pages, pas sur les utilisateurs. Le plan Team à 29 $/mois prend en charge 15 éditeurs — sur n'importe quelle plateforme à tarification par utilisateur, 15 utilisateurs coûteraient 90-150 $/mois.

Plus important encore, les lecteurs sont gratuits. Si votre entreprise a 200 personnes qui ont besoin de lire la documentation mais seulement 15 qui l'écrivent, vous ne payez pas pour 200 postes. Vous payez pour le plan Team.

Cela aligne correctement les incitatifs : vous voulez que le plus de personnes possible lisent et contribuent à votre documentation. Le modèle de tarification ne devrait pas pénaliser cela.

## Quand le tarif par utilisateur a du sens

La tarification par utilisateur n'est pas toujours mauvaise. Pour les outils où chaque utilisateur génère un coût significatif (charges de calcul lourdes, applications gourmandes en stockage), facturer par utilisateur reflète une utilisation réelle des ressources.

Les plateformes de documentation n'ont pas cette caractéristique. Rendre du markdown est peu coûteux. Stocker du texte est peu coûteux. Le coût marginal d'ajouter le 51e utilisateur à une plateforme de documentation est approximativement zéro. Facturer 6-10 $/mois pour ce 51e utilisateur est un choix de modèle économique, pas un reflet des coûts.

## Le calcul de l'édition Community

Pour les équipes capables d'auto-héberger, l'édition Community change complètement le calcul :

| Dépense | Coût annuel |
|---|---:|
| Serveur (Hetzner CX22) | 50 $ |
| Nom de domaine | 12 $ |
| Certificat TLS (Let's Encrypt) | 0 $ |
| Licence DocPlatform CE | 0 $ |
| **Total** | **62 $/an** |

C'est 62 $/an pour des utilisateurs illimités, des pages illimitées, des workspaces illimités, la recherche plein texte, la synchronisation git, le RBAC, WebAuthn et l'intégration MCP. Pas de frais par utilisateur, pas de restrictions de fonctionnalités, pas de « contactez le commercial pour un tarif entreprise ».

À 100 utilisateurs, cela revient à 0,62 $/utilisateur/an contre 72-120 $/utilisateur/an pour les plateformes hébergées à tarification par utilisateur.

## Prendre la décision

Voici un cadre simple :

**Choisissez Valoryx Cloud (29 $/mois)** si vous ne voulez pas gérer d'infrastructure mais souhaitez une tarification forfaitaire. Adapté aux équipes petites à moyennes qui veulent une solution hébergée sans l'escalade des coûts par utilisateur.

**Choisissez l'édition Community Valoryx (0 $)** si votre équipe peut gérer un serveur Linux. Idéal pour les équipes qui tiennent à la souveraineté des données, veulent zéro coût récurrent, ou ont des exigences de conformité imposant l'auto-hébergement. Consultez le [guide d'installation](/install/).

**Choisissez une plateforme à tarification par utilisateur** si votre organisation a moins de 10 utilisateurs, que votre équipe n'écrit pas beaucoup de documentation, et que vous êtes déjà intégrés dans l'écosystème de ce fournisseur (par exemple Confluence si vous êtes all-in sur Atlassian).

**Ne choisissez pas en fonction du prix à 5 utilisateurs.** Choisissez en fonction du prix à 50 utilisateurs, parce que c'est là que vous allez. Les outils de documentation ont tendance à se répandre dans les organisations — si l'outil est bon, plus de gens veulent y accéder. Votre modèle de tarification devrait récompenser cela, pas le pénaliser.

Comparez tous les plans sur la [page de tarification](/pricing/) ou consultez la [page open source](/open-source/) pour la liste complète des fonctionnalités de l'édition Community.
