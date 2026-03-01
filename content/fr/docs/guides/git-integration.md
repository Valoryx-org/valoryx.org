---
title: Intégration Git
description: Synchronisation git bidirectionnelle — éditez dans le navigateur ou poussez depuis votre IDE, tout reste synchronisé.
weight: 3
---

# Intégration Git

La synchronisation git bidirectionnelle de DocPlatform permet à votre équipe de travailler comme elle le préfère. Les rédacteurs techniques utilisent l'éditeur web. Les développeurs poussent depuis leur IDE. Tout le monde voit le même contenu.

## Fonctionnement

```
        ┌─────────────┐
        │ Web Editor   │
        │ (browser)    │
        └──────┬───────┘
               │ save
               ▼
        ┌─────────────┐          ┌──────────────┐
        │ Content     │  commit  │ Local Git    │  push    ┌──────────────┐
        │ Ledger      │ ───────► │ Repository   │ ───────► │ Remote Repo  │
        │             │          │ (.git)       │          │ (GitHub etc) │
        └─────────────┘          └──────┬───────┘          └──────┬───────┘
               ▲                        │                         │
               │ reconcile              │ pull                    │
               │                 ┌──────▼───────┐                 │
               └──────────────── │ Sync Engine  │ ◄───────────────┘
                                 │ (polling /   │   webhook / poll
                                 │  webhook)    │
                                 └──────────────┘
```

### Web → Git (sortant)

1. Vous sauvegardez une page dans l'éditeur web
2. Le Content Ledger écrit le fichier `.md` sur le disque
3. Le moteur git effectue un auto-commit : `docs: update {page-title}`
4. Les commits sont poussés vers le dépôt distant

### Git → Web (entrant)

1. Quelqu'un pousse un commit vers le dépôt distant (depuis un IDE, la CI, etc.)
2. Le moteur de synchronisation détecte le changement (polling ou webhook)
3. Les modifications sont tirées vers le dépôt local
4. Le Content Ledger effectue la réconciliation : système de fichiers → base de données → index de recherche
5. Le WebSocket diffuse la mise à jour aux navigateurs connectés

## Configuration

### Connecter un dépôt distant

**Lors de l'initialisation :**

```bash
docplatform init \
  --workspace-name "Docs" \
  --slug docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

**Après l'initialisation** — modifiez la configuration de l'espace de travail :

```yaml
# .docplatform/workspaces/{id}/.docplatform/config.yaml
git_remote: git@github.com:your-org/docs.git
git_branch: main
git_auto_commit: true
sync_interval: 300
```

Redémarrez le serveur ou déclenchez une synchronisation manuelle.

### Authentification

#### SSH (recommandé)

Générez une clé de déploiement et ajoutez-la à votre dépôt :

```bash
ssh-keygen -t ed25519 -f ~/.ssh/docplatform_deploy_key -N ""
```

Définissez la variable d'environnement :

```bash
export GIT_SSH_KEY_PATH=~/.ssh/docplatform_deploy_key
```

Ajoutez la clé publique (`~/.ssh/docplatform_deploy_key.pub`) aux clés de déploiement de votre dépôt. **Activez l'accès en écriture** si vous souhaitez que DocPlatform pousse des commits.

#### HTTPS avec token

Pour les dépôts HTTPS, intégrez le token dans l'URL :

```yaml
git_remote: https://x-access-token:ghp_xxxxxxxxxxxx@github.com/your-org/docs.git
```

Ou utilisez un assistant d'identification Git configuré sur l'hôte.

## Comportement de la synchronisation

### Auto-commit

Lorsque `git_auto_commit: true` (par défaut), chaque sauvegarde dans l'éditeur web produit un commit git. Les modifications rapides dans un court intervalle sont regroupées en un seul commit.

Format du message de commit :

```
docs: update Getting Started

Edited via DocPlatform web editor
Author: jane@example.com
```

Définissez `git_auto_commit: false` pour désactiver l'auto-commit. Dans ce mode, l'éditeur web écrit sur le système de fichiers mais ne crée pas de commits git — utile si vous souhaitez commiter manuellement ou selon un calendrier.

### Polling

DocPlatform interroge le dépôt distant à l'intervalle configuré (par défaut : 300 secondes / 5 minutes). Ajustez avec :

```yaml
sync_interval: 60  # check every minute
```

Des intervalles plus courts signifient une synchronisation plus rapide mais plus de trafic réseau.

### Webhooks

Pour une synchronisation instantanée, configurez un webhook dans votre dépôt :

**GitHub :**

1. Allez dans **Settings** → **Webhooks** → **Add webhook**
2. URL du payload : `https://your-domain.com/api/v1/webhooks/github`
3. Type de contenu : `application/json`
4. Secret : Définissez la variable d'environnement `GIT_WEBHOOK_SECRET` avec la même valeur
5. Événements : Sélectionnez **Push events**

**GitLab :**

1. Allez dans **Settings** → **Webhooks**
2. URL : `https://your-domain.com/api/v1/webhooks/gitlab`
3. Token secret : Correspondant à `GIT_WEBHOOK_SECRET`
4. Déclencheur : **Push events**

**Bitbucket :**

1. Allez dans **Repository settings** → **Webhooks** → **Add webhook**
2. URL : `https://your-domain.com/api/v1/webhooks/bitbucket`
3. Déclencheurs : **Repository push**

### Synchronisation manuelle

Déclenchez une synchronisation depuis l'interface web (**Settings** → **Git** → **Sync Now**) ou via l'API :

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{id}/sync \
  -H "Authorization: Bearer {token}"
