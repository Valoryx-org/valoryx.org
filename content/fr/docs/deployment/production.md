---
title: Checklist de production
description: Tout ce que vous devez vérifier avant d'exécuter DocPlatform dans un environnement de production.
weight: 3
---

# Checklist de production

Utilisez cette checklist avant de déployer DocPlatform dans un environnement de production. Chaque élément renvoie vers la section de documentation correspondante.

## Requis

Ces éléments sont nécessaires pour un déploiement en production sécurisé et fiable.

### Serveur

- [ ] **Stockage persistant configuré** — Montez un volume ou utilisez un chemin de système de fichiers stable pour `DATA_DIR`. La perte de ce répertoire signifie la perte de toutes les données.
- [ ] **Gestionnaire de processus en place** — Utilisez systemd, Docker avec `restart: unless-stopped` ou un orchestrateur de conteneurs pour garantir le redémarrage du serveur après un crash ou un redémarrage.
- [ ] **Port accessible** — Assurez-vous que le `PORT` configuré (par défaut : 3000) est accessible depuis votre réseau ou reverse proxy.
- [ ] **Ressources suffisantes** — Minimum 128 Mo de RAM, 200 Mo de disque. Recommandé 512 Mo de RAM, 1 Go de disque.

### Sécurité

- [ ] **TLS activé** — Exécutez derrière un reverse proxy (Caddy, nginx, load balancer cloud) avec HTTPS. DocPlatform ne gère pas la terminaison TLS lui-même.
- [ ] **Clé JWT sécurisée** — Le fichier `jwt-key.pem` permet de forger des tokens d'authentification. Restreignez les permissions du système de fichiers : `chmod 600`.
- [ ] **Premier utilisateur enregistré** — Le premier utilisateur inscrit devient SuperAdmin. Enregistrez votre compte administrateur avant d'ouvrir le serveur aux autres.
- [ ] **Liaison à localhost** — Si vous utilisez un reverse proxy sur le même hôte, définissez `HOST=127.0.0.1` pour que DocPlatform ne soit pas directement accessible.

### Sauvegardes

- [ ] **Sauvegardes activées** — `BACKUP_ENABLED=true` (par défaut). Vérifiez que les sauvegardes sont créées dans `{DATA_DIR}/backups/`.
- [ ] **Rétention des sauvegardes configurée** — `BACKUP_RETENTION_DAYS` configuré selon votre politique (par défaut : 7 jours).
- [ ] **Sauvegarde hors serveur** — Copiez les fichiers de sauvegarde vers un emplacement séparé (S3, NFS, autre serveur). Les sauvegardes sur disque ne protègent pas contre une panne de disque.

## Recommandé

Ces éléments améliorent la fiabilité, la sécurité et l'expérience de l'équipe.

### Authentification

- [ ] **OIDC configuré** — Si votre équipe utilise Google ou GitHub, activez la connexion OIDC pour déléguer la gestion des mots de passe. Consultez [Authentification](../configuration/authentication.md).
- [ ] **SMTP configuré** — Activez l'e-mail pour les invitations à l'espace de travail et la réinitialisation de mot de passe. Sans SMTP, les tokens s'affichent sur stdout. Consultez [Variables d'environnement](../configuration/environment.md).

### Git

- [ ] **Clé SSH de déploiement provisionnée** — Pour les dépôts privés, générez une clé de déploiement dédiée avec accès en écriture. Consultez [Intégration Git](../guides/git-integration.md).
- [ ] **Webhook configuré** — Pour une synchronisation quasi instantanée, configurez un webhook push chez votre hébergeur git. Le polling (par défaut : 5 minutes) fonctionne mais ajoute un délai.
- [ ] **Git installé sur l'hôte** — Bien que go-git gère la plupart des opérations, le Git CLI natif est nécessaire pour les gros dépôts (>1 Go).

### Supervision

- [ ] **Endpoint de santé supervisé** — Interrogez `GET /health` depuis votre système de supervision (Uptime Robot, Prometheus blackbox exporter, etc.).
- [ ] **Journaux collectés** — DocPlatform produit des journaux JSON structurés sur stdout. Transférez-les vers votre agrégateur de logs (ELK, Datadog, CloudWatch).
- [ ] **Utilisation disque supervisée** — Les bases de données SQLite et les index de recherche grossissent avec le contenu. Alertez lorsque l'utilisation disque dépasse 80%.

### Opérations

