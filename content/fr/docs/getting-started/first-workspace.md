---
title: Votre premier espace de travail
description: Créez et configurez un espace de travail de documentation — connectez git, définissez la structure du contenu et invitez votre équipe.
weight: 3
---

# Votre premier espace de travail

Un espace de travail est le conteneur principal d'un projet de documentation. Chaque espace de travail correspond à un répertoire de fichiers Markdown et se synchronise optionnellement avec un dépôt git.

## Concepts de l'espace de travail

| Concept | Description |
|---|---|
| **Workspace** | Un projet de documentation contenant des pages, des membres et des paramètres |
| **Page** | Un fichier Markdown avec un frontmatter YAML (titre, description, tags, accès) |
| **Slug** | L'identifiant compatible URL de votre espace de travail (ex. `my-docs` → `/p/my-docs/`) |
| **Membre** | Un utilisateur avec un rôle dans l'espace de travail (de Viewer à WorkspaceAdmin) |

## Créer un espace de travail

### Via CLI

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs
```

### Via l'interface web

1. Connectez-vous en tant que SuperAdmin ou WorkspaceAdmin
2. Ouvrez le sélecteur d'espace de travail (menu déroulant en haut à gauche)
3. Cliquez sur **Create Workspace**
4. Saisissez un nom et un slug
5. Configurez optionnellement un dépôt git distant

## Connecter un dépôt git

La synchronisation bidirectionnelle maintient les fichiers de votre espace de travail et un dépôt git distant parfaitement en phase.

### Lors de l'initialisation

```bash
docplatform init \
  --workspace-name "Engineering Docs" \
  --slug eng-docs \
  --git-url git@github.com:your-org/eng-docs.git \
  --branch main
```

### Après la création

Mettez à jour la configuration de l'espace de travail dans `.docplatform/workspaces/{id}/.docplatform/config.yaml` :

```yaml
git_remote: git@github.com:your-org/eng-docs.git
git_branch: main
git_auto_commit: true
sync_interval: 300  # seconds
```

Puis redémarrez le serveur ou déclenchez une synchronisation manuelle depuis l'interface web.

### Configuration de la clé SSH

Pour les dépôts privés, DocPlatform utilise une clé SSH de déploiement dédiée :

```bash
# Générer une clé de déploiement (sans phrase de passe)
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""

# Ajouter la clé publique aux clés de déploiement de votre dépôt
cat ~/.ssh/docplatform_deploy_key.pub
# → Copiez ceci dans GitHub/GitLab Settings → Deploy Keys (activez l'accès en écriture)
```

Définissez la variable d'environnement :

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

### Fonctionnement de la synchronisation

```
┌─────────────┐     auto-commit + push      ┌──────────────┐
│ Web Editor   │ ──────────────────────────► │ Remote Repo  │
│ (browser)    │                             │ (GitHub, etc)│
│              │ ◄────────────────────────── │              │
└─────────────┘     polling / webhook        └──────────────┘
```

**Web → Git :** Lorsque vous sauvegardez dans l'éditeur, DocPlatform écrit le fichier `.md`, effectue un auto-commit avec un message descriptif et pousse vers le dépôt distant.

**Git → Web :** DocPlatform interroge le dépôt distant (par défaut : toutes les 5 minutes) ou écoute les webhooks. Les nouveaux commits sont tirés et l'interface web se met à jour en temps réel via WebSocket.

**Conflits :** Si les deux côtés modifient le même fichier entre deux synchronisations, DocPlatform détecte la collision à l'aide de hash de contenu, renvoie HTTP 409, et rend les deux versions téléchargeables pour une résolution manuelle.

## Organiser votre contenu

### Hiérarchie des pages

Les pages peuvent être imbriquées à n'importe quelle profondeur. La structure des fichiers dans `docs/` correspond directement à la structure des URLs :

```
docs/
├── index.md                → /p/eng-docs/
├── getting-started.md      → /p/eng-docs/getting-started
├── api/
│   ├── index.md            → /p/eng-docs/api/
│   ├── authentication.md   → /p/eng-docs/api/authentication
│   └── endpoints.md        → /p/eng-docs/api/endpoints
└── guides/
    ├── deployment.md       → /p/eng-docs/guides/deployment
    └── contributing.md     → /p/eng-docs/guides/contributing
```

### Frontmatter

Chaque page commence par un bloc de frontmatter YAML :

```yaml
---
title: Authentication
description: How to authenticate with the API using JWT tokens.
tags: [api, auth, jwt]
published: true
access: public        # public, workspace, restricted
allowed_roles: []     # only used when access: restricted
---
```

Le champ `title` est obligatoire. Tous les autres champs sont optionnels et ont des valeurs par défaut pertinentes.

## Inviter votre équipe

### Via l'interface web

1. Ouvrez **Workspace Settings** → **Members**
2. Cliquez sur **Invite**
3. Saisissez l'adresse e-mail de la personne
4. Sélectionnez un rôle (Viewer, Commenter, Editor, Admin)
5. Cliquez sur **Send Invitation**

Si SMTP est configuré, l'invitation est envoyée par e-mail. Sinon, un lien d'invitation partageable est affiché.

### Rôles

| Rôle | Peut voir | Peut commenter | Peut modifier | Peut gérer les membres | Peut gérer l'espace de travail |
|---|---|---|---|---|---|
| **Viewer** | Oui | | | | |
| **Commenter** | Oui | Oui | | | |
| **Editor** | Oui | Oui | Oui | | |
| **Admin** | Oui | Oui | Oui | Oui | |
| **WorkspaceAdmin** | Oui | Oui | Oui | Oui | Oui |
| **SuperAdmin** | Accès complet à la plateforme sur tous les espaces de travail |

Pour une configuration détaillée des permissions, consultez [Rôles et permissions](../configuration/permissions.md).

## Paramètres de l'espace de travail

Accédez aux paramètres de l'espace de travail via l'interface web (icône **Settings** en forme d'engrenage) ou en modifiant directement le fichier de configuration.

Paramètres clés :

| Paramètre | Description | Par défaut |
|---|---|---|
| `name` | Nom affiché de l'espace de travail | — |
| `slug` | Slug URL pour la documentation publiée | — |
| `git_remote` | URL du dépôt git distant | (aucun) |
| `git_branch` | Branche à synchroniser | `main` |
| `git_auto_commit` | Auto-commit des sauvegardes de l'éditeur | `true` |
| `sync_interval` | Intervalle de polling git (secondes) | `300` |
| `theme.mode` | Thème de couleur : `light`, `dark`, `auto` | `auto` |
| `theme.accent` | Couleur d'accentuation | `blue` |
| `permissions.default_role` | Rôle pour les nouveaux membres | `viewer` |

Pour la référence complète de configuration, consultez [Paramètres de l'espace de travail](../configuration/workspace-config.md).

## Et ensuite

Votre espace de travail est prêt. Voici la suite :

| Objectif | Guide |
|---|---|
| Découvrir l'éditeur web | [L'éditeur web](../guides/editor.md) |
| Configurer la documentation publiée | [Publication](../guides/publishing.md) |
| Configurer l'authentification | [Authentification](../configuration/authentication.md) |
| Déployer en production | [Checklist de production](../deployment/production.md) |