```

## Résolution des conflits

Les conflits surviennent lorsque le même fichier est modifié à la fois dans l'éditeur web et via un push git entre deux intervalles de synchronisation.

### Comment les conflits sont détectés

DocPlatform suit les hash de contenu (SHA-256) pour chaque page. Lors du pull des modifications distantes, il compare le hash entrant au hash local. Si les deux diffèrent de l'ancêtre commun, un conflit est déclaré.

### Ce qui se passe en cas de conflit

1. L'opération de sauvegarde ou de synchronisation renvoie **HTTP 409 Conflict**
2. Les deux versions (locale et distante) sont préservées
3. L'interface web affiche une bannière de conflit avec les options :
   - **Keep local** — écarter la version distante
   - **Keep remote** — écarter la version locale
   - **Download both** — télécharger les deux fichiers pour une fusion manuelle
4. Une branche de conflit (`conflict/{page-slug}-{timestamp}`) est créée avec la version locale

### Prévenir les conflits

- **Utilisez des webhooks** au lieu du polling — une synchronisation plus rapide réduit la fenêtre de conflit
- **Attribuez la propriété des pages** — un seul rédacteur par page réduit le risque de collision
- **Utilisez l'éditeur web pour le contenu**, l'IDE pour le code — séparation naturelle
- **Intervalles de synchronisation courts** — `sync_interval: 30` dans les environnements à forte collaboration

## Synchronisation par lot

Lorsqu'un push distant contient plus de 20 fichiers modifiés, DocPlatform bascule en mode par lot :

1. Récupère tous les fichiers modifiés en un seul diff
2. Acquiert des mutex par chemin pour tous les chemins concernés (triés pour éviter les deadlocks)
3. Traite tous les fichiers en une seule transaction de base de données
4. Invalide le cache de permissions une seule fois (pas par fichier)
5. Émet un seul message WebSocket `bulk-sync` avec le nombre total de modifications

Cela évite les tempêtes de notifications et la surcharge de la base de données lorsque des modifications importantes sont poussées (par ex. import initial de dépôt ou restructuration en masse).

## Stockage des conflits

Lorsqu'un conflit est détecté, les deux versions sont stockées sur le disque :

```
.docplatform/conflicts/
└── {page-id}/
    └── 20250115T103045Z/
        ├── ours.md      # Local version (web editor)
        └── theirs.md    # Remote version (git push)
```

Les conflits persistent jusqu'à résolution explicite via l'interface web ou l'API. La commande `docplatform doctor` signale les conflits non résolus.

## Détails du moteur git

DocPlatform utilise un moteur git hybride qui sélectionne automatiquement le meilleur backend :

| Condition | Moteur | Pourquoi |
|---|---|---|
| Moins de 5 000 fichiers | **go-git** (in-process) | Rapide, pas de dépendance externe, Go pur |
| Plus de 5 000 fichiers | **Git CLI natif** (sous-processus) | Meilleure gestion des gros dépôts, clones superficiels |
| RSS go-git > 512 Mo | **Git CLI natif** (repli) | Sécurité mémoire — prévient les OOM sur les gros dépôts |

Un pool de **4 workers concurrents** gère les opérations git pour tous les espaces de travail. Chaque espace de travail a son propre mutex — les opérations sur des espaces de travail différents s'exécutent en parallèle, tandis que les opérations sur le même espace de travail sont sérialisées.

Les messages d'auto-commit utilisent ce format :

```
docs: update {page-title}

Edited via DocPlatform web editor
Author: user@example.com
Committer: DocPlatform <docplatform@local>
```

## Travailler avec des dépôts existants

DocPlatform fonctionne avec les dépôts de documentation existants. Lorsque vous connectez un dépôt :

1. Le dépôt est cloné (ou tiré s'il existe déjà localement)
2. Tous les fichiers `.md` dans le répertoire `docs/` sont indexés
3. Le frontmatter est analysé et les métadonnées des pages sont stockées dans SQLite
4. L'index de recherche est construit de manière incrémentale

Les fichiers en dehors de `docs/` ne sont pas indexés ni affichés dans l'éditeur, mais ils restent dans le dépôt git sans être modifiés.

### Importer depuis d'autres plateformes

DocPlatform fonctionne avec tout contenu Markdown. Voici comment migrer depuis les plateformes courantes :

| Source | Méthode d'export | Notes |
|---|---|---|
| **Docusaurus** | Copie directe | Déjà basé sur `.md` — copiez le répertoire `docs/` tel quel, ajoutez le frontmatter si manquant |
| **GitBook** | Export JSON → conversion | Exportez via l'API GitBook, convertissez en Markdown |
| **Notion** | Export Markdown | Exportez l'espace de travail en Markdown, restructurez en hiérarchie `docs/` |
| **Confluence** | Export HTML → conversion | Exportez les espaces en HTML, convertissez en Markdown avec pandoc ou similaire |
| **Wiki.js** | Export base de données | Exportez les pages en Markdown depuis le panneau d'administration |

**Étapes générales de migration :**

1. Exportez votre contenu sous forme de fichiers Markdown
2. Placez-les dans un dépôt git sous `docs/`
3. Ajoutez un frontmatter YAML (au minimum, `title`) à chaque fichier
4. Connectez le dépôt à DocPlatform
5. Exécutez `docplatform rebuild` pour forcer une réconciliation complète

Le réconciliateur de DocPlatform découvre automatiquement tous les fichiers `.md`, analyse leur frontmatter, attribue des ULIDs aux pages sans champ `id`, et construit l'index de recherche.
