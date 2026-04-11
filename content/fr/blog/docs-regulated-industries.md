---
title: "Documentation auto-hébergée pour les équipes réglementées"
description: "Quand vos données ne peuvent pas quitter votre infrastructure, les options de documentation se réduisent. Ce qu'il faut rechercher et comment les outils auto-hébergés répondent aux exigences de conformité."
date: "2026-03-23"
author: "Valoryx Team"
tags: ["compliance", "self-hosted", "security", "documentation"]
---

Si vous travaillez dans la santé, la défense, la finance ou tout secteur où la résidence des données compte, vous avez déjà eu la conversation : « Peut-on utiliser cet outil SaaS, ou doit-il passer par une évaluation de sécurité de six mois ? » Pour la plupart des plateformes de documentation cloud, la réponse est l'évaluation — et elle se termine souvent par « non ».

Le problème n'est pas que les outils cloud sont insécurisés. La plupart sont compétents en matière de sécurité. Le problème est le contrôle. Les environnements réglementés doivent prouver où vivent les données, qui peut y accéder, comment elles sont chiffrées et ce qui se passe quand quelque chose tourne mal. Avec une plateforme SaaS, vous faites confiance à leurs réponses. Avec l'auto-hébergement, vous pouvez vérifier les vôtres.

## Pourquoi la documentation est négligée en matière de conformité

Les équipes de sécurité auditent les bases de données, les dépôts de code et les outils de communication. Les plateformes de documentation passent souvent entre les mailles parce qu'elles sont perçues comme « juste de la doc » — des wikis internes avec des notes de réunion et des guides d'onboarding.

Mais la documentation contient fréquemment :

- **Des diagrammes d'architecture** avec la topologie réseau et les plages d'adresses IP
- **Des spécifications API** avec les flux d'authentification et les formats de tokens
- **Des runbooks** avec des identifiants, des chaînes de connexion et des procédures d'escalade
- **De la documentation destinée aux clients** avec des capacités produit soumises au contrôle des exportations
- **Des rapports d'incidents** avec des détails sur les vulnérabilités

Ce sont des informations sensibles. Si elles vivent sur un serveur tiers dans une juridiction que vous ne contrôlez pas, vous pourriez être en non-conformité sans le réaliser.

## La checklist de conformité

Lors de l'évaluation d'outils de documentation pour des environnements réglementés, voici les exigences non négociables :

### Résidence des données

Où vivent physiquement les données ? Avec des outils auto-hébergés, la réponse est simple : sur votre infrastructure, dans la région de votre choix. Avec des outils SaaS, vous devez vérifier les emplacements des data centers du fournisseur et les éventuels sous-traitants tiers.

