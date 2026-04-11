---
title: "How Bidirectional Git Sync Works"
description: "Most doc tools claim git integration but break on conflicts. Here's how the Content Ledger pattern makes true bidirectional sync reliable."
date: "2026-03-19"
author: "Valoryx Team"
tags: ["git-sync", "architecture", "documentation"]
---

Every documentation platform with a git integration page makes the same promise: your docs live in git, your team edits in the browser, and everything stays in sync. In practice, most of these integrations are one-way mirrors that fall apart the moment two people edit from different directions.

We wrote about [why this happens](/blog/why-git-sync-breaks/) in a previous post. This one goes deeper into the solution: how Valoryx implements bidirectional sync using the Content Ledger pattern, and why this approach handles the scenarios that break other tools.

## The Core Problem

A web-based editor and a git repository have fundamentally different consistency models.

In a web editor, saves are immediate and atomic. You click save, the content is persisted, and anyone loading the page sees your version. There's no concept of "staging" or "committing" — the write is the publish.

In git, changes are batched into commits, commits are pushed to a remote, and the remote must be fetched and merged by other participants. There's an inherent delay between "I made a change" and "everyone sees my change."

When you combine both models — a web editor and a git repo pointing at the same content — you create a window where two people can make conflicting edits without knowing about each other. Person A edits in the browser. Person B pushes a commit from VS Code. Neither knows about the other until sync runs, and then something has to give.

Most platforms handle this by picking a winner: either the database always wins (Wiki.js) or the git repo always wins (most static site generators). Both approaches lose data silently.

## The Content Ledger Pattern

The Content Ledger is an append-only log of every content mutation, regardless of where it originated. Think of it like a write-ahead log in a database, but for documentation edits.

Every change — whether it comes from the web editor, the API, an MCP tool call, or a git push — gets recorded as a ledger entry before it's applied. Each entry contains:

- **Timestamp** — when the change was made
- **Origin** — where it came from (web, git, api, mcp)
- **Page path** — which page was affected
- **Operation** — create, update, move, delete
- **Content hash** — SHA-256 of the new content
- **Parent hash** — SHA-256 of the content this change was based on

The parent hash is the key innovation. It creates a chain of causality, similar to how [git commits reference their parent commits](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects). When two changes have the same parent hash but different content hashes, you have a conflict — and you know about it before either change is applied.

## How Sync Works: Step by Step

Here's what happens during a sync cycle. Valoryx runs this automatically on a configurable interval (default: 30 seconds) or on-demand when a user triggers it.

### Step 1: Collect Pending Changes

The sync engine reads all ledger entries since the last successful sync. These are local changes that haven't been pushed to git yet.

### Step 2: Fetch Remote Changes

The engine runs `git fetch` to get any new commits from the remote repository. It then compares the remote HEAD with the local sync pointer to identify incoming changes.

### Step 3: Reconcile

For each page that has changes on both sides (local ledger entries AND remote git commits), the engine checks parent hashes:

- **No overlap:** The local change was based on the same version that git has. Fast-forward merge — apply both changes in order.
- **Diverged, no conflict:** Both sides changed different pages. Apply both sets of changes independently.
- **Diverged, same page:** Both sides changed the same page. This is a real conflict.

### Step 4: Conflict Resolution

When a genuine conflict is detected, Valoryx does not silently pick a winner. Instead, it:

1. Preserves both versions in the ledger
2. Marks the page as "conflicted" in the UI
3. Shows a diff between the two versions
4. Lets a human choose which version to keep, or merge them manually

This is the same model as `git merge` with conflicts — except it works through the web UI, so non-technical editors can resolve conflicts without learning git commands.

### Step 5: Commit and Push

After reconciliation, local changes are committed to the git repo and pushed. The commit message includes the origin of each change (web edit, API call, etc.) so your git history tells you not just what changed, but how.

## What This Looks Like in Practice

Consider this real scenario. A developer updates the API authentication docs from VS Code and pushes to the repo. Meanwhile, a technical writer edits the same page's introduction in the Valoryx web editor.

With a one-way sync tool, one edit overwrites the other. With the Content Ledger:

1. The developer's push creates a remote change (new commit on the git side)
2. The writer's save creates a local ledger entry (new mutation on the web side)
3. Sync runs, detects both changes touch the same page
4. Parent hashes diverge — it's a real conflict
5. The page is flagged, both versions are preserved
6. The writer sees a notification: "This page has a sync conflict" with a diff view
7. The writer merges the changes (the developer fixed a code block, the writer rewrote the intro — both edits are valid)
8. The merged version is committed and pushed

No data loss. No silent overwrites. The merge happened through a web UI, not a terminal.

## Comparison with One-Way Approaches

| Scenario | One-way (DB wins) | One-way (Git wins) | Content Ledger |
|----------|-------------------|---------------------|---------------|
| Web edit + git push (same page) | Git change lost | Web change lost | Conflict surfaced, both preserved |
| Web edit + git push (different pages) | Works | Works | Works |
| Rapid web edits | Works | Works | Works (batched into single commit) |
| Offline git edits, bulk push | Some changes lost | Works | Works |
| Git branch merge into main | Unpredictable | Works | Works (treats merge commit like any other) |
| Rename/move in web + edit in git | Path mismatch, sync breaks | Path mismatch, sync breaks | Ledger tracks moves, reconciles paths |

The last row matters more than it seems. Renaming or moving a page in a web UI while someone edits the old path in git is one of the hardest edge cases. Most tools give up here. The Content Ledger tracks move operations explicitly, so it knows that `/docs/auth.md` became `/docs/authentication.md` and can apply the incoming git edit to the correct new path.

## Why Not Just Use Git Directly?

If git is so central to this design, why not skip the web editor and use git directly? Two reasons:

First, not everyone on a documentation team uses git. Product managers, support engineers, and technical writers often prefer a web editor. Forcing them into a git workflow creates friction and reduces contribution.

Second, git alone doesn't give you published documentation. You still need a rendering layer, search indexing, access control, and a navigation structure. Valoryx provides all of that while keeping git as the canonical storage layer.

The Content Ledger bridges these two worlds. Git users work in git. Web users work in the browser. Both workflows are first-class, and the ledger keeps them consistent.

## Setting Up Git Sync

If you want to try this with your own repository:

1. [Install Valoryx](/install/) — single binary, no external dependencies
2. Create a workspace and connect it to a git repository in the workspace settings
3. Configure the remote URL, branch, and sync interval
4. Start editing from both sides

The [git integration guide](/docs/guides/git-integration/) covers the full setup, including SSH key configuration, branch strategies, and sync interval tuning.

For teams already managing documentation in git repositories, this means you don't have to choose between a good editing experience and a git-native workflow. The Content Ledger makes both possible without the compromises that plague every other approach we've tested.
