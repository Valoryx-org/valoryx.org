---
title: Équipes et collaboration
description: Invitez votre équipe, attribuez des rôles et collaborez sur la documentation avec présence en temps réel et journaux d'audit.
weight: 4
---

# Équipes et collaboration

DocPlatform est conçu pour la documentation en équipe. Invitez des membres, attribuez des rôles granulaires et suivez chaque modification grâce à un journal d'audit complet.

## Appartenance à l'espace de travail

Chaque utilisateur appartient à un ou plusieurs espaces de travail avec un rôle spécifique. Les rôles déterminent les actions qu'un utilisateur peut effectuer.

### Inviter des membres

**Via l'interface web :**

1. Ouvrez **Workspace Settings** → **Members**
2. Cliquez sur **Invite Member**
3. Saisissez l'adresse e-mail de la personne
4. Sélectionnez un rôle
5. Cliquez sur **Send**

Si SMTP est configuré, un e-mail d'invitation est envoyé avec un lien unique. Sans SMTP, le lien d'invitation est affiché à l'écran — copiez-le et partagez-le manuellement.

**Via l'API :**

```bash
curl -X POST http://localhost:3000/api/v1/workspaces/{workspace-id}/invitations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "colleague@example.com",
    "role": "editor"
  }'
```

### Retirer des membres

Les administrateurs de l'espace de travail peuvent retirer des membres depuis **Settings** → **Members** → cliquez sur l'utilisateur → **Remove**.

Le retrait d'un membre révoque immédiatement son accès. Ses modifications passées et ses entrées dans le journal d'audit sont conservées.

### Modifier les rôles

Cliquez sur le rôle actuel d'un membre pour le modifier. Les changements de rôle prennent effet immédiatement — les sessions actives sont mises à jour lors du prochain appel API.

## Rôles

DocPlatform utilise une hiérarchie de rôles à 6 niveaux. Les rôles supérieurs héritent de toutes les permissions des rôles inférieurs.

```
SuperAdmin
    └── WorkspaceAdmin
            └── Admin
                  └── Editor
                        └── Commenter
                              └── Viewer
```

| Rôle | Portée | Capacités |
|---|---|---|
| **Viewer** | Espace de travail | Consulter les pages et rechercher |
| **Commenter** | Espace de travail | Consulter + laisser des commentaires sur les pages |
| **Editor** | Espace de travail | Consulter + commenter + créer, modifier, supprimer des pages |
| **Admin** | Espace de travail | Editor + gérer les membres et les rôles |
| **WorkspaceAdmin** | Espace de travail | Admin + gérer les paramètres de l'espace de travail, la configuration git, le thème |
| **SuperAdmin** | Plateforme | Accès complet à tous les espaces de travail + paramètres de la plateforme |

### Rôle par défaut pour les nouveaux membres

Configurez le rôle par défaut attribué lorsque les utilisateurs acceptent une invitation :

```yaml
# .docplatform/config.yaml
permissions:
  default_role: viewer
```

### Accès au niveau de la page

Restreignez des pages individuelles à des rôles spécifiques en utilisant le frontmatter :

```yaml
---
title: Internal Runbook
access: restricted
allowed_roles: [admin, editor]
---
```

Les pages avec `access: restricted` sont invisibles pour les utilisateurs sans le rôle requis — elles n'apparaissent pas dans les résultats de recherche, la navigation ni la documentation publiée.

## Présence en temps réel

Lorsque plusieurs utilisateurs sont actifs dans le même espace de travail, l'éditeur web montre qui est en ligne :

- **Indicateurs dans la barre latérale** — points colorés à côté des pages consultées ou éditées par d'autres utilisateurs
- **Pile d'avatars** — avatars des utilisateurs dans l'en-tête de la page montrant qui d'autre consulte la page actuelle

La présence est alimentée par des connexions WebSocket et se met à jour en temps réel.

### Fonctionnement de la présence

| Paramètre | Valeur |
|---|---|
| **Protocole** | WebSocket (authentifié via un ticket à usage unique) |
| **Intervalle de heartbeat** | Toutes les 30 secondes |
| **Délai d'expulsion** | 90 secondes sans heartbeat |
| **Événements** | `presence-join` (première connexion), `presence-leave` (timeout ou déconnexion) |
| **Buffer** | 256 événements par espace de travail (empêche la contre-pression) |

La connexion WebSocket transmet également des événements de contenu en temps réel :

