---
title: Déploiement Docker
description: Déployez DocPlatform en tant que conteneur Docker avec des volumes persistants et une configuration par variables d'environnement.
weight: 2
---

# Déploiement Docker

DocPlatform est distribué sous forme d'image Docker multi-architecture (amd64/arm64) construite sur Alpine Linux.

## Démarrage rapide

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Ouvrez [http://localhost:3000](http://localhost:3000) et enregistrez votre compte administrateur.

## Premier lancement

Au premier démarrage, DocPlatform effectue automatiquement :

1. Création de la base de données SQLite dans `/data/data.db`
2. Génération d'une clé de signature RS256 dans `/data/jwt-key.pem`
3. Initialisation de l'index de recherche plein texte
4. Début de l'écoute sur le port 3000

Le premier utilisateur à s'inscrire devient le **SuperAdmin** avec un accès complet à la plateforme. Aucune étape `init` manuelle n'est nécessaire — le conteneur est prêt à l'emploi immédiatement.

```bash
# Vérifier que le conteneur a démarré correctement
docker logs docplatform
# → INFO  Server starting            port=3000 version=v0.5.0
# → INFO  Database initialized       path=/data/data.db
# → INFO  Search index ready         documents=0
# → INFO  Listening on               http://0.0.0.0:3000
```

## Docker Compose

Pour une gestion plus simple, utilisez Docker Compose :

```yaml
# docker-compose.yml
services:
  docplatform:
    image: ghcr.io/valoryx-org/docplatform:latest
    container_name: docplatform
    ports:
      - "3000:3000"
    volumes:
      - docplatform-data:/data
      - ./deploy_key:/etc/docplatform/deploy_key:ro
    environment:
      - DATA_DIR=/data
      - PORT=3000
      - GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
      - BACKUP_RETENTION_DAYS=30
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  docplatform-data:
```

```bash
docker compose up -d
```

## Détails de l'image

| Propriété | Valeur |
|---|---|
| **Registre** | `ghcr.io/valoryx-org/docplatform` |
| **Image de base** | Alpine Linux 3.19 |
| **Architectures** | `linux/amd64`, `linux/arm64` |
| **Taille** | ~120 Mo compressé |
| **Utilisateur** | Non-root (`docplatform`, UID 1000) |
| **Port exposé** | 3000 |
| **Répertoire de données** | `/data` |

### Tags

| Tag | Description |
|---|---|
| `latest` | Version stable la plus récente |
| `v0.5.0` | Version spécifique |
| `v0.5` | Dernier patch pour v0.5.x |

## Volumes

Montez un volume persistant dans `/data` pour préserver les données entre les redémarrages du conteneur :

```bash
-v docplatform-data:/data
```

Le répertoire `/data` contient :

```
/data/
├── data.db              # SQLite database
├── jwt-key.pem          # Auto-generated RS256 signing key
├── backups/             # Daily backup files
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Markdown files
        ├── .git/        # Git repository (if connected)
        └── .docplatform/
            └── config.yaml
```

**Ne sautez pas le montage de volume.** Sans lui, toutes les données sont perdues lorsque le conteneur est supprimé.

## Variables d'environnement

Passez la configuration via les flags `-e`, `--env-file` ou la section `environment` de Docker Compose :

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  -e DATA_DIR=/data \
  -e SMTP_HOST=smtp.example.com \
  -e SMTP_PORT=587 \
  -e SMTP_FROM=docs@example.com \
  -e SMTP_USERNAME=docs@example.com \
  -e SMTP_PASSWORD=app-password \
  -e OIDC_GOOGLE_CLIENT_ID=your-client-id \
  -e OIDC_GOOGLE_CLIENT_SECRET=your-client-secret \
  ghcr.io/valoryx-org/docplatform:latest
```

Ou utilisez un fichier env :

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  --env-file .env.production \
  ghcr.io/valoryx-org/docplatform:latest
```

Consultez [Variables d'environnement](../configuration/environment.md) pour la référence complète.

## Clé SSH pour la synchronisation git

Montez votre clé de déploiement en tant que volume en lecture seule :

```bash
-v /path/to/deploy_key:/etc/docplatform/deploy_key:ro
-e GIT_SSH_KEY_PATH=/etc/docplatform/deploy_key
```

Assurez-vous que le fichier de clé a les permissions correctes sur l'hôte :

```bash
chmod 600 /path/to/deploy_key
```

## Vérifications de santé

DocPlatform expose des endpoints de santé :

| Endpoint | Objectif |
|---|---|
| `GET /health` | Vérification de vivacité de base (le serveur fonctionne) |
| `GET /ready` | Vérification de disponibilité (la base de données et la recherche sont initialisées) |

Utilisez-les pour les healthchecks Docker, les sondes de load balancer ou les sondes de vivacité/disponibilité d'orchestrateur.

```bash
# Vérification rapide de vivacité
curl -f http://localhost:3000/health
# → {"status":"ok"}

# Vérification de disponibilité (base de données + recherche initialisées)
curl -f http://localhost:3000/ready
# → {"status":"ok","database":"ok","search":"ok"}
```

## Avec un reverse proxy

### Caddy + Docker Compose

```yaml
services:
  docplatform:
    image: ghcr.io/valoryx-org/docplatform:latest
    volumes:
      - docplatform-data:/data
    environment:
      - DATA_DIR=/data
      - HOST=0.0.0.0
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config
    restart: unless-stopped

volumes:
  docplatform-data:
  caddy-data:
  caddy-config:
```

```
# Caddyfile
docs.yourcompany.com {
    reverse_proxy docplatform:3000
}
```

Caddy gère automatiquement le TLS via Let's Encrypt.

## Mises à jour

```bash
# Télécharger la dernière image
docker pull ghcr.io/valoryx-org/docplatform:latest

# Recréer le conteneur
docker compose up -d
```

Ou avec Docker standard :

```bash
docker pull ghcr.io/valoryx-org/docplatform:latest
docker stop docplatform
docker rm docplatform
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Les données dans le volume persistent entre les recréations de conteneur.

## Compilation depuis les sources

Compilez votre propre image depuis le Dockerfile :

```bash
cd Phase05/src
docker build -t docplatform:custom .
```

Le Dockerfile utilise une compilation multi-étapes :

1. **Étape de compilation** — Compilation Go avec CGO désactivé
2. **Étape frontend** — Export statique Next.js
3. **Étape d'exécution** — Alpine Linux avec le binaire compilé et les assets statiques

## Journaux

```bash
# Suivre les journaux du conteneur
docker logs -f docplatform

# 100 dernières lignes
docker logs --tail 100 docplatform
```

Les journaux sont structurés en JSON avec des identifiants de requête pour l'observabilité.

## Sauvegarde et restauration

### Sauvegarde manuelle

```bash
# Copier la base de données depuis le conteneur
docker cp docplatform:/data/data.db ./backup-$(date +%Y%m%d).db
```

### Sauvegardes automatisées

Les sauvegardes quotidiennes s'exécutent automatiquement à l'intérieur du conteneur (activées par défaut). Elles sont stockées dans `/data/backups/` et incluses dans le volume.

### Restauration

```bash
docker stop docplatform
docker cp ./backup-20250115.db docplatform:/data/data.db
docker start docplatform
```
