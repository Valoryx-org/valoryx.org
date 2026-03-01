---
title: Configuration
description: Configurez DocPlatform avec des variables d'environnement, des paramètres d'espace de travail, des fournisseurs d'authentification et des permissions basées sur les rôles.
weight: 3
---

# Configuration

DocPlatform suit une approche convention-plutôt-que-configuration. Il fonctionne avec des valeurs par défaut pertinentes dès l'installation, mais chaque aspect est configurable pour les déploiements en production.

## Couches de configuration

La configuration est appliquée en trois couches, de la plus large à la plus spécifique :

| Couche | Portée | Méthode |
|---|---|---|
| **Variables d'environnement** | Plateforme entière | Fichier `.env` ou environnement shell |
| **Configuration de l'espace de travail** | Par espace de travail | `.docplatform/config.yaml` |
| **Frontmatter de page** | Par page | Bloc YAML dans chaque fichier `.md` |

Les couches de plus grande spécificité prennent le dessus sur les couches inférieures. Par exemple, un `access: restricted` d'une page supplante la valeur par défaut `access: public` de l'espace de travail.

## Guides

| Guide | Ce qu'il couvre |
|---|---|
| [Variables d'environnement](environment.md) | Tous les paramètres au niveau de la plateforme : port, répertoire de données, git, SMTP, télémétrie |
| [Paramètres de l'espace de travail](workspace-config.md) | Configuration par espace de travail : dépôt git distant, thème, navigation, valeurs par défaut de publication |
| [Authentification](authentication.md) | Authentification locale, fournisseurs OIDC (Google, GitHub), paramètres JWT, politiques de mot de passe |
| [Rôles et permissions](permissions.md) | Hiérarchie RBAC à 6 niveaux, contrôle d'accès au niveau de la page, configuration Casbin |

## Référence rapide

Les tâches de configuration les plus courantes :

| Tâche | Où |
|---|---|
| Changer le port du serveur | Variable d'environnement `PORT` |
| Connecter un dépôt git | Configuration de l'espace de travail `git_remote` |
| Activer la connexion Google/GitHub | Variables d'environnement `OIDC_*` |
| Configurer l'e-mail (invitations, réinitialisation de mot de passe) | Variables d'environnement `SMTP_*` |
| Changer le rôle par défaut des nouveaux utilisateurs | Configuration de l'espace de travail `permissions.default_role` |
| Restreindre la documentation publiée aux membres de l'équipe uniquement | Variable d'environnement `PUBLISH_REQUIRE_AUTH=true` |
| Restreindre une page à des rôles spécifiques (éditeur web) | Frontmatter de page `access: restricted` |
| Désactiver la télémétrie | `DOCPLATFORM_TELEMETRY=off` |
