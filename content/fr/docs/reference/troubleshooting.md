---
title: Dépannage
description: Problèmes courants et solutions pour DocPlatform — démarrage du serveur, synchronisation git, authentification, recherche et récupération de données.
weight: 3
---

# Dépannage

Ce guide couvre les problèmes courants et leurs solutions. Pour des informations diagnostiques, commencez toujours par :

```bash
docplatform doctor
```

## Démarrage du serveur

### Le serveur ne démarre pas : « address already in use »

**Cause :** Un autre processus utilise le port configuré.

**Solution :**

```bash
# Trouver ce qui utilise le port 3000
lsof -i :3000  # macOS/Linux
ss -tlnp | grep 3000  # Linux

# Option 1 : Arrêter l'autre processus
# Option 2 : Utiliser un port différent
docplatform serve --port 8080
```

### Le serveur ne démarre pas : « permission denied »

**Cause :** Le processus n'a pas les droits de lecture/écriture sur le répertoire de données.

**Solution :**

```bash
# Vérifier la propriété
ls -la .docplatform/

# Corriger la propriété (si exécuté en tant qu'utilisateur docplatform)
sudo chown -R docplatform:docplatform .docplatform/

# Corriger les permissions
chmod 700 .docplatform/
```

### Le serveur ne démarre pas : « database is locked »

**Cause :** Un autre processus DocPlatform est en cours d'exécution, ou un processus précédent ne s'est pas arrêté proprement.

**Solution :**

```bash
# Vérifier s'il y a d'autres processus docplatform
ps aux | grep docplatform

# Si un processus est bloqué, le terminer
kill -SIGTERM <pid>

# Si le fichier de verrouillage persiste alors qu'aucun processus n'est en cours
# Le mode WAL de SQLite gère cela automatiquement au redémarrage
docplatform serve
```

## Synchronisation git

### « Permission denied (publickey) » lors de la synchronisation git

**Cause :** La clé SSH n'est pas configurée ou n'a pas accès au dépôt.

**Solution :**

1. Vérifiez que la clé existe :
   ```bash
   ls -la $GIT_SSH_KEY_PATH
   ```

2. Vérifiez que la clé a été ajoutée aux clés de déploiement du dépôt :
   ```bash
   ssh -T -i $GIT_SSH_KEY_PATH git@github.com
   ```

3. Assurez-vous que l'accès en écriture est activé sur la clé de déploiement (nécessaire pour le push)

### La synchronisation git affiche « no changes » mais des fichiers ont été modifiés

**Cause :** Les modifications ont été apportées à des fichiers en dehors du répertoire `docs/`, que DocPlatform n'indexe pas.

**Solution :** Assurez-vous que vos fichiers Markdown sont dans le répertoire `docs/` de l'espace de travail. Les fichiers dans d'autres répertoires sont préservés dans git mais ne sont pas suivis par DocPlatform.

### Conflit : HTTP 409 lors de la sauvegarde

**Cause :** La page a été modifiée par un autre utilisateur ou via un push git entre votre chargement et votre sauvegarde.

**Solution :**

1. L'interface web affiche une bannière de conflit avec les deux versions
2. Cliquez sur **Download both** pour obtenir les deux fichiers
3. Fusionnez manuellement les modifications
4. Sauvegardez la version fusionnée

**Prévention :**

- Activez les webhooks pour une synchronisation plus rapide (réduire la fenêtre de conflit)
- Utilisez les indicateurs de présence pour voir qui édite quoi
- Attribuez la propriété des pages pour éviter les modifications simultanées

### Le push git échoue : « remote rejected »

**Cause :** La clé de déploiement n'a pas l'accès en écriture, ou les règles de protection de branche empêchent les push directs.

**Solution :**

1. Vérifiez que la clé de déploiement a l'accès en écriture dans les paramètres de votre dépôt
2. Vérifiez les règles de protection de branche — DocPlatform pousse directement vers la branche configurée
3. Si la protection de branche est requise, configurez DocPlatform pour pousser vers une branche non protégée

## Authentification

### « 401 Unauthorized » sur chaque requête

**Cause :** Le token d'accès JWT a expiré (durée de vie de 15 minutes par défaut).

**Solution :** L'éditeur web gère automatiquement le rafraîchissement des tokens. Si vous utilisez l'API directement, appelez l'endpoint de rafraîchissement :

