---
title: "MCP für Dokumentation: Ein technischer Leitfaden"
description: "Wie Model Context Protocol KI-Assistenten mit Ihrer Dokumentation verbindet. Claude Desktop konfigurieren, 13 eingebaute Tools nutzen und Dokumentationspflege automatisieren."
date: "2026-03-16"
author: "Valoryx Team"
tags: ["mcp", "ai", "documentation", "tutorial"]
---

Model Context Protocol (MCP) ist ein offener Standard, der KI-Assistenten die Interaktion mit externen Tools und Datenquellen über eine strukturierte Schnittstelle ermöglicht. Anstatt Text in ein Chat-Fenster zu kopieren und darauf zu hoffen, dass das Modell den Kontext versteht, gibt MCP dem Assistenten direkten, typisierten Zugriff auf Ihre Systeme — Dateien lesen, Suchen ausführen, Inhalte erstellen, alles über wohldefinierte Tool-Aufrufe.

Für Dokumentationsteams verändert dies den Workflow grundlegend. Ihr KI-Assistent ist nicht mehr ein Textgenerator, der mit veraltetem Kontext arbeitet, sondern wird zu einem Teilnehmer, der Ihre tatsächliche Dokumentation liest, Ihre Wissensbasis durchsucht und Bearbeitungen vorschlägt, die Sie prüfen können, bevor sie live gehen.

Valoryx liefert einen eingebauten MCP-Server mit 26 Tools. Keine Plugins zu installieren, keine API-Schlüssel zu konfigurieren. Wenn Sie eine laufende Instanz haben, ist der MCP-Server bereits da.

## Was MCP tatsächlich macht

MCP definiert ein Protokoll für Tool-Erkennung und -Aufruf. Ein KI-Client (wie Claude Desktop) verbindet sich mit einem MCP-Server, fragt, welche Tools verfügbar sind, und ruft sie mit strukturierten Parametern auf. Der Server führt die Operation aus und gibt strukturierte Ergebnisse zurück.

Das unterscheidet sich von „KI-Features", die nachträglich an ein Produkt angebaut werden. Es gibt keine proprietäre Integration. Jeder MCP-kompatible Client funktioniert. Die [MCP-Spezifikation](https://modelcontextprotocol.io) ist offen, und mehrere KI-Assistenten unterstützen sie bereits.

Das praktische Ergebnis: Sie können Claude fragen „Finde alle Seiten, die Authentifizierung erwähnen" und es wird tatsächlich Ihre Dokumentationsinstanz durchsuchen, nicht Seitentitel aus Trainingsdaten halluzinieren.

## Die 13 eingebauten Tools

Die MCP-Tools von Valoryx fallen in vier Kategorien:

### Lese-Tools
Diese rufen Inhalte ab, ohne etwas zu verändern.

- **get_page** — Eine einzelne Seite nach ID oder Pfad abrufen. Gibt Titel, Markdown-Inhalt, Metadaten und den Zeitstempel der letzten Änderung zurück.
- **get_workspace** — Alle Workspaces mit Seitenzahlen und Einstellungen auflisten.
- **get_page_tree** — Den vollständigen Navigationsbaum für einen Workspace zurückgeben. Nützlich, um die Dokumentationsstruktur zu verstehen, bevor Änderungen vorgenommen werden.

### Such-Tools
Volltextsuche basierend auf derselben Bleve-Engine, die die Web-Oberfläche antreibt.

- **search_pages** — Über alle Seiten in einem Workspace suchen. Unterstützt Phrasenabfragen, feldspezifische Suchen und boolesche Operatoren.
- **search_by_tag** — Seiten mit bestimmten Tags finden. Nützlich für Audits: „Zeige mir alles mit dem Tag `deprecated`."
- **search_recent** — Seiten finden, die in den letzten N Tagen geändert wurden. Gut für die Überprüfung aktueller Änderungen.

