---
title: "Why Every Git Docs Tool Breaks Sync (And How We Fixed It)"
description: "Every documentation platform claims git integration. Most of them lie. Here's what actually goes wrong — and the Content Ledger pattern that finally solves it."
date: "2026-02-22"
author: "Valoryx Team"
tags: ["git-sync", "documentation", "architecture"]
---

If you maintain technical documentation, you've probably been burned by this promise: "Full git integration." You connect your repo, make some edits in the web UI, push a commit from your IDE — and everything falls apart. Merge conflicts. Lost edits. Pages that silently revert. A sync status that says "up to date" while your content diverges.

This isn't a bug in any single product. It's a fundamental design flaw in how most documentation platforms think about git.

## The Three Ways Git Sync Fails

After studying every major docs platform that claims git integration — GitBook, Wiki.js, Notion (via third-party), Outline, BookStack — we identified three failure patterns that appear over and over.

### 1. One-Way Mirror, Not True Sync

Most platforms treat git as a backup target, not a source of truth. Edits flow from the web UI into git (as commits), but changes pushed to git from an IDE or CI pipeline are either ignored or cause conflicts.

GitBook's "Git Sync" is the most visible example. It works well for simple cases — edit in the browser, see the commit in GitHub. But push a markdown change from VS Code, and you'll get a merge conflict notification that requires manual resolution in their UI. For teams where developers edit docs alongside code, this breaks the workflow entirely.

### 2. Database-First, Git-Second

Wiki.js stores all content in a database (PostgreSQL, MySQL, or SQLite). It offers git "synchronization" as an optional feature, but the database is always the canonical source. If the database and git diverge — which happens when someone edits directly in git — the database wins.

This means git is not your source of truth. It's a read-only export. You cannot `git clone` the repo, make changes, push, and see them reflected in the UI without going through the database layer first. For developers who think in git-native workflows, this is a dealbreaker.

### 3. Destructive Conflict Resolution

When sync does break, most platforms handle conflicts badly. Common approaches include silently overwriting one version (usually the git version loses), creating duplicate pages with timestamps appended, or simply marking the sync as "failed" and leaving the user to figure out what happened.

None of these are acceptable for documentation that teams depend on.

## Why This Is Hard

Bidirectional sync between a web application and a git repository is genuinely difficult. The core challenge is that a web UI expects immediate, atomic writes (click save, content is persisted), while git operates on snapshots (commit, push, merge). These two models create a timing gap where concurrent edits can diverge.

Consider this scenario:

1. Alice edits `getting-started.md` in the web editor
2. Bob edits the same file in VS Code and pushes to main
3. Alice clicks "Save" — her edit creates a commit
4. Now there are two divergent commits on the same branch

In a pure git workflow, this produces a merge conflict. But a web UI cannot show a merge conflict dialog — users expect their save to just work.

## The Content Ledger Pattern

This is the problem we set out to solve with Valoryx. Our approach is called the **Content Ledger** — a synchronization engine that treats both the web UI and git as equal peers, with a shared event log that prevents conflicts before they happen.

Here's how it works:

**Every mutation is an event.** When you edit a page in the web UI, Valoryx doesn't write directly to the database or directly to git. It creates a ledger entry — a structured event that says "page X was modified, here's the diff." The ledger is append-only and totally ordered.

**Events are applied to both targets.** A background worker reads the ledger and applies each event to both the database (for the web UI) and the git repository (for IDE users). Because events are ordered, both targets converge to the same state.

**Git pushes become ledger entries.** When someone pushes to the git remote, a webhook triggers Valoryx to read the new commits, convert each file change into a ledger entry, and apply it. The web UI updates within seconds.

**Conflicts are impossible by design.** Because every mutation goes through the ledger, and the ledger is strictly ordered, there is no window where two writes can diverge. If Alice and Bob edit the same page simultaneously, their edits are serialized in the ledger — the second one is applied on top of the first, just like sequential git commits.

## What This Means in Practice

With the Content Ledger, you can:

- Edit in the browser, and the commit appears in `git log` within seconds
- Push from VS Code, and the change appears in the web UI without manual sync
- Run CI pipelines that modify docs (auto-generated API references, for example) and see the results in the web editor
- Roll back any change using `git revert` — the web UI reflects the revert immediately

There is no "sync status" to check. There is no conflict resolution UI. There is no divergence. The git repo and the web UI are always in agreement because they share a single source of truth: the ledger.

## Try It Yourself

Valoryx is a single Go binary with zero external dependencies. Download it, point it at a git repo, and see bidirectional sync that actually works. No Docker required, no database to configure, no YAML to write.

We built this because we were tired of documentation tools that treat git as an afterthought. If you feel the same way, we'd love to hear from you.
