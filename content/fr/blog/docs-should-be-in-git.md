---
title: "Votre documentation devrait être dans Git. Point."
description: "Le code vit dans git. L'infrastructure vit dans git. Pourquoi votre documentation vit-elle encore dans un wiki ? Un plaidoyer pour la documentation versionnée."
date: "2026-03-09"
author: "Valoryx Team"
tags: ["git", "documentation", "opinion"]
---

Voici un inventaire de ce qu'une équipe d'ingénierie typique conserve dans git :

- Code source de l'application
- Définitions d'infrastructure (Terraform, Pulumi, CloudFormation)
- Configurations de pipelines CI/CD
- Scripts de migration de base de données
- Spécifications API (OpenAPI, protobuf)
- Manifestes de déploiement (Kubernetes, Docker Compose)
- Templates de configuration d'environnement

Et voici ce qui vit habituellement en dehors de git :

- La documentation

C'est étrange. La documentation décrit le système. Elle change quand le système change. Elle nécessite de la revue, du versionnage, de l'attribution et la possibilité de revenir en arrière. Tous les autres artefacts partageant ces propriétés vivent dans git. Pas la documentation — et personne ne peut donner une bonne raison.

## Les excuses habituelles

### « Les non-techniciens doivent pouvoir éditer la doc »

C'est l'argument le plus courant pour garder la documentation dans Confluence ou Notion. Et il est valide — vous ne pouvez pas demander à un product manager d'apprendre le branching git pour corriger une faute de frappe. Mais ce n'est pas un argument contre git. C'est un argument pour un meilleur outillage par-dessus git.

Git est un backend de stockage et de versionnage. Rien n'oblige les humains à interagir directement avec lui. Un éditeur web peut créer des commits et pousser des modifications de la même manière qu'un pipeline CI. L'utilisateur écrit dans un navigateur ; le système gère les opérations git.

L'opposition « git vs. utilisateurs non techniques » est une fausse dichotomie. Vous pouvez avoir les deux.

### « La doc change trop souvent pour des PR »

Certaines équipes estiment que requérir des pull requests pour la documentation ralentirait la rédaction. Et si votre processus de PR exige deux relecteurs, un check CI et une merge queue — oui, c'est trop de friction pour corriger une faute de frappe.

Mais rien dans git n'impose un processus de revue lourd. Vous pouvez pousser directement sur main pour les modifications mineures et utiliser des branches pour les réécritures structurelles. L'important est que l'historique existe. Chaque modification est suivie, attribuée et réversible. Que vous révisiez chaque changement est une décision de processus, pas une contrainte d'outillage.

### « Notre plateforme de documentation ne supporte pas git »

C'était vrai autrefois et ça comptait. Confluence, Notion et la plupart des wikis stockent le contenu dans une base de données propriétaire sans réelle intégration git. L'export vers markdown est avec perte et unidirectionnel.

Mais c'est une limitation de produits spécifiques, pas une contrainte fondamentale. Des plateformes de documentation qui traitent git comme source de vérité — tout en fournissant un éditeur web pour la commodité — existent désormais. La technologie a rattrapé le besoin.

### « Le markdown est limité »

Critique juste pour certains types de contenu. Le markdown ne prend pas en charge nativement les tableaux complexes, les diagrammes intégrés ou les éléments interactifs. Mais pour 90 % de la documentation interne — guides, runbooks, décisions d'architecture, documentation API, matériaux d'onboarding — le markdown est plus que suffisant.

Et le markdown dans git vous donne quelque chose qu'aucun format propriétaire ne peut offrir : la portabilité. Si vous décidez de changer d'outil dans deux ans, votre contenu est constitué de fichiers texte brut dans un format standard. Essayez d'exporter cinq ans de contenu Confluence vers quelque chose d'utilisable.

## Ce que vous perdez sans Git

Si votre documentation vit en dehors de git, vous perdez des capacités que les ingénieurs considèrent comme acquises avec le code :

### Blame

Qui a écrit ce paragraphe affirmant que l'API prend en charge la pagination ? Quand ? En réponse à quoi ? Avec `git blame`, vous pouvez tracer chaque ligne jusqu'à son auteur, son horodatage et son message de commit. Dans un wiki, vous obtenez peut-être « dernière modification par Sarah, il y a 6 mois » — sans contexte sur le pourquoi.

### Branching

Vous réécrivez le guide de déploiement pour une nouvelle infrastructure. L'ancien guide doit rester exact jusqu'à ce que la migration soit terminée. Dans git, vous créez une branche. Les deux versions coexistent. Vous mergez quand la migration est terminée. Dans un wiki, vous maintenez deux pages (qui divergent inévitablement) ou vous éditez sur place en espérant que personne ne suive les instructions à moitié mises à jour.

