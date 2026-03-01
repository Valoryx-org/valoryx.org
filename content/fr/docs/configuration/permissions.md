---
title: Rôles et permissions
description: Configurez la hiérarchie de rôles à 6 niveaux de DocPlatform, le contrôle d'accès au niveau de la page et la mise en cache des permissions.
weight: 3
---

# Rôles et permissions

DocPlatform utilise un contrôle d'accès basé sur les rôles (RBAC) alimenté par Casbin, un moteur d'autorisation in-process. Les permissions sont évaluées en moins de 0,1 ms par vérification, sans aucun service externe.

## Hiérarchie des rôles

DocPlatform définit 6 rôles dans une hiérarchie stricte. Les rôles supérieurs héritent de toutes les permissions des rôles inférieurs.

```
SuperAdmin          ← Full platform access (all workspaces)
    │
WorkspaceAdmin      ← Manage workspace settings, git config, theme
    │
Admin               ← Manage members, assign roles
    │
Editor              ← Create, edit, delete pages
    │
Commenter           ← View pages, leave comments
    │
Viewer              ← View pages only
```

### Matrice des permissions

| Permission | Viewer | Commenter | Editor | Admin | WS Admin | Super Admin |
|---|---|---|---|---|---|---|
| Consulter les pages | Oui | Oui | Oui | Oui | Oui | Oui |
| Rechercher du contenu | Oui | Oui | Oui | Oui | Oui | Oui |
| Laisser des commentaires | | Oui | Oui | Oui | Oui | Oui |
| Créer des pages | | | Oui | Oui | Oui | Oui |
| Modifier des pages | | | Oui | Oui | Oui | Oui |
| Supprimer des pages | | | Oui | Oui | Oui | Oui |
| Télécharger des assets | | | Oui | Oui | Oui | Oui |
| Inviter des membres | | | | Oui | Oui | Oui |
| Retirer des membres | | | | Oui | Oui | Oui |
| Modifier les rôles des membres | | | | Oui | Oui | Oui |
| Gérer les paramètres de l'espace de travail | | | | | Oui | Oui |
| Configurer le dépôt git distant | | | | | Oui | Oui |
| Gérer le thème et la navigation | | | | | Oui | Oui |
| Accéder à tous les espaces de travail | | | | | | Oui |
| Gérer les paramètres de la plateforme | | | | | | Oui |
| Créer/supprimer des espaces de travail | | | | | | Oui |

## Attribuer des rôles

### Premier utilisateur

Le premier utilisateur à s'inscrire sur une nouvelle instance DocPlatform reçoit automatiquement le rôle **SuperAdmin**. Cela ne se produit qu'une seule fois — les inscriptions suivantes ne reçoivent aucun rôle d'espace de travail tant qu'ils ne sont pas invités.

### Membres de l'espace de travail

Lors de l'invitation d'un utilisateur à un espace de travail, spécifiez son rôle :

**Interface web :** Workspace Settings → Members → Invite → sélectionner le rôle

**API :**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{id}/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "role": "editor"
  }'
```

### Rôle par défaut

Définissez le rôle par défaut pour les nouveaux membres qui acceptent une invitation sans rôle spécifique attribué :

```yaml
# .docplatform/config.yaml
permissions:
  default_role: viewer
```

Valeurs disponibles : `viewer`, `commenter`, `editor`, `admin`, `workspace_admin`

## Contrôle d'accès au niveau de la page

Supplantez les permissions au niveau de l'espace de travail sur des pages individuelles en utilisant le frontmatter.

### Niveaux d'accès (éditeur web — utilisateurs internes)

Pour les utilisateurs authentifiés dans l'éditeur web, l'accès au niveau de la page restreint la visibilité par rôle :

| Niveau | Comportement |
|---|---|
| `public` | Tout membre de l'espace de travail peut consulter |
| `workspace` | Tout membre de l'espace de travail peut consulter (identique à `public` pour les utilisateurs authentifiés) |
| `restricted` | Seuls les utilisateurs avec les rôles listés dans `allowed_roles` peuvent consulter |

### Exemples

**Page publique** (par défaut) :

```yaml
---
title: Getting Started
access: public
---
```

**Restreinte aux administrateurs uniquement :**

```yaml
---
title: Infrastructure Runbook
access: restricted
allowed_roles: [admin, workspace_admin]
---
```

### Ce que signifie « restricted »

Lorsqu'une page a `access: restricted` :

- Les utilisateurs sans le rôle requis **ne peuvent pas consulter** la page
- La page **n'apparaît pas** dans les résultats de recherche pour les utilisateurs non autorisés
- L'accès direct par URL renvoie **403 Forbidden**

### Accès à la documentation publiée

Pour le **site de documentation publiée** (`/p/{slug}/...`), le contrôle d'accès fonctionne différemment :

- Toutes les pages publiées sont **publiques par défaut** — aucune connexion requise
- Pour exiger la connexion pour l'ensemble du site publié, définissez [`PUBLISH_REQUIRE_AUTH=true`](environment.md) — cela s'applique à toutes les pages de tous les espaces de travail
- Le contrôle d'accès par page dans la documentation publiée (par ex. rendre une page réservée à l'espace de travail tandis que les autres sont publiques) est prévu pour une future version

> Dans la v0.5, le champ `access` du frontmatter est stocké et disponible pour une utilisation future, mais n'est pas appliqué sur les routes publiées. Utilisez `PUBLISH_REQUIRE_AUTH` pour la restriction d'accès au niveau du site.

## Niveaux de rôles internes

Pour référence, chaque rôle correspond à un niveau numérique. Les niveaux supérieurs héritent de toutes les permissions des niveaux inférieurs :

| Rôle | Niveau | Action minimale |
|---|---|---|
| Viewer | 10 | `read` |
| Commenter | 20 | `read` |
| Editor | 30 | `read`, `write`, `delete` |
| Admin | 40 | `read`, `write`, `delete`, `admin` (gestion des membres) |
| WorkspaceAdmin | 50 | Toutes les actions de l'espace de travail |
| SuperAdmin | 60 | Toutes les actions de la plateforme (contourne toutes les vérifications) |

Les actions ont des niveaux minimaux : `read` nécessite le niveau 10+, `write` nécessite 30+, `delete` nécessite 30+, `admin` nécessite 50+. Le niveau du rôle d'un utilisateur est comparé au niveau minimum de l'action.

## Comment les permissions sont évaluées

```
API Request
    │
    ▼