Sous le [RGPD](https://commission.europa.eu/law/law-topic/data-protection_en), les transferts de données personnelles hors de l'UE nécessitent des mécanismes juridiques spécifiques. Si votre documentation contient des données personnelles (noms d'employés, informations clients, recherche utilisateur), l'emplacement d'hébergement compte.

### Authentification et contrôle d'accès

Qui peut accéder à la documentation, et comment le prouver ? Les environnements réglementés exigent typiquement :

- **Authentification multifacteur** — les mots de passe seuls ne suffisent pas
- **Contrôle d'accès basé sur les rôles (RBAC)** — tout le monde ne devrait pas tout voir
- **Gestion des sessions** — expirations automatiques, limites de sessions concurrentes
- **Piste d'audit** — qui a accédé à quoi, quand, depuis où

### Chiffrement

Les données doivent être chiffrées en transit et au repos. « Nous utilisons HTTPS » couvre le transit. Au repos, la question est plus difficile : la base de données est-elle chiffrée ? Les pièces jointes sont-elles chiffrées ? Quel algorithme et quelle longueur de clé ?

### Journalisation d'audit

Les cadres de conformité exigent des preuves. Quand un auditeur demande « qui a accédé à ce document le 15 mars », vous avez besoin d'une réponse. Les journaux d'audit doivent capturer :

- L'identité de l'utilisateur (pas seulement « quelqu'un »)
- L'action effectuée (lecture, écriture, suppression, export)
- L'horodatage
- L'adresse IP ou l'identifiant de session
- Le succès ou l'échec

### Portabilité des données

Si vous devez changer d'outil — ou si un régulateur demande un export de données — pouvez-vous récupérer votre contenu dans un format standard ? Les formats propriétaires créent du verrouillage et du risque de conformité.

## Ce que Valoryx fournit

Voici comment Valoryx répond à chaque exigence. Ce ne sont pas des affirmations marketing — ce sont des détails d'implémentation que vous pouvez vérifier dans la [documentation de sécurité](/security/) et le code source.

### Authentification

Valoryx prend en charge l'authentification WebAuthn/passkey et l'authentification traditionnelle par mot de passe. Les mots de passe sont hachés avec **Argon2id** — le gagnant du Password Hashing Competition, conçu pour résister aux attaques GPU et ASIC. Argon2id est la recommandation actuelle de l'OWASP pour le stockage des mots de passe.

Le RBAC est intégré avec cinq rôles : Owner, Admin, Editor, Viewer et Guest. Chaque rôle dispose de permissions explicites pour l'accès aux workspaces, l'édition de pages, la gestion des utilisateurs et la configuration système. Les permissions sont appliquées au niveau de l'API, pas seulement de l'interface — même les appels API directs respectent les limites des rôles.

### Chiffrement

Toutes les données au repos sont chiffrées avec **AES-256-GCM**. Cela inclut la base de données SQLite, les pièces jointes et tout contenu en cache. AES-256-GCM fournit à la fois la confidentialité et l'intégrité — les données altérées sont détectées, pas seulement illisibles.

En transit, Valoryx sert via HTTPS. Pour les installations derrière un reverse proxy (le schéma courant), le TLS se termine au proxy. Le [guide d'installation](/install/) couvre les configurations TLS direct et reverse proxy.

### Content Security Policy

Valoryx envoie des en-têtes **Content Security Policy (CSP)** stricts qui empêchent le cross-site scripting, le clickjacking et l'exfiltration de données via des scripts inline. Les en-têtes CSP sont configurés par défaut — aucune configuration manuelle requise.

### Journalisation d'audit

Chaque action significative est journalisée : consultations de pages, modifications, suppressions, tentatives de connexion (réussies et échouées), changements de permissions, opérations de synchronisation git et utilisation des clés API. Les journaux incluent l'identité de l'utilisateur, l'horodatage, l'adresse IP et la ressource spécifique concernée.

Les journaux sont stockés localement dans la même base de données SQLite, ce qui signifie qu'ils sont couverts par les mêmes politiques de chiffrement et de sauvegarde que votre contenu. Pour les organisations qui transmettent les journaux à un SIEM, le journal d'activité est accessible via l'API d'administration.

### Portabilité des données

Tout le contenu est stocké en markdown standard. La synchronisation git signifie que votre contenu existe déjà dans un dépôt git en fichiers texte brut. Si vous arrêtez d'utiliser Valoryx demain, votre documentation est toujours là — dans votre dépôt, dans un format standard, avec l'historique complet.

Pas d'étape d'export propriétaire. Pas de contournement « télécharger en ZIP ». Votre contenu est toujours accessible dans le format dans lequel vous l'avez écrit.

## Comparaison : auto-hébergé vs. cloud pour la conformité

| Exigence | SaaS cloud | Auto-hébergé (Valoryx) |
|------------|------------|----------------------|
| Résidence des données | Data centers du fournisseur (vérifier les régions) | Votre infrastructure, votre région |
| Authentification | Gérée par le fournisseur (généralement OAuth/SAML) | Vous contrôlez : WebAuthn, mots de passe Argon2id, RBAC |
| Chiffrement au repos | Géré par le fournisseur (vérifier l'algorithme) | AES-256-GCM, clés sur votre serveur |
| Journaux d'audit | Format du fournisseur, leur rétention | Vos journaux, votre rétention, votre SIEM |
| Sous-traitants | Chaîne de fournisseurs (lire le DPA) | Aucun — binaire unique, aucun appel externe |
| Export des données | Format d'export du fournisseur (peut être propriétaire) | Markdown standard dans un dépôt git |
| Réponse aux incidents | Le fournisseur vous notifie (vérifier les SLA) | Vous détectez, vous répondez, vous contrôlez le calendrier |

La ligne « sous-traitants » mérite d'être soulignée. De nombreux outils de documentation SaaS utilisent des services tiers pour la recherche (Algolia), l'analytique (Segment), le suivi d'erreurs (Sentry) et l'hébergement (AWS, GCP). Chaque sous-traitant est un maillon de la chaîne de conformité qui nécessite sa propre évaluation. Valoryx est un binaire Go unique avec zéro dépendance externe et zéro appel réseau sortant. Il n'y a pas de chaîne de fournisseurs à auditer.

## Étapes pratiques

Si vous évaluez des outils de documentation pour un environnement réglementé :

1. **Cartographiez vos données.** Qu'y a-t-il réellement dans votre documentation ? Détails d'architecture, identifiants, données clients ? Cela détermine quels cadres de conformité s'appliquent.

2. **Vérifiez les exigences de votre cadre.** RGPD, SOC 2, HIPAA, ITAR et FedRAMP ont chacun des exigences différentes en matière de résidence des données, de chiffrement et de contrôle d'accès. Sachez lesquels s'appliquent à votre organisation.

3. **Essayez d'abord l'auto-hébergement.** [Installez Valoryx](/install/) sur votre infrastructure, connectez-le à votre fournisseur d'identité et vérifiez les contrôles de sécurité vous-même. L'édition Community est gratuite sans restriction de fonctionnalités — la même authentification, le même chiffrement et la même journalisation d'audit disponibles dans chaque installation.

4. **Documentez vos contrôles.** Quand l'auditeur arrive, vous devrez montrer : où vivent les données, comment elles sont chiffrées, qui a accès et ce que montre la piste d'audit. Les outils auto-hébergés rendent chacune de ces questions vérifiable avec des preuves de vos propres systèmes.

Consultez notre [politique de confidentialité](/privacy/) et nos [conditions d'utilisation](/terms/) pour les détails sur la façon dont Valoryx gère les données dans notre offre cloud. Pour les installations auto-hébergées, vos données ne touchent jamais notre infrastructure.

La conformité ne devrait pas dicter vos choix d'outillage — mais c'est souvent le cas. La documentation auto-hébergée donne aux équipes réglementées un système de moins à expliquer à l'auditeur et un système de plus entièrement sous leur propre contrôle.