### Modifications atomiques inter-dépôts

Les meilleures modifications de documentation accompagnent les modifications de code. Une PR qui ajoute un endpoint API devrait inclure la documentation de cet endpoint. Un commit qui déprécie une fonctionnalité devrait mettre à jour la documentation dans le même commit — ou au moins la même PR. Quand la documentation vit dans un wiki, ce couplage est impossible. Le code est livré, et quelqu'un crée un ticket pour « mettre à jour la doc » qui reste dans un backlog pendant des semaines.

### Diffing

Qu'est-ce qui a changé dans les dernières notes de version ? Montrez-moi le diff. Dans git, `git diff v1.4..v1.5 -- docs/` vous donne exactement ce qui a changé. Dans un wiki, vous cliquez page par page dans les historiques, en comparant le rendu et en espérant repérer chaque modification.

### Automatisation

Avec la documentation dans git, vous pouvez construire des automatisations :

```bash
# Trouver les docs non mises à jour depuis 90 jours
git log --all --diff-filter=M --name-only --since="90 days ago" -- docs/ \
  | sort -u > recently_modified.txt

# Comparer avec tous les fichiers de documentation
find docs/ -name "*.md" | sort > all_docs.txt

# Fichiers NON modifiés depuis 90 jours
comm -23 all_docs.txt recently_modified.txt
```

Essayez de faire ça avec un wiki. Vous devriez appeler une API, analyser des horodatages et gérer la pagination — si l'API expose les dates de modification.

## La vraie raison pour laquelle la doc n'est pas dans Git

Ce n'est pas technique. C'est historique. La documentation précède les pratiques DevOps modernes. Les wikis ont émergé au début des années 2000 quand « infrastructure as code » n'existait pas et que le contrôle de versions signifiait SVN. Le modèle wiki — éditer dans le navigateur, sauvegarder en base de données — avait du sens quand l'alternative était d'envoyer des documents Word par email.

Mais les pratiques d'ingénierie ont évolué. L'infrastructure est passée de serveurs configurés manuellement à du code déclaratif dans git. Le CI/CD est passé de jobs Jenkins configurés via une interface web à du pipeline-as-code en YAML. La configuration est passée de pages de paramètres applicatifs à des variables d'environnement et des fichiers de config dans des dépôts.

La documentation est le dernier bastion. Non pas parce qu'elle est différente, mais parce que l'outillage n'a pas suivi. Les générateurs de sites statiques ont résolu le problème « docs dans git » pour les développeurs mais ont exclu quiconque n'utilise pas un terminal. Les wikis ont résolu le problème « tout le monde peut écrire » mais ont abandonné le contrôle de versions. Aucun des deux n'a comblé le fossé — jusqu'à récemment.

## Ce à quoi ça ressemble quand c'est bien fait

Un workflow de documentation qui respecte git devrait ressembler à ceci :

1. Les rédacteurs créent et éditent du contenu via une interface web — pas de terminal requis
2. Chaque sauvegarde crée un commit git — automatiquement, de manière invisible
3. Les développeurs peuvent éditer le même contenu dans leur IDE et pousser vers le même dépôt
4. Les deux côtés restent synchronisés — pas de conflits, pas de merge manuel
5. Les pull requests fonctionnent pour la documentation de la même manière que pour le code
6. L'historique git complet est disponible : blame, diff, log, branch

Ce n'est pas hypothétique. Le [pattern Content Ledger](/blog/why-git-sync-breaks/) résout le problème de synchronisation. Les plateformes qui l'implémentent vous offrent une expérience d'édition type wiki avec un dépôt git comme backend.

Si vous construisez un nouveau workflow de documentation — ou si vous en reconstruisez un qui ne fonctionne pas — commencez avec git comme fondation. Choisissez un outillage qui traite le dépôt comme la source de vérité, pas comme une cible d'export. Votre futur vous, auditant ce qui a changé et pourquoi, sera content que l'historique existe.

Comme [la documentation Git elle-même le dit](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control) : le contrôle de versions enregistre les modifications apportées aux fichiers au fil du temps afin que vous puissiez rappeler des versions spécifiques plus tard. Cela s'applique à la documentation tout autant qu'au code. Peut-être même davantage — car le code a des tests pour détecter les régressions, mais la documentation n'a que la mémoire humaine.

Si votre documentation vaut la peine d'être écrite, elle vaut la peine d'être versionnée. Mettez-la dans git.

---

*Si vous voulez essayer une plateforme de documentation où git est la source de vérité — pas un ajout après coup — [DocPlatform](/install/) est gratuit et auto-hébergé. Un binaire, pas de base de données à gérer, synchronisation bidirectionnelle git intégrée.*
