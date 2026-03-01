---
title: Konfiguration
description: Konfigurieren Sie DocPlatform mit Umgebungsvariablen, Workspace-Einstellungen, Authentifizierungsanbietern und rollenbasierten Berechtigungen.
weight: 3
---

# Konfiguration

DocPlatform folgt dem Prinzip Konvention-vor-Konfiguration. Es läuft mit sinnvollen Standardwerten direkt nach der Installation, aber jeder Aspekt ist für Produktions-Deployments konfigurierbar.

## Konfigurationsebenen

Die Konfiguration wird in drei Ebenen angewendet, von der breitesten zur spezifischsten:

| Ebene | Geltungsbereich | Methode |
|---|---|---|
| **Umgebungsvariablen** | Plattformweit | `.env`-Datei oder Shell-Umgebung |
| **Workspace-Konfiguration** | Pro Workspace | `.docplatform/config.yaml` |
| **Seiten-Frontmatter** | Pro Seite | YAML-Block in jeder `.md`-Datei |

Spezifischere Ebenen überschreiben allgemeinere. Zum Beispiel überschreibt `access: restricted` einer Seite den Workspace-Standard von `access: public`.

## Leitfäden

| Leitfaden | Was er abdeckt |
|---|---|
| [Umgebungsvariablen](environment.md) | Alle plattformweiten Einstellungen: Port, Datenverzeichnis, Git, SMTP, Telemetrie |
| [Workspace-Einstellungen](workspace-config.md) | Workspace-spezifische Konfiguration: Git-Remote, Theme, Navigation, Veröffentlichungsstandards |
| [Authentifizierung](authentication.md) | Lokale Authentifizierung, OIDC-Anbieter (Google, GitHub), JWT-Einstellungen, Passwortrichtlinien |
| [Rollen & Berechtigungen](permissions.md) | 6-stufige RBAC-Hierarchie, Zugriffskontrolle auf Seitenebene, Casbin-Konfiguration |

## Kurzreferenz

Die häufigsten Konfigurationsaufgaben:

| Aufgabe | Wo |
|---|---|
| Server-Port ändern | Umgebungsvariable `PORT` |
| Git-Repository verbinden | Workspace-Konfiguration `git_remote` |
| Google/GitHub-Anmeldung aktivieren | Umgebungsvariablen `OIDC_*` |
| E-Mail einrichten (Einladungen, Passwort-Zurücksetzung) | Umgebungsvariablen `SMTP_*` |
| Standardrolle für neue Benutzer ändern | Workspace-Konfiguration `permissions.default_role` |
| Veröffentlichte Dokumentation auf Teammitglieder beschränken | Umgebungsvariable `PUBLISH_REQUIRE_AUTH=true` |
| Eine Seite auf bestimmte Rollen beschränken (Web-Editor) | Seiten-Frontmatter `access: restricted` |
| Telemetrie deaktivieren | `DOCPLATFORM_TELEMETRY=off` |
