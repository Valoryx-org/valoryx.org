---
title: Installation
description: Installez DocPlatform à l'aide d'un binaire pré-compilé, de Docker ou depuis les sources.
weight: 2
---

# Installation

DocPlatform est distribué sous forme de binaire unique sans aucune dépendance d'exécution. Choisissez la méthode d'installation qui convient à votre workflow.

## Option 1 : Binaire pré-compilé (recommandé)

Téléchargez la dernière version pour votre plateforme.

### Linux / macOS

```bash
# Recommandé (détection automatique de la plateforme)
curl -fsSL https://valoryx.org/install.sh | sh

# Ou téléchargement manuel
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform

# Vérifier l'installation
docplatform version
```

**Sortie attendue :**

```
docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
```
### Windows```powershell# Download and runInvoke-WebRequest https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-windows-amd64.exe -OutFile docplatform.exe# Verify.docplatform.exe version# Start the server.docplatform.exe serve```Open [http://localhost:3000](http://localhost:3000) to get started.

### Téléchargement manuel

Si vous préférez télécharger manuellement, rendez-vous sur la page [GitHub Releases](https://github.com/Valoryx-org/releases/releases). Des binaires sont disponibles pour :

| Plateforme | Architecture | Nom du fichier |
|---|---|---|
| Linux | amd64 | `docplatform-linux-amd64` |
| Linux | arm64 | `docplatform-linux-arm64` |
| macOS | amd64 (Intel) | `docplatform-darwin-amd64` |
| macOS | arm64 (Apple Silicon) | `docplatform-darwin-arm64` |
| Windows | amd64 | `docplatform-windows-amd64.exe` |

Chaque version inclut des sommes de contrôle SHA-256 pour vérification.

## Option 2 : Docker

Exécutez DocPlatform en tant que conteneur avec des données persistantes stockées dans un volume.

```bash
docker run -d \
  --name docplatform \
  -p 3000:3000 \
  -v docplatform-data:/data \
  ghcr.io/valoryx-org/docplatform:latest
```

Le conteneur s'initialise automatiquement au premier lancement. Ouvrez [http://localhost:3000](http://localhost:3000) pour commencer.

### Docker Compose

Pour une configuration plus facile à gérer, utilisez Docker Compose :

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
    environment:
      - PORT=3000
      - DATA_DIR=/data
    restart: unless-stopped

volumes:
  docplatform-data:
```

```bash
docker compose up -d
```

Pour les déploiements Docker en production, consultez le [guide de déploiement Docker](../deployment/docker.md).

## Option 3 : Compilation depuis les sources

Compilez depuis les sources si vous souhaitez contribuer ou utiliser une version de développement.

**Prérequis :**

- Go 1.24+
- Node.js 20+ et pnpm (pour la compilation du frontend)
- Git
- Make

```bash
# Cloner le dépôt
git clone https://github.com/Valoryx-org/docplatform.git
cd docplatform/Phase05/src

# Compiler le binaire (compile Go + intègre l'export statique Next.js)
make build

# Vérifier
./docplatform version
```

### Mode développement

Pour le rechargement à chaud pendant le développement :

```bash
make dev
```

Cela démarre le serveur Go avec rechargement automatique et le serveur de développement Next.js avec HMR.

## Étapes suivantes

Une fois DocPlatform installé, continuez avec :

1. **[Démarrage rapide](quickstart.md)** — initialiser un espace de travail et démarrer le serveur en 2 commandes
2. **[Votre premier espace de travail](first-workspace.md)** — configurer la synchronisation git, inviter des utilisateurs et personnaliser les paramètres

## Désinstallation

### Binaire

```bash
# Supprimer le binaire
sudo rm /usr/local/bin/docplatform

# Supprimer les données (si vous souhaitez repartir de zéro)
rm -rf .docplatform/
```

### Docker

```bash
docker stop docplatform && docker rm docplatform
docker volume rm docplatform-data  # supprime toutes les données
```
