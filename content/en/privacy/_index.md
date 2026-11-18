---
title: "Privacy Policy"
description: "DocPlatform Privacy Policy — Version 1.3, effective November 12, 2026"
layout: "list"
---

**Effective Date:** November 12, 2026
**Version:** 1.3

This Privacy Policy explains how Valoryx ("Company", "we", "us") collects, uses, stores, and protects personal data when you use the DocPlatform software and services ("Software"). This policy applies to both the Cloud Service (app.valoryx.dev) and the Community Edition (self-hosted).

We are committed to protecting your privacy and complying with the EU General Data Protection Regulation (GDPR), applicable French data protection laws (Loi Informatique et Libertés), the California Consumer Privacy Act (CCPA/CPRA), and other applicable data protection legislation.

---

## 1. Data Controller

**Valoryx**
Email: privacy@valoryx.org
Website: https://valoryx.org

Valoryx is the data controller for personal data processed through the Cloud Service and through the valoryx.org website.

For the Community Edition (self-hosted), **you** are the data controller for all data stored on your infrastructure. Valoryx does not access or process data on your self-hosted instance unless you explicitly opt in to telemetry (see Section 5).

## 2. Data We Collect

### 2a. Account Data (Cloud Service and Community Edition)

| Data | Purpose | Legal Basis (GDPR) |
|------|---------|-------------------|
| Email address | Account identification, login, password reset, service notifications | Contract performance (Art. 6(1)(b)) |
| Full name | Display in workspace, comments, activity feed | Contract performance (Art. 6(1)(b)) |
| Password hash | Authentication (Argon2id, OWASP-recommended parameters) | Contract performance (Art. 6(1)(b)) |
| Avatar URL | Profile display (if provided via OIDC provider) | Legitimate interest (Art. 6(1)(f)) |

### 2b. Authentication Data

| Data | Purpose | Legal Basis |
|------|---------|------------|
| Session tokens | Maintaining login state (SHA-256 hashed in database) | Contract performance |
| WebAuthn credentials | Passkey authentication (public key and sign count only) | Contract performance |
| OIDC provider ID | Social login (Google, GitHub) | Contract performance |
| API key hashes | Programmatic access (HMAC-peppered, hashed before storage) | Contract performance |

### 2c. Security and Audit Data

| Data | Purpose | Retention | Legal Basis |
|------|---------|-----------|------------|
| IP address | Audit log, rate limiting, abuse prevention | Indefinite (anonymizable on request) | Legitimate interest |
| User agent | Audit log, session management | Indefinite (anonymizable on request) | Legitimate interest |
| Audit log entries | Security compliance, incident investigation | Indefinite (anonymizable on request) | Legitimate interest |
| Server request logs (IP address, request path, status, time, for each request to the service except health checks) | Operating the service, security, abuse prevention | No fixed period: the service writes them to the system log and does not delete them itself; they go when that log is rotated out (on the Cloud Service this has so far meant several months) | Legitimate interest |
| Terms acceptance records | Legal compliance, proof of consent | Indefinite | Legal obligation (Art. 6(1)(c)) |

### 2d. Usage Analytics (Optional, Consent-Based)

| Data | Purpose | Retention | Legal Basis |
|------|---------|-----------|------------|
| Page views (path, referrer) | Published docs analytics | 90 days | Consent (Art. 6(1)(a)) |
| Search queries | Search analytics | 90 days | Consent (Art. 6(1)(a)) |
| Analytics consent records (choice, policy version, time, workspace, user agent, one-way IP hash; normally not linked to an account, see "Consent records" below) | Proof of the choice, recorded when the banner is accepted and when it is declined (Art. 7(1)) | Kept as proof of consent. Anonymized on request. Account deletion changes only a record that carries the account ID, which a record normally does not (see "Consent records" below) | Legal obligation (Art. 6(1)(c)) |

Analytics data is only collected for published documentation sites when the visitor has explicitly consented via the cookie consent banner. **No IP addresses are stored** in page-view or search records, and those records hold no user agent, so they cannot be used to identify individual visitors. The consent records described next are the one exception: they hold a user agent and a one-way hash of the IP address, and they are listed separately above.

