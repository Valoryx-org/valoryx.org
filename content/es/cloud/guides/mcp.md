---
title: IA e integracion MCP
description: Conecte Claude, Cursor y otras herramientas de IA para leer y escribir en su documentacion.
weight: 5
---

# IA e integracion MCP

Valoryx Cloud incluye un servidor MCP (Model Context Protocol) integrado que permite a los asistentes de IA interactuar con su documentacion directamente.

## Que es MCP?

MCP es un protocolo estandar que permite a las herramientas de IA conectarse con servicios externos. Piense en ello como darle a Claude o Cursor una forma de "ver" sus documentos y realizar cambios — con su permiso.

## Que puede hacer la IA con sus documentos

- **Leer** paginas para responder preguntas sobre su documentacion
- **Buscar** en todas las paginas para encontrar contenido relevante
- **Crear** nuevas paginas segun sus instrucciones
- **Editar** paginas existentes (reescribir, mejorar, traducir)
- **Analizar** sus documentos en busca de vacios, inconsistencias o contenido desactualizado

## Configuracion

> **Estado:** el endpoint MCP alojado de Valoryx Cloud **aun no esta habilitado** — las herramientas de IA remotas todavia no pueden conectarse a `app.valoryx.dev`. Esta pagina se actualizara en cuanto entre en servicio. En una instancia **auto-alojada**, MCP funciona hoy mismo — siga los pasos siguientes en la maquina donde se ejecuta DocPlatform.

### Auto-alojado: Claude Desktop

1. Vaya a **Workspace Settings** → **API Keys**
2. Cree una API key — empieza por `dp_live_` y se muestra una sola vez
3. En `claude_desktop_config.json`, agregue:

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

4. Reinicie Claude Desktop
5. Pregunte a Claude: *"Que hay en mi documentacion?"*

### En Cursor

La misma configuracion — agregue la misma entrada `docplatform` en el archivo `.cursor/mcp.json` de su proyecto.

## Herramientas MCP disponibles

El servidor MCP proporciona 26 herramientas:

| Herramienta | Que hace |
|---|---|
| `list_pages` | Listar todas las paginas de un workspace |
| `read_page` | Leer el contenido de una pagina especifica |
| `write_page` | Crear una pagina, o actualizarla si ya existe |
| `update_page` | Actualizar una pagina existente |
| `delete_page` | Eliminar una pagina |
| `search` | Busqueda de texto completo en todas las paginas |
| `list_workspaces` | Listar los workspaces disponibles |
| *...y mas* | Comentarios, metadatos, estructura de arbol |

## Seguridad

- Las API keys se almacenan como hash (nunca en texto plano)
- Usted controla el alcance por key: `read`, `write` y `delete`
- Revoque las keys en cualquier momento desde Workspace Settings
- Los fallos de autorizacion se registran, y cada cambio de contenido queda rastreado en el historial de la pagina
