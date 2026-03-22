---
title: Ihr Konto
description: Profil, Passwort, Abrechnung und Daten verwalten.
weight: 6
---

# Ihr Konto

## Registrierung

Besuchen Sie [app.valoryx.dev](https://app.valoryx.dev/#/register) und erstellen Sie ein Konto mit Ihrer E-Mail-Adresse und einem Passwort. Sie müssen die [Nutzungsbedingungen](/terms/) und die [Datenschutzerklärung](/privacy/) akzeptieren.

Sie können sich auch mit **Google** oder **GitHub** anmelden, sofern diese Optionen verfügbar sind.

## Profileinstellungen

Klicken Sie auf Ihren Avatar in der oberen linken Ecke und dann auf **Profile**, um:

- Ihren Anzeigenamen zu ändern
- Ihre E-Mail-Adresse zu aktualisieren
- Ihr Passwort zu ändern
- Einen Passkey (WebAuthn) für passwortlose Anmeldung einzurichten

## Abrechnung

Gehen Sie zu **Workspace Settings** → **Billing**, um:

- Ihren aktuellen Tarif und die Nutzung einzusehen
- Auf Team ($29/Monat) oder Business ($79/Monat) zu upgraden
- Ihr Abonnement über das Stripe-Portal zu verwalten
- Rechnungen und Zahlungsverlauf einzusehen

## Ihre Daten

### Was wir speichern

- Ihre E-Mail-Adresse, Ihren Namen und Ihr Passwort (gehasht mit Argon2id)
- Ihre Dokumentationsinhalte (in Workspaces)
- Aktivitätsprotokolle (wer was wann bearbeitet hat)

### Was wir nicht speichern

- Kreditkartennummern (werden vollständig über Stripe abgewickelt)
- Ihre Git-Zugangsdaten (OAuth-Tokens, nicht dauerhaft gespeichert)
- Tracking-Cookies (Analysen sind Opt-in, GDPR-konform)

### Datenexport

Ihre Inhalte sind jederzeit portabel:

- **Mit GitHub Sync** — Ihre Dokumentation befindet sich bereits als Markdown-Dateien in Ihrem GitHub-Repository
- **Ohne GitHub Sync** — verwenden Sie die **Export**-Schaltfläche in den Workspace-Einstellungen, um eine ZIP-Datei mit all Ihren Markdown-Dateien herunterzuladen
- **Kontodaten** — fordern Sie einen vollständigen Datenexport an, indem Sie uns kontaktieren

### Konto löschen

Kontaktieren Sie uns unter valoryxeu@gmail.com, um die Löschung Ihres Kontos anzufordern. Wir entfernen alle Ihre Daten innerhalb von 30 Tagen, wie von der GDPR vorgeschrieben.

## Sicherheit

- Passwörter werden mit Argon2id gehasht (von OWASP empfohlen)
- Sitzungen verwenden HttpOnly-Cookies (für JavaScript nicht zugänglich)
- Der gesamte Datenverkehr ist mit TLS verschlüsselt
- Optionaler Passkey/WebAuthn für passwortlose Anmeldung
- Vollständiger Audit-Trail aller Kontoaktionen
