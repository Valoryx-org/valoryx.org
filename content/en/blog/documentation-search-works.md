---
title: "How Documentation Search Actually Works"
description: "Most doc tools use basic keyword matching or require Elasticsearch. DocPlatform embeds Bleve for full-text search with stemming and fuzzy matching — no extra services."
date: "2026-04-02"
author: "Valoryx Team"
tags: ["search", "architecture", "documentation"]
---

You type a query into your documentation search bar. Results appear. But what happened between the keystroke and the results? For most documentation platforms, the answer is either "not much" (basic keyword matching that misses obvious results) or "a lot of infrastructure" (an Elasticsearch cluster that your ops team has to maintain).

There's a middle ground that most teams don't know about: embedded full-text search. DocPlatform uses [Bleve](https://blevesearch.com/), a search library written in Go, compiled directly into the binary. No external services, no network calls, no cluster to manage — but with the features you actually need: stemming, fuzzy matching, field boosting, and relevance ranking.

Here's how it works from the ground up.

## Why Keyword Matching Fails

The simplest search implementation is `LIKE '%query%'` in SQL. It's what you get when a developer adds search as an afterthought. It works for exact matches but fails in every other case:

- Searching for "install" doesn't find pages containing "installation" or "installing"
- Searching for "authn" doesn't find pages about "authentication"
- A typo like "deploymnet" returns nothing
- Every result has equal ranking — a page titled "Installation Guide" ranks the same as a page that mentions "install" once in the footer

Some platforms improve on this with SQLite's FTS5 extension, which adds tokenization and basic ranking. It's a step up, but it still lacks stemming, fuzzy matching, and the ability to boost certain fields (like titles) over others.

## What Full-Text Search Actually Does

A proper search engine processes text in two phases: indexing (when content is written) and querying (when someone searches). Both phases do more work than you'd expect.

### Indexing: What Happens When You Save a Page

When you create or update a page in DocPlatform, the content goes through an analysis pipeline before being indexed:

**1. Tokenization** — The text is split into individual terms. "Getting started with DocPlatform" becomes `["getting", "started", "with", "docplatform"]`.

**2. Lowercasing** — All tokens are normalized to lowercase. "DocPlatform" and "docplatform" match.

**3. Stop word removal** — Common words like "the", "is", "with", "a" are removed. They appear in almost every document and don't help distinguish relevant results.

**4. Stemming** — Words are reduced to their root form. "installing", "installation", and "installed" all become "instal". This means a search for any of these words finds all of them.

**5. Field separation** — Different parts of the document are indexed separately. The title, body, tags, and path each get their own field in the index. This enables field boosting at query time.

The resulting index is a data structure called an inverted index — a map from each term to the list of documents containing it, along with positional information (where in the document the term appears and how often).

```
"instal"     → [doc_3 (title, pos:0), doc_7 (body, pos:45), doc_12 (body, pos:102)]
"deploy"     → [doc_3 (body, pos:23), doc_5 (title, pos:0)]
"kubernetes" → [doc_5 (body, pos:15), doc_5 (body, pos:89)]
```

### Querying: What Happens When You Search

When a user types a query, the search engine runs the same analysis pipeline on the query text (tokenize, lowercase, stem), then looks up each term in the inverted index.

But the real value is in ranking. Not all matches are equal. Bleve uses a TF-IDF variant (term frequency, inverse document frequency) combined with field boosting to produce a relevance score:

- **Term frequency:** A page that mentions "deployment" 10 times is probably more relevant than one that mentions it once.
- **Inverse document frequency:** A term that appears in only 3 out of 500 documents is more distinctive (and more useful for ranking) than a term that appears in 400 documents.
- **Field boost:** A match in the title is worth more than a match in the body. In DocPlatform, title matches get a 3x boost, tag matches get 2x, and body matches get 1x.

The formula produces a numeric score for each matching document, and results are returned sorted by score.

## Fuzzy Matching: Handling Typos

Real users make typos. "Kuberntes" instead of "Kubernetes." "Authentcation" instead of "Authentication." Basic search returns nothing for these queries.

Bleve supports fuzzy matching using edit distance (Levenshtein distance). A query term matches a document term if they differ by N or fewer character operations (insertions, deletions, substitutions). DocPlatform uses an edit distance of 1 by default — enough to catch single-character typos without producing too many false positives.

```
Query: "authentcation"
Edit distance 1: matches "authentication" (one missing 'i')
Results: all documents containing "authentication"
```

This happens transparently. Users don't need to know about fuzzy matching or configure anything. They just search and get results even when they mistype.

## How DocPlatform Keeps the Index in Sync

The tricky part of embedded search isn't the search itself — it's keeping the index consistent with the content. DocPlatform has two content sources: the web editor and git. Both can create, update, and delete pages.

Here's the indexing flow:

**Web editor save:** User clicks save → content is written to the database → the search indexer updates the Bleve index → the git sync engine commits the change.

**Git push received:** Git webhook fires → the sync engine pulls changes → new/modified pages are written to the database → the search indexer updates the Bleve index.

**Bulk operations:** When you import a repository with hundreds of markdown files, the indexer processes them in batches. A 500-page import takes about 3 seconds to fully index on modest hardware.

**Deletions:** When a page is deleted (from either the web UI or git), the corresponding document is removed from the Bleve index. No orphaned search results.

The important detail: indexing is synchronous with the write operation. When the save/sync completes, the search index is already updated. There's no "wait for reindexing" delay. This is possible because Bleve runs in the same process — there's no network hop to a separate Elasticsearch cluster.

For more on how the sync engine works, see our post on [why git sync breaks](/blog/why-git-sync-breaks/) and the Content Ledger pattern that solves it.

## Comparison: Embedded vs. External Search

| Capability | SQL LIKE | SQLite FTS5 | Bleve (embedded) | Elasticsearch |
|---|---|---|---|---|
| Tokenization | No | Yes | Yes | Yes |
| Stemming | No | Limited | Yes | Yes |
| Fuzzy matching | No | No | Yes | Yes |
| Field boosting | No | No | Yes | Yes |
| Relevance ranking | No | Basic | TF-IDF | BM25 |
| Extra service | No | No | No | Yes |
| Memory overhead | None | ~1MB | ~10MB | 1-4 GB (JVM) |
| Ops complexity | None | None | None | High |

Elasticsearch wins on advanced features: aggregations, nested document queries, custom analyzers, distributed search across clusters. If you're building a search product, you probably need it.

But for documentation search — where the corpus is thousands of pages, not millions of records — embedded Bleve covers the requirements with zero operational overhead. You don't need a separate cluster to search your docs.

As we covered in [the single binary architecture post](/blog/single-binary-architecture/), keeping everything in one process eliminates an entire class of operational problems.

## What Users Actually Search For

We built our search configuration around how people actually search documentation:

**Exact feature names:** "RBAC", "WebAuthn", "git sync" — these need to match precisely in titles and tags.

**Conceptual queries:** "how to set up permissions" — these rely on stemming and body text matching.

**Partial recall:** "that page about deploy..." — fuzzy matching and title boosting help surface the right result even with incomplete queries.

**Error messages:** Users paste error messages into search. These benefit from exact matching with long token sequences.

The default configuration handles all of these well. No tuning required.

## Try It

If you want to see this in action, [install DocPlatform](/install/) and create a few pages. The search bar in the published docs site uses exactly the system described here. Type a query, misspell something intentionally, and watch it still find what you need.

The Community Edition includes full search capabilities — no feature gates, no "upgrade for better search." The [search configuration guide](/docs/guides/search/) covers the details of customizing search behavior if you need it.