**Consent records.** When a visitor accepts or declines the analytics banner, we keep a record of that choice so that we can demonstrate consent (GDPR Art. 7(1)). A record is written for a decline as well as for an acceptance. A consent record contains: the choice, the privacy-policy version shown, the time, the workspace, the browser's user-agent string, and a one-way SHA-256 hash of the visitor's IP address. It is normally not linked to an account: the request that records the choice does not identify the visitor, so the record holds no account ID even when the visitor is signed in. There is one exception, on the Cloud Service only: a choice made during a support session in which a Valoryx platform administrator is acting on a user's account with write access is recorded with that user's account ID. The IP address itself is not written to the consent record; like every request to the service, this one appears in the server request log with its IP address (section 2c). On the Cloud Service the hash has been made with a secret salt since 6 November 2026, 12:49 UTC; records written before that time were hashed without one. On a self-hosted Community Edition installation the hash is salted only if the operator has set a salt (`DOCPLATFORM_IP_SALT`). We treat this hash as personal data, not as an anonymous value: a hash of an IP address made without a salt can be reversed by trying every possible address, and a salted one can be reversed by whoever holds the salt. Consent records are separate from the analytics records described above and are not used for analytics. They are kept as proof of consent. A consent record without an account ID cannot be found from a name, an email address or an account, and deleting an account does not remove or change it. A record that does carry an account ID (the exception above) is anonymized when that account is deleted. If you want your record anonymized (the workspace, IP hash and user agent removed; the choice, policy version and time remain), write to privacy@valoryx.org with the IP address you used and the approximate time of the visit; without that information we cannot tell which record is yours (GDPR Art. 11). This applies whether or not you were signed in when you made the choice. Questions about consent records: privacy@valoryx.org.

### 2e. Telemetry (Optional, Opt-In Only)

The Community Edition includes optional, anonymous usage telemetry that is **disabled by default**. It can be enabled by setting the environment variable `DOCPLATFORM_TELEMETRY=on`.

Telemetry data does not include personal information, Content, IP addresses, or any data that could identify you or your users. It includes only aggregate feature usage counts (e.g., "pages created: 47", "git syncs: 12"). Telemetry data is transmitted via HTTPS and cannot be linked to any individual or organization.

### 2f. Billing Data (Cloud Service Only)

Payment processing is handled entirely by Stripe, Inc. Valoryx **does not** store credit card numbers, bank account details, or other payment instruments on its servers. We store only:

| Data | Purpose | Legal Basis |
|------|---------|------------|
| Stripe customer ID | Link your organization to Stripe billing | Contract performance |
| Stripe subscription ID | Manage your subscription | Contract performance |
| Plan name and billing interval | Feature gating, billing | Contract performance |

For Stripe's privacy practices, see [Stripe Privacy Policy](https://stripe.com/privacy).

### 2g. Update Checks

The Software periodically checks whether a newer DocPlatform release is available, so that operators learn about updates and security patches. This check:

