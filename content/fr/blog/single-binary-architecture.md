---
title: "Pourquoi nous livrons un binaire Go unique"
description: "DocPlatform est un binaire unique sans aucune dépendance. Pas de Docker, pas de Postgres, pas de Redis. Voici l'architecture derrière une installation en 30 secondes."
date: "2026-03-30"
author: "Valoryx Team"
tags: ["architecture", "golang", "self-hosted", "documentation"]
---

La plupart des plateformes de documentation sont livrées sous forme de stack. Vous obtenez une application Node.js, une base de données PostgreSQL, un cache Redis, un cluster Elasticsearch pour la recherche et un reverse proxy Nginx pour lier le tout. Cinq services, cinq choses qui peuvent casser, cinq choses à surveiller, patcher et mettre à jour.

DocPlatform est livré sous forme d'un seul fichier. Téléchargez-le, lancez-le, c'est fait.

Ce n'est pas un artifice marketing. C'est une décision d'architecture prise dès le premier jour, et chaque choix de conception depuis en découle. Voici pourquoi.

## La stack de documentation typique

Voyons ce que vous déployez réellement quand vous installez une plateforme de documentation moderne :

```
┌─────────────┐
│   Nginx     │  ← reverse proxy, terminaison TLS
├─────────────┤
│   Node.js   │  ← serveur applicatif
├─────────────┤
│  PostgreSQL │  ← stockage du contenu
├─────────────┤
│    Redis    │  ← cache de sessions, file de tâches
├─────────────┤
│Elasticsearch│  ← recherche plein texte
└─────────────┘
```

Ce sont cinq processus, chacun avec ses propres fichiers de configuration, ses exigences de version et ses modes de défaillance. Docker Compose aide à gérer l'orchestration, mais ne réduit pas la surface d'attaque. Vous devez toujours :

- Surveiller chaque service pour les crashs et l'utilisation des ressources
- Exécuter les migrations de base de données lors des mises à jour
- Ajuster les tailles de heap Elasticsearch et les paramètres d'index
- Gérer les politiques d'éviction Redis quand la mémoire se remplit
- Faire la rotation des logs Nginx et renouveler les certificats TLS

Pour une entreprise du Fortune 500 avec une équipe plateforme, c'est de la routine. Pour une startup de 10 personnes qui veut juste de la documentation interne, c'est un surcoût qui ne finit jamais.

## Ce que donne un binaire unique

Voici le déploiement DocPlatform :

```
┌──────────────────────────┐
│      docplatform          │  ← binaire Go unique
│  ┌────────┐ ┌──────────┐ │
│  │ SQLite │ │  Bleve   │ │
│  │  (BDD) │ │(recherche)│ │
│  └────────┘ └──────────┘ │
└──────────────────────────┘
```