```bash
curl -X POST http://localhost:3000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

### Impossible de se connecter après une rotation de clé JWT

**Cause :** Tous les tokens ont été invalidés lorsque la clé JWT a été supprimée et régénérée.

**Solution :** C'est le comportement attendu. Tous les utilisateurs doivent se reconnecter après une rotation de clé. Effacez les cookies/le stockage de votre navigateur et connectez-vous avec votre mot de passe.

### La connexion OIDC redirige vers une page d'erreur

**Cause :** L'URL de callback OAuth ne correspond pas à ce qui est configuré dans Google/GitHub.

**Solution :**

1. Vérifiez l'URL de callback dans les paramètres de votre fournisseur OAuth
2. Elle devrait être : `https://your-domain.com/api/v1/auth/callback/google` (ou `/github`)
3. Assurez-vous que les variables d'environnement `OIDC_*_CLIENT_ID` et `OIDC_*_CLIENT_SECRET` sont correctement définies
4. Redémarrez le serveur après avoir modifié les variables d'environnement OIDC

### Le premier utilisateur n'est pas SuperAdmin

**Cause :** La base de données contenait déjà des enregistrements utilisateur d'une installation précédente.

**Solution :**

```bash
# ATTENTION : Cela supprime toutes les données
docplatform serve  # arrêtez d'abord
rm .docplatform/data.db
docplatform serve
# Enregistrez votre compte administrateur
```

Ne faites cela que sur une installation neuve. Pour les installations existantes, utilisez la base de données pour mettre à jour les rôles utilisateur directement (avancé).

## Recherche

### La recherche ne renvoie aucun résultat

**Cause :** L'index de recherche est peut-être vide ou désynchronisé.

**Solution :**

```bash
# Vérifier la santé de la recherche
docplatform doctor

# Si l'index est désynchronisé, le reconstruire
docplatform rebuild
```

### Les résultats de recherche sont obsolètes (ne reflètent pas les modifications récentes)

**Cause :** La tâche d'indexation asynchrone n'a pas encore été traitée (typiquement < 1 seconde de délai).

**Solution :** Attendez un instant et réessayez. Si le problème persiste :

1. Vérifiez les journaux du serveur pour des erreurs d'indexation
2. Exécutez `docplatform rebuild` pour forcer une ré-indexation complète

### La recherche est lente

**Cause :** Espaces de travail très volumineux (1000+ pages) avec des requêtes complexes.

**Solution :**

- Utilisez des termes de recherche plus spécifiques
- Utilisez des filtres par tag pour restreindre le périmètre
- Les futures versions supporteront Meilisearch pour une recherche haute performance

## Récupération de données

### Page supprimée accidentellement

**Option 1 : Historique git** (si la synchronisation git est activée)

```bash
cd .docplatform/workspaces/{id}/docs/
git log --all -- path/to/deleted-page.md
git checkout <commit-hash> -- path/to/deleted-page.md
```

Puis exécutez `docplatform rebuild` pour ré-indexer.

**Option 2 : Sauvegarde de base de données**

```bash
# Lister les sauvegardes
ls .docplatform/backups/

# Restaurer depuis la sauvegarde (arrêtez le serveur d'abord)
cp .docplatform/backups/{latest}.db .docplatform/data.db
docplatform serve
```

### La base de données est corrompue

**Solution :**

1. Arrêtez le serveur
2. Vérifiez s'il existe une sauvegarde récente :
   ```bash
   ls -la .docplatform/backups/
   ```
3. Restaurez depuis la sauvegarde :
   ```bash
   cp .docplatform/backups/{latest}.db .docplatform/data.db
   ```
4. Si aucune sauvegarde n'est disponible, reconstruisez depuis le système de fichiers :
   ```bash
   rm .docplatform/data.db
   docplatform rebuild
   ```
5. Démarrez le serveur

Le système de fichiers (fichiers `.md`) est la source de vérité. Même si la base de données est perdue, `rebuild` la recrée à partir de vos fichiers.

### Clé JWT perdue

**Cause :** Le fichier `jwt-key.pem` a été supprimé.

**Impact :** Toutes les sessions utilisateur sont invalidées. Les utilisateurs doivent se reconnecter.

**Solution :** Démarrez le serveur — une nouvelle clé est générée automatiquement. Aucune donnée n'est perdue, mais tous les utilisateurs doivent se ré-authentifier.