- is made **directly from your instance to GitHub** (`api.github.com`) — the same unaffiliated third party that distributes DocPlatform binaries. **No data is sent to Valoryx, and Valoryx receives nothing** from this check.
- carries **no identifier and no version number**. The request contains only a generic `docplatform` User-Agent and the connection metadata (such as your instance's IP address) that any HTTPS request necessarily reveals to the host being contacted. For GitHub's handling of such requests, see the [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).
- can be **disabled entirely** by setting the environment variable `DISABLE_UPDATE_CHECK=true`. Disabling it has no other effect on the Software.

**Scope of this section and of our self-hosting statements.** The statements above and in Section 3 describe the live application UI served by your instance and the instance-initiated traffic disclosed in this policy. They do not yet extend to three residual areas: separately published documentation sites and exported HTML files currently reference Google Fonts servers, and social-media preview images on published pages currently reference valoryx.org. These residual references are tracked and are being reduced in future releases.

## 3. Data We Do NOT Collect

- We do **not** track users across websites.
- We do **not** sell, rent, or share personal data with advertisers.
- We do **not** use personal data for profiling or automated decision-making.
- We do **not** store payment card numbers (handled entirely by Stripe).
- We do **not** collect data from the Community Edition unless you opt in to telemetry.
- We do **not** include any identifier, account data, or even the installed version number in update checks — the check is a plain "what is the latest release" request made directly from your instance to GitHub (see Section 2g).
- We do **not** use your Content to train AI or machine learning models.
- We do **not** share your data with data brokers.

## 4. Cookies

The Software uses the following cookies:

| Cookie | Purpose | Duration | Type |
|--------|---------|----------|------|
| `dp_refresh` | JWT refresh token (authentication) | 7 days | Essential |
| `dp_pub` | Published docs access token | Session | Essential |
| `dp_ws_token` | WebSocket authentication | Session | Essential |
| `dp_analytics_consent` | Records analytics consent choice | 1 year | Consent |

All authentication cookies are:
- **HttpOnly** (not accessible to JavaScript)
- **SameSite=Strict** (CSRF protection)
- **Secure** (HTTPS only in production)
- **Path-scoped** (minimal exposure)

**No third-party cookies or tracking pixels are used.** We do not use Google Analytics, Facebook Pixel, or any third-party tracking service.

## 5. How We Use Your Data

We use personal data exclusively for:

1. **Providing the service** — account creation, authentication, workspace management, content storage, collaboration features, git synchronization.
2. **Security** — audit logging, rate limiting, abuse detection, session management, incident investigation.
3. **Service communications** — password reset emails, invitation emails, subscription notifications. **We do not send marketing emails.**
4. **Billing** — processing payments, managing subscriptions, enforcing plan limits (Cloud Service only).
5. **Legal compliance** — recording Terms of Service acceptance, responding to lawful requests from competent authorities.
6. **Service improvement** — anonymous, aggregate usage statistics (only if telemetry is opted in via Community Edition).

## 6. Data Sharing

We share personal data only with the following service providers, each acting as a data processor:

| Recipient | Data Shared | Purpose | Location |
|-----------|------------|---------|----------|
| Stripe, Inc. | Email, org name, subscription details | Payment processing | EU/US (SCCs in place) |
| Email provider (Resend or your configured SMTP) | Email address, message content | Transactional emails only | Depends on provider |
| OIDC providers (Google, GitHub) | OAuth tokens (during login flow only) | Social authentication | US (SCCs/adequacy) |
| Hetzner Online GmbH | Infrastructure hosting (Cloud Service) | Server hosting | Germany (EU) |

We do **not** share data with any other third parties. We do **not** sell data. We do **not** share data with advertisers.

The update check described in Section 2g is a direct instance-to-GitHub request initiated by your own installation; it is not a disclosure of data by Valoryx, and GitHub is not a data processor for Valoryx.

In the event of a merger, acquisition, or sale of assets, personal data may be transferred to the successor entity, subject to the same privacy commitments described in this policy. We will notify affected users before any such transfer.

## 7. Data Retention

| Data Category | Retention Period | Deletion Method |
|--------------|-----------------|----------------|
| Account data | Until account deletion | Hard delete on request |
| Sessions | 7 days | Auto-purged |
| Password reset tokens | 1 hour | Auto-purged |
| Invitations | 7 days after expiry | Auto-purged |
| Soft-deleted pages | 30 days | Auto-purged |
| Analytics events | 90 days | Auto-purged |
| Analytics consent records | Kept as proof of consent | Anonymized on request (workspace, IP hash and user agent removed; choice, policy version and time remain). Account deletion anonymizes only a record that carries the account ID, which a record normally does not (section 2d) |
| Server request logs | No fixed period | Not deleted entry by entry; entries go when the log is rotated out by size (section 2c) |
| Audit log | Indefinite (anonymizable on request) | Anonymization available |
| Terms acceptance | Indefinite | Legal requirement |
| Billing data | As required by French tax law (10 years for invoices) | Legal retention period |

Automated data cleanup runs every 6 hours to enforce retention periods.

## 8. Your Rights

### 8a. Rights Under GDPR (EU/EEA Residents)

Under the General Data Protection Regulation, you have the following rights:

**Right of Access (Article 15)** — You can request a copy of all personal data we hold about you. Use the built-in data export feature or contact us.

**Right to Rectification (Article 16)** — You can update your name and profile information at any time through the Software. For email changes, contact us.

**Right to Erasure (Article 17)** — You can delete your account at any time. Account deletion:
- Removes your user record and personal profile data.
- Anonymizes your entries in the audit log (replaces user ID, IP, and user agent with "anonymized").
- Does not reach an analytics consent record unless it carries your account ID, which a record normally does not. See "Consent records" in section 2d, which also says how to have yours anonymized.
- Does not remove entries about your past requests from the server request log (section 2c); they go when that log is rotated out.
- Removes your sessions, API keys, and credentials.
- Does not delete Content in Workspaces where other members remain (the Workspace is reassigned to another administrator).
- Platform owners can initiate deletion via the admin panel.

**Right to Data Portability (Article 20)** — Your Content is stored as standard Markdown files. You can export it at any time via:
- Git synchronization (bidirectional)
- ZIP export (built-in)
- API export endpoints
- Platform owner data export (GDPR compliance)

**Right to Restriction of Processing (Article 18)** — You can request that we restrict processing of your data while a complaint is being resolved.

**Right to Object (Article 21)** — You can object to processing based on legitimate interest. For analytics, you can withdraw consent at any time by clearing the `dp_analytics_consent` cookie or contacting us.

**Right to Lodge a Complaint** — You have the right to lodge a complaint with your national data protection authority. For France:

CNIL (Commission Nationale de l'Informatique et des Libertés)
3 Place de Fontenoy, TSA 80715
75334 Paris Cedex 07
https://www.cnil.fr

### 8b. Rights Under CCPA/CPRA (California Residents)

If you are a California resident, you have additional rights under the California Consumer Privacy Act (as amended by the CPRA):

**Right to Know** — You may request disclosure of the categories and specific pieces of personal information we have collected, the sources of collection, the business purposes, and the categories of third parties with whom we share it.

**Right to Delete** — You may request deletion of your personal information, subject to certain exceptions (legal obligations, security, completing transactions).

**Right to Opt-Out of Sale/Sharing** — We do **not** sell your personal information. We do **not** share your personal information for cross-context behavioral advertising. No opt-out is necessary because we do not engage in these practices.

**Right to Non-Discrimination** — We will not discriminate against you for exercising your CCPA rights.

**Categories of Personal Information Collected (CCPA disclosure):**
- Identifiers (email address, name, IP address)
- Internet activity (page views via opt-in analytics, audit logs)
- Commercial information (subscription plan, billing history via Stripe)

**We do not collect:** Social Security numbers, driver's license numbers, financial account numbers, geolocation data, biometric data, or any sensitive personal information as defined by the CCPA.

### 8c. How to Exercise Your Rights

Contact us at **privacy@valoryx.org**. We will respond within:
- 30 days for GDPR requests
- 45 days for CCPA requests (extendable by 45 days with notice)

We may request identity verification before processing your request to prevent unauthorized disclosure.

## 9. Data Security

We implement the following security measures:

- **Encryption in transit:** All connections use TLS 1.2+ (HTTPS). HTTP is redirected to HTTPS in production.
- **Password hashing:** Argon2id with OWASP-recommended parameters (64 MB memory, 3 iterations, 2 threads).
- **Token security:** All tokens (sessions, password resets, invitations, API keys) are SHA-256 hashed before storage. API keys are additionally HMAC-peppered.
- **WebAuthn/passkeys:** Public key cryptography for passwordless authentication. Private keys never leave your device.
- **Content Security Policy:** Per-route CSP headers with cryptographic nonces prevent XSS attacks.
- **Rate limiting:** Per-organization, per-category token bucket rate limiting prevents abuse.
- **Git token encryption:** Repository connection tokens encrypted with AES-256-GCM at rest.
- **Input sanitization:** HTML content sanitized with bluemonday to prevent stored XSS. Email headers sanitized to prevent injection.
- **Database separation:** Analytics data is stored in a separate SQLite database from application data, ensuring analytics collection does not affect core data integrity.
- **Infrastructure:** Cloud Service is hosted on Hetzner Online GmbH servers in Germany (EU). Data does not leave the EU unless explicitly configured by the user (e.g., connecting to a non-EU git provider).

## 10. International Data Transfers

For the Cloud Service, data is processed within the European Union (Hetzner, Germany). Where data transfers outside the EU are necessary (e.g., Stripe payment processing), we ensure appropriate safeguards are in place:

- **Stripe:** Standard Contractual Clauses (SCCs) and Stripe's certification under the EU-US Data Privacy Framework.
- **OIDC Providers:** Data transmitted during authentication only; governed by the provider's privacy policy and applicable adequacy decisions or SCCs.

For the Community Edition, data remains on your own infrastructure in the jurisdiction of your choosing. You are responsible for ensuring compliance with applicable data protection laws in your jurisdiction.

## 11. Children's Privacy

The Software is not intended for use by individuals under the age of 16 (or the applicable age of digital consent in your jurisdiction). We do not knowingly collect personal data from children. If you believe a child has provided us with personal data, contact us immediately at privacy@valoryx.org to request deletion.

## 12. Do Not Track

The Software respects the Do Not Track (DNT) browser signal. When DNT is enabled, no analytics data is collected regardless of cookie consent status.

## 13. Changes to This Policy

We may update this Privacy Policy to reflect changes in our practices or legal requirements. Material changes will be communicated via:

- In-app notification (requiring re-acceptance of Terms for material changes)
- Updated "Effective Date" at the top of this document
- Email notification to registered users for significant changes (Cloud Service)

Previous versions of this policy are available upon request.

## 14. Contact

For any privacy-related questions, data subject requests, or to exercise your rights:

**Valoryx**
Email: privacy@valoryx.org
Security incidents: security@valoryx.org
Website: https://valoryx.org