Un binaire. Un répertoire de données. SQLite gère le stockage du contenu, les sessions et la configuration. [Bleve](https://blevesearch.com/) gère la recherche plein texte. Les deux sont des bibliothèques embarquées compilées directement dans le binaire — pas de processus externes, pas d'appels réseau entre services.

L'installation prend 30 secondes :

```bash
curl -fsSL https://get.valoryx.org | sh
docplatform serve
```

C'est tout. Pas de `docker-compose up`, pas d'initialisation de base de données, pas de variables d'environnement pour les chaînes de connexion. Le binaire crée son répertoire de données au premier lancement et commence à servir sur le port 3000.

Pour plus d'options d'installation, consultez le [guide d'installation](/install/).

## Pourquoi Go rend cela possible

Nous avons choisi Go spécifiquement parce qu'il permet cette architecture. Trois propriétés comptent :

### Compilation statique

Go compile en un binaire unique lié statiquement. Pas de dépendances runtime, pas de bibliothèques partagées, pas de JVM, pas de `node_modules`. Le binaire tourne sur un serveur Linux nu sans rien d'autre installé.

```bash
# Cross-compilation pour Linux depuis n'importe quel OS
GOOS=linux GOARCH=amd64 go build -o docplatform ./cmd/server/
```

Cette seule commande produit un binaire que vous pouvez `scp` sur un serveur et exécuter. Comparez cela avec le déploiement d'une application Node.js, où vous devez installer Node, lancer `npm install`, espérer que les dépendances natives compilent correctement sur l'architecture cible, et configurer un gestionnaire de processus.

### Goroutines pour la concurrence

Une plateforme de documentation doit gérer des requêtes concurrentes (consultations de pages, requêtes de recherche, sauvegardes de l'éditeur), exécuter des tâches en arrière-plan (synchronisation git, indexation de recherche), et gérer des connexions WebSocket (collaboration en temps réel) — le tout simultanément.

Les goroutines de Go rendent cela économique. Chaque connexion WebSocket obtient sa propre goroutine, coûtant environ 2 Ko de mémoire. Un serveur Node.js gérant les mêmes connexions doit les gérer sur une seule boucle d'événements, ou les décharger vers des worker threads avec la complexité de la mémoire partagée.

Le moteur de synchronisation git, qui interroge et réconcilie les changements entre l'éditeur web et les dépôts git, fonctionne comme un ensemble de goroutines au sein du même processus. Pas de service worker séparé, pas de file de tâches, pas de Redis.

### Bases de données embarquées

SQLite et Bleve sont écrits respectivement en C et en Go, et les deux se compilent directement dans le binaire via `cgo` (SQLite) et Go pur (Bleve). Cela signifie :

- Pas de serveur de base de données à installer, configurer ou surveiller
- Pas de latence réseau entre l'application et ses données
- Les sauvegardes sont des copies de fichiers — `cp data.db data.db.bak`
- Les mises à jour préservent les données automatiquement — le nouveau binaire lit les anciens fichiers de données

SQLite gère des [milliards de lignes](https://www.sqlite.org/whentouse.html) en production dans des entreprises bien plus grandes que la nôtre. Pour une plateforme de documentation servant des centaines d'utilisateurs concurrents, c'est plus que suffisant.

## L'avantage opérationnel

L'approche du binaire unique paie des dividendes en exploitation :

**Les mises à jour** consistent à remplacer un fichier. Arrêtez l'ancien binaire, copiez le nouveau, démarrez-le. Pas de migrations de base de données à gérer — l'application gère les changements de schéma au démarrage.

**Les sauvegardes** consistent à copier deux fichiers : la base de données SQLite et l'index Bleve. Ou juste la base de données — l'index de recherche peut être reconstruit à partir du contenu.

**La surveillance** consiste à observer un seul processus. S'il tourne, tout tourne. S'il crashe, redémarrez-le. Il n'y a pas de panne partielle où la base de données est active mais la recherche est en panne.

**L'utilisation des ressources** est prévisible. Un processus, une empreinte mémoire. Pas de pics de mémoire surprise venant du heap JVM d'Elasticsearch ou de Redis accumulant des clés.

**La surface de sécurité** est minimale. Un binaire, un port en écoute. Pas de communication inter-services à sécuriser, pas de Redis exposé sur un port réseau, pas de cluster Elasticsearch avec sa propre couche d'authentification. Consultez notre [documentation de sécurité](/security/) pour le modèle complet.

## Compromis que nous acceptons

Cette architecture a des limites, et nous sommes honnêtes à ce sujet :

**Mise à l'échelle verticale uniquement.** SQLite tourne sur une seule machine. Vous ne pouvez pas distribuer la base de données sur un cluster. Pour la plupart des cas d'utilisation documentaires — même les grands avec des milliers de pages — un seul serveur moderne gère la charge facilement. Mais si vous avez besoin d'une mise à l'échelle horizontale entre data centers, ce n'est pas la bonne architecture.

**Écrivain unique pour SQLite.** SQLite prend en charge les lecteurs concurrents mais sérialise les écritures. En pratique, les plateformes de documentation sont orientées lecture (beaucoup de consultations de pages, peu de modifications), donc c'est rarement un goulot d'étranglement. Mais une équipe de 200 personnes sauvegardant toutes des pages simultanément verrait une certaine contention en écriture.

**Pas de remplacement de composants.** Vous ne pouvez pas remplacer Bleve par Elasticsearch si vous voulez des fonctionnalités de recherche plus avancées. Le moteur de recherche est embarqué, pas interchangeable. Nous pensons que le compromis en vaut la peine — Bleve prend en charge la racinisation, la correspondance floue et le boosting par champ, ce qui couvre les besoins de la recherche documentaire.

## Exemples de déploiement

Le binaire unique tourne partout où un processus Linux/macOS/Windows peut tourner :

**Bare metal ou VM :**
```bash
# Télécharger, lancer, c'est fait
curl -fsSL https://get.valoryx.org | sh
docplatform serve --port 3000
```

**Service systemd :**
```ini
[Unit]
Description=DocPlatform
After=network.target

[Service]
ExecStart=/opt/docplatform/bin/docplatform serve
WorkingDirectory=/opt/docplatform
Restart=always

[Install]
WantedBy=multi-user.target
```

**Docker (si vous le souhaitez) :**
```dockerfile
FROM scratch
COPY docplatform /docplatform
ENTRYPOINT ["/docplatform", "serve"]
```

Notez le `FROM scratch` — puisque le binaire n'a aucune dépendance, l'image Docker ne contient littéralement rien d'autre que le binaire lui-même. L'image fait moins de 30 Mo.

Pour les options de déploiement détaillées, consultez le [guide de déploiement binaire](/docs/deployment/binary/).

## Ce que cela signifie pour votre équipe

Chaque service supplémentaire dans votre stack est un service que quelqu'un doit comprendre, surveiller et réparer à 2h du matin quand il casse. L'infrastructure de documentation devrait s'effacer — c'est quelque chose que vous installez une fois et que vous oubliez.

Un binaire unique qui embarque tout ce dont il a besoin est ce qui se rapproche le plus de cet idéal. Pas de conteneurs à orchestrer, pas de bases de données à ajuster, pas de clusters de recherche à surveiller. Juste un fichier qui fait tourner votre documentation.

[Installez DocPlatform](/install/) en 30 secondes et constatez par vous-même. L'édition Community est gratuite — utilisateurs illimités, pages illimitées, sans limite de temps.
