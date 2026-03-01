---
title: Variables d'environnement
description: Référence complète de toutes les variables d'environnement DocPlatform — serveur, base de données, git, authentification, e-mail et opérations.
weight: 1
---

# Variables d'environnement

DocPlatform lit sa configuration depuis les variables d'environnement. Définissez-les dans votre shell, un fichier `.env` dans le répertoire de travail ou votre orchestrateur de conteneurs.

## Serveur

| Variable | Par défaut | Description |
|---|---|---|
| `PORT` | `3000` | Port d'écoute HTTP |
| `HOST` | `0.0.0.0` | Adresse d'écoute HTTP. Définissez à `127.0.0.1` pour restreindre à localhost. |
| `DATA_DIR` | `.docplatform` | Répertoire racine pour toutes les données DocPlatform (base de données, sauvegardes, espaces de travail, clés) |
| `BASE_DOMAIN` | — | Domaine personnalisé pour la documentation publiée (par ex. `docs.yourcompany.com`). Lorsque défini, la documentation publiée utilise ce domaine pour les URLs canoniques et les entrées du sitemap. |
| `PUBLISH_REQUIRE_AUTH` | `false` | Lorsque `true`, tous les sites de documentation publiée exigent que le visiteur soit connecté en tant que membre de l'espace de travail. Les visiteurs non authentifiés sont redirigés vers la page de connexion puis renvoyés vers la page d'origine après connexion. |

## Authentification

| Variable | Par défaut | Description |
|---|---|---|
| `JWT_SECRET_PATH` | `{DATA_DIR}/jwt-key.pem` | Chemin vers la clé privée RS256 pour la signature JWT. Générée automatiquement au premier lancement si absente. |
| `JWT_ACCESS_TTL` | `900` | Durée de vie du token d'accès en secondes (par défaut : 15 minutes) |
| `JWT_REFRESH_TTL` | `2592000` | Durée de vie du token de rafraîchissement en secondes (par défaut : 30 jours) |

## Fournisseurs OIDC (optionnel)

Activez la connexion Google et/ou GitHub en définissant ces variables. Lorsqu'elles ne sont pas définies, seule l'authentification locale (e-mail + mot de passe) est disponible.

| Variable | Par défaut | Description |
|---|---|---|
| `OIDC_GOOGLE_CLIENT_ID` | — | Identifiant client OAuth 2.0 Google |
| `OIDC_GOOGLE_CLIENT_SECRET` | — | Secret client OAuth 2.0 Google |
| `OIDC_GITHUB_CLIENT_ID` | — | Identifiant client OAuth GitHub |
| `OIDC_GITHUB_CLIENT_SECRET` | — | Secret client OAuth GitHub |

Consultez [Authentification](authentication.md) pour les instructions de configuration.

## Git

| Variable | Par défaut | Description |
|---|---|---|
| `GIT_SSH_KEY_PATH` | `~/.ssh/docplatform_deploy_key` | Chemin vers la clé privée SSH pour les opérations git. Requis pour les dépôts privés via SSH. |
| `GIT_SYNC_INTERVAL` | `300` | Intervalle de polling par défaut en secondes pour la synchronisation distante (minimum : 10). Supplanté par le `sync_interval` par espace de travail. Définissez à `0` pour une synchronisation uniquement par webhook (pas de polling). |
| `GIT_AUTO_COMMIT` | `true` | Comportement d'auto-commit par défaut. Supplanté par le `git_auto_commit` par espace de travail. |
| `GIT_WEBHOOK_SECRET` | — | Secret partagé pour vérifier les payloads webhook (HMAC-SHA256) depuis GitHub, GitLab ou Bitbucket. |
| `GIT_COMMIT_NAME` | `DocPlatform` | Nom du committer git pour les auto-commits |
| `GIT_COMMIT_EMAIL` | `docplatform@local` | E-mail du committer git pour les auto-commits |

## E-mail (optionnel)

Configurez SMTP pour les invitations à l'espace de travail et les e-mails de réinitialisation de mot de passe. Sans SMTP, les tokens sont affichés sur stdout (journaux du serveur).