- [ ] **`docplatform doctor` exécuté** — Lancez `docplatform doctor` après la configuration initiale pour vérifier la cohérence FS/DB, la santé de la recherche et les liens cassés.
- [ ] **Processus de mise à jour documenté** — Documentez comment votre équipe met à jour DocPlatform (remplacement du binaire + redémarrage, ou Docker pull + recréation).
- [ ] **Plan de retour en arrière en place** — Conservez la version précédente du binaire et sachez comment restaurer depuis une sauvegarde de base de données.

## Limites de ressources de la Community Edition

La Community Edition inclut les limites codées en dur suivantes :

| Ressource | Limite |
|---|---|
| Utilisateurs avec le rôle Editor ou supérieur | 5 |
| Espaces de travail | 3 |
| Viewers et Commenters | Illimité |
| Pages par espace de travail | Illimité |

Ces limites sont vérifiées lors de l'attribution du rôle d'éditeur et de la création d'espace de travail. Si vous avez besoin de plus d'éditeurs ou d'espaces de travail, la future Enterprise Edition proposera des limites configurables via une clé de licence.

## Considérations de dimensionnement

DocPlatform Community Edition fonctionne comme une instance unique avec une base de données SQLite à écrivain unique. C'est l'architecture appropriée pour l'échelle cible :

| Métrique | Limite testée |
|---|---|
| **Pages** | 1 000 |
| **Utilisateurs simultanés** | 50 |
| **Espaces de travail** | 10 |
| **Latence de rendu de page** | < 50 ms (p99) |
| **Latence de recherche** | < 50 ms (p99) |
| **Utilisation mémoire** | < 200 Mo sous charge |

Si vous devez aller au-delà de ces limites, les futures éditions supporteront le déploiement multi-instances, les bases de données externes et Meilisearch.

## Renforcement de la sécurité

### Réseau

- Exécutez derrière un reverse proxy avec TLS
- Définissez `HOST=127.0.0.1` pour bloquer l'accès direct
- Utilisez des règles de pare-feu pour restreindre l'accès au serveur
- **Proxy WebSocket** — assurez-vous que votre reverse proxy supporte la mise à niveau WebSocket. Sans cela, la présence en temps réel et les mises à jour en direct ne fonctionneront pas. Caddy et nginx (avec `proxy_http_version 1.1` et les en-têtes `Upgrade`) le supportent.

### En-têtes de réponse

DocPlatform définit automatiquement des en-têtes de sécurité sur toutes les réponses :

| En-tête | Valeur |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| `X-Request-ID` | ULID (unique par requête) |

### Système de fichiers

- Exécutez en tant qu'utilisateur non-root dédié (systemd : `User=docplatform`)
- Restreignez les permissions du répertoire de données : `chmod 700 {DATA_DIR}`
- Restreignez les permissions de la clé JWT : `chmod 600 {DATA_DIR}/jwt-key.pem`

### Authentification

- Activez OIDC pour réduire les identifiants stockés localement
- Utilisez des mots de passe forts (DocPlatform utilise argon2id — résistant aux attaques par force brute)
- Consultez régulièrement les sessions actives (panneau Admin → Users → Sessions)

### Mises à jour

- Abonnez-vous aux versions GitHub pour les mises à jour de sécurité
- Mettez à jour rapidement lorsque des correctifs de sécurité sont publiés
- Exécutez `docplatform doctor` après chaque mise à jour

## Exemple : configuration de production minimale

```bash
# 1. Installer
sudo mv docplatform /usr/local/bin/

# 2. Créer l'utilisateur de service et le répertoire de données
sudo useradd -r -s /sbin/nologin docplatform
sudo mkdir -p /var/lib/docplatform
sudo chown docplatform:docplatform /var/lib/docplatform

# 3. Initialiser l'espace de travail
cd /var/lib/docplatform
sudo -u docplatform docplatform init \
  --workspace-name "Docs" \
  --slug docs

# 4. Configurer l'environnement
sudo mkdir -p /etc/docplatform
sudo tee /etc/docplatform/.env <<EOF
PORT=3000
HOST=127.0.0.1
DATA_DIR=/var/lib/docplatform
BACKUP_RETENTION_DAYS=30
EOF

# 5. Créer le service systemd (voir le guide de déploiement binaire)
# 6. Configurer le reverse proxy avec TLS (voir le guide de déploiement binaire)

# 7. Démarrer et vérifier
sudo systemctl enable --now docplatform
docplatform doctor

# 8. Enregistrer le compte administrateur sur https://docs.yourcompany.com
```
