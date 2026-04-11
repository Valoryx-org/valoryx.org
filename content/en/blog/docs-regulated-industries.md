---
title: "Self-Hosted Docs for Regulated Teams"
description: "When your data can't leave your infrastructure, documentation options shrink. What to look for and how self-hosted tools meet compliance needs."
date: "2026-03-23"
author: "Valoryx Team"
tags: ["compliance", "self-hosted", "security", "documentation"]
---

If you work in healthcare, defense, finance, or any industry where data residency matters, you've already had the conversation: "Can we use this SaaS tool, or does it need to go through a six-month security review?" For most cloud documentation platforms, the answer is the review — and it often ends with "no."

The issue isn't that cloud tools are insecure. Most of them are competent at security. The issue is control. Regulated environments need to prove where data lives, who can access it, how it's encrypted, and what happens when something goes wrong. With a SaaS platform, you're trusting their answers. With self-hosted, you can verify your own.

## Why Documentation Gets Overlooked in Compliance

Security teams audit databases, code repositories, and communication tools. Documentation platforms often slip through because they're seen as "just docs" — internal wikis with meeting notes and onboarding guides.

But documentation frequently contains:

- **Architecture diagrams** with network topology and IP ranges
- **API specifications** with authentication flows and token formats
- **Runbooks** with credentials, connection strings, and escalation procedures
- **Customer-facing docs** with product capabilities that are export-controlled
- **Incident reports** with vulnerability details

This is sensitive material. If it lives on a third-party server in a jurisdiction you don't control, you may be out of compliance without realizing it.

## The Compliance Checklist

When evaluating documentation tools for regulated environments, these are the non-negotiable requirements:

### Data Residency

Where does the data physically live? With self-hosted tools, the answer is simple: on your infrastructure, in your chosen region. With SaaS tools, you need to verify the provider's data center locations and any third-party subprocessors.

Under [GDPR](https://commission.europa.eu/law/law-topic/data-protection_en), personal data transfers outside the EU require specific legal mechanisms. If your documentation contains any personal data (employee names, customer information, user research), the hosting location matters.

### Authentication and Access Control

Who can access the docs, and how do you prove it? Regulated environments typically require:

- **Multi-factor authentication** — passwords alone aren't sufficient
- **Role-based access control (RBAC)** — not everyone should see everything
- **Session management** — automatic timeouts, concurrent session limits
- **Audit trail** — who accessed what, when, from where

### Encryption

Data must be encrypted in transit and at rest. "We use HTTPS" covers transit. At rest is the harder question: is the database encrypted? Are file attachments encrypted? What algorithm and key length?

### Audit Logging

Compliance frameworks require evidence. When an auditor asks "who accessed this document on March 15th," you need an answer. Audit logs must capture:

- User identity (not just "someone")
- Action performed (read, write, delete, export)
- Timestamp
- IP address or session identifier
- Success or failure

### Data Portability

If you need to switch tools — or if a regulator requests a data export — can you get your content out in a standard format? Proprietary formats create lock-in and compliance risk.

## What Valoryx Provides

Here's how Valoryx addresses each requirement. These aren't marketing claims — they're implementation details you can verify in the [security documentation](/security/) and the source code.

### Authentication

Valoryx supports WebAuthn/passkey authentication and traditional password auth. Passwords are hashed with **Argon2id** — the winner of the Password Hashing Competition, designed to resist both GPU and ASIC attacks. Argon2id is the current recommendation from OWASP for password storage.

RBAC is built in with five roles: Owner, Admin, Editor, Viewer, and Guest. Each role has explicit permissions for workspace access, page editing, user management, and system configuration. Permissions are enforced at the API level, not just the UI — so even direct API calls respect role boundaries.

### Encryption

All data at rest is encrypted with **AES-256-GCM**. This includes the SQLite database, file attachments, and any cached content. AES-256-GCM provides both confidentiality and integrity — tampered data is detected, not just unreadable.

In transit, Valoryx serves over HTTPS. For installations behind a reverse proxy (the common pattern), TLS terminates at the proxy. The [installation guide](/install/) covers both direct TLS and reverse-proxy configurations.

### Content Security Policy

Valoryx sends strict **Content Security Policy (CSP)** headers that prevent cross-site scripting, clickjacking, and data exfiltration via inline scripts. CSP headers are configured by default — no manual setup required.

### Audit Logging

Every significant action is logged: page views, edits, deletions, login attempts (successful and failed), permission changes, git sync operations, and API key usage. Logs include user identity, timestamp, IP address, and the specific resource affected.

Logs are stored locally in the same SQLite database, which means they're covered by the same encryption and backup policies as your content. For organizations that forward logs to a SIEM, the activity log is accessible via the admin API.

### Data Portability

All content is stored as standard markdown. Git sync means your content already exists in a git repository in plain-text files. If you stop using Valoryx tomorrow, your documentation is still there — in your repo, in standard format, with full history.

No proprietary export step. No "download as ZIP" workaround. Your content is always accessible in the format you wrote it.

## Comparison: Self-Hosted vs. Cloud for Compliance

| Requirement | Cloud SaaS | Self-Hosted (Valoryx) |
|------------|------------|----------------------|
| Data residency | Provider's data centers (verify regions) | Your infrastructure, your region |
| Authentication | Provider-managed (usually OAuth/SAML) | You control: WebAuthn, Argon2id passwords, RBAC |
| Encryption at rest | Provider-managed (verify algorithm) | AES-256-GCM, keys on your server |
| Audit logs | Provider's log format, their retention | Your logs, your retention, your SIEM |
| Subprocessors | Provider's vendor chain (read the DPA) | None — single binary, no external calls |
| Data export | Provider's export format (may be proprietary) | Standard markdown in a git repo |
| Incident response | Provider notifies you (check SLA timing) | You detect, you respond, you control the timeline |

The "subprocessors" row deserves emphasis. Many SaaS documentation tools use third-party services for search (Algolia), analytics (Segment), error tracking (Sentry), and hosting (AWS, GCP). Each subprocessor is a link in the compliance chain that needs its own assessment. Valoryx is a single Go binary with zero external dependencies and zero outbound network calls. There is no vendor chain to audit.

## Practical Steps

If you're evaluating documentation tools for a regulated environment:

1. **Map your data.** What's actually in your docs? Architecture details, credentials, customer data? This determines which compliance frameworks apply.

2. **Check your framework's requirements.** GDPR, SOC 2, HIPAA, ITAR, and FedRAMP each have different requirements for data residency, encryption, and access control. Know which ones apply to your organization.

3. **Try self-hosted first.** [Install Valoryx](/install/) on your infrastructure, connect it to your identity provider, and verify the security controls yourself. The Community Edition is free with no feature restrictions — the same authentication, encryption, and audit logging available in every installation.

4. **Document your controls.** When the auditor arrives, you'll need to show: where data lives, how it's encrypted, who has access, and what the audit trail shows. Self-hosted tools make each of these answerable with evidence from your own systems.

Read our [privacy policy](/privacy/) and [terms of service](/terms/) for details on how Valoryx handles data in our cloud offering. For self-hosted installations, your data never touches our infrastructure.

Compliance shouldn't dictate your tooling choices — but it often does. Self-hosted documentation gives regulated teams one less thing to explain to the auditor and one more system fully under their own control.