### Schreib-Tools
Diese erstellen oder ändern Inhalte. Jede Schreiboperation erstellt einen Ledger-Eintrag, sodass Änderungen nachverfolgt und sync-sicher sind.

- **create_page** — Eine neue Seite mit Titel, Inhalt, übergeordnetem Pfad und Tags erstellen.
- **update_page** — Den Inhalt einer bestehenden Seite ersetzen. Die vorherige Version wird in der Historie aufbewahrt.
- **move_page** — Die Position einer Seite im Navigationsbaum ändern.
- **delete_page** — Eine Seite vorläufig löschen (wiederherstellbar über das Admin-Panel).

### Admin-Tools
Workspace- und Benutzerverwaltungsoperationen.

- **list_users** — Alle Benutzer mit ihren Rollen abrufen. Nützlich für Zugriffsprüfungen.
- **get_activity_log** — Aktuelle Aktivitäten abrufen (Bearbeitungen, Anmeldungen, Berechtigungsänderungen).
- **get_sync_status** — Den Git-Sync-Status für einen Workspace prüfen — letzte Synchronisierungszeit, ausstehende Änderungen, eventuelle Konflikte.

## Claude Desktop konfigurieren

Um Claude Desktop mit Ihrer Valoryx-Instanz zu verbinden, fügen Sie einen MCP-Server-Eintrag in Ihre Konfigurationsdatei ein. Unter macOS befindet sich diese unter `~/Library/Application Support/Claude/claude_desktop_config.json`. Unter Windows unter `%APPDATA%\Claude\claude_desktop_config.json`.

```json
{
  "mcpServers": {
    "valoryx-docs": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-client",
        "--server-url",
        "https://docs.yourcompany.com/api/mcp"
      ],
      "env": {
        "MCP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Generieren Sie einen API-Schlüssel im Valoryx Admin-Panel unter **Einstellungen > API-Schlüssel**. Der Schlüssel erbt die Berechtigungen des Benutzers, der ihn erstellt hat. Verwenden Sie also ein dediziertes Dienstkonto mit entsprechender RBAC-Rolle, wenn Sie einschränken möchten, was die KI tun kann.

Für die Community Edition, die lokal läuft, lautet die URL typischerweise `http://localhost:3000/api/mcp`.

## Praktische Beispiele

Sobald die Verbindung steht, können Sie konkret Folgendes tun:

### Veraltete Inhalte finden

```
"Finde alle Seiten im Engineering-Workspace, die in den letzten 
90 Tagen nicht aktualisiert wurden"
```

Der Assistent ruft `search_recent` mit einem 90-Tage-Fenster auf, invertiert das Ergebnis gegen `get_page_tree` und gibt eine Liste potenziell veralteter Seiten zurück. Sie erhalten Seitenpfade, Daten der letzten Änderung und letzte Bearbeiter — genug, um Review-Aufgaben zuzuweisen.

### Konsistenz prüfen

```
"Durchsuche alle Seiten nach Verweisen auf unseren alten API-Endpoint 
api.example.com/v1 und liste sie auf"
```

Dies ruft `search_pages` mit der alten Endpoint-Zeichenkette auf. Sie erhalten eine Liste jeder Seite, die noch die veraltete URL referenziert, mit umgebendem Kontext. Kein manuelles Grep durch ein Docs-Repository nötig.

### Inhalte entwerfen und aktualisieren

```
"Lies den aktuellen Authentifizierungsleitfaden, dann aktualisiere ihn 
um den neuen Passkey-Login-Flow. Behalte die bestehende Struktur bei."
```

Der Assistent ruft `get_page` auf, um den aktuellen Inhalt zu lesen, entwirft die Aktualisierung und ruft `update_page` auf, um sie anzuwenden. Die vorherige Version bleibt in der Historie. Wenn [Git-Sync](/docs/guides/git-integration/) konfiguriert ist, erscheint die Bearbeitung als Commit in Ihrem Repository.

