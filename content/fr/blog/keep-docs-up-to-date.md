---
title: "Comment garder la documentation à jour"
description: "La documentation devient obsolète parce que sa mise à jour est déconnectée des modifications de code. Trois approches qui fonctionnent : synchronisation git, revue assistée par MCP et workflows de PR."
date: "2026-03-26"
author: "Valoryx Team"
tags: ["documentation", "maintenance", "ai", "git"]
---

Chaque équipe d'ingénierie a le même problème de documentation. Quelqu'un rédige une documentation complète lors d'un lancement. Six mois plus tard, l'API a changé, le format de configuration est différent, et trois pages référencent une fonctionnalité qui a été renommée. Personne n'a mis à jour la documentation parce que mettre à jour la documentation est une tâche séparée de l'écriture du code, et les tâches séparées sont oubliées.

Le conseil habituel — « faites de la documentation une partie de votre culture » — ne fonctionne pas. La culture ne survit pas à la pression des deadlines. Ce qui fonctionne, c'est d'intégrer les mises à jour de documentation dans les workflows existants pour qu'elles se produisent automatiquement ou avec un minimum de friction.

Voici trois approches qui réduisent réellement l'obsolescence de la documentation, chacune ciblant une partie différente du problème.

## Approche 1 : Synchronisation Git — la doc change avec le code

La façon la plus fiable de garder la documentation à jour est de la stocker dans le même dépôt que le code qu'elle décrit, ou dans un dépôt connecté qui se synchronise de manière bidirectionnelle.

Quand la documentation vit dans git, vous pouvez :

- **Exiger des mises à jour de doc dans les PR.** Ajoutez un check CI ou une règle de revue : si du code dans `/api/` change, la PR doit aussi toucher des fichiers dans `/docs/api/`. Cela ne garantit pas la qualité, mais cela garantit que quelqu'un a au moins regardé la documentation concernée.

- **Utiliser `git log` pour détecter la dérive.** Comparez les dates de dernière modification des fichiers de code et de leurs pages de documentation correspondantes. Si `auth_handler.go` a été mis à jour il y a 3 mois mais que `docs/authentication.md` n'a pas changé depuis 8 mois, c'est un signal d'obsolescence.

- **Réviser la doc dans le même diff.** Quand un développeur modifie le fonctionnement de la pagination, le relecteur voit à la fois la modification de code et la mise à jour de documentation dans une seule pull request. Le contexte est préservé. Le relecteur peut vérifier que la documentation correspond à l'implémentation.

Le défi avec la documentation basée sur git est que tout le monde dans une équipe de documentation n'utilise pas git. Les rédacteurs techniques, les product managers et les ingénieurs support préfèrent souvent un éditeur web. C'est là que la [synchronisation bidirectionnelle git](/docs/guides/git-integration/) compte — elle permet aux utilisateurs de l'éditeur web et aux utilisateurs git de travailler sur le même contenu sans que l'un casse le workflow de l'autre.

Le pattern Content Ledger de Valoryx gère cela en suivant chaque modification quelle que soit son origine (interface web, push git, API, outil MCP) et en réconciliant les changements automatiquement. Consultez [Comment fonctionne la synchronisation bidirectionnelle Git](/blog/bidirectional-git-sync/) pour les détails techniques.

## Approche 2 : Revue assistée par MCP — l'IA signale le contenu obsolète

Les audits manuels de documentation sont complets mais rares. Personne n'a le temps de lire chaque page trimestriellement et de la vérifier par rapport au codebase actuel. Les assistants IA avec un accès structuré à votre documentation peuvent le faire en continu.

Avec le [Model Context Protocol (MCP)](/mcp/), vous pouvez connecter un assistant IA à votre instance de documentation et exécuter des audits ciblés. Voici à quoi cela ressemble en pratique.

### Trouver les pages qui référencent des endpoints dépréciés

```
Prompt : "Recherche dans toutes les pages les références à /api/v1/ —
nous avons migré vers /api/v2/ le mois dernier. Liste chaque page qui
mentionne encore v1."
```

L'assistant appelle l'outil MCP `docplatform_search`, trouve chaque occurrence et renvoie la liste des pages correspondantes. Ce qui prendrait 30 minutes de grep-et-lecture à un humain prend environ 10 secondes à l'IA.

### Détecter la dérive terminologique

```
Prompt : "Trouve toutes les pages qui utilisent le terme 'workspace group'.
Nous avons renommé cela en 'organization' dans la v3.2. Liste-les."
```

Même outil, requête différente. L'assistant trouve chaque instance de terminologie obsolète. Vous révisez la liste et décidez quelles pages mettre à jour.

### Générer un rapport d'obsolescence

```
Prompt : "Quelles pages du workspace API Reference ne montrent aucune
activité récente ? Liste les plus inactives en premier."
```

L'assistant récupère le fil d'activité récente avec `docplatform_get_activity` et le croise avec l'arborescence complète des pages de `docplatform_get_tree` — les pages sans modifications récentes sont vos candidates à l'obsolescence.

### Effectuer les mises à jour

Une fois le contenu obsolète identifié, l'IA peut rédiger des mises à jour :

