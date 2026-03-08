---
title: DocPlatform Community Edition
description: Plateforme de documentation auto-hébergée et sauvegardée par git, avec un éditeur web élégant. Gardez le contrôle de vos docs. Maîtrisez votre workflow.
weight: 1
---

# DocPlatform Community Edition

DocPlatform est une plateforme de documentation auto-hébergée qui combine un éditeur web riche avec une synchronisation git bidirectionnelle — le tout dans un binaire unique, sans aucune dépendance externe.

Écrivez dans votre navigateur. Poussez depuis votre IDE. Tout reste synchronisé.

## Pourquoi DocPlatform

Les plateformes de documentation vous obligent à choisir : un éditeur web soigné avec un verrouillage fournisseur, ou des fichiers bruts dans git sans fonctionnalités de collaboration. DocPlatform élimine ce compromis.

| Ce que vous obtenez | Comment ça fonctionne |
|---|---|
| **Binaire unique, zéro dépendance** | Un seul binaire Go intègre l'éditeur, la base de données, le moteur de recherche et le moteur git. Pas de runtime Node.js, pas de Postgres, pas d'Elasticsearch. |
| **Chaque page est un fichier `.md`** | Votre contenu est stocké sous forme de fichiers Markdown dans un vrai dépôt git. Pas de format propriétaire. Pas d'export nécessaire. |
| **Synchronisation git bidirectionnelle** | Éditez dans le navigateur — les modifications sont auto-commitées et poussées. Poussez depuis votre IDE — l'interface web se met à jour automatiquement. |
| **Documentation publiée élégante** | Un clic pour publier un site de documentation avec mode sombre, coloration syntaxique et 7 composants intégrés. |
| **Collaboration en équipe** | Hiérarchie de rôles à 6 niveaux, invitations à l'espace de travail, indicateurs de présence en temps réel et journal d'audit complet. |
| **Recherche plein texte** | Moteur de recherche intégré avec résultats instantanés. Aucun service externe à configurer. |

## À qui s'adresse-t-il

DocPlatform Community Edition est conçu pour :

- **Les mainteneurs open source** qui conservent la documentation de leur projet dans le dépôt mais souhaitent une meilleure expérience d'édition que le Markdown brut sur GitHub
- **Les équipes plateforme interne / DevEx** qui ont besoin de docs-as-code avec contrôle d'accès et un éditeur web — pas l'un ou l'autre
- **Les petites agences de développement** gérant plusieurs dépôts de documentation clients avec sauvegarde git et aucune option auto-hébergée abordable
- **Les rédacteurs techniques** qui ont besoin d'une expérience de rédaction soignée, adossée au contrôle de version
- **Les développeurs solo** qui souhaitent une base de connaissances personnelle avec publication publique — sans abonnement

**Ne cible pas :** les entreprises soumises à de fortes contraintes de conformité nécessitant SAML/SCIM (voir la future Enterprise Edition), ni les équipes de contenu non techniques sans familiarité avec git.

## Comment ça fonctionne

```
┌──────────────────────────────────────────────────┐
│              DocPlatform (single binary)          │
│                                                  │
│   ┌────────────┐  ┌──────────┐  ┌────────────┐  │
│   │ Web Editor  │  │ SQLite   │  │ Bleve      │  │
│   │ (Next.js)   │  │ Database │  │ Search     │  │
│   └──────┬──────┘  └────┬─────┘  └──────┬─────┘  │
│          │              │               │        │
│          └──────┬───────┴───────┬───────┘        │
│                 │               │                │
│          ┌──────▼──────┐ ┌─────▼──────┐         │
│          │ Content     │ │ Git        │         │
│          │ Ledger      │ │ Engine     │         │
│          └──────┬──────┘ └─────┬──────┘         │
│                 │              │                 │
└─────────────────┼──────────────┼─────────────────┘
                  │              │
           ┌──────▼──────┐ ┌────▼──────┐
           │ Filesystem  │ │ Remote    │
           │ (.md files) │ │ Git Repo  │
           └─────────────┘ └───────────┘
```

Chaque modification de contenu — qu'elle provienne de l'éditeur web, d'un push git ou d'un appel API — passe par le **Content Ledger**, un pipeline unique qui maintient le système de fichiers, la base de données et l'index de recherche en parfaite synchronisation.

## Démarrage rapide

Lancez DocPlatform en moins de 5 minutes :

```bash
# Télécharger le binaire (recommandé — détection automatique de la plateforme)
curl -fsSL https://valoryx.org/install.sh | sh

# Initialiser un espace de travail
docplatform init --workspace-name "My Docs" --slug my-docs

# Démarrer le serveur
docplatform serve
```