## Erreurs de frontmatter

### La page devient inaccessible après une modification du frontmatter

**Cause :** YAML invalide dans le bloc de frontmatter. DocPlatform utilise le **mode strict** par défaut — si l'analyse du frontmatter échoue, la page est restreinte à l'accès WorkspaceAdmin uniquement pour empêcher qu'une faute de frappe YAML ne rende accidentellement publique une page privée.

**Symptômes :**

- La page disparaît des résultats de recherche
- La page est exclue de la documentation publiée
- Les utilisateurs non-admin obtiennent 403 Forbidden
- L'admin voit une bannière d'avertissement sur la page

**Solution :**

1. Connectez-vous en tant que WorkspaceAdmin ou SuperAdmin
2. Ouvrez la page affectée dans l'éditeur web
3. Basculez en mode Markdown brut (bouton `</>`)
4. Corrigez le frontmatter YAML (problèmes courants : guillemets manquants autour de valeurs avec des deux-points, indentation incorrecte, crochets non fermés)
5. Sauvegardez — la page est ré-indexée et l'accès est restauré

**Si vous ne pouvez pas accéder à l'éditeur web**, corrigez le fichier directement sur le disque :

```bash
# Modifier le fichier Markdown
nano .docplatform/workspaces/{id}/docs/{path-to-page}.md

# Reconstruire pour ré-indexer
docplatform rebuild
```

### Comprendre les modes d'erreur du frontmatter

| Mode | Comportement en cas de YAML invalide | Quand l'utiliser |
|---|---|---|
| **Strict** (par défaut) | Page restreinte à WorkspaceAdmin uniquement, exclue de la recherche et de la documentation publiée | Production — empêche l'exposition accidentelle |
| **Lenient** | Conserve le dernier frontmatter valide connu depuis la base de données, affiche un avertissement | Développement — moins de perturbation pendant l'édition |

Le mode strict garantit qu'une faute de frappe YAML ne rende jamais accidentellement publique une page restreinte. C'est un choix de conception délibéré pour la sécurité.

## Espace disque

### Avertissement « Low disk space » du diagnostic

**Cause :** DocPlatform avertit lorsque l'espace disque libre descend en dessous de 1 Go.

**Impact :** SQLite nécessite de l'espace disque libre pour les opérations WAL (write-ahead log). Si le disque est complètement plein, les écritures échouent et les données peuvent être corrompues.

**Solution :**

1. Vérifiez l'utilisation disque : `df -h`
2. Nettoyez les anciennes sauvegardes : réduisez `BACKUP_RETENTION_DAYS` ou supprimez manuellement les anciens fichiers dans `{DATA_DIR}/backups/`
3. Déplacez le répertoire de données vers un disque plus grand : mettez à jour `DATA_DIR` et déplacez le répertoire
4. Si vous utilisez Docker, augmentez la taille du volume

## Performances

### Utilisation mémoire élevée

**Attendu :** < 80 Mo au repos, < 200 Mo sous charge.

Si l'utilisation mémoire dépasse 200 Mo :

1. Vérifiez le nombre de connexions WebSocket actives
2. Vérifiez le nombre d'espaces de travail et le nombre total de pages
3. Les gros dépôts git (>5 000 fichiers) utilisent plus de mémoire — le moteur hybride bascule automatiquement vers le Git CLI natif lorsque go-git dépasse 512 Mo de RSS

### Rendus de page lents

**Attendu :** < 50 ms p99.

Si les rendus de page sont lents :

1. Vérifiez les E/S disque — les performances de SQLite dépendent de la vitesse du disque
2. Utilisez un SSD pour le répertoire de données
3. Vérifiez si le fichier de base de données est sur un système de fichiers réseau (NFS/CIFS) — déplacez-le sur un disque local

## Obtenir de l'aide

Si vous ne parvenez pas à résoudre un problème :

1. Exécutez `docplatform doctor --bundle` pour générer un bundle diagnostique
2. Vérifiez les journaux du serveur pour les messages d'erreur
3. Ouvrez une issue sur GitHub avec le bundle diagnostique et les entrées de journal pertinentes

Le bundle diagnostique **ne contient pas** votre contenu, vos mots de passe ou vos tokens API — uniquement des métadonnées structurelles et la configuration (avec les secrets masqués).
