---
title: "Votre compte"
description: "Gerez votre profil, votre mot de passe, votre facturation et vos donnees."
weight: 6
---

# Votre compte

## Inscription

Rendez-vous sur [app.valoryx.dev](https://app.valoryx.dev/#/register) et creez un compte avec votre adresse e-mail et un mot de passe. Vous devrez accepter les [Conditions d'utilisation](/terms/) et la [Politique de confidentialite](/privacy/).

Vous pouvez egalement vous connecter avec **Google** ou **GitHub** si ces options sont disponibles.

## Parametres du profil

Cliquez sur votre avatar en haut a gauche, puis **Profile** pour :

- Modifier votre nom d'affichage
- Mettre a jour votre adresse e-mail
- Changer votre mot de passe
- Configurer une passkey (WebAuthn) pour la connexion sans mot de passe

## Facturation

Allez dans **Workspace Settings** → **Billing** pour :

- Consulter votre offre actuelle et votre utilisation
- Passer a l'offre Team (29 $/mois) ou Business (79 $/mois)
- Gerer votre abonnement via le portail Stripe
- Consulter vos factures et l'historique des paiements

## Vos donnees

### Ce que nous stockons

- Votre adresse e-mail, votre nom et votre mot de passe (hache avec Argon2id)
- Le contenu de votre documentation (dans les espaces de travail)
- Les journaux d'activite (qui a modifie quoi et quand)

### Ce que nous ne stockons pas

- Les numeros de carte bancaire (geres entierement par Stripe)
- Vos identifiants Git (tokens OAuth, non conserves a long terme)
- Les cookies de suivi (les analyses sont opt-in, conformes au RGPD)

### Exporter vos donnees

Votre contenu est toujours portable :

- **Avec GitHub sync** — vos documents sont deja dans votre depot GitHub sous forme de fichiers Markdown
- **Sans GitHub sync** — utilisez le bouton **Export** dans les parametres de l'espace de travail pour telecharger un ZIP contenant tous vos fichiers Markdown
- **Donnees du compte** — demandez un export complet de vos donnees en nous contactant

### Supprimer votre compte

Contactez-nous a valoryxeu@gmail.com pour demander la suppression de votre compte. Nous supprimerons toutes vos donnees sous 30 jours, conformement au RGPD.

## Securite

- Les mots de passe sont haches avec Argon2id (recommande par l'OWASP)
- Les sessions utilisent des cookies HttpOnly (inaccessibles au JavaScript)
- Tout le trafic est chiffre via TLS
- Connexion sans mot de passe optionnelle via passkey/WebAuthn
- Journal d'audit complet de toutes les actions sur le compte
