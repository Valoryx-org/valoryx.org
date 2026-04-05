---
title: Rôles et permissions
description: Configurez la hiérarchie à 5 rôles de DocPlatform, le contrôle d'accès au niveau de l'espace de travail, les permissions de l'éditeur et les limites de sièges par plan.
weight: 3
---

# Rôles et permissions

DocPlatform utilise un contrôle d'accès basé sur les rôles (RBAC) alimenté par un RBAC personnalisé, un moteur d'autorisation in-process. Les permissions sont évaluées en moins de 0,1 ms par vérification, sans aucun service externe.

## Hiérarchie des rôles

DocPlatform définit 5 rôles publics dans une hiérarchie stricte. Les rôles supérieurs héritent de toutes les permissions des rôles inférieurs.

```
Super Admin         ← Propriétaire de l'org / créateur du compte (rôle public le plus élevé)
    │
Admin               ← Gérer les paramètres de l'espace de travail, membres, git, thème
    │
Editor              ← Créer et modifier des pages (configurable par workspace)
    │
Commenter           ← Consulter les pages, laisser des commentaires
    │
Viewer              ← Consulter les pages uniquement
```

> **Platform Owner** est un rôle interne réservé aux opérateurs auto-hébergés pour la maintenance de la plateforme (migrations de base de données, gestion des licences, configuration système). Il n'apparaît pas dans l'interface ou l'API et ne fait pas partie de la hiérarchie publique des rôles.

### Matrice des permissions

| Permission | Viewer | Commenter | Editor | Admin | Super Admin |
|---|---|---|---|---|---|
| Consulter les pages | Oui | Oui | Oui | Oui | Oui |
| Rechercher du contenu | Oui | Oui | Oui | Oui | Oui |
| Laisser des commentaires | | Oui | Oui | Oui | Oui |
| Modifier des pages | | | Oui | Oui | Oui |
| Créer des pages | | | Configurable | Oui | Oui |
| Supprimer des pages | | | Configurable | Oui | Oui |
| Télécharger des assets | | | Oui | Oui | Oui |
| Assigner des membres de l'org au workspace | | | | Oui | Oui |
| Retirer des membres du workspace | | | | Oui | Oui |
| Modifier les rôles des membres (dans le workspace) | | | | Oui | Oui |
| Gérer les paramètres de l'espace de travail | | | | Oui | Oui |
| Gérer le thème et la navigation | | | | Oui | Oui |
| Inviter des utilisateurs externes dans l'org | | | | | Oui |
| Créer/supprimer des espaces de travail | | | | | Oui |
| Configurer le dépôt git distant | | | | | Oui |
| Gérer la facturation et l'abonnement | | | | | Oui |
| Accéder à tous les espaces de travail | | | | | Oui |
| Gérer les paramètres au niveau de l'org | | | | | Oui |

### Permissions configurables de l'éditeur

Les capacités de l'éditeur peuvent être ajustées par workspace. Les administrateurs et super administrateurs configurent ces options dans les paramètres du workspace :

| Paramètre | Par défaut | Description |
|---|---|---|
| `editor_can_create_pages` | `true` | Les éditeurs peuvent créer de nouvelles pages |
| `editor_can_delete_pages` | `false` | Les éditeurs peuvent supprimer des pages |

Lorsqu'une permission est désactivée, les éditeurs voient l'action grisée dans l'interface et reçoivent `403 Forbidden` de l'API.

## Attribuer des rôles

### Premier utilisateur (Super Admin)

Le premier utilisateur à s'inscrire sur une nouvelle instance DocPlatform reçoit automatiquement le rôle **Super Admin**. Cela ne se produit qu'une seule fois — les inscriptions suivantes ne reçoivent aucun rôle d'espace de travail tant qu'ils ne sont pas invités.

Le Super Admin est le propriétaire de l'org et le créateur du compte. Il a le contrôle total sur tous les espaces de travail, la facturation, les connexions git et les invitations d'utilisateurs externes.

### Inviter des utilisateurs externes

Seul le **Super Admin** peut inviter des utilisateurs externes dans l'organisation :

**Interface web :** Paramètres de l'org → Membres → Inviter un utilisateur externe

**API :**

```bash
curl -X POST http://localhost:3000/api/v1/org/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "default_role": "editor"
  }'
```

L'utilisateur invité rejoint l'org et peut ensuite être assigné à des espaces de travail par n'importe quel Admin ou Super Admin.

### Assigner des membres aux espaces de travail

