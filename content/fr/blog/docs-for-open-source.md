---
title: "Documentation pour les projets open source"
description: "Les mainteneurs OSS ont besoin de documentation mais ne peuvent pas se permettre des outils payants. Voici comment mettre en place une documentation gratuite et auto-hébergée avec synchronisation git en moins de 5 minutes."
date: "2026-04-06"
author: "Valoryx Team"
tags: ["open-source", "documentation", "free", "tutorial"]
---

Les projets open source vivent ou meurent par leur documentation. Une bibliothèque avec une bonne documentation est adoptée. Une bibliothèque avec un simple README et une attitude « lisez le code » est forkée par quelqu'un qui écrit une meilleure documentation — ou tout simplement ignorée.

Mais la plupart des outils de documentation sont conçus pour des entreprises, pas pour des mainteneurs OSS. Ils facturent par utilisateur, par page ou par workspace. Pour un projet maintenu par des bénévoles avec un budget de zéro, c'est rédhibitoire.

Nous avons conçu l'édition Community de DocPlatform pour être gratuite pour toujours, sans aucune limite. Utilisateurs illimités, pages illimitées, workspaces illimités. Pas de « tier gratuit » qui vous pousse à passer à la version payante — l'édition Community est le produit complet sans l'hébergement cloud. Voici comment la configurer pour votre projet open source.

## La configuration typique de documentation OSS

La plupart des projets open source se retrouvent avec l'une de ces approches :

