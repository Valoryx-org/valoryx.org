---
title: Authentification
description: Configurez l'authentification locale, la connexion OIDC Google et GitHub, les paramètres JWT et les politiques de mot de passe.
weight: 2
---

# Authentification

DocPlatform prend en charge l'authentification locale (e-mail + mot de passe) par défaut, avec la connexion OIDC Google et GitHub optionnelle pour les équipes utilisant ces fournisseurs.

## Authentification locale (par défaut)

L'authentification locale fonctionne sans aucune configuration. Les utilisateurs s'inscrivent avec un e-mail et un mot de passe, et se connectent avec les mêmes identifiants.

### Fonctionnement

1. **Inscription** — L'utilisateur soumet e-mail + mot de passe. Le mot de passe est haché avec argon2id (algorithme recommandé par l'OWASP 2024).
2. **Connexion** — L'utilisateur soumet ses identifiants. Le serveur vérifie le hash du mot de passe et renvoie des tokens JWT.
3. **Session** — Le token d'accès (RS256, durée de vie de 15 minutes) est envoyé avec chaque requête API. Le token de rafraîchissement (durée de vie de 30 jours) est utilisé pour obtenir de nouveaux tokens d'accès sans ré-authentification.

### Hachage du mot de passe

DocPlatform utilise argon2id avec les paramètres suivants (standard OWASP 2024) :

| Paramètre | Valeur |
|---|---|
| **Algorithme** | argon2id |
| **Mémoire** | 64 Mo |
| **Itérations** | 3 |
| **Parallélisme** | 4 |
| **Longueur du sel** | 16 octets |
| **Longueur de la clé** | 32 octets |

Ces paramètres ne sont pas configurables — ils suivent les bonnes pratiques de sécurité. Les hash de mots de passe sont stockés dans la base de données SQLite et ne quittent jamais le serveur.

### Réinitialisation du mot de passe

Lorsqu'un utilisateur demande une réinitialisation de mot de passe :

- **Avec SMTP configuré** — un lien de réinitialisation à usage unique est envoyé par e-mail à l'utilisateur
- **Sans SMTP** — le token de réinitialisation est affiché sur stdout (journaux du serveur)

```bash
# Vérifier les journaux du serveur pour le token de réinitialisation
docplatform serve 2>&1 | grep "password reset"
```

Le token expire après 1 heure et ne peut être utilisé qu'une seule fois.

## Tokens JWT

DocPlatform émet des JSON Web Tokens RS256 (RSA-SHA256) pour l'authentification.

### Cycle de vie des tokens

```
User logs in
    │
    ▼
┌─────────────────────────────────┐
│ Access Token (15 min)            │  ──►  Sent with every API request
│ Refresh Token (30 days)          │  ──►  Used to get new access tokens
└─────────────────────────────────┘
    │
    │  Access token expires
    ▼
┌─────────────────────────────────┐
│ POST /api/v1/auth/refresh        │
│ Body: { refresh_token: "..." }   │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ New Access Token (15 min)        │  ──►  Old refresh token rotated
│ New Refresh Token (30 days)      │  ──►  Old one invalidated
└─────────────────────────────────┘
```

### Rotation des tokens de rafraîchissement

Chaque fois qu'un token de rafraîchissement est utilisé, un nouveau token de rafraîchissement est émis et l'ancien est invalidé. Cela limite la fenêtre d'exposition en cas de compromission d'un token.

### Configuration

| Variable | Par défaut | Description |
|---|---|---|
| `JWT_SECRET_PATH` | `{DATA_DIR}/jwt-key.pem` | Chemin vers la clé privée RS256 |
| `JWT_ACCESS_TTL` | `900` | Durée de vie du token d'accès (secondes) |
| `JWT_REFRESH_TTL` | `2592000` | Durée de vie du token de rafraîchissement (secondes) |

### Gestion des clés

La paire de clés RS256 est générée automatiquement au premier démarrage si le fichier n'existe pas. Pour effectuer une rotation des clés :

1. Arrêtez le serveur
2. Supprimez le fichier de clé (`{DATA_DIR}/jwt-key.pem`)
3. Démarrez le serveur — une nouvelle clé est générée

Toutes les sessions existantes sont invalidées lors de la rotation des clés. Les utilisateurs doivent se reconnecter.

## Connexion OIDC Google (optionnel)

Permettez aux utilisateurs de se connecter avec leur compte Google.

### Configuration

