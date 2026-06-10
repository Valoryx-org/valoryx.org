---
title: "Auto-hébergez votre documentation en 5 minutes"
description: "Un tutoriel pas à pas : téléchargez DocPlatform, lancez un binaire unique, créez votre premier workspace et publiez votre documentation. Sans Docker, sans base de données."
date: "2026-03-02"
author: "Valoryx Team"
tags: ["self-hosted", "tutorial", "documentation"]
---

La plupart des outils de documentation auto-hébergés nécessitent une base de données, un reverse proxy et une demi-après-midi d'édition de YAML avant de voir un écran d'accueil. DocPlatform est un binaire Go unique sans aucune dépendance externe. Ce tutoriel vous emmène de zéro à une documentation publiée en environ cinq minutes.

## Prérequis

Vous avez besoin d'une machine Linux, macOS ou Windows. C'est tout. Pas de Docker, pas de PostgreSQL, pas de runtime Node.js. DocPlatform se compile en un binaire statique unique — le runtime Go est intégré. Si vous êtes curieux concernant le langage d'implémentation, [Go](https://go.dev/) produit des exécutables autonomes qui fonctionnent sans rien installer sur la machine hôte.

## Étape 1 : Téléchargement et installation

Sur Linux ou macOS, le script d'installation gère tout :

```bash
curl -fsSL https://valoryx.org/install.sh | bash
```

Cela télécharge le dernier binaire dans `/usr/local/bin/docplatform` (ou `~/.local/bin/` si vous n'avez pas l'accès root). Sur macOS avec Homebrew, vous pouvez aussi lancer :

```bash
brew install valoryx/tap/docplatform
```

Sur Windows, récupérez le `.exe` depuis la [page de téléchargement](/install/) et ajoutez-le à votre PATH.

Vérifiez l'installation :

```bash
docplatform version
# DocPlatform v1.x.x (linux/amd64)
```

## Étape 2 : Démarrer le serveur

Lancez le serveur avec les paramètres par défaut :

```bash
docplatform serve
```

Vous verrez une sortie semblable à celle-ci :

```
INFO  Starting DocPlatform server
INFO  Data directory: ./data
INFO  Listening on http://localhost:3000
INFO  Full-text search index: ready
INFO  Admin setup required — visit http://localhost:3000 to create your account
```

Ouvrez `http://localhost:3000` dans votre navigateur. DocPlatform sert à la fois l'éditeur et le site publié depuis le même binaire sur le même port. Aucune étape de build frontend séparée.

Au premier lancement, vous verrez l'écran de configuration administrateur. Choisissez un nom d'utilisateur et un mot de passe. Cela crée le compte super admin — celui qui peut tout gérer. Vous pourrez ajouter d'autres utilisateurs plus tard via le panneau d'administration.

## Étape 3 : Créer votre premier workspace

Après la connexion, le tableau de bord affiche une liste de workspaces vide. Cliquez sur **New Workspace** et renseignez :