**GitHub Pages + générateur de site statique.** Vous écrivez des fichiers markdown, configurez un pipeline de build et déployez sur GitHub Pages. Le stack le plus courant est [Docusaurus](https://docusaurus.io/) (basé sur React) ou MkDocs (basé sur Python).

**Avantages :** Hébergement gratuit, contenu versionné, workflow git familier.

**Inconvénients :** Pas d'éditeur web (les contributeurs doivent connaître git, le markdown et le système de build), pas de prévisualisation en temps réel, pas de recherche sans services tiers (Algolia DocSearch a une liste d'attente et un processus d'approbation), pas de fonctionnalités de collaboration.

**Plateforme hébergée avec un tier gratuit.** GitBook, ReadMe ou Notion avec une page publique. Vous obtenez un éditeur web et une recherche hébergée.

**Avantages :** Facile à démarrer, l'éditeur web abaisse la barrière pour les contributeurs non techniques.

**Inconvénients :** Les tiers gratuits sont limités (GitBook : 1 espace, intégrations limitées ; ReadMe : références API limitées). Votre contenu vit sur le serveur de quelqu'un d'autre. S'ils changent leurs tarifs ou ferment, vous migrez sous pression.

**Markdown brut dans le dépôt.** Un dossier `docs/` avec des fichiers markdown. Pas d'étape de build, pas d'hébergement, pas de recherche.

**Avantages :** Zéro configuration. Le contenu est versionné.

**Inconvénients :** Pas moyen pour les utilisateurs de parcourir la documentation sans aller sur GitHub. Pas de recherche. Pas de structure de navigation au-delà des noms de fichiers.

## Une meilleure approche

DocPlatform vous donne le meilleur des trois : du contenu stocké en markdown dans votre dépôt git, un éditeur web pour les contributeurs non techniques, la recherche plein texte et un site de documentation publié — le tout depuis un binaire unique que vous pouvez héberger n'importe où.

Voici la configuration.

### Étape 1 : Installer DocPlatform

Sur n'importe quelle machine Linux, macOS ou Windows :

```bash
curl -fsSL https://get.valoryx.org | sh
```

Ou téléchargez le binaire directement depuis la [page d'installation](/install/). Il n'y a rien d'autre à installer — pas de base de données, pas de Docker, pas de runtime.

### Étape 2 : Démarrer le serveur

```bash
docplatform serve
```

Ouvrez `http://localhost:3000`. Créez votre compte administrateur. Votre serveur tourne.

Pour une installation permanente, utilisez un service systemd :

```ini
[Unit]
Description=DocPlatform
After=network.target

[Service]
ExecStart=/opt/docplatform/bin/docplatform serve
WorkingDirectory=/opt/docplatform
Restart=always

[Install]
WantedBy=multi-user.target
```

### Étape 3 : Créer un workspace

Un workspace dans DocPlatform est un projet de documentation. Pour un projet open source, vous aurez typiquement un workspace pour votre documentation publique.

1. Allez dans Settings → Workspaces → Create
2. Nommez-le d'après votre projet (par exemple « MyProject Docs »)
3. Choisissez un thème — il y a 5 thèmes intégrés, tous conçus pour la documentation technique

### Étape 4 : Connecter votre dépôt GitHub

C'est là que ça devient intéressant. DocPlatform prend en charge la synchronisation bidirectionnelle git — les modifications faites dans l'interface web sont commitées dans votre dépôt, et les changements poussés vers le dépôt apparaissent dans l'interface.

1. Allez dans Workspace Settings → Git Sync
2. Ajoutez l'URL de votre dépôt : `https://github.com/yourorg/yourproject.git`
3. Configurez le chemin des docs (par exemple `docs/` si votre markdown vit dans un sous-dossier)
4. Ajoutez une clé de déploiement ou un token d'accès personnel pour l'accès en écriture

Une fois connecté, DocPlatform tire vos fichiers markdown existants et les indexe pour la recherche. Tout fichier `.md` dans le chemin configuré devient une page.

### Étape 5 : Publier votre documentation

Activez « Publish » dans les paramètres du workspace. DocPlatform génère un site de documentation navigable avec :

- Une arborescence de navigation basée sur votre structure de dossiers
- La recherche plein texte avec tolérance aux fautes de frappe
- Un design responsive qui fonctionne sur mobile
- La coloration syntaxique pour les blocs de code
- Un sélecteur de mode sombre

Votre documentation publiée est accessible à `http://yourserver:3000/docs/workspace-slug/`.

## Le workflow Git

Voici à quoi ressemble le workflow en pratique pour un projet open source avec plusieurs contributeurs :

**Les mainteneurs** utilisent l'éditeur web pour les corrections rapides — corrections de fautes de frappe, restructuration de pages, mise à jour de captures d'écran. Chaque sauvegarde crée automatiquement un commit git.

**Les contributeurs externes** soumettent des PR vers le répertoire de documentation dans votre dépôt GitHub, exactement comme ils le feraient pour du code. Quand vous mergez la PR, DocPlatform récupère les modifications via la synchronisation git et met à jour le site publié.

**Les contributeurs non techniques** (community managers, rédacteurs techniques) utilisent l'éditeur WYSIWYG dans le navigateur. Ils n'ont pas besoin de connaître git ou la syntaxe markdown. Leurs modifications sont quand même commitées dans le dépôt.

Cela signifie que votre documentation a le même processus de revue que votre code. Vous voulez que quelqu'un révise une modification de documentation avant qu'elle soit en ligne ? Demandez-lui de soumettre une PR. Vous voulez laisser des contributeurs de confiance éditer directement ? Donnez-leur un accès éditeur dans DocPlatform.

## Comparaison : DocPlatform vs. Docusaurus

Puisque Docusaurus est l'outil de documentation OSS le plus populaire, voici une comparaison directe :

| Fonctionnalité | Docusaurus | DocPlatform CE |
|---|---|---|
| Éditeur web | Non — éditer le markdown, commiter, attendre le build | Oui — WYSIWYG, modifications en direct |
| Recherche | Nécessite Algolia DocSearch (liste d'attente) ou Lunr.js (côté client, limité) | Recherche plein texte intégrée (Bleve) |
| Étape de build | Oui — build React, peut prendre 30+ secondes | Non — les pages sont rendues à la sauvegarde |
| Intégration git | Native (c'est un générateur de site statique) | Synchronisation bidirectionnelle (web ↔ git) |
| Versions multiples | Oui (docs versionnés) | Basé sur les workspaces (un workspace par version) |
| Temps d'installation | 10-30 minutes (Node.js, npm, config) | 2 minutes (télécharger le binaire, lancer) |
| Hébergement | GitHub Pages, Netlify, Vercel (gratuit) | Auto-hébergé (vous avez besoin d'un serveur) |
| RBAC | Aucun (c'est un outil de build) | 5 rôles (admin, manager, éditeur, relecteur, lecteur) |
| i18n | Basé sur les plugins | Basé sur les workspaces |

Docusaurus gagne si vous voulez un hébergement gratuit sur GitHub Pages et que vos contributeurs sont tous à l'aise avec git et React. DocPlatform gagne si vous voulez un éditeur web, une recherche intégrée, un contrôle d'accès, ou si vos contributeurs ne sont pas tous des développeurs.

## Hébergement à petit budget

Une objection courante : « Docusaurus est gratuit parce que GitHub Pages l'héberge. L'auto-hébergement signifie que j'ai besoin d'un serveur. »

C'est vrai. Mais les serveurs sont bon marché :

- **Hetzner CX22 :** 2 vCPU, 4 Go RAM, 40 Go disque — 3,99 EUR/mois
- **Oracle Cloud Free Tier :** Instance ARM, 24 Go RAM — gratuit pour toujours
- **Vieux laptop dans un placard :** Gratuit si vous en avez déjà un

DocPlatform utilise environ 50 Mo de RAM au repos et 100-200 Mo en charge. Tout serveur capable d'exécuter un binaire Go peut le faire tourner.

Si vous exécutez déjà un serveur CI, un bot Discord ou tout autre service pour votre projet, DocPlatform peut tourner sur la même machine.

## Configuration réelle : de zéro à une documentation publiée

Parcourons un exemple concret. Vous maintenez un outil CLI appelé `fastgrep` et voulez passer d'un README à une vraie documentation.

```bash
# Installer DocPlatform
curl -fsSL https://get.valoryx.org | sh

# Démarrer le serveur
docplatform serve &

# Ouvrir le navigateur, créer le compte admin, créer le workspace
# Connecter à github.com/yourname/fastgrep, chemin docs : docs/

# Créer vos premières pages dans l'éditeur web :
# - Premiers pas
# - Installation
# - Configuration
# - Référence CLI
# - Contribuer
```

Chaque page que vous créez dans l'éditeur web est commitée dans `docs/` de votre dépôt. Vos fichiers markdown `docs/` existants (s'il y en a) sont importés automatiquement.

Publiez le workspace, pointez votre domaine vers le serveur, et votre projet dispose d'une documentation avec recherche et éditeur web — configurée en moins de 5 minutes.

Pour la configuration complète de publication, consultez le [guide de publication](/docs/guides/publishing/).

## Gratuit signifie gratuit

L'[édition Community](/open-source/) n'est pas un essai. Ce n'est pas un tier gratuit limité. C'est le produit complet :

- Utilisateurs et éditeurs illimités
- Workspaces et pages illimités
- Recherche plein texte
- Synchronisation git
- RBAC avec 5 rôles
- Les 5 thèmes
- Authentification WebAuthn/passkey
- Serveur MCP avec 13 outils IA

La seule chose que l'édition Community n'inclut pas est l'hébergement cloud — vous l'exécutez sur votre propre infrastructure. Pour les projets open source qui gèrent déjà leur propre infrastructure, ce n'est pas une limitation ; c'est un avantage.

[Téléchargez DocPlatform](/install/) et donnez à votre projet la documentation qu'il mérite.