1. Rendez-vous sur la [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet (ou utilisez un projet existant)
3. Naviguez vers **APIs & Services** → **Credentials**
4. Cliquez sur **Create Credentials** → **OAuth 2.0 Client ID**
5. Type d'application : **Web application**
6. Ajoutez l'URI de redirection autorisée : `https://your-domain.com/api/v1/auth/callback/google`
7. Copiez l'identifiant client et le secret client

Définissez les variables d'environnement :

```bash
export OIDC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
export OIDC_GOOGLE_CLIENT_SECRET=your-client-secret
```

Redémarrez le serveur. Un bouton **Sign in with Google** apparaît sur la page de connexion.

### Provisionnement des utilisateurs

Lorsqu'un utilisateur se connecte via Google pour la première fois :

- Un compte DocPlatform est créé avec son e-mail Google
- Il se voit attribuer le rôle par défaut (`permissions.default_role`) dans tout espace de travail auquel il est invité
- Aucun mot de passe n'est défini (il peut en ajouter un plus tard depuis son profil)

## Connexion OIDC GitHub (optionnel)

Permettez aux utilisateurs de se connecter avec leur compte GitHub.

### Configuration

1. Rendez-vous sur [GitHub Developer Settings](https://github.com/settings/developers)
2. Cliquez sur **New OAuth App**
3. Définissez l'URL de callback d'autorisation : `https://your-domain.com/api/v1/auth/callback/github`
4. Copiez l'identifiant client et générez un secret client

Définissez les variables d'environnement :

```bash
export OIDC_GITHUB_CLIENT_ID=your-client-id
export OIDC_GITHUB_CLIENT_SECRET=your-client-secret
```

Redémarrez le serveur. Un bouton **Sign in with GitHub** apparaît sur la page de connexion.

### Provisionnement des utilisateurs

Identique à Google — un compte DocPlatform est créé en utilisant l'e-mail principal de GitHub. Si le compte GitHub n'a pas d'e-mail public, l'utilisateur est invité à en saisir un.

## Gestion des sessions

DocPlatform suit les sessions actives par utilisateur :

| Champ | Description |
|---|---|
| **Appareil** | Chaîne User-Agent |
| **Adresse IP** | IP du client (à des fins d'audit) |
| **Créée** | Quand la session a été établie |
| **Dernière activité** | Requête API la plus récente |

Les utilisateurs peuvent consulter et révoquer leurs sessions depuis leur page de profil. Les administrateurs peuvent consulter toutes les sessions depuis le panneau d'administration.

### Révoquer des sessions

- **Initiée par l'utilisateur** — Profil → Sessions → Révoquer
- **Initiée par l'administrateur** — Admin → Users → sélectionner l'utilisateur → Revoke All Sessions
- **Rotation des clés** — La suppression de la clé JWT invalide toutes les sessions globalement

## Politique de mot de passe

| Contrainte | Valeur |
|---|---|
| Longueur minimale | 8 caractères |
| Longueur maximale | 128 caractères |
| Hachage | argon2id (64 Mo de mémoire, 3 itérations, parallélisme 4) |

Les mots de passe sont validés lors de l'inscription et de la réinitialisation. DocPlatform n'impose pas d'exigences de classes de caractères (majuscules, caractères spéciaux) — la longueur est la principale mesure de sécurité conformément aux recommandations NIST actuelles.

## Authentification WebSocket

Les connexions WebSocket utilisent un système de ticket à usage unique pour éviter d'exposer les tokens JWT dans les URLs (qui apparaîtraient dans les journaux du serveur et l'historique du navigateur).

**Flux :**

1. Le client appelle `POST /api/v1/auth/ws-ticket` avec un JWT valide
2. Le serveur renvoie un ticket aléatoire (valide pendant **30 secondes**, usage unique)
3. Le client se connecte à `ws://host/ws?ticket={ticket}`
4. Le serveur valide le ticket, établit le WebSocket et supprime le ticket

Ceci est transparent pour les utilisateurs — l'éditeur web gère l'acquisition du ticket automatiquement.

## Recommandations de sécurité

- **Activez OIDC** pour les équipes avec des comptes Google ou GitHub — déléguez la gestion des mots de passe à des fournisseurs établis
- **Utilisez HTTPS** en production — les tokens JWT sont des tokens porteur ; des tokens interceptés accordent un accès complet
- **Gardez des durées de vie de token courtes** — les tokens d'accès de 15 minutes limitent l'exposition
- **Surveillez les sessions** — consultez régulièrement les sessions actives pour détecter des appareils ou IPs inattendus
- **Effectuez une rotation des clés** annuellement ou après toute suspicion de compromission
- **Utilisez des cookies HttpOnly** — DocPlatform stocke les tokens dans des cookies HttpOnly + Secure + SameSite=Strict, empêchant le vol de tokens par XSS