| Événement | Quand |
|---|---|
| `page-created` | Une nouvelle page est créée (toute source) |
| `page-updated` | Une page est modifiée (toute source) |
| `page-deleted` | Une page est supprimée |
| `sync-status` | Le statut de synchronisation git change (synced, ahead, behind, conflict) |
| `conflict-detected` | Un conflit de merge git est détecté |
| `bulk-sync` | 20+ fichiers synchronisés en une opération (notification unique, pas par fichier) |

### Édition concurrente

DocPlatform ne prend pas en charge l'édition collaborative en temps réel (style Google Docs). Si deux utilisateurs modifient la même page simultanément :

1. La première sauvegarde réussit
2. La seconde sauvegarde déclenche une **détection de conflit** (HTTP 409)
3. Les deux versions sont préservées pour résolution manuelle

Pour éviter les conflits :

- Utilisez des conventions de propriété de page (un seul rédacteur par page à la fois)
- Les indicateurs de présence aident votre équipe à coordonner qui édite quoi
- Pour les équipes à forte concurrence, envisagez des intervalles de synchronisation git plus courts

## Journal d'audit

Chaque modification de contenu est enregistrée avec :

| Champ | Description |
|---|---|
| **Horodatage** | Quand l'action s'est produite (UTC) |
| **Utilisateur** | Qui a effectué l'action (e-mail, identifiant utilisateur) |
| **Opération** | Ce qui s'est passé : `create`, `update`, `delete`, `publish`, `unpublish` |
| **Page** | Quelle page a été affectée (ID, titre, chemin) |
| **Source** | D'où vient la modification : `web_editor`, `git_sync`, `api` |
| **Hash du contenu** | SHA-256 du nouveau contenu (pour vérification) |

### Consulter le journal d'audit

Accédez au journal d'audit depuis **Workspace Settings** → **Activity**.

Filtrez par :

- **Utilisateur** — voir toutes les modifications d'un membre spécifique de l'équipe
- **Page** — voir l'historique complet d'une page spécifique
- **Plage de dates** — restreindre à une fenêtre temporelle
- **Type d'opération** — filtrer par créations, modifications, suppressions, etc.

### Types d'actions d'audit

Le champ `action` dans le journal d'audit utilise une notation pointée pour un filtrage précis :

| Action | Description |
|---|---|
| `page.create` | Nouvelle page créée |
| `page.update` | Contenu ou frontmatter de la page modifié |
| `page.delete` | Page supprimée |
| `page.publish` | Page publiée (rendue publique) |
| `page.unpublish` | Page dépubliée |
| `auth.login` | Utilisateur connecté |
| `auth.register` | Nouvel utilisateur enregistré |
| `auth.password_reset` | Réinitialisation de mot de passe effectuée |
| `workspace.create` | Nouvel espace de travail créé |
| `workspace.member_add` | Utilisateur ajouté à l'espace de travail |
| `workspace.member_remove` | Utilisateur retiré de l'espace de travail |
| `workspace.role_change` | Rôle de l'utilisateur modifié |

### Rétention

Les journaux d'audit sont stockés dans SQLite avec vos données habituelles. Ils sont inclus dans les sauvegardes quotidiennes. La rétention par défaut est de 1 an (configurable). Une tâche de nettoyage hebdomadaire supprime les entrées plus anciennes que la période de rétention.

## Notifications par e-mail

Avec SMTP configuré, DocPlatform envoie des e-mails transactionnels pour :

| Événement | Destinataire | Contenu |
|---|---|---|
| **Invitation à l'espace de travail** | Utilisateur invité | Lien d'adhésion + nom de l'espace de travail |
| **Réinitialisation de mot de passe** | Utilisateur demandeur | Token de réinitialisation à usage unique |

DocPlatform n'envoie pas de notifications par e-mail pour les modifications de contenu. Les mises à jour WebSocket en temps réel remplissent ce rôle pour les utilisateurs actifs, et le journal d'audit couvre la revue historique.

### Configuration SMTP

```bash
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_FROM=docs@yourcompany.com
export SMTP_USERNAME=docs@yourcompany.com
export SMTP_PASSWORD=your-app-password
```

Sans SMTP, les liens d'invitation et les tokens de réinitialisation de mot de passe sont affichés sur stdout (journaux du serveur).

## Conseils pour les workflows d'équipe

- **Un seul rédacteur par page** — utilisez les indicateurs de présence pour éviter les conflits
- **Les éditeurs rédigent, les admins publient** — séparez les responsabilités grâce aux rôles
- **Utilisez des tags pour la propriété** — taguez les pages avec `owner:jane` pour clarifier les responsabilités
- **Git pour les workflows de revue** — poussez les modifications vers une branche, ouvrez une PR, fusionnez après revue
- **Auditez avant de publier** — consultez le journal d'audit pour détecter les modifications inattendues avant de rendre le contenu public
