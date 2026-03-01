---
title: Référence de l'API REST
description: Référence complète de l'API REST de DocPlatform — authentification, gestion de contenu, espaces de travail, recherche et endpoints d'administration.
weight: 1
---

# Référence de l'API REST

DocPlatform expose une API JSON RESTful à `/api/v1/`. Tous les endpoints nécessitent une authentification sauf indication contraire.

## URL de base

```
http://localhost:3000/api/v1
```

## Authentification

La plupart des endpoints nécessitent un token d'accès JWT dans l'en-tête `Authorization` :

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

Obtenez des tokens via les endpoints de connexion ou OIDC.

### Cycle de vie des tokens

| Token | Durée de vie | Objectif |
|---|---|---|
| Token d'accès | 15 minutes | Authentification API |
| Token de rafraîchissement | 30 jours | Obtenir de nouveaux tokens d'accès |

---

## Endpoints d'authentification

### Inscription

```
POST /api/v1/auth/register
```

Créer un nouveau compte utilisateur. Le premier utilisateur devient SuperAdmin.

**Requête :**

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Réponse :** `201 Created`

```json
{
  "user": {
    "id": "01HJK...",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "role": "superadmin"
  },
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

### Connexion

```
POST /api/v1/auth/login
```

S'authentifier avec e-mail et mot de passe.

**Requête :**

```json
{
  "email": "jane@example.com",
  "password": "secure-password-here"
}
```

**Réponse :** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

**Erreurs :**

| Code | Description |
|---|---|
| `401` | Identifiants invalides |
| `429` | Trop de tentatives de connexion (limitation de débit) |

### Rafraîchir le token

```
POST /api/v1/auth/refresh
```

Échanger un token de rafraîchissement contre un nouveau token d'accès. Le token de rafraîchissement est roté (l'ancien est invalidé).

**Requête :**

```json
{
  "refresh_token": "eyJhbG..."
}
```

**Réponse :** `200 OK`

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

### Demande de réinitialisation de mot de passe

```
POST /api/v1/auth/password-reset
```

Demander un token de réinitialisation de mot de passe. Avec SMTP configuré, un e-mail est envoyé. Sans SMTP, le token est enregistré sur stdout.

**Requête :**

```json
{
  "email": "jane@example.com"
}
```

**Réponse :** `200 OK` (toujours, que l'e-mail existe ou non — empêche l'énumération)

### Confirmation de réinitialisation de mot de passe

```
POST /api/v1/auth/password-reset/confirm
```

Définir un nouveau mot de passe à l'aide d'un token de réinitialisation.

**Requête :**

```json
{
  "token": "reset-token-here",
  "new_password": "new-secure-password"
}
```

**Réponse :** `200 OK`

---

## Endpoints de contenu

Tous les endpoints de contenu sont limités à un espace de travail.

### Lister les pages

```
GET /api/v1/workspaces/{workspace_id}/pages
```

Renvoie toutes les pages que l'utilisateur courant a la permission de consulter.

**Paramètres de requête :**

| Paramètre | Type | Description |
|---|---|---|
| `parent_id` | string | Filtrer par page parente (pour la navigation en arbre) |
| `tag` | string | Filtrer par tag |
| `published` | boolean | Filtrer par statut de publication |
| `limit` | int | Résultats max (par défaut : 100) |
| `offset` | int | Décalage de pagination |

**Réponse :** `200 OK`

```json
{
  "pages": [
    {
      "id": "01HJK...",
      "title": "Getting Started",
      "slug": "getting-started",
      "description": "Install and configure DocPlatform.",
      "path": "getting-started.md",
      "tags": ["guide"],
      "published": true,
      "access": "public",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-16T14:30:00Z",
      "author_id": "01HJK..."
    }
  ],
  "total": 42,
  "limit": 100,
  "offset": 0
}
```

### Obtenir une page

```
GET /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Réponse :** `200 OK`

```json
{
  "id": "01HJK...",
  "title": "Getting Started",
  "slug": "getting-started",
  "description": "Install and configure DocPlatform.",
  "path": "getting-started.md",
  "content": "# Getting Started\n\nThis guide walks you through...",
  "content_hash": "sha256:abc123...",
  "tags": ["guide"],
  "published": true,
  "access": "public",
  "parent_id": null,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-16T14:30:00Z",
  "author_id": "01HJK..."
}
```

**Erreurs :**

| Code | Description |
|---|---|
| `403` | Permissions insuffisantes |
| `404` | Page non trouvée |

### Créer une page

```
POST /api/v1/workspaces/{workspace_id}/pages
```

**Requête :**

```json
{
  "title": "New Page",
  "slug": "new-page",
  "content": "# New Page\n\nContent here...",
  "description": "Description for search and SEO.",
  "tags": ["guide"],
  "published": false,
  "parent_id": null
}
```