- **Name :** `engineering-handbook` (ou le sujet de votre documentation)
- **Slug :** `engineering-handbook` (cela devient le chemin de l'URL)
- **Theme :** Choisissez l'un des 7 thèmes intégrés — vous pourrez le changer plus tard

Cliquez sur **Create**. Vous avez maintenant un workspace avec une page racine prête à être éditée.

## Étape 4 : Rédiger de la documentation

Cliquez sur votre nouveau workspace et vous arriverez dans l'[éditeur WYSIWYG](/docs/getting-started/first-workspace/). Il prend en charge les raccourcis markdown — tapez `##` suivi d'un espace pour créer un H2, utilisez les backticks pour le code en ligne, les triples backticks pour les blocs de code. Tout ce que vous attendez d'un éditeur moderne, rendu en texte riche au fur et à mesure que vous tapez.

Créez quelques pages pour vous familiariser :

1. Cliquez sur **New Page** dans la barre latérale
2. Donnez-lui un titre : « Premiers pas »
3. Rédigez du contenu — collez du markdown existant si vous en avez
4. Appuyez sur **Ctrl+S** (ou Cmd+S sur macOS) pour sauvegarder

La page est enregistrée dans la base de données SQLite locale de DocPlatform (intégrée dans le binaire — aucune base de données externe à gérer). Chaque sauvegarde crée une version vers laquelle vous pouvez revenir.

Essayez de créer une page enfant : survolez « Premiers pas » dans la barre latérale et cliquez sur l'icône **+**. Vous avez maintenant une hiérarchie de pages.

## Étape 5 : Publier votre documentation

Pour rendre votre documentation accessible publiquement, allez dans **Workspace Settings > Publishing** et activez la publication. Votre documentation est maintenant en ligne à :

```
http://localhost:3000/s/engineering-handbook
```

Le préfixe `/s/` sert la vue publiée en lecture seule. Il utilise le thème que vous avez sélectionné, dispose d'une recherche plein texte propulsée par Bleve, et inclut une arborescence de navigation construite à partir de votre hiérarchie de pages.

C'est tout. Cinq commandes, aucun fichier de configuration, et vous avez un site de documentation fonctionnel.

## Ce qui tourne sous le capot

Lorsque vous avez lancé `docplatform serve`, vous avez démarré un processus unique qui gère :

- **Serveur HTTP** — sert l'interface de l'éditeur, l'API et le site de documentation publié
- **Base de données SQLite** — stocke les utilisateurs, les workspaces, les pages et les versions
- **Index de recherche Bleve** — recherche plein texte avec tolérance aux fautes de frappe et classement par pertinence
- **Authentification WebAuthn/passkey** — authentification moderne sans mot de passe en plus de l'authentification traditionnelle par identifiant/mot de passe
- **RBAC** — 5 rôles (super admin, admin, éditeur, lecteur, invité) avec des permissions granulaires

Tout cela fonctionne dans un seul processus utilisant environ 50–80 Mo de RAM. Pas de workers en arrière-plan, pas de files de messages, pas de microservices.

## Étape 6 : Connecter Git (optionnel)

Si vous souhaitez que votre documentation soit stockée dans un dépôt git — versionnée, révisable, éditable depuis votre IDE — DocPlatform prend en charge la synchronisation bidirectionnelle avec git. Consultez le [guide de démarrage rapide](/docs/getting-started/quickstart/) pour la configuration complète, mais en résumé :

1. Allez dans **Workspace Settings > Git Sync**
2. Collez l'URL de votre dépôt et la clé de déploiement
3. Choisissez une branche
4. Cliquez sur **Enable Sync**

À partir de ce moment, chaque sauvegarde dans l'éditeur crée un commit git, et chaque push vers le dépôt depuis un IDE ou un pipeline CI se reflète dans l'éditeur. Ce n'est pas un miroir unidirectionnel — c'est une véritable synchronisation bidirectionnelle utilisant le pattern Content Ledger (voir [Pourquoi les outils de documentation Git cassent la synchronisation](/blog/why-git-sync-breaks/) pour l'explication technique).

## Déploiement en production

Pour un déploiement en production, vous voudrez définir quelques variables d'environnement :

```bash
export DOCPLATFORM_PORT=3000
export DOCPLATFORM_DATA_DIR=/var/lib/docplatform
export DOCPLATFORM_BASE_URL=https://docs.yourcompany.com

docplatform serve
```

Placez-le derrière un reverse proxy (Nginx, Caddy ou Cloudflare Tunnel) pour la terminaison HTTPS. Utilisez une unité systemd ou similaire pour le maintenir en fonctionnement :

```ini
[Unit]
Description=DocPlatform Documentation Server
After=network.target

[Service]
ExecStart=/usr/local/bin/docplatform serve
WorkingDirectory=/var/lib/docplatform
Restart=always
User=docplatform

[Install]
WantedBy=multi-user.target
```

Sauvegardez le répertoire de données périodiquement — il contient la base de données SQLite et l'index de recherche. Un simple `cp` ou `rsync` pendant que le serveur tourne fonctionne très bien (SQLite gère les lectures concurrentes).

## Étapes suivantes

Vous avez maintenant une plateforme de documentation fonctionnelle. Voici la suite :

- [Guide de démarrage rapide complet](/docs/getting-started/quickstart/) — couvre la synchronisation git, les thèmes et la gestion des utilisateurs
- [Créer votre premier workspace](/docs/getting-started/first-workspace/) — configuration détaillée du workspace
- [Options d'installation](/install/) — toutes les méthodes de téléchargement, y compris les builds ARM

L'édition Community de DocPlatform est gratuite, sans limite d'utilisateurs, sans limite de pages, et sans restriction de fonctionnalités. Téléchargez le binaire et commencez à écrire. Tout ce dont vous avez besoin est dans ce fichier unique.
