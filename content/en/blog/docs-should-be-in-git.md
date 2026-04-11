---
title: "Your Docs Should Be in Git. Period."
description: "Code lives in git. Infrastructure lives in git. Why do your docs still live in a wiki? An argument for version-controlled documentation."
date: "2026-03-09"
author: "Valoryx Team"
tags: ["git", "documentation", "opinion"]
---

Here's an inventory of what a typical engineering team keeps in git:

- Application source code
- Infrastructure definitions (Terraform, Pulumi, CloudFormation)
- CI/CD pipeline configurations
- Database migration scripts
- API specifications (OpenAPI, protobuf)
- Deployment manifests (Kubernetes, Docker Compose)
- Environment configuration templates

And here's what usually lives outside git:

- Documentation

This is strange. Documentation describes the system. It changes when the system changes. It needs review, versioning, attribution, and the ability to roll back. Every other artifact that shares these properties lives in git. Documentation doesn't — and nobody can give a good reason why.

## The Usual Excuses

### "Non-technical people need to edit docs"

This is the most common argument for keeping docs in Confluence or Notion. And it's valid — you can't ask a product manager to learn git branching to fix a typo. But it's not an argument against git. It's an argument for better tooling on top of git.

Git is a storage and versioning backend. Nothing requires humans to interact with it directly. A web editor can create commits and push changes the same way a CI pipeline does. The user writes in a browser; the system handles the git operations.

The framing of "git vs. non-technical users" is a false dichotomy. You can have both.

### "Docs change too often for PRs"

Some teams feel that requiring pull requests for documentation would slow down writing. And if your PR process requires two reviewers, a CI check, and a merge queue — yes, that's too much friction for fixing a typo.

But nothing about git mandates a heavy review process. You can push directly to main for minor changes and use branches for structural rewrites. The point is that the history exists. Every change is tracked, attributed, and reversible. Whether you review each change is a process decision, not a tooling constraint.

### "Our docs platform doesn't support git"

This used to be true and it used to matter. Confluence, Notion, and most wikis store content in a proprietary database with no real git integration. Exporting to markdown is lossy and one-way.

But this is a limitation of specific products, not a fundamental constraint. Documentation platforms that treat git as the source of truth — while providing a web editor for convenience — exist now. The technology caught up to the need.

### "Markdown is limiting"

Fair criticism for certain content types. Markdown doesn't natively support complex tables, embedded diagrams, or interactive elements. But for 90% of internal documentation — guides, runbooks, architecture decisions, API docs, onboarding materials — markdown is more than sufficient.

And markdown in git gives you something no proprietary format can: portability. If you decide to switch tools in two years, your content is plain text files in a standard format. Try exporting five years of Confluence content to anything useful.

## What You Lose Without Git

If your documentation lives outside git, you lose capabilities that engineers take for granted with code:

### Blame

Who wrote this paragraph claiming the API supports pagination? When? In response to what? With `git blame`, you can trace every line to its author, timestamp, and commit message. In a wiki, you might get "last edited by Sarah, 6 months ago" — with no context for why.

### Branching

You're rewriting the deployment guide for a new infrastructure. The old guide needs to stay accurate until the migration is done. In git, you create a branch. Both versions coexist. You merge when the migration is complete. In a wiki, you either maintain two pages (that inevitably diverge) or you edit in place and hope nobody follows the half-updated instructions.

### Atomic cross-repository changes

The best docs changes happen alongside code changes. A PR that adds an API endpoint should include the documentation for that endpoint. A commit that deprecates a feature should update the docs in the same commit — or at least the same PR. When docs live in a wiki, this coupling is impossible. The code ships, and someone files a ticket to "update the docs" that sits in a backlog for weeks.

### Diffing

What changed in the last release notes? Show me the diff. In git, `git diff v1.4..v1.5 -- docs/` gives you exactly what changed. In a wiki, you click through page histories one at a time, comparing rendered output and hoping you catch every edit.

### Automation

With docs in git, you can build automation:

```bash
# Find docs not updated in 90 days
git log --all --diff-filter=M --name-only --since="90 days ago" -- docs/ \
  | sort -u > recently_modified.txt

# Compare against all doc files
find docs/ -name "*.md" | sort > all_docs.txt

# Files NOT modified in 90 days
comm -23 all_docs.txt recently_modified.txt
```

Try doing this with a wiki. You'd need to hit an API, parse timestamps, and handle pagination — if the API even exposes modification dates.

## The Real Reason Docs Aren't in Git

It's not technical. It's historical. Documentation predates modern DevOps practices. Wikis emerged in the early 2000s when "infrastructure as code" didn't exist and version control meant SVN. The wiki model — edit in browser, save to database — made sense when the alternative was emailing Word documents.

But engineering practices moved on. Infrastructure went from manually configured servers to declarative code in git. CI/CD went from Jenkins jobs configured through a web UI to pipeline-as-code in YAML files. Configuration went from application settings pages to environment variables and config files in repos.

Documentation is the last holdout. Not because it's different, but because the tooling didn't catch up. Static site generators solved the "docs in git" problem for developers but excluded everyone who doesn't use a terminal. Wikis solved the "anyone can write" problem but abandoned version control. Neither side bridged the gap — until recently.

## What Good Looks Like

A documentation workflow that respects git should look like this:

1. Writers create and edit content through a web interface — no terminal required
2. Every save creates a git commit — automatically, invisibly
3. Developers can edit the same content in their IDE and push to the same repo
4. Both sides stay in sync — no conflicts, no manual merging
5. Pull requests work for docs the same way they work for code
6. The full git history is available: blame, diff, log, branch

This is not hypothetical. The [Content Ledger pattern](/blog/why-git-sync-breaks/) solves the synchronization problem. Platforms that implement it give you a wiki-like editing experience with a git repository as the backend.

If you're building a new documentation workflow — or rebuilding one that isn't working — start with git as the foundation. Pick tooling that treats the repository as the source of truth, not as an export target. Your future self, auditing what changed and why, will be glad the history exists.

As [the Git documentation itself puts it](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control): version control records changes to files over time so you can recall specific versions later. That applies to documentation just as much as it applies to code. Maybe more — because code has tests to catch regressions, but documentation only has human memory.

If your docs are worth writing, they're worth versioning. Put them in git.

---

*If you want to try a documentation platform where git is the source of truth — not an afterthought — [DocPlatform](/install/) is free and self-hosted. One binary, no database to manage, bidirectional git sync built in.*