**Réponse :** `201 Created` — renvoie l'objet page complet.

### Mettre à jour une page

```
PUT /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Requête :**

```json
{
  "title": "Updated Title",
  "content": "# Updated Title\n\nUpdated content...",
  "content_hash": "sha256:abc123..."
}
```

Le champ `content_hash` active la concurrence optimiste. Si le hash ne correspond pas à la version actuelle, le serveur renvoie `409 Conflict`.

**Réponse :** `200 OK` — renvoie l'objet page mis à jour.

**Erreurs :**

| Code | Description |
|---|---|
| `409` | Le hash du contenu ne correspond pas (modification concurrente détectée) |

### Supprimer une page

```
DELETE /api/v1/workspaces/{workspace_id}/pages/{page_id}
```

**Réponse :** `204 No Content`

---

## Endpoints d'espace de travail

### Lister les espaces de travail

```
GET /api/v1/workspaces
```

Renvoie les espaces de travail dont l'utilisateur courant est membre.

### Créer un espace de travail

```
POST /api/v1/workspaces
```

Nécessite le rôle SuperAdmin.

**Requête :**

```json
{
  "name": "API Docs",
  "slug": "api-docs",
  "git_remote": "git@github.com:org/api-docs.git",
  "git_branch": "main"
}
```

### Membres de l'espace de travail

```
GET /api/v1/workspaces/{workspace_id}/members
POST /api/v1/workspaces/{workspace_id}/invitations
DELETE /api/v1/workspaces/{workspace_id}/members/{user_id}
PUT /api/v1/workspaces/{workspace_id}/members/{user_id}/role
```

---

## Recherche

```
GET /api/v1/workspaces/{workspace_id}/search?q={query}
```

**Paramètres de requête :**

| Paramètre | Type | Description |
|---|---|---|
| `q` | string | Requête de recherche (obligatoire) |
| `tag` | string | Filtrer par tag |
| `limit` | int | Résultats max (par défaut : 20) |

**Réponse :** `200 OK`

```json
{
  "results": [
    {
      "page_id": "01HJK...",
      "title": "Git Integration",
      "description": "Bidirectional git sync...",
      "path": "guides/git-integration.md",
      "score": 0.95,
      "highlights": [
        "...bidirectional <mark>git sync</mark> lets your team..."
      ]
    }
  ],
  "total": 5,
  "query": "git sync",
  "took_ms": 12
}
```

Les résultats sont filtrés par permissions — les utilisateurs ne voient que les pages auxquelles ils ont accès.

---

## Synchronisation git

### Déclencher la synchronisation

```
POST /api/v1/workspaces/{workspace_id}/sync
```

Déclencher manuellement un pull git + réconciliation. Nécessite le rôle Admin.

**Réponse :** `200 OK`

```json
{
  "status": "completed",
  "changes": {
    "added": 2,
    "updated": 1,
    "deleted": 0
  }
}
```

### Endpoints webhook

```
POST /api/v1/webhooks/github
POST /api/v1/webhooks/gitlab
POST /api/v1/webhooks/bitbucket
```

Ces endpoints reçoivent les payloads d'événements push des hébergeurs git. Aucun en-tête d'authentification requis — ils valident en utilisant le secret partagé `GIT_WEBHOOK_SECRET`.

---

## Santé

Ces endpoints ne nécessitent pas d'authentification.

```
GET /health    → 200 OK { "status": "ok" }
GET /ready     → 200 OK { "status": "ready", "db": "ok", "search": "ok" }
```

---

## Format d'erreur

Toutes les réponses d'erreur utilisent un format cohérent :

```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Content hash mismatch. The page was modified by another user.",
    "details": {
      "current_hash": "sha256:def456...",
      "provided_hash": "sha256:abc123..."
    }
  }
}
```

### Codes d'erreur courants

| HTTP | Code | Description |
|---|---|---|
| `400` | `BAD_REQUEST` | Corps de requête ou paramètres invalides |
| `401` | `UNAUTHORIZED` | Authentification manquante ou invalide |
| `403` | `FORBIDDEN` | Permissions insuffisantes |
| `404` | `NOT_FOUND` | Ressource non trouvée |
| `409` | `CONFLICT` | Modification concurrente détectée |
| `429` | `RATE_LIMITED` | Trop de requêtes |
| `500` | `INTERNAL_ERROR` | Erreur serveur (vérifiez les journaux) |

## Pagination

Les endpoints de listage de contenu utilisent une **pagination par curseur** avec des ULIDs pour des résultats stables même lorsque du contenu est ajouté ou supprimé.

**Paramètres de requête :**

| Paramètre | Type | Par défaut | Description |
|---|---|---|---|
| `cursor` | string | — | ULID du dernier élément de la page précédente. Omettez pour la première page. |
| `limit` | int | 20 | Nombre de résultats par page (max : 100) |

**Métadonnées de réponse :**

```json
{
  "data": [...],
  "next_cursor": "01HJK...",
  "has_more": true
}
```

Passez `next_cursor` comme paramètre `cursor` dans la requête suivante. Lorsque `has_more` est `false`, vous avez atteint la fin.

---

## Upload d'assets

```
POST /api/v1/workspaces/{workspace_id}/assets
```

Télécharger des images et fichiers vers un espace de travail. Les assets sont stockés dans le répertoire `assets/` de l'espace de travail et commités dans git si la synchronisation est activée.

**Requête :** `multipart/form-data` avec un champ `file`.

**Limites :**

| Contrainte | Valeur |
|---|---|
| Taille maximale du fichier | 10 Mo |
| Types acceptés | PNG, JPG, GIF, SVG, WebP, PDF |

**Réponse :** `201 Created`

```json
{
  "path": "assets/screenshot-2025-01-15.png",
  "url": "/api/v1/workspaces/{workspace_id}/assets/screenshot-2025-01-15.png",
  "size": 245760,
  "content_type": "image/png"
}
```

---

## Résolution des conflits

### Lister les conflits

```
GET /api/v1/workspaces/{workspace_id}/conflicts
```

**Réponse :** `200 OK`

```json
{
  "workspace_id": "01HJK...",
  "sync_status": "conflict",
  "conflicts": [
    {
      "path": "guides/editor.md",
      "ours_hash": "abc123...",
      "theirs_hash": "def456...",
      "page_id": "01HJK...",
      "timestamp": "20250115T103045Z"
    }
  ]
}
```

### Télécharger une version de conflit

```
GET /api/v1/conflicts/{page_id}/{timestamp}/{version}
```

Le paramètre `version` est soit `ours` (local) soit `theirs` (distant).

**Réponse :** `200 OK` avec `Content-Type: text/markdown` — contenu brut du fichier.

### Résoudre un conflit

```
POST /api/v1/conflicts/{page_id}/{timestamp}/resolve
```

Supprime les artefacts de conflit après résolution manuelle.

**Réponse :** `200 OK`

```json
{
  "message": "Conflict resolved",
  "page_id": "01HJK..."
}
```

---

## WebSocket

### Obtenir un ticket de connexion

```
POST /api/v1/auth/ws-ticket
```

Les connexions WebSocket utilisent un système de ticket à usage unique pour éviter d'exposer les tokens JWT dans les URLs.

**Réponse :** `200 OK`

```json
{
  "ticket": "random-ticket-value",
  "expires_in": 30
}
```

Le ticket est valide pendant **30 secondes** et ne peut être utilisé qu'une seule fois. Connectez-vous via :

```
ws://localhost:3000/ws?ticket={ticket}
```

### Événements serveur

| Type d'événement | Payload | Quand |
|---|---|---|
| `page-created` | `{workspace_id, path, actor}` | Une nouvelle page est créée |
| `page-updated` | `{workspace_id, path, actor}` | Une page est modifiée |
| `page-deleted` | `{workspace_id, path, actor}` | Une page est supprimée |
| `presence-join` | `{workspace_id, user_id}` | Un utilisateur se connecte |
| `presence-leave` | `{workspace_id, user_id}` | Un utilisateur se déconnecte (timeout de 90s) |
| `sync-status` | `{workspace_id, status}` | Changement du statut de synchronisation git |
| `conflict-detected` | `{workspace_id, path}` | Conflit de merge git détecté |
| `bulk-sync` | `{workspace_id, changed_count, paths[]}` | Plusieurs fichiers synchronisés (>20 fichiers) |

### Messages client

```json
{"type": "subscribe", "workspace_id": "01HJK..."}
{"type": "unsubscribe", "workspace_id": "01HJK..."}
```

---

## En-têtes de sécurité

DocPlatform définit les en-têtes suivants sur toutes les réponses :

| En-tête | Valeur |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| `X-Request-ID` | ULID (unique par requête, inclus dans les réponses d'erreur et les journaux) |

La documentation publiée définit en plus :

| En-tête | Valeur |
|---|---|
| `Cache-Control` | `public, max-age=300` |
| `ETag` | Hash du contenu de la page rendue |

---

## Limitation de débit

| Catégorie d'endpoints | Community Edition |
|---|---|
| Opérations de lecture | 100 / minute par utilisateur |
| Opérations d'écriture | 20 / minute par utilisateur |
| Recherche | 30 / minute par utilisateur |
| Authentification (connexion, inscription, réinitialisation) | 5 / minute par IP |
| Webhooks git | 10 / minute par espace de travail |
| Documentation publiée (publique) | 1 000 / minute par IP |

Les réponses de limitation de débit incluent les en-têtes `Retry-After` (secondes) et `X-RateLimit-Reset` (horodatage Unix).
