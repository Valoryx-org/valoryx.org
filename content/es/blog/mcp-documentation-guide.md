---
title: "MCP para Documentación: Una Guía Técnica"
description: "Cómo Model Context Protocol conecta asistentes de IA a su documentación. Configure Claude Desktop, use las 26 herramientas integradas y automatice el mantenimiento de documentación."
date: "2026-03-16"
author: "Equipo Valoryx"
tags: ["mcp", "ai", "documentation", "tutorial"]
---

Model Context Protocol (MCP) es un estándar abierto que permite a los asistentes de IA interactuar con herramientas externas y fuentes de datos a través de una interfaz estructurada. En lugar de copiar texto en una ventana de chat y esperar que el modelo entienda el contexto, MCP le da al asistente acceso directo y tipado a sus sistemas — leer archivos, ejecutar búsquedas, crear contenido, todo mediante llamadas a herramientas bien definidas.

Para los equipos de documentación, esto cambia el flujo de trabajo fundamentalmente. Su asistente de IA deja de ser un generador de texto que trabaja con contexto obsoleto y se convierte en un participante que lee su documentación real, busca en su base de conocimiento y realiza ediciones que usted puede revisar antes de que se publiquen.

Valoryx incluye un servidor MCP integrado con 26 herramientas. Sin plugins que instalar, sin servicio aparte que ejecutar — si tiene una instancia en ejecución, el servidor MCP ya está ahí. Lo único que necesita es una clave de API.

## Qué hace realmente MCP

MCP define un protocolo para descubrimiento e invocación de herramientas. Un cliente de IA (como Claude Desktop) se conecta a un servidor MCP, pregunta qué herramientas están disponibles y las llama con parámetros estructurados. El servidor ejecuta la operación y devuelve resultados estructurados.