Les **Admins** assignent les membres existants de l'org à leur espace de travail. Les Admins ne peuvent pas inviter d'utilisateurs externes — seul le Super Admin peut le faire.

**Interface web :** Workspace Settings → Members → Ajouter un membre → sélectionner parmi les membres de l'org → sélectionner le rôle

**API :**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/:id/members \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "01HY5K3M7Q8P",
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

Valeurs disponibles : `viewer`, `commenter`, `editor`, `admin`

## Contrôle d'accès au niveau de la page

Supplantez les permissions au niveau de l'espace de travail sur des pages individuelles en utilisant le frontmatter. Les règles d'accès du frontmatter **restreignent** dans le cadre du rôle d'un utilisateur — elles n'accordent jamais de permissions au-delà du rôle.

### Syntaxe du contrôle d'accès

Utilisez des règles d'accès basées sur les rôles et les utilisateurs pour contrôler qui peut accéder à une page :

```yaml
---
title: Internal Security Policy
access:
  roles: ["security-team", "engineering-leads"]
  users: ["@01HY5K3M7Q8P"]
---
```

| Champ | Type de valeur | Description |
|---|---|---|
| `access.roles` | liste de noms de rôles | Rôles pouvant accéder à cette page |
| `access.users` | liste de `@user_id` | Utilisateurs individuels pouvant accéder à cette page |

**Règles :**
- Préfixez les identifiants utilisateur avec `@` pour cibler des utilisateurs individuels
- Le Super Admin et l'Admin ont toujours accès indépendamment des règles du frontmatter
- Le frontmatter ne peut que **restreindre** — une page ne peut pas accorder un accès au-delà du rôle de l'utilisateur dans l'espace de travail

### Exemples