Auth Middleware
(extract JWT, identify user)
    │
    ▼
Permission Middleware
(Casbin check: user + role + resource + action)
    │
    ├── Allowed → proceed to handler
    │
    └── Denied → 403 Forbidden
```

### Flux d'évaluation

1. **Extraire l'identité de l'utilisateur** depuis le token d'accès JWT
2. **Rechercher le rôle de l'utilisateur** pour l'espace de travail cible
3. **Vérifier la permission au niveau de l'espace de travail** — le rôle autorise-t-il l'action ?
4. **Vérifier l'accès au niveau de la page** — si la page a `access: restricted`, le rôle de l'utilisateur est-il dans `allowed_roles` ?
5. **Renvoyer le résultat** — autorisé ou refusé

### Performances

| Métrique | Valeur |
|---|---|
| **Moteur** | Casbin (in-process, en mémoire) |
| **Temps d'évaluation** | < 0,1 ms par vérification |
| **Cache** | Versionné (auto-invalidé lors d'un changement de rôle ou de permission) |
| **Stockage des politiques** | SQLite (chargé en mémoire au démarrage) |

## Mise en cache des permissions

Les politiques Casbin sont chargées depuis SQLite en mémoire au démarrage du serveur. Les modifications des rôles ou des déclarations d'accès dans le frontmatter déclenchent une invalidation du cache :

1. Un administrateur modifie le rôle d'un utilisateur → la version du cache de permissions est incrémentée
2. Un éditeur met à jour le frontmatter d'une page avec un nouvel `access` ou `allowed_roles` → le cache est invalidé pour cette page
3. La prochaine vérification de permission charge la politique fraîche depuis SQLite

Le cache est versionné, pas basé sur le temps — il n'y a pas de fenêtre de permission obsolète.

## Modèles courants

### Documentation publique en lecture seule avec pages internes restreintes

```yaml
# La plupart des pages : par défaut
access: public

# Pages internes : restreintes
---
title: Incident Response Playbook
access: restricted
allowed_roles: [admin, workspace_admin]
---
```

### L'éditeur crée, l'admin publie

1. Définissez `publishing.default_published: false` dans la configuration de l'espace de travail
2. Les éditeurs créent et modifient des pages (non publiées par défaut)
3. Les administrateurs vérifient et basculent `published: true`

### Espaces de travail par équipe

Créez des espaces de travail séparés par équipe avec des listes de membres indépendantes :

- Espace de travail `eng-docs` → équipe d'ingénierie
- Espace de travail `product-docs` → équipe produit
- Espace de travail `internal-wiki` → tout le monde

Le SuperAdmin a accès à tous les espaces de travail pour une visibilité transversale.

## Limites de la Community Edition

La Community Edition applique les limites de ressources suivantes :

| Ressource | Limite |
|---|---|
| Utilisateurs avec le rôle Editor ou supérieur | 5 |
| Espaces de travail | 3 |
| Viewers et Commenters | Illimité |
| Pages | Illimité |

Ces limites sont codées en dur (aucune clé de licence requise). Les viewers et commenters ne sont jamais comptabilisés dans la limite d'éditeurs. Lorsque la limite d'éditeurs est atteinte, de nouveaux utilisateurs peuvent toujours être invités en tant que Viewers ou Commenters.

## Dépannage

### « 403 Forbidden » sur une page à laquelle je devrais avoir accès

1. Vérifiez votre rôle : Profil → Workspace Membership
2. Vérifiez le frontmatter de la page : `access: restricted` + `allowed_roles` inclut-il votre rôle ?
3. Demandez à un administrateur de l'espace de travail de vérifier votre attribution de rôle

### Les changements de permissions ne prennent pas effet

Les changements de permissions devraient être instantanés (l'invalidation du cache est synchrone). Si ce n'est pas le cas :

1. Déconnectez-vous et reconnectez-vous (rafraîchissez vos tokens JWT)
2. Vérifiez les journaux du serveur pour des erreurs d'invalidation du cache
3. Exécutez `docplatform doctor` pour vérifier la santé du système de permissions

### Le premier utilisateur n'est pas SuperAdmin

Cela se produit si le premier utilisateur s'inscrit alors que la base de données contient déjà des enregistrements utilisateur (par ex. d'une installation précédente). Pour corriger :

1. Arrêtez le serveur
2. Supprimez la base de données : `rm {DATA_DIR}/data.db`
3. Démarrez le serveur et inscrivez-vous à nouveau

Cela réinitialise toutes les données. À utiliser uniquement sur des installations neuves.
