---
title: "MCP für Dokumentation: Ein technischer Leitfaden"
description: "Wie Model Context Protocol KI-Assistenten mit Ihrer Dokumentation verbindet. Claude Desktop konfigurieren, 26 eingebaute Tools nutzen und Dokumentationspflege automatisieren."
date: "2026-03-16"
author: "Valoryx Team"
tags: ["mcp", "ai", "documentation", "tutorial"]
---

Model Context Protocol (MCP) ist ein offener Standard, der KI-Assistenten die Interaktion mit externen Tools und Datenquellen über eine strukturierte Schnittstelle ermöglicht. Anstatt Text in ein Chat-Fenster zu kopieren und darauf zu hoffen, dass das Modell den Kontext versteht, gibt MCP dem Assistenten direkten, typisierten Zugriff auf Ihre Systeme — Dateien lesen, Suchen ausführen, Inhalte erstellen, alles über wohldefinierte Tool-Aufrufe.

Für Dokumentationsteams verändert dies den Workflow grundlegend. Ihr KI-Assistent ist nicht mehr ein Textgenerator, der mit veraltetem Kontext arbeitet, sondern wird zu einem Teilnehmer, der Ihre tatsächliche Dokumentation liest, Ihre Wissensbasis durchsucht und Änderungen vornimmt, die Sie prüfen können, bevor sie live gehen.

Valoryx liefert einen eingebauten MCP-Server mit 26 Tools. Keine Plugins zu installieren, kein separater Dienst, der laufen muss — wenn Sie eine laufende Instanz haben, ist der MCP-Server bereits da. Alles, was Sie brauchen, ist ein API-Schlüssel.

## Was MCP tatsächlich macht

MCP definiert ein Protokoll für Tool-Erkennung und -Aufruf. Ein KI-Client (wie Claude Desktop) verbindet sich mit einem MCP-Server, fragt, welche Tools verfügbar sind, und ruft sie mit strukturierten Parametern auf. Der Server führt die Operation aus und gibt strukturierte Ergebnisse zurück.