**Page publique** (par défaut — tous les membres de l'espace de travail peuvent consulter) :

```yaml
---
title: Getting Started
---
```

**Restreinte à des équipes spécifiques :**

```yaml
---
title: Infrastructure Runbook
access:
  roles: ["security-team", "sre-team"]
---
```

**Restreinte avec accès utilisateur individuel :**

```yaml
---
title: Budget Proposal
access:
  roles: ["finance-team"]
  users: ["@01HY5K3M7Q8P"]
---
```

### Ce que signifie l'accès restreint

Lorsqu'une page a des règles `access` :

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

| Rôle | Niveau | Portée | Action minimale |
|---|---|---|---|
| Viewer | 10 | Workspace | `read` |
| Commenter | 20 | Workspace | `read`, `comment` |
| Editor | 30 | Workspace | `read`, `comment`, `edit` (+ `create`/`delete` si activé) |
| Admin | 40 | Workspace | Toutes les actions du workspace |
| Super Admin | — | Org | Contourne toutes les vérifications du workspace |

> Le Super Admin est un **rôle au niveau de l'org** — il contourne entièrement les vérifications de permissions du workspace plutôt que d'avoir un niveau numérique. Le Platform Owner est un flag booléen sur l'enregistrement utilisateur qui contourne toutes les vérifications globalement.

Les actions ont des niveaux minimaux : `read` nécessite le niveau 10+, `comment` nécessite 20+, `edit` nécessite 30+, `write`/`delete` nécessite 40+ (les éditeurs obtiennent `edit` mais pas `write`/`delete` sauf si les flags configurables sont activés), `admin` nécessite 40+. Le niveau du rôle d'un utilisateur est comparé au niveau minimum de l'action.

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
(custom RBAC check: user + role + resource + action)
    │
    ├── Allowed → proceed to handler
    │
    └── Denied → 403 Forbidden
```

### Flux d'évaluation en 5 étapes

1. **L'utilisateur est-il Platform Owner ?** → AUTORISER (bypass global)
2. **L'utilisateur est-il Org Super Admin pour l'organisation de ce workspace ?** → AUTORISER (bypass au niveau org)
3. **Rechercher le rôle workspace de l'utilisateur** → si non membre, REFUSER
4. **Le niveau du rôle atteint-il le minimum requis pour l'action ?** → comparer `role_level >= action_min_level`, plus les flags de permissions éditeur
5. **La page a-t-elle des règles d'accès dans le frontmatter ?** → vérifier `access.roles`/`access.users`, RESTREINDRE dans le rôle

Le frontmatter RESTREINT dans le cadre du rôle, il n'ACCORDE jamais au-delà. Un frontmatter malformé passe par défaut en **mode strict** — page restreinte aux Admins uniquement.

### Performances

| Métrique | Valeur |
|---|---|
| **Moteur** | RBAC personnalisé (in-process, en mémoire) |
| **Temps d'évaluation** | < 0,1 ms par vérification |
| **Cache** | Versionné (auto-invalidé lors d'un changement de rôle ou de permission) |
| **Stockage des politiques** | SQLite (chargé en mémoire au démarrage) |

## Mise en cache des permissions

Les politiques RBAC sont chargées depuis SQLite en mémoire au démarrage du serveur. Les modifications des rôles ou des déclarations d'accès dans le frontmatter déclenchent une invalidation du cache :

1. Un administrateur modifie le rôle d'un utilisateur → la version du cache de permissions est incrémentée
2. Un éditeur met à jour le frontmatter d'une page avec de nouvelles règles `access` → le cache est invalidé pour cette page
3. La prochaine vérification de permission charge la politique fraîche depuis SQLite

Le cache est versionné, pas basé sur le temps — il n'y a pas de fenêtre de permission obsolète.

## Modèles courants

### Documentation publique en lecture seule avec pages internes restreintes

```yaml
# La plupart des pages : pas de règles d'accès (ouvertes à tous les membres du workspace)

# Pages internes : restreintes
---
title: Incident Response Playbook
access:
  roles: ["sre-team", "admin"]
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

Le Super Admin a accès à tous les espaces de travail pour une visibilité transversale.

## Plans et limites de sièges

### Comptage des sièges

Les rôles **Super Admin**, **Admin** et **Editor** comptent tous dans la limite de sièges `max_editors` du plan. Les rôles Commenter et Viewer sont **illimités sur tous les plans** et ne comptent jamais dans une limite de sièges.

Lorsque la limite de sièges est atteinte, de nouveaux membres de l'org peuvent toujours être invités — mais ils ne peuvent être assignés qu'aux rôles Commenter ou Viewer jusqu'à ce qu'un siège soit libéré.

### Community Edition

La Community Edition est gratuite et auto-hébergée, sans clé de licence requise :

| Ressource | Limite |
|---|---|
| Espaces de travail | Illimité |
| Éditeurs (Super Admin + Admin + Editor) | Illimité |
| Viewers et Commenters | Illimité |
| Pages | Illimité |

### Plans Cloud

| | Free | Team | Business |
|---|---|---|---|
| **Espaces de travail** | 1 | 5 | 15 |
| **Sièges** (Super Admin + Admin + Editor) | 3 | 15 | 50 |
| **Viewers et Commenters** | Illimité | Illimité | Illimité |
| **Pages** | Illimité | Illimité | Illimité |

> Besoin de plus ? [Contactez les ventes](https://valoryx.org/contact) pour les plans Enterprise avec des limites personnalisées, SSO et SLA.

Pour les détails complets de facturation, consultez [Facturation et plans](../guides/billing.md).

## Dépannage

### « 403 Forbidden » sur une page à laquelle je devrais avoir accès

1. Vérifiez votre rôle : Profil → Workspace Membership
2. Vérifiez le frontmatter de la page : `access.roles` inclut-il votre rôle ?
3. Demandez à un administrateur de l'espace de travail de vérifier votre attribution de rôle
4. Si vous êtes un éditeur, vérifiez si l'action requiert que `editor_can_create_pages` ou `editor_can_delete_pages` soit activé

### Les changements de permissions ne prennent pas effet

Les changements de permissions devraient être instantanés (l'invalidation du cache est synchrone). Si ce n'est pas le cas :

1. Déconnectez-vous et reconnectez-vous (rafraîchissez vos tokens JWT)
2. Vérifiez les journaux du serveur pour des erreurs d'invalidation du cache
3. Exécutez `docplatform doctor` pour vérifier la santé du système de permissions

### Le premier utilisateur n'est pas Super Admin

Cela se produit si le premier utilisateur s'inscrit alors que la base de données contient déjà des enregistrements utilisateur (par ex. d'une installation précédente). Pour corriger :

1. Arrêtez le serveur
2. Supprimez la base de données : `rm {DATA_DIR}/data.db`
3. Démarrez le serveur et inscrivez-vous à nouveau

Cela réinitialise toutes les données. À utiliser uniquement sur des installations neuves.

### « Limite de sièges atteinte » lors de l'invitation d'un membre

La limite `max_editors` du plan a été atteinte. Options :

1. Rétrograder un Admin ou éditeur existant en Commenter ou Viewer pour libérer un siège
2. Inviter le nouvel utilisateur en tant que Commenter ou Viewer (ceux-ci sont illimités)
3. Mettre à niveau votre plan pour obtenir plus de sièges
