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

### In Claude Desktop

1. Gehen Sie zu **Workspace Settings** → **API Keys**
2. Erstellen Sie einen API Key (Read & Write oder Read Only)
3. Fügen Sie in den Claude Desktop-Einstellungen diesen MCP-Server hinzu:

```json
{
  "mcpServers": {
    "valoryx-docs": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-remote", "https://app.valoryx.dev/api/v1/mcp"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

4. Starten Sie Claude Desktop neu
5. Fragen Sie Claude: *„Was steht in meiner Dokumentation?"*

### In Cursor

Gleiche Konfiguration — fügen Sie den MCP-Server in den Cursor-Einstellungen hinzu und verwenden Sie denselben API Key.

## Verfügbare MCP-Tools

Der MCP-Server stellt 13 Tools bereit:

| Tool | Beschreibung |
|---|---|
| `list_pages` | Alle Seiten eines Workspace auflisten |
| `read_page` | Den Inhalt einer bestimmten Seite lesen |
| `create_page` | Eine neue Seite erstellen |
| `update_page` | Eine bestehende Seite aktualisieren |
| `delete_page` | Eine Seite löschen |
| `search` | Volltextsuche über alle Seiten |
| `list_workspaces` | Verfügbare Workspaces auflisten |
| *...und mehr* | Kommentare, Metadaten, Baumstruktur |

## Sicherheit

- API Keys werden gehasht (niemals im Klartext gespeichert)
- Sie bestimmen den Umfang: Read Only oder Read & Write
- Widerrufen Sie Keys jederzeit über die Workspace Settings
- Alle MCP-Anfragen werden im Audit-Trail protokolliert
