---
title: Référence CLI
description: Référence complète de toutes les commandes CLI de DocPlatform — serve, init, rebuild, doctor et version.
weight: 2
---

# Référence CLI

DocPlatform fournit 5 commandes CLI pour la gestion du serveur, l'initialisation des espaces de travail, les diagnostics et la maintenance.

## Options globales

Ces options s'appliquent à toutes les commandes :

| Flag | Description |
|---|---|
| `--help`, `-h` | Afficher l'aide pour n'importe quelle commande |
| `--version`, `-v` | Afficher les informations de version |

## `docplatform serve`

Démarrer le serveur HTTP.

```bash
docplatform serve [flags]
```

### Flags

| Flag | Par défaut | Description |
|---|---|---|
| `--port` | `3000` | Port d'écoute HTTP (supplante la variable d'environnement `PORT`) |
| `--host` | `0.0.0.0` | Adresse d'écoute HTTP (supplante la variable d'environnement `HOST`) |
| `--data-dir` | `.docplatform` | Chemin du répertoire de données (supplante la variable d'environnement `DATA_DIR`) |

### Comportement

- Charge les variables d'environnement depuis le fichier `.env` (si présent)
- Initialise la base de données SQLite en mode WAL
- Exécute les migrations de base de données en attente
- Charge les politiques de permissions Casbin en mémoire
- Construit ou ouvre l'index de recherche Bleve
- Démarre le moteur de synchronisation git pour tous les espaces de travail configurés
- Démarre le planificateur de sauvegardes (si activé)
- Sert l'éditeur web et l'API sur le port configuré

### Séquence de démarrage

Lorsque `docplatform serve` s'exécute, voici ce qui se passe dans l'ordre :

1. Charger la configuration (variables d'environnement + fichier `.env` + valeurs par défaut)
2. Ouvrir la base de données SQLite (mode WAL) et exécuter les migrations en attente
3. Initialiser l'organisation par défaut si c'est un premier lancement
4. Initialiser les services : Content Ledger, Git Engine (pool de 4 workers), Search Engine, Permission Service, Auth Service, WebSocket Hub
5. Démarrer les goroutines en arrière-plan : hub WebSocket, polling de synchronisation git, planificateur de sauvegardes, télémétrie (si activée)
6. Commencer l'écoute sur l'hôte:port configuré

Les requêtes de lecture sont servies immédiatement. Si les espaces de travail ont du contenu existant, la réconciliation s'exécute en arrière-plan sans bloquer.

### Signaux

| Signal | Effet |
|---|---|
| `SIGTERM` | Arrêt gracieux — arrête d'accepter les requêtes, termine les opérations en cours, vide la base de données |
| `SIGINT` | Identique à SIGTERM (Ctrl+C) |

**Séquence d'arrêt** (délai de 15 secondes) :

1. Annuler le contexte applicatif (signale à toutes les goroutines de s'arrêter)
2. Arrêter le hub WebSocket (fermer toutes les connexions client)
3. Arrêter le gestionnaire de synchronisation git (terminer les opérations de synchronisation en cours)
4. Fermer le moteur de recherche (écrire l'index Bleve sur le disque)
5. Drainer le pool de workers git (attendre les opérations git en cours)
6. Arrêter le serveur HTTP (timeout de 10 secondes pour les requêtes en cours)

Si l'arrêt dépasse 15 secondes, le processus se termine de force.

### Exemple

```bash
# Démarrer sur le port par défaut
docplatform serve

# Démarrer sur un port personnalisé
docplatform serve --port 8080

# Démarrer avec un répertoire de données explicite
docplatform serve --data-dir /var/lib/docplatform
```

### Sortie

```
INFO  Server starting            port=3000 version=v0.5.2
INFO  Database initialized       path=.docplatform/data.db wal=true
INFO  Migrations applied         count=1
INFO  Search index ready         documents=42
INFO  Workspace loaded           name="Docs" slug=docs git_remote=git@github.com:...
INFO  Backup scheduler started   retention_days=7
INFO  Listening on               http://0.0.0.0:3000
```

---

## `docplatform init`

Initialiser un nouvel espace de travail.

```bash
docplatform init [flags]
```

### Flags

| Flag | Obligatoire | Par défaut | Description |
|---|---|---|---|
| `--workspace-name` | Oui | — | Nom affiché de l'espace de travail |
| `--slug` | Oui | — | Identifiant compatible URL (utilisé dans l'URL de la documentation publiée) |
| `--git-url` | Non | — | URL du dépôt git distant (SSH ou HTTPS) |
| `--branch` | Non | `main` | Branche git à synchroniser |
| `--data-dir` | Non | `.docplatform` | Chemin du répertoire de données |

### Comportement

1. Crée la structure du répertoire de données (`{DATA_DIR}/`)
2. Initialise la base de données SQLite (si pas déjà présente)
3. Génère une clé de signature JWT RS256 (si pas déjà présente)
4. Crée le répertoire de l'espace de travail (`{DATA_DIR}/workspaces/{ulid}/`)
5. Si `--git-url` est fourni, clone le dépôt
6. Crée le fichier de configuration de l'espace de travail
7. Indexe tous les fichiers `.md` existants

### Exemple

```bash
# Espace de travail local (sans git)
docplatform init \
  --workspace-name "Internal Wiki" \
  --slug wiki

# Avec git
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git \
  --branch main
```

### Sortie

```
INFO  Data directory created     path=.docplatform
INFO  Database initialized       path=.docplatform/data.db
INFO  JWT key generated          path=.docplatform/jwt-key.pem
INFO  Workspace created          id=01KJJ10NTF... name="API Docs" slug=api-docs
INFO  Repository cloned          url=git@github.com:your-org/api-docs.git branch=main
INFO  Pages indexed              count=15
INFO  Ready. Run 'docplatform serve' to start.
```

---

## `docplatform rebuild`

Reconstruire la base de données et l'index de recherche depuis le système de fichiers. À utiliser lorsque la base de données est désynchronisée par rapport aux fichiers réels sur le disque.

```bash
docplatform rebuild [flags]
```

### Flags

| Flag | Obligatoire | Par défaut | Description |
|---|---|---|---|
| `--workspace-id` | Non | tous | ULID d'un espace de travail spécifique à reconstruire. Sans ce flag, tous les espaces de travail sont reconstruits. |
| `--search` | Non | `false` | Supprimer et reconstruire également l'index de recherche Bleve |
| `--data-dir` | Non | `.docplatform` | Chemin du répertoire de données |

### Comportement

1. Crée une sauvegarde de la base de données actuelle
2. Supprime la table `pages`
3. Analyse le système de fichiers pour tous les fichiers `.md` dans les répertoires `docs/` des espaces de travail
4. Analyse le frontmatter et le contenu de chaque fichier
5. Insère les enregistrements de page dans la base de données
6. Reconstruit l'index de recherche Bleve
7. Rapporte les résultats de la réconciliation

### Quand l'utiliser

- Après avoir manuellement ajouté, déplacé ou supprimé des fichiers `.md` en dehors de DocPlatform
- Après un crash qui peut avoir laissé la base de données incohérente
- Après avoir restauré des fichiers depuis une sauvegarde git
- Lorsque `docplatform doctor` signale des incohérences FS/DB

### Exemple

```bash
# Reconstruire tous les espaces de travail
docplatform rebuild

# Reconstruire un espace de travail spécifique
docplatform rebuild --workspace-id 01KJJ10NTF31Z1QJTG4ZRQZ2Z2
```

### Sortie

```
INFO  Backup created             path=.docplatform/backups/pre-rebuild-20250115.db
INFO  Rebuilding workspace       id=01KJJ10NTF... name="API Docs"
INFO  Scanning filesystem        path=.docplatform/workspaces/01KJJ.../docs/
INFO  Pages found                count=42
INFO  Database rebuilt            inserted=42 updated=0 orphaned=3
INFO  Search index rebuilt        documents=42
INFO  Ghost recovery             matched=2 unmatched=1
INFO  Rebuild complete
```

**Récupération fantôme :** Lorsque des enregistrements orphelins dans la base de données (aucun fichier correspondant) sont trouvés, DocPlatform tente de les faire correspondre à des fichiers non indexés par hash de contenu. Cela récupère les pages qui ont été déplacées ou renommées en dehors de DocPlatform.

---

## `docplatform doctor`

Exécuter 9 vérifications diagnostiques sur la santé de la plateforme.

```bash
docplatform doctor [flags]
```

### Flags

| Flag | Obligatoire | Par défaut | Description |
|---|---|---|---|
| `--bundle` | Non | `false` | Créer un fichier ZIP contenant la sortie diagnostique pour le support |
| `--data-dir` | Non | `.docplatform` | Chemin du répertoire de données |

### Vérifications

| # | Vérification | Description |
|---|---|---|
| 1 | **Connexion à la base de données** | Le fichier SQLite existe, est lisible, mode WAL activé |
| 2 | **Version du schéma** | Les migrations sont à jour |
| 3 | **Cohérence FS/DB** | Chaque fichier dans `docs/` a un enregistrement en base, et réciproquement |
| 4 | **Fichiers orphelins** | Fichiers sur le disque sans enregistrement en base |
| 5 | **Enregistrements orphelins** | Enregistrements en base sans fichier sur le disque |
| 6 | **Santé de l'index de recherche** | Le nombre de documents dans l'index Bleve correspond au nombre de pages |
| 7 | **Liens internes cassés** | Liens Markdown pointant vers des pages inexistantes |
| 8 | **Validité du frontmatter** | Toutes les pages ont un frontmatter YAML valide avec un titre |
| 9 | **Connectivité du dépôt git distant** | Si git est configuré, le dépôt distant est-il accessible ? |

### Codes de sortie

| Code | Signification |
|---|---|
| `0` | Toutes les vérifications ont réussi (sain) |
| `1` | Une ou plusieurs vérifications ont échoué ou ont des avertissements |

Utilisez le code de sortie dans les scripts et la supervision :

```bash
docplatform doctor || echo "Health check failed"
```

### Exemple

```bash
docplatform doctor
```

### Sortie

```
DocPlatform Health Check
========================

✓ Database connection          OK (WAL mode, 42 pages, 3 users)
✓ Schema version               OK (v1, up to date)
✓ FS/DB consistency            OK (42 files, 42 records)
✓ Orphaned files               OK (0 found)
✓ Orphaned records             OK (0 found)
✓ Search index health          OK (42 indexed, 42 expected)
⚠ Broken internal links        WARNING (2 broken links found)
  → guides/editor.md:15 → "old-page.md" (file not found)
  → api/endpoints.md:42 → "deprecated.md" (file not found)
✓ Frontmatter validity         OK (42/42 valid)
✓ Git remote connectivity      OK (git@github.com:your-org/docs.git)

Result: 8/9 passed, 1 warning
```

### Mode bundle

```bash
docplatform doctor --bundle
# Creates: docplatform-doctor-20250115.zip
```

Le bundle est sauvegardé dans `{DATA_DIR}/diagnostics/docplatform-diagnostics-{timestamp}.zip` et contient :

- `report.json` — résultats diagnostiques structurés
- Informations de schéma (définitions des tables, pas de données)
- Liste des fichiers (chemins et tailles, pas de contenu)
- Informations système (OS, architecture, version Go)
- 1 000 dernières lignes des journaux d'erreur
- Version du serveur et configuration (avec les secrets masqués)

Le bundle **ne contient jamais** le contenu des pages, les mots de passe, les tokens ou les clés privées.

---

## `docplatform version`

Afficher la version, le hash du commit et la date de compilation.

```bash
docplatform version
```

### Sortie

```
docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
```

Les informations de version sont intégrées au moment de la compilation via les flags du linker. Utile pour vérifier quelle version est déployée et pour les demandes de support.
