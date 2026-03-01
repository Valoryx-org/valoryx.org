---
title: Démarrage rapide
description: Lancez DocPlatform en moins de 5 minutes avec un espace de travail de documentation entièrement fonctionnel.
weight: 1
---

# Démarrage rapide

Passez de zéro à une plateforme de documentation fonctionnelle en moins de 5 minutes. Ce guide couvre le chemin le plus rapide — pour les options détaillées, consultez le guide d'[Installation](installation.md).

## Étape 1 : Installer

```bash
# Recommandé (détection automatique de la plateforme)
curl -fsSL https://valoryx.org/install.sh | sh
```

Ou télécharger manuellement :

```bash
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform
```

Ou avec Docker :

```bash
docker run -d --name docplatform -p 3000:3000 -v docplatform-data:/data ghcr.io/valoryx-org/docplatform:latest
```

Si vous utilisez Docker, passez directement à l'[Étape 3](#étape-3--enregistrer-votre-compte) — le conteneur s'initialise automatiquement.

## Étape 2 : Initialiser un espace de travail

```bash
docplatform init --workspace-name "My Docs" --slug my-docs
```

Cela crée :

```
.docplatform/
├── data.db              # SQLite database
├── jwt-key.pem          # Auto-generated RS256 signing key
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Your documentation lives here
        └── .docplatform/
            └── config.yaml
```

### Avec git (optionnel)

Connectez-vous à un dépôt git existant lors de l'initialisation :

```bash
docplatform init \
  --workspace-name "My Docs" \
  --slug my-docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

DocPlatform clone le dépôt et commence la synchronisation. Tous les fichiers `.md` existants sont automatiquement indexés.

## Étape 3 : Démarrer le serveur

```bash
docplatform serve
```

```
INFO  Server starting            port=3000 version=v0.5.0
INFO  Database initialized       path=.docplatform/data.db
INFO  Search index ready         documents=0
INFO  Workspace loaded           name="My Docs" slug=my-docs
INFO  Listening on               http://localhost:3000
```

Ouvrez [http://localhost:3000](http://localhost:3000) dans votre navigateur.

## Étape 4 : Enregistrer votre compte

Le premier utilisateur à s'enregistrer devient automatiquement **SuperAdmin** avec un accès complet à la plateforme.

1. Cliquez sur **Create Account**
2. Saisissez votre nom, e-mail et mot de passe
3. Vous êtes connecté et prêt à rédiger

> **Note de sécurité :** Le mécanisme « premier utilisateur = admin » ne s'applique que lorsqu'aucun utilisateur n'existe. Après la première inscription, les nouveaux comptes reçoivent le rôle par défaut configuré pour l'espace de travail.

## Étape 5 : Créer votre première page

1. Cliquez sur **New Page** dans la barre latérale
2. Donnez-lui un titre — le slug d'URL est généré automatiquement à partir du titre
3. Commencez à rédiger dans l'éditeur riche
4. Les modifications sont sauvegardées automatiquement toutes les quelques secondes

La page est stockée sous forme de fichier Markdown dans le répertoire `docs/` de votre espace de travail. Si vous avez connecté git, elle est auto-commitée et poussée.

## Étape 6 : Essayer

Voici quelques actions à essayer immédiatement :

| Action | Comment |
|---|---|
| **Basculer en Markdown brut** | Cliquez sur le bouton `</>` dans la barre d'outils de l'éditeur |
| **Rechercher** | Appuyez sur `Cmd+K` (ou `Ctrl+K`) pour ouvrir la recherche instantanée |
| **Créer une sous-page** | Cliquez sur le `+` à côté d'une page existante dans la barre latérale |
| **Aperçu du site publié** | Accédez à `http://localhost:3000/p/my-docs/` |
| **Lancer les diagnostics** | Exécutez `docplatform doctor` dans votre terminal |

## Et ensuite

| Objectif | Guide |
|---|---|
| Connecter un dépôt git | [Intégration Git](../guides/git-integration.md) |
| Inviter votre équipe | [Équipes et collaboration](../guides/collaboration.md) |
| Publier la documentation | [Publication](../guides/publishing.md) |
| Déployer en production | [Déploiement](../deployment/binary.md) |
| Configurer les fournisseurs d'authentification | [Authentification](../configuration/authentication.md) |