Esto es diferente de las "funcionalidades de IA" añadidas a un producto. No hay integración propietaria. Cualquier cliente compatible con MCP funciona. La [especificación MCP](https://modelcontextprotocol.io) es abierta, y múltiples asistentes de IA ya la soportan.

El resultado práctico: puede pedirle a Claude "encuentra todas las páginas que mencionan autenticación" y realmente buscará en su instancia de documentación, no alucinará títulos de páginas desde datos de entrenamiento.

## Las 26 herramientas integradas

Cada herramienta lleva el prefijo de espacio de nombres `docplatform_*`, de modo que nunca colisiona con otros servidores MCP en su cliente. La referencia completa a nivel de parámetros está en la [página de MCP](/mcp/); este es el registro completo por categoría:

### Contenido
Cree, lea y reorganice páginas. Cada escritura pasa por el mismo servicio de contenido que el editor web, por lo que los cambios se rastrean y son seguros para la sincronización.

- **docplatform_list_pages** — lista las páginas del workspace conectado.
- **docplatform_read_page** — lee el contenido markdown y los metadatos de una página.
- **docplatform_write_page** — escribe una página: la crea si no existe, la actualiza si existe. La operación única de "simplemente escríbelo" para agentes de IA.
- **docplatform_update_page** — actualiza una página existente (falla en lugar de crear — útil cuando la página debe existir previamente).
- **docplatform_delete_page** — elimina una página.
- **docplatform_move_page** — mueve una página a una nueva ruta en el árbol.

### Descubrimiento y contexto
- **docplatform_search** — búsqueda de texto completo en el workspace, con coincidencia difusa y resultados ordenados por relevancia — el mismo motor Bleve que impulsa la interfaz web.
- **docplatform_get_context** — el caballo de batalla del RAG: devuelve una página junto con su padre, sus páginas hermanas y los destinos de sus wikilinks en una sola llamada, de modo que el asistente obtiene el contexto circundante sin cinco viajes de ida y vuelta.
- **docplatform_get_tree** — el árbol de navegación completo de un workspace. Útil para entender la estructura de la documentación antes de hacer cambios.
- **docplatform_list_workspaces** — lista los workspaces a los que puede acceder la clave de API.
- **docplatform_get_manifest** — un manifiesto del workspace legible por máquina.

### Calidad
- **docplatform_validate_links** — encuentra enlaces internos y wikilinks rotos.
- **docplatform_quality_scan** — analiza el contenido en busca de problemas de calidad.

### Versionado
- **docplatform_list_versions** / **docplatform_create_version** — listan y crean instantáneas de versión con nombre.

### Comentarios y actividad
- **docplatform_list_comments** / **docplatform_add_comment** — leen y participan en las discusiones de página.
- **docplatform_get_activity** — el feed de actividad reciente: quién cambió qué, y cuándo.

### Gestión de workspaces
- **docplatform_create_workspace** / **docplatform_get_workspace** — crean e inspeccionan workspaces.
- **docplatform_publish_workspace** — publica un workspace como sitio público.

### Temas, exportación, IA y sincronización git
- **docplatform_get_theme** / **docplatform_update_theme** — leen y cambian el tema del workspace.
- **docplatform_export** — exporta el contenido del workspace.
- **docplatform_writing_assist** — asistencia de escritura del lado del servidor (mejorar, simplificar, expandir, resumir, corregir gramática, traducir) cuando hay un proveedor de IA configurado.
- **docplatform_resolve_sync_conflict** — resuelve un conflicto de sincronización git eligiendo un lado o aportando el contenido fusionado.

## Configuración de Claude Desktop

El servidor MCP habla stdio a través del propio binario `docplatform` — sin paquetes intermediarios. Añada una entrada a su archivo de configuración (en macOS, `~/Library/Application Support/Claude/claude_desktop_config.json`; en Windows, `%APPDATA%\Claude\claude_desktop_config.json`):

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

Cree la clave de API en **Workspace Settings → API Keys**. Empieza por `dp_live_` y se muestra una sola vez. Las claves llevan scopes (`read`, `write`, `delete` — `admin` es opcional, opt-in), y cada llamada MCP se verifica además contra el rol del usuario en el workspace, de modo que la clave de un Editor no puede realizar operaciones de administrador sin importar qué scopes declare.

Para instancias remotas o en la nube existe también un transporte Streamable HTTP (endpoint `/mcp`) — consulte la [página de MCP](/mcp/) para la matriz de transportes y la configuración por cliente (Claude Code, Cursor, VS Code).

## Ejemplos prácticos

Una vez conectado, estas son cosas concretas que puede hacer:

### Auditar consistencia

```
"Search all pages for references to our old API endpoint
api.example.com/v1 and list them"
```

Esto llama a `docplatform_search` con la cadena del endpoint antiguo. Obtiene una lista de cada página que todavía referencia la URL obsoleta. Sin necesidad de hacer grep manual en un repositorio de documentación.

### Redactar y actualizar contenido

```
"Read the current authentication guide, then update it to include
the new passkey login flow. Keep the existing structure."
```

El asistente llama a `docplatform_read_page` para leer el contenido actual, redacta la actualización y llama a `docplatform_update_page` para aplicarla. Si [la sincronización git](/docs/guides/git-integration/) está configurada, la edición aparece como un commit en su repositorio, atribuido al usuario que actúa.

### Revisar cambios recientes

```
"Show me everything that changed this week in this workspace"
```

Llama a `docplatform_get_activity`. Devuelve qué cambió, quién lo cambió y cuándo. Útil para revisiones semanales de documentación sin iniciar sesión en la interfaz web.

### Verificar la calidad antes de un lanzamiento

```
"Validate all internal links in this workspace and list anything broken"
```

Llama a `docplatform_validate_links` y devuelve los destinos rotos junto con sus páginas de origen — el tipo de barrido que resulta tedioso a mano e instantáneo con acceso estructurado.

## Qué significa esto para el mantenimiento de documentación

El flujo de trabajo tradicional de mantenimiento de documentación es: alguien nota que la documentación está mal, registra un ticket, alguien más eventualmente actualiza la página. La brecha entre "notar" y "arreglar" es generalmente semanas.

Con MCP, el flujo de trabajo se convierte en: pedirle a la IA que audite una sección, revisar los hallazgos, aprobar los cambios. La brecha se reduce a minutos. No porque la IA escriba mejor documentación — no lo hace, no de forma confiable — sino porque el cuello de botella siempre fue encontrar qué está mal y hacer la edición, no componer el texto.

Esto funciona especialmente bien para actualizaciones mecánicas: cambios de URL, renombramientos de terminología, actualizaciones de números de versión, avisos de deprecación. El tipo de cambios que son tediosos para humanos y directos para una IA con acceso estructurado al contenido.

Para más información sobre cómo usar MCP para mantener la documentación actualizada, consulte [Cómo Mantener la Documentación Actualizada](/blog/keep-docs-up-to-date/).

## Limitaciones que vale la pena conocer

Las herramientas MCP operan sobre páginas individuales. No hay una herramienta para "reescribir todo el sitio de documentación" — por diseño. La reestructuración a gran escala todavía necesita juicio humano sobre la arquitectura de información.

Las herramientas de escritura crean cambios reales. Si le entrega al asistente una clave con los scopes `write` y `delete`, puede modificar y eliminar páginas. Empiece en solo lectura: cree una clave con únicamente el scope `read` para flujos de auditoría, y conceda scopes de escritura cuando confíe en el ciclo de revisión. Los scopes se aplican del lado del servidor, junto con el rol del usuario en el workspace.

La calidad de la búsqueda depende de su contenido. Si su documentación usa terminología inconsistente, la IA encontrará resultados inconsistentes. MCP hace la búsqueda rápida, pero no arregla los problemas subyacentes del contenido.

## Primeros pasos

1. [Instale Valoryx](/install/) — binario único, sin dependencias, funcionando en menos de 2 minutos
2. Cree una clave de API en **Workspace Settings → API Keys**
3. Añada la configuración del servidor MCP a Claude Desktop
4. Comience con un flujo de trabajo de solo lectura: busque y audite antes de habilitar las escrituras

La [documentación de MCP](/mcp/) cubre la referencia completa de las 26 herramientas, incluyendo tipos de parámetros y esquemas de respuesta.

El mantenimiento de documentación no tiene que ser un proceso manual. Con un protocolo estructurado entre su asistente de IA y su plataforma de documentación, las partes tediosas — encontrar contenido obsoleto, verificar consistencia, hacer actualizaciones mecánicas — se convierten en algo que puede delegar con confianza.
