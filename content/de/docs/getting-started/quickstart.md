---
title: Schnellstart
description: Bringen Sie DocPlatform in unter 5 Minuten mit einem voll funktionsfähigen Dokumentations-Workspace zum Laufen.
weight: 1
---

# Schnellstart

In unter 5 Minuten von Null zu einer laufenden Dokumentationsplattform. Dieser Leitfaden beschreibt den schnellsten Weg — für detaillierte Optionen siehe den [Installations](installation.md)-Leitfaden.

## Schritt 1: Installieren

```bash
# Empfohlen (erkennt die Plattform automatisch)
curl -fsSL https://valoryx.org/install.sh | sh
```

Oder manuell herunterladen:

```bash
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform
```

Oder mit Docker:

```bash
docker run -d --name docplatform -p 3000:3000 -v docplatform-data:/data ghcr.io/valoryx-org/docplatform:latest
```

Bei Verwendung von Docker springen Sie zu [Schritt 3](#schritt-3-konto-registrieren) — der Container initialisiert sich automatisch.

## Schritt 2: Workspace initialisieren

```bash
docplatform init --workspace-name "My Docs" --slug my-docs
```

Dies erstellt:

```
.docplatform/
├── data.db              # SQLite-Datenbank
├── jwt-key.pem          # Automatisch generierter RS256-Signaturschlüssel
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Hier liegt Ihre Dokumentation
        └── .docplatform/
            └── config.yaml
```

### Mit Git (optional)

Verbinden Sie sich während der Initialisierung mit einem bestehenden Git-Repository:

```bash
docplatform init \
  --workspace-name "My Docs" \
  --slug my-docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

DocPlatform klont das Repository und beginnt mit der Synchronisation. Vorhandene `.md`-Dateien werden automatisch indiziert.

## Schritt 3: Server starten

```bash
docplatform serve
```

```
INFO  Server starting            port=3000 version=v0.5.0
INFO  Database initialized       path=.docplatform/data.db
INFO  Search index ready         documents=0
INFO  Workspace loaded           name="My Docs" slug=my-docs
INFO  Listening on               http://localhost:3000
```

Öffnen Sie [http://localhost:3000](http://localhost:3000) in Ihrem Browser.

## Schritt 4: Konto registrieren

Der erste Benutzer, der sich registriert, wird automatisch zum **SuperAdmin** mit vollem Plattformzugriff.

1. Klicken Sie auf **Create Account**
2. Geben Sie Ihren Namen, Ihre E-Mail-Adresse und ein Passwort ein
3. Sie sind angemeldet und können mit dem Schreiben beginnen

> **Sicherheitshinweis:** Der Ablauf „Erster Benutzer wird Admin" gilt nur, wenn keine Benutzer vorhanden sind. Nach der ersten Registrierung erhalten neue Konten die für den Workspace konfigurierte Standardrolle.

## Schritt 5: Erste Seite erstellen

1. Klicken Sie auf **New Page** in der Seitenleiste
2. Vergeben Sie einen Titel — der URL-Slug wird automatisch aus dem Titel generiert
3. Beginnen Sie mit dem Schreiben im Rich-Editor
4. Änderungen werden alle paar Sekunden automatisch gespeichert

Die Seite wird als Markdown-Datei im `docs/`-Verzeichnis Ihres Workspace gespeichert. Wenn Sie Git verbunden haben, wird automatisch committet und gepusht.

## Schritt 6: Ausprobieren

Hier sind einige Dinge, die Sie sofort ausprobieren können:

| Aktion | Wie |
|---|---|
| **Zum rohen Markdown wechseln** | Klicken Sie auf den `</>` Umschalter in der Editor-Symbolleiste |
| **Suchen** | Drücken Sie `Cmd+K` (oder `Ctrl+K`), um die Sofortsuche zu öffnen |
| **Unterseite erstellen** | Klicken Sie auf das `+` neben einer bestehenden Seite in der Seitenleiste |
| **Veröffentlichte Seite anzeigen** | Navigieren Sie zu `http://localhost:3000/p/my-docs/` |
| **Diagnose ausführen** | Führen Sie `docplatform doctor` in Ihrem Terminal aus |

## Nächste Schritte

| Ziel | Leitfaden |
|---|---|
| Git-Repository verbinden | [Git-Integration](../guides/git-integration.md) |
| Ihr Team einladen | [Teams & Zusammenarbeit](../guides/collaboration.md) |
| Dokumentation öffentlich veröffentlichen | [Veröffentlichung](../guides/publishing.md) |
| In Produktion deployen | [Deployment](../deployment/binary.md) |
| Authentifizierungsanbieter konfigurieren | [Authentifizierung](../configuration/authentication.md) |
