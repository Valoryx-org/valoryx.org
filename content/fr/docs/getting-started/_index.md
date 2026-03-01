---
title: Premiers pas
description: Installez DocPlatform, créez votre premier espace de travail et commencez à rédiger de la documentation en moins de 10 minutes.
weight: 1
---

# Premiers pas

Cette section vous guide dans l'installation de DocPlatform, son premier lancement et la création d'un espace de travail où votre équipe peut commencer à rédiger.

## Choisissez votre parcours

| Parcours | Durée | Idéal pour |
|---|---|---|
| [Démarrage rapide](quickstart.md) | 5 minutes | Évaluer le produit rapidement — une seule commande, le voir fonctionner |
| [Installation](installation.md) | 10 minutes | Installation complète — choisir votre méthode (binaire, Docker, source), comprendre ce qui se passe |
| [Votre premier espace de travail](first-workspace.md) | 10 minutes | Déjà en fonctionnement — apprendre à créer des espaces de travail, connecter git, inviter votre équipe |

## Avant de commencer

DocPlatform n'a aucune dépendance externe. Vous n'avez pas besoin d'installer de base de données, de moteur de recherche ou de runtime Node.js. Le binaire unique inclut tout.

**Dépendances optionnelles :**

- **Git 2.30+** — uniquement nécessaire si vous souhaitez synchroniser avec un dépôt git distant
- **Clé SSH** — uniquement nécessaire pour les dépôts git privés via SSH
- **Serveur SMTP** — uniquement nécessaire pour les invitations par e-mail et la réinitialisation de mot de passe (sans SMTP, les tokens de réinitialisation sont affichés sur stdout)

## Architecture en un coup d'oeil

Lorsque vous exécutez `docplatform serve`, un processus unique démarre qui inclut :

- **Serveur HTTP** — sert l'éditeur web et l'API sur le port 3000
- **Base de données SQLite** — stocke les utilisateurs, espaces de travail, métadonnées des pages et journaux d'audit
- **Moteur de recherche Bleve** — indexe tout le contenu pour une recherche plein texte instantanée
- **Moteur git** — synchronise le contenu de manière bidirectionnelle avec les dépôts distants
- **Frontend statique** — l'éditeur web Next.js, intégré dans le binaire

Toutes les données résident dans un seul répertoire (par défaut : `.docplatform/`), ce qui rend les sauvegardes et les migrations simples — il suffit de copier le répertoire.
