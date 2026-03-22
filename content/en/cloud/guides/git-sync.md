---
title: GitHub Sync
description: Connect your workspace to GitHub for backup, IDE editing, and version control.
weight: 4
---

# GitHub Sync

Valoryx Cloud can sync your documentation with a GitHub repository. This gives you the best of both worlds: a beautiful web editor AND the full power of git.

## Why connect GitHub?

- **Backup** — your docs are always safe in GitHub, even if you cancel your account
- **IDE editing** — developers on your team can edit docs in VS Code, Vim, or any editor
- **Pull requests** — use GitHub's PR workflow for doc reviews before publishing
- **Version history** — full git blame, diff, and rollback for every change
- **CI/CD integration** — trigger builds or tests when docs change

## How it works

```
You edit in browser → auto-saves → auto-commits → pushes to GitHub
                                                        ↕
Teammate pushes from IDE → GitHub → webhook → pulls to Valoryx
```

Changes flow in both directions automatically. You never have to think about syncing.

## Setting up

1. Go to **Workspace Settings** → **Git Sync**
2. Click **Connect GitHub**
3. Authorize Valoryx to access your repositories
4. Select the repo and branch to sync with
5. Done — your workspace is now connected

## What gets synced

Every page in your workspace maps to a `.md` file in the repository:

```
your-repo/
├── getting-started.md
├── api/
│   ├── authentication.md
│   └── endpoints.md
├── guides/
│   ├── deployment.md
│   └── troubleshooting.md
└── .docplatform.yaml     ← workspace metadata
```

## Do I need GitHub?

**No.** GitHub sync is completely optional. Valoryx Cloud works perfectly without it. Your docs are stored securely on our servers. GitHub adds backup and IDE access — but it's not required for any feature to work.