Ouvrez [http://localhost:3000](http://localhost:3000) et enregistrez votre premier utilisateur — il devient automatiquement SuperAdmin.

Pour le guide complet, consultez le guide [Premiers pas](getting-started/index.md).

## Aperçu des fonctionnalités

### Plateforme principale

- **Éditeur web riche** — Éditeur basé sur Tiptap avec formulaire de frontmatter, bascule Markdown brut et sauvegarde automatique
- **Synchronisation git bidirectionnelle** — Web → commit git → push ; push CLI → polling → mise à jour web
- **Détection des conflits** — Concurrence optimiste basée sur les hash avec diff téléchargeable en cas de collision
- **Recherche plein texte** — Moteur Bleve intégré avec résultats filtrés par permissions et raccourci Cmd+K
- **Permissions RBAC** — 6 rôles : SuperAdmin, WorkspaceAdmin, Admin, Editor, Commenter, Viewer
- **Authentification** — Locale (argon2id) + OIDC optionnel Google/GitHub
- **Modèle d'espace de travail** — Hiérarchie Org → Workspace → Pages avec invitations d'équipe
- **Journal d'audit** — Chaque modification enregistrée avec utilisateur, horodatage et type d'opération

### Documentation publiée

- **Site public** — Servez vos docs à `/p/{workspace-slug}/{page-path}`
- **Mode sombre** — Thème clair/sombre automatique avec bascule manuelle
- **7 composants intégrés** — Callout, Code (200+ langages), Tabs, Accordion, Cards, Steps, API Block
- **Prêt pour le SEO** — Balises OpenGraph, URLs canoniques, sitemap.xml, robots.txt

### Opérations

- **Diagnostics de santé** — Commande `doctor` à 9 points vérifiant la cohérence FS/DB, la santé de la recherche et les liens cassés
- **Sauvegardes quotidiennes** — Sauvegardes SQLite automatisées avec rétention configurable
- **Arrêt gracieux** — Gestion propre des signaux pour des déploiements sans interruption
- **Journalisation structurée** — Logs JSON avec identifiants de requête pour l'observabilité

## Configuration requise

| Exigence | Minimum | Recommandé |
|---|---|---|
| **OS** | Linux (amd64/arm64), macOS (amd64/arm64) | Linux amd64 |
| **Mémoire** | 128 Mo | 512 Mo |
| **Disque** | 200 Mo (binaire + données) | 1 Go |
| **Git** | Optionnel (pour la synchronisation distante) | Git 2.30+ |
| **Réseau** | Aucun (fonctionne hors ligne) | Port 3000 ouvert |

## Et ensuite

| Guide | Description |
|---|---|
| [Premiers pas](getting-started/index.md) | Installer, configurer et créer votre premier espace de travail |
| [Guides utilisateur](guides/editor.md) | Découvrir l'éditeur, la synchronisation git, la publication et la recherche |
| [Configuration](configuration/index.md) | Variables d'environnement, authentification, permissions et paramètres d'espace de travail |
| [Déploiement](deployment/binary.md) | Déploiement en production avec binaire, Docker ou conteneurs |
| [Référence CLI](reference/cli.md) | Référence complète des commandes |
| [Référence API](reference/api.md) | Points d'accès de l'API REST et exemples |
| [Dépannage](reference/troubleshooting.md) | Problèmes courants et comment les résoudre |

## Performances

Mesurées sur Apple M2, SSD NVMe, espace de travail de 1 000 pages :

| Opération | Latence |
|---|---|
| Sauvegarde de page (sync core) | < 30 ms |
| Rendu de page (réponse API) | < 50 ms p99 |
| Recherche plein texte | < 8 ms p99 |
| Vérification des permissions | < 0,1 ms |
| Vérification par lot des permissions (100 pages) | < 1 ms |
| Démarrage à froid du serveur | < 1 seconde |
| Réconciliation complète (1 000 fichiers) | < 5 secondes |
| Commit git (fichier unique) | < 2 secondes |
| Mémoire (au repos) | < 80 Mo |
| Mémoire (10 utilisateurs simultanés) | < 200 Mo |
| Taille du binaire | ~120 Mo |

## Comparaison de DocPlatform

| Fonctionnalité | DocPlatform | GitBook | Notion | Docusaurus | Confluence | Wiki.js |
|---|---|---|---|---|---|---|
| Auto-hébergé | Oui | Non | Non | Oui | Non | Oui |
| Sauvegardé par git | Oui | Partiel | Non | Oui | Non | Non |
| Éditeur web | Oui | Oui | Oui | Non | Oui | Oui |
| Synchronisation git bidirectionnelle | Oui | Non | Non | N/A | Non | Non |
| Binaire unique (zéro dépendance) | Oui | N/A | N/A | Non (Node.js) | N/A | Docker |
| RBAC intégré | Oui | Payant | Payant | Non | Oui | Oui |
| Site de documentation publié | Oui | Oui | Oui | Oui | Oui | Oui |
| Offre gratuite | Oui | Non | Non | Oui | Non | Oui |
| Fonctionne hors ligne | Oui | Non | Non | Oui | Non | Non |

## Limites de la Community Edition

La Community Edition est le noyau complet et auto-hébergeable de DocPlatform. Elle inclut tout ce qui est documenté sur ce site, avec les limites suivantes :

| Ressource | Community Edition |
|---|---|
| **Éditeurs** (utilisateurs pouvant créer/modifier des pages) | Jusqu'à 5 |
| **Espaces de travail** | Jusqu'à 3 |
| **Lecteurs et commentateurs** | Illimité (jamais comptabilisés) |
| **Pages par espace de travail** | Illimité |
| **Documentation publiée** | Illimité |

Ces limites couvrent la majorité des petites et moyennes équipes. La future Enterprise Edition offrira un nombre illimité d'éditeurs, d'espaces de travail, le support SAML/SSO, PostgreSQL et la recherche avancée via Meilisearch — mais la Community Edition restera toujours la fondation complète et auto-hébergeable.