| Variable | Par défaut | Description |
|---|---|---|
| `SMTP_HOST` | — | Nom d'hôte du serveur SMTP (par ex. `smtp.gmail.com`) |
| `SMTP_PORT` | `587` | Port SMTP (587 pour STARTTLS, 465 pour SSL) |
| `SMTP_FROM` | — | Adresse e-mail de l'expéditeur (par ex. `docs@yourcompany.com`) |
| `SMTP_USERNAME` | — | Nom d'utilisateur pour l'authentification SMTP |
| `SMTP_PASSWORD` | — | Mot de passe pour l'authentification SMTP |

## Sauvegardes

| Variable | Par défaut | Description |
|---|---|---|
| `BACKUP_ENABLED` | `true` | Activer les sauvegardes SQLite quotidiennes automatisées |
| `BACKUP_RETENTION_DAYS` | `7` | Nombre de jours de rétention des fichiers de sauvegarde. Les sauvegardes plus anciennes sont supprimées automatiquement. |
| `BACKUP_DIR` | `{DATA_DIR}/backups` | Répertoire pour les fichiers de sauvegarde |

## Télémétrie

| Variable | Par défaut | Description |
|---|---|---|
| `DOCPLATFORM_TELEMETRY` | `off` | Définissez à `on` pour activer les métriques d'utilisation anonymes et optionnelles. Lorsque activé, un identifiant d'installation SHA-256 (aucune information personnellement identifiable) est envoyé chaque semaine. |
| `DOCPLATFORM_TELEMETRY_ENDPOINT` | — | Point de terminaison personnalisé pour les données de télémétrie (avancé — pour les environnements isolés avec des analyses internes) |

### Ce que la télémétrie envoie (lorsqu'elle est activée)

- Identifiant d'installation SHA-256 (dérivé du répertoire de données, non réversible)
- Nombre d'espaces de travail et nombre total de pages
- Version de DocPlatform
- OS et architecture

La télémétrie **n'envoie jamais** : le contenu des pages, les e-mails des utilisateurs, les adresses IP, les noms de fichiers ou toute information personnellement identifiable. Fréquence : hebdomadaire.

## Gestion du frontmatter

| Variable | Par défaut | Description |
|---|---|---|
| `FRONTMATTER_ERROR_MODE` | `strict` | Comment gérer un frontmatter YAML invalide : `strict` restreint la page à un accès admin uniquement (empêche l'exposition accidentelle) ; `lenient` conserve le dernier frontmatter valide connu et affiche un avertissement. |

## Utiliser un fichier `.env`

Créez un fichier `.env` dans le répertoire où vous exécutez `docplatform serve` :

```bash
# .env
PORT=8080
DATA_DIR=/var/lib/docplatform
GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_FROM=docs@example.com
SMTP_USERNAME=docs@example.com
SMTP_PASSWORD=app-specific-password
BACKUP_RETENTION_DAYS=30
```

DocPlatform charge le fichier `.env` automatiquement. Les variables d'environnement définies dans le shell ont priorité sur les valeurs du `.env`.

## Environnement Docker

Passez les variables d'environnement à Docker avec les flags `-e` ou un fichier env :

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  -e DATA_DIR=/data \
  -e SMTP_HOST=smtp.example.com \
  -e SMTP_FROM=docs@example.com \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

## Notes de sécurité

- **Ne commitez jamais les fichiers `.env`** dans le contrôle de version. Ajoutez `.env` à votre `.gitignore`.
- **Les clés JWT** sont générées automatiquement. Si vous devez effectuer une rotation, supprimez le fichier de clé et redémarrez — une nouvelle clé est générée et toutes les sessions existantes sont invalidées.
- **Mots de passe SMTP** — utilisez des mots de passe d'application ou des clés API, pas le mot de passe principal de votre compte.
- **Tokens git** — utilisez des tokens limités au dépôt avec des permissions minimales (lecture + écriture pour la synchronisation).
