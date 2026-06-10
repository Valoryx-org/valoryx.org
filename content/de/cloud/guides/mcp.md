---
title: KI & MCP-Integration
description: Verbinden Sie Claude, Cursor und andere KI-Tools, um Ihre Dokumentation zu lesen und zu bearbeiten.
weight: 5
---

# KI & MCP-Integration

Valoryx Cloud enthält einen integrierten MCP-Server (Model Context Protocol), der KI-Assistenten die direkte Interaktion mit Ihrer Dokumentation ermöglicht.

## Was ist MCP?

MCP ist ein Standardprotokoll, das KI-Tools die Verbindung mit externen Diensten ermöglicht. Stellen Sie es sich so vor, als würden Sie Claude oder Cursor die Möglichkeit geben, Ihre Dokumentation zu „sehen" und Änderungen vorzunehmen — mit Ihrer Genehmigung.

## Was KI mit Ihrer Dokumentation tun kann

- **Lesen** — Seiten lesen, um Fragen zu Ihrer Dokumentation zu beantworten
- **Suchen** — seitenübergreifend nach relevanten Inhalten suchen
- **Erstellen** — neue Seiten nach Ihren Anweisungen anlegen
- **Bearbeiten** — bestehende Seiten überarbeiten, verbessern oder übersetzen
- **Analysieren** — Ihre Dokumentation auf Lücken, Widersprüche oder veraltete Inhalte prüfen

## Einrichtung

> **Status:** Der gehostete MCP-Endpunkt für Valoryx Cloud ist **noch nicht aktiviert** — Remote-KI-Tools können sich noch nicht mit `app.valoryx.dev` verbinden. Diese Seite wird aktualisiert, sobald er live geht. Auf einer **selbst gehosteten** Instanz funktioniert MCP bereits heute — führen Sie die folgenden Schritte auf dem Rechner aus, auf dem DocPlatform läuft.

### Selbst gehostet: Claude Desktop

1. Gehen Sie zu **Workspace Settings** → **API Keys**
2. Erstellen Sie einen API Key — er beginnt mit `dp_live_` und wird nur einmal angezeigt
3. Fügen Sie in `claude_desktop_config.json` Folgendes hinzu:

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

4. Starten Sie Claude Desktop neu
5. Fragen Sie Claude: *„Was steht in meiner Dokumentation?"*

### In Cursor

Gleiche Konfiguration — fügen Sie denselben `docplatform`-Eintrag in die Datei `.cursor/mcp.json` Ihres Projekts ein.

## Verfügbare MCP-Tools

Der MCP-Server stellt 26 Tools bereit:

| Tool | Beschreibung |
|---|---|
| `list_pages` | Alle Seiten eines Workspace auflisten |
| `read_page` | Den Inhalt einer bestimmten Seite lesen |
| `write_page` | Eine Seite erstellen oder, falls sie bereits existiert, aktualisieren |
| `update_page` | Eine bestehende Seite aktualisieren |
| `delete_page` | Eine Seite löschen |
| `search` | Volltextsuche über alle Seiten |
| `list_workspaces` | Verfügbare Workspaces auflisten |
| *...und mehr* | Kommentare, Metadaten, Baumstruktur |

## Sicherheit

- API Keys werden gehasht (niemals im Klartext gespeichert)
- Sie bestimmen den Umfang pro Key: `read`, `write` und `delete`
- Widerrufen Sie Keys jederzeit über die Workspace Settings
- Autorisierungsfehler werden protokolliert, und jede Inhaltsänderung wird im Seitenverlauf nachverfolgt