Das unterscheidet sich von „KI-Features“, die nachträglich an ein Produkt angebaut werden. Es gibt keine proprietäre Integration. Jeder MCP-kompatible Client funktioniert. Die [MCP-Spezifikation](https://modelcontextprotocol.io) ist offen, und mehrere KI-Assistenten unterstützen sie bereits.

Das praktische Ergebnis: Sie können Claude fragen „Finde alle Seiten, die Authentifizierung erwähnen“ und es wird tatsächlich Ihre Dokumentationsinstanz durchsuchen, nicht Seitentitel aus Trainingsdaten halluzinieren.

## Die 26 eingebauten Tools

Jedes Tool trägt den Namespace `docplatform_*`, damit es nie mit anderen MCP-Servern in Ihrem Client kollidiert. Die vollständige Referenz auf Parameterebene finden Sie auf der [MCP-Seite](/mcp/); hier ist das komplette Register nach Kategorien:

### Inhalte
Seiten erstellen, lesen und umstrukturieren. Jeder Schreibvorgang läuft über denselben Content-Service wie der Web-Editor, sodass Änderungen nachverfolgt und sync-sicher sind.

- **docplatform_list_pages** — die Seiten im verbundenen Workspace auflisten.
- **docplatform_read_page** — Markdown-Inhalt und Metadaten einer Seite lesen.
- **docplatform_write_page** — eine Seite schreiben: erstellt sie, wenn sie nicht existiert, aktualisiert sie, wenn doch. Die eine „einfach schreiben“-Operation für KI-Agenten.
- **docplatform_update_page** — eine bestehende Seite aktualisieren (schlägt fehl, statt zu erstellen — nützlich, wenn die Seite bereits existieren muss).
- **docplatform_delete_page** — eine Seite löschen.
- **docplatform_move_page** — eine Seite an einen neuen Pfad im Baum verschieben.

### Suche & Kontext
- **docplatform_search** — Volltextsuche über den Workspace, mit Fuzzy-Matching und nach Relevanz sortierten Ergebnissen — dieselbe Bleve-Engine, die auch die Web-Oberfläche antreibt.
- **docplatform_get_context** — das RAG-Arbeitspferd: liefert eine Seite zusammen mit ihrer übergeordneten Seite, ihren Geschwisterseiten und den Zielen ihrer Wikilinks in einem einzigen Aufruf, sodass der Assistent den umgebenden Kontext ohne fünf Roundtrips erhält.
- **docplatform_get_tree** — der vollständige Navigationsbaum eines Workspace. Nützlich, um die Dokumentationsstruktur zu verstehen, bevor Änderungen vorgenommen werden.
- **docplatform_list_workspaces** — die Workspaces auflisten, auf die der API-Schlüssel zugreifen kann.
- **docplatform_get_manifest** — ein maschinenlesbares Manifest des Workspace.

### Qualität
- **docplatform_validate_links** — defekte interne Links und Wikilinks finden.
- **docplatform_quality_scan** — Inhalte auf Qualitätsprobleme prüfen.

### Versionierung
- **docplatform_list_versions** / **docplatform_create_version** — benannte Versions-Snapshots auflisten und erstellen.

### Kommentare & Aktivität
- **docplatform_list_comments** / **docplatform_add_comment** — Seitendiskussionen lesen und sich daran beteiligen.
- **docplatform_get_activity** — der Feed der letzten Aktivitäten: wer hat was geändert, und wann.

### Workspace-Verwaltung
- **docplatform_create_workspace** / **docplatform_get_workspace** — Workspaces erstellen und inspizieren.
- **docplatform_publish_workspace** — einen Workspace als öffentliche Website veröffentlichen.

### Themes, Export, KI und Git-Sync
- **docplatform_get_theme** / **docplatform_update_theme** — das Workspace-Theme lesen und ändern.
- **docplatform_export** — Workspace-Inhalte exportieren.
- **docplatform_writing_assist** — serverseitige Schreibassistenz (verbessern, vereinfachen, erweitern, zusammenfassen, Grammatik korrigieren, übersetzen), wenn ein KI-Provider konfiguriert ist.
- **docplatform_resolve_sync_conflict** — einen Git-Sync-Konflikt auflösen, indem eine Seite gewählt oder zusammengeführter Inhalt übergeben wird.

## Claude Desktop konfigurieren

Der MCP-Server spricht stdio über das `docplatform`-Binary selbst — keine Wrapper-Pakete. Fügen Sie einen Eintrag in Ihre Konfigurationsdatei ein (unter macOS `~/Library/Application Support/Claude/claude_desktop_config.json`, unter Windows `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "docplatform": {
      "command": "docplatform",
      "args": ["mcp", "--workspace", "my-docs", "--api-key", "dp_live_abc123"]
    }
  }
}
```

Erstellen Sie den API-Schlüssel unter **Workspace Settings → API Keys**. Er beginnt mit `dp_live_` und wird nur einmal angezeigt. Schlüssel tragen Scopes (`read`, `write`, `delete` — `admin` ist Opt-in), und jeder MCP-Aufruf wird zusätzlich gegen die Workspace-Rolle des handelnden Benutzers geprüft — der Schlüssel eines Editors kann also keine Admin-Operationen ausführen, egal welche Scopes er beansprucht.

Für entfernte oder Cloud-Instanzen gibt es außerdem einen Streamable-HTTP-Transport (`/mcp`-Endpoint) — siehe die [MCP-Seite](/mcp/) für die Transport-Matrix und die Einrichtung pro Client (Claude Code, Cursor, VS Code).

## Praktische Beispiele

Sobald die Verbindung steht, können Sie konkret Folgendes tun:

### Konsistenz prüfen

```
"Search all pages for references to our old API endpoint
api.example.com/v1 and list them"
```

Dies ruft `docplatform_search` mit der alten Endpoint-Zeichenkette auf. Sie erhalten eine Liste jeder Seite, die die veraltete URL noch referenziert. Kein manuelles Grep durch ein Docs-Repository nötig.

### Inhalte entwerfen und aktualisieren

```
"Read the current authentication guide, then update it to include
the new passkey login flow. Keep the existing structure."
```

Der Assistent ruft `docplatform_read_page` auf, um den aktuellen Inhalt zu lesen, entwirft die Aktualisierung und ruft `docplatform_update_page` auf, um sie anzuwenden. Wenn [Git-Sync](/docs/guides/git-integration/) konfiguriert ist, erscheint die Bearbeitung als Commit in Ihrem Repository, zugeordnet dem handelnden Benutzer.

### Aktuelle Änderungen überprüfen

```
"Show me everything that changed this week in this workspace"
```

Ruft `docplatform_get_activity` auf. Liefert, was sich geändert hat, wer es geändert hat und wann. Nützlich für wöchentliche Dokumentationsreviews, ohne sich in die Web-Oberfläche einzuloggen.

### Qualität vor einem Release prüfen

```
"Validate all internal links in this workspace and list anything broken"
```

Ruft `docplatform_validate_links` auf und liefert die defekten Ziele mit ihren Quellseiten — die Art von Durchlauf, die von Hand mühsam ist und mit strukturiertem Zugriff sofort erledigt ist.

## Was das für die Dokumentationspflege bedeutet

Der traditionelle Workflow für die Dokumentationspflege ist: Jemand bemerkt, dass die Dokumentation falsch ist, erstellt ein Ticket, jemand anderes aktualisiert irgendwann die Seite. Die Lücke zwischen „bemerkt“ und „behoben“ beträgt normalerweise Wochen.

Mit MCP wird der Workflow zu: Bitten Sie die KI, einen Bereich zu prüfen, überprüfen Sie die Ergebnisse, genehmigen Sie die Änderungen. Die Lücke schrumpft auf Minuten. Nicht weil KI bessere Dokumentation schreibt — das tut sie nicht, nicht zuverlässig — sondern weil der Engpass immer das Finden des Fehlers und das Durchführen der Bearbeitung war, nicht das Verfassen des Textes.

Das funktioniert besonders gut für mechanische Aktualisierungen: URL-Änderungen, Terminologieumbenennungen, Versionsnummern-Aktualisierungen, Veralterungshinweise. Die Art von Änderungen, die für Menschen mühsam und für eine KI mit strukturiertem Zugriff auf den Inhalt unkompliziert sind.

Mehr zur Nutzung von MCP für die Aktualität der Dokumentation finden Sie unter [Wie man Dokumentation aktuell hält](/blog/keep-docs-up-to-date/).

## Einschränkungen, die Sie kennen sollten

MCP-Tools arbeiten auf einzelnen Seiten. Es gibt kein „Schreibe die gesamte Docs-Seite um“-Tool — absichtlich. Großangelegte Umstrukturierungen erfordern weiterhin menschliches Urteilsvermögen bezüglich der Informationsarchitektur.

Die Schreib-Tools erstellen echte Änderungen. Wenn Sie dem Assistenten einen Schlüssel mit den Scopes `write` und `delete` geben, kann er Seiten ändern und entfernen. Beginnen Sie schreibgeschützt: Erstellen Sie für Audit-Workflows einen Schlüssel nur mit dem Scope `read` und vergeben Sie Schreib-Scopes erst, wenn Sie dem Review-Loop vertrauen. Scopes werden serverseitig durchgesetzt, zusätzlich zur Workspace-Rolle des handelnden Benutzers.

Die Suchqualität hängt von Ihrem Inhalt ab. Wenn Ihre Dokumentation inkonsistente Terminologie verwendet, findet die KI inkonsistente Ergebnisse. MCP macht die Suche schnell, behebt aber nicht die zugrundeliegenden Inhaltsprobleme.

## Erste Schritte

1. [Valoryx installieren](/install/) — einzelnes Binary, keine Abhängigkeiten, in unter 2 Minuten betriebsbereit
2. Einen API-Schlüssel unter **Workspace Settings → API Keys** erstellen
3. Die MCP-Server-Konfiguration zu Claude Desktop hinzufügen
4. Mit einem schreibgeschützten Workflow beginnen: Suchen und prüfen, bevor Sie Schreibzugriff aktivieren

Die [MCP-Dokumentation](/mcp/) deckt die vollständige Referenz für alle 26 Tools ab, einschließlich Parametertypen und Antwortschemas.

Dokumentationspflege muss kein manueller Prozess sein. Mit einem strukturierten Protokoll zwischen Ihrem KI-Assistenten und Ihrer Dokumentationsplattform werden die mühsamen Teile — veraltete Inhalte finden, Konsistenz prüfen, mechanische Aktualisierungen durchführen — zu etwas, das Sie mit Vertrauen delegieren können.