```
Prompt : "Lis le guide d'authentification actuel. L'endpoint de connexion
accepte maintenant les passkeys en plus des mots de passe. Mets à jour
le guide pour couvrir les deux méthodes, en gardant la structure existante."
```

L'assistant lit la page via `docplatform_read_page`, rédige la mise à jour et l'applique via `docplatform_update_page`. La modification apparaît dans l'historique des révisions et, si la synchronisation git est configurée, apparaît comme un commit que vous pouvez réviser dans une pull request.

L'insight clé est que [MCP fait de l'IA un participant dans votre workflow documentaire](/blog/mcp-documentation-guide/), pas un générateur de texte déconnecté. Elle lit votre contenu réel, effectue des modifications via le même système que votre équipe utilise, et laisse une piste d'audit.

## Approche 3 : Revues de documentation basées sur les PR

La troisième approche est organisationnelle : utiliser le même processus de revue pour la documentation que pour le code.

### La PR de revue documentaire

Quand une fonctionnalité est livrée, créez une tâche de suivi : « Mettre à jour la doc pour la fonctionnalité X ». Cette tâche aboutit à une pull request qui :

1. Met à jour les pages de documentation concernées
2. Est révisée par quelqu'un qui comprend la fonctionnalité
3. Passe par le même pipeline CI que les modifications de code

Cela fonctionne parce que ce n'est pas un nouveau processus. Votre équipe révise déjà des PR. Ajouter les mises à jour de documentation au même workflow signifie qu'elles reçoivent la même attention.

### Vérifications automatisées d'obsolescence en CI

Vous pouvez automatiser la détection d'obsolescence dans votre pipeline CI. Une approche simple :

```bash
#!/bin/bash
# Trouver les docs non mises à jour depuis 90 jours
STALE_THRESHOLD=$(date -d '90 days ago' +%s)

for doc in docs/**/*.md; do
  LAST_MODIFIED=$(git log -1 --format="%ct" -- "$doc")
  if [ "$LAST_MODIFIED" -lt "$STALE_THRESHOLD" ]; then
    echo "STALE: $doc (last updated $(git log -1 --format='%ci' -- "$doc"))"
  fi
done
```

Exécutez cela dans le CI chaque semaine. Si des documents obsolètes sont trouvés, créez automatiquement une issue. Cela transforme « la doc est peut-être obsolète » d'une vague préoccupation en une tâche concrète et suivie.

### Rotation de revue

Assignez la revue de documentation à un planning tournant, de la même manière que vous assignez les rotations d'astreinte. Chaque semaine, une personne révise 5 à 10 pages. Pas tout le site — juste une tranche. Sur un trimestre, l'ensemble de la documentation est révisé.

C'est un travail peu glamour. Mais c'est le seul moyen de détecter le type d'obsolescence que les outils automatisés manquent : des pages techniquement exactes mais mal organisées, des exemples utilisant des patterns dépréciés, des guides qui supposent un contexte que le lecteur n'a pas.

## Combiner les trois approches

Ces approches fonctionnent mieux ensemble :

- **La synchronisation git** détecte la dérive à la source — quand le code change, la doc est dans la même PR
- **La revue assistée par MCP** détecte ce que la synchronisation git manque — changements de terminologie, références dépréciées, pages obsolètes
- **Les revues basées sur les PR** détectent ce que l'IA manque — problèmes structurels, rédaction peu claire, contexte manquant

Un workflow hebdomadaire pratique :

1. **Lundi :** Exécutez un audit MCP des sections de documentation les plus critiques (référence API, guide de démarrage). Révisez et mergez les mises à jour.
2. **Pendant la semaine :** Exigez des mises à jour de documentation dans les PR de code qui touchent un comportement visible par l'utilisateur.
3. **Vendredi :** Le relecteur en rotation lit 5 à 10 pages, crée des issues pour tout ce qui nécessite attention.

Cela ne nécessite pas une équipe de documentation dédiée. Le travail est distribué parmi les personnes qui comprennent déjà le contenu. L'outillage — [synchronisation git](/docs/guides/git-integration/), [MCP](/mcp/), checks CI — réduit l'effort par personne à quelque chose de soutenable.

## Pour commencer

Si votre documentation est déjà obsolète, commencez par les pages les plus consultées. Le trafic documentaire est très asymétrique — une petite fraction des pages reçoit la majorité des visites. Corrigez celles-là en premier.

Puis mettez en place l'infrastructure pour prévenir l'obsolescence future :

1. [Installez Valoryx](/install/) et connectez votre documentation à un dépôt git
2. Configurez MCP pour votre assistant IA afin de pouvoir exécuter des audits à la demande
3. Ajoutez une vérification d'obsolescence à votre pipeline CI
4. Démarrez une rotation de revue légère

La documentation devient obsolète parce que la boucle de feedback entre les modifications de code et les mises à jour de documentation est cassée. La synchronisation git resserre la boucle à la source. MCP vous donne un outil d'audit rapide. Les revues basées sur les PR ajoutent le jugement humain. Ensemble, ils font de « garder la documentation à jour » un problème traitable plutôt qu'une bataille perdue.