### Aktuelle Änderungen überprüfen

```
"Zeige mir alles, was sich in der letzten Woche über alle 
Workspaces geändert hat"
```

Ruft `search_recent` mit einem 7-Tage-Fenster auf. Gibt eine Zusammenfassung zurück, was sich geändert hat, wer es geändert hat und wann. Nützlich für wöchentliche Dokumentationsreviews, ohne sich in die Web-Oberfläche einzuloggen.

## Was das für die Dokumentationspflege bedeutet

Der traditionelle Workflow für die Dokumentationspflege ist: Jemand bemerkt, dass die Dokumentation falsch ist, erstellt ein Ticket, jemand anderes aktualisiert irgendwann die Seite. Die Lücke zwischen „bemerkt" und „behoben" beträgt normalerweise Wochen.

Mit MCP wird der Workflow zu: Bitten Sie die KI, einen Bereich zu prüfen, überprüfen Sie die Ergebnisse, genehmigen Sie die Änderungen. Die Lücke schrumpft auf Minuten. Nicht weil KI bessere Dokumentation schreibt — das tut sie nicht, nicht zuverlässig — sondern weil der Engpass immer das Finden des Fehlers und das Durchführen der Bearbeitung war, nicht das Verfassen des Textes.

Das funktioniert besonders gut für mechanische Aktualisierungen: URL-Änderungen, Terminologieumbenennungen, Versionsnummern-Aktualisierungen, Veralterungshinweise. Die Art von Änderungen, die für Menschen mühsam und für eine KI mit strukturiertem Zugriff auf den Inhalt unkompliziert sind.

Mehr zur Nutzung von MCP für die Aktualität der Dokumentation finden Sie unter [Wie man Dokumentation aktuell hält](/blog/keep-docs-up-to-date/).

## Einschränkungen, die Sie kennen sollten

MCP-Tools arbeiten auf einzelnen Seiten. Es gibt kein „Schreibe die gesamte Docs-Seite um"-Tool — absichtlich. Großangelegte Umstrukturierungen erfordern weiterhin menschliches Urteilsvermögen bezüglich der Informationsarchitektur.

Die Schreib-Tools erstellen echte Änderungen. Wenn Sie Claude Desktop mit einem API-Schlüssel auf Admin-Ebene konfigurieren, kann die KI Seiten löschen. Verwenden Sie RBAC, um die Berechtigungen des API-Schlüssels entsprechend einzuschränken. Eine „Editor"-Rolle kann Inhalte lesen und schreiben, aber keine Workspaces löschen oder Benutzer verwalten.

Die Suchqualität hängt von Ihrem Inhalt ab. Wenn Ihre Dokumentation inkonsistente Terminologie verwendet, findet die KI inkonsistente Ergebnisse. MCP macht die Suche schnell, behebt aber nicht die zugrundeliegenden Inhaltsprobleme.

## Erste Schritte

1. [Valoryx installieren](/install/) — einzelnes Binary, keine Abhängigkeiten, in unter 2 Minuten betriebsbereit
2. Einen API-Schlüssel im Admin-Panel generieren
3. Die MCP-Server-Konfiguration zu Claude Desktop hinzufügen
4. Mit einem schreibgeschützten Workflow beginnen: Suchen und prüfen, bevor Sie Schreibzugriff aktivieren

Die [MCP-Dokumentation](/mcp/) deckt die vollständige API-Referenz für alle 26 Tools ab, einschließlich Parametertypen und Antwortschemas.

Dokumentationspflege muss kein manueller Prozess sein. Mit einem strukturierten Protokoll zwischen Ihrem KI-Assistenten und Ihrer Dokumentationsplattform werden die mühsamen Teile — veraltete Inhalte finden, Konsistenz prüfen, mechanische Aktualisierungen durchführen — zu etwas, das Sie mit Vertrauen delegieren können.
