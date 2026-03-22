---
title: "Synchronisation GitHub"
description: "Connectez votre espace de travail a GitHub pour la sauvegarde, l'edition dans votre IDE et le controle de version."
weight: 4
---

# Synchronisation GitHub

Valoryx Cloud peut synchroniser votre documentation avec un depot GitHub. Vous profitez ainsi du meilleur des deux mondes : un editeur web elegant ET toute la puissance de git.

## Pourquoi connecter GitHub ?

- **Sauvegarde** — vos documents sont toujours en securite sur GitHub, meme si vous resiliez votre compte
- **Edition dans l'IDE** — les developpeurs de votre equipe peuvent modifier les documents dans VS Code, Vim ou tout autre editeur
- **Pull requests** — utilisez le workflow de PR de GitHub pour relire les documents avant publication
- **Historique des versions** — git blame, diff et rollback complets pour chaque modification
- **Integration CI/CD** — declenchez des builds ou des tests lorsque la documentation change

## Comment ca fonctionne

```
Vous editez dans le navigateur → sauvegarde auto → commit auto → push vers GitHub
                                                                       ↕
Un collegue pousse depuis son IDE → GitHub → webhook → pull vers Valoryx
```

Les modifications circulent dans les deux sens automatiquement. Vous n'avez jamais a vous soucier de la synchronisation.

## Mise en place

1. Allez dans **Workspace Settings** → **Git Sync**
2. Cliquez sur **Connect GitHub**
3. Autorisez Valoryx a acceder a vos depots
4. Selectionnez le depot et la branche a synchroniser
5. C'est fait — votre espace de travail est maintenant connecte

## Ce qui est synchronise

Chaque page de votre espace de travail correspond a un fichier `.md` dans le depot :

```
your-repo/
├── getting-started.md
├── api/
│   ├── authentication.md
│   └── endpoints.md
├── guides/
│   ├── deployment.md
│   └── troubleshooting.md
└── .docplatform.yaml     ← metadonnees de l'espace de travail
```

## Ai-je besoin de GitHub ?

**Non.** La synchronisation GitHub est entierement optionnelle. Valoryx Cloud fonctionne parfaitement sans. Vos documents sont stockes en toute securite sur nos serveurs. GitHub ajoute la sauvegarde et l'acces depuis un IDE — mais ce n'est requis pour aucune fonctionnalite.
