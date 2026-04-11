---
title: "MCP para Documentación: Una Guía Técnica"
description: "Cómo Model Context Protocol conecta asistentes de IA a su documentación. Configure Claude Desktop, use 13 herramientas integradas y automatice el mantenimiento de documentación."
date: "2026-03-16"
author: "Equipo Valoryx"
tags: ["mcp", "ai", "documentation", "tutorial"]
---

Model Context Protocol (MCP) es un estándar abierto que permite a los asistentes de IA interactuar con herramientas externas y fuentes de datos a través de una interfaz estructurada. En lugar de copiar texto en una ventana de chat y esperar que el modelo entienda el contexto, MCP le da al asistente acceso directo y tipado a sus sistemas — leer archivos, ejecutar búsquedas, crear contenido, todo mediante llamadas a herramientas bien definidas.

Para los equipos de documentación, esto cambia el flujo de trabajo fundamentalmente. Su asistente de IA deja de ser un generador de texto que trabaja con contexto obsoleto y se convierte en un participante que lee su documentación real, busca en su base de conocimiento y realiza ediciones que usted puede revisar antes de que se publiquen.

Valoryx incluye un servidor MCP integrado con 13 herramientas. Sin plugins que instalar, sin claves de API que configurar. Si tiene una instancia en ejecución, el servidor MCP ya está ahí.

## Qué hace realmente MCP

MCP define un protocolo para descubrimiento e invocación de herramientas. Un cliente de IA (como Claude Desktop) se conecta a un servidor MCP, pregunta qué herramientas están disponibles y las llama con parámetros estructurados. El servidor ejecuta la operación y devuelve resultados estructurados.

Esto es diferente de las "funcionalidades de IA" añadidas a un producto. No hay integración propietaria. Cualquier cliente compatible con MCP funciona. La [especificación MCP](https://modelcontextprotocol.io) es abierta, y múltiples asistentes de IA ya la soportan.

El resultado práctico: puede pedirle a Claude "encuentra todas las páginas que mencionan autenticación" y realmente buscará en su instancia de documentación, no alucinará títulos de páginas desde datos de entrenamiento.

## Las 13 herramientas integradas

Las herramientas MCP de Valoryx se dividen en cuatro categorías:

### Herramientas de lectura
Estas recuperan contenido sin modificar nada.

- **get_page** — Obtener una sola página por ID o ruta. Devuelve título, contenido markdown, metadatos y marca de tiempo de última modificación.
- **get_workspace** — Listar todos los workspaces con sus conteos de páginas y configuraciones.
- **get_page_tree** — Devolver el árbol de navegación completo para un workspace. Útil para entender la estructura de la documentación antes de hacer cambios.

### Herramientas de búsqueda
Búsqueda de texto completo impulsada por el mismo motor Bleve que impulsa la interfaz web.

- **search_pages** — Buscar en todas las páginas de un workspace. Soporta consultas por frase, búsquedas por campo específico y operadores booleanos.
- **search_by_tag** — Encontrar páginas con etiquetas específicas. Útil para auditoría: "muéstrame todo etiquetado como `deprecated`."
- **search_recent** — Encontrar páginas modificadas en los últimos N días. Bueno para revisar cambios recientes.

### Herramientas de escritura
Estas crean o modifican contenido. Cada operación de escritura crea una entrada en el ledger, por lo que los cambios se rastrean y son seguros para la sincronización.

- **create_page** — Crear una nueva página con título, contenido, ruta padre y etiquetas.
- **update_page** — Reemplazar el contenido de una página existente. La versión anterior se preserva en el historial.
- **move_page** — Cambiar la posición de una página en el árbol de navegación.
- **delete_page** — Eliminación suave de una página (recuperable desde el panel de administración).

### Herramientas de administración
Operaciones de gestión de workspaces y usuarios.

- **list_users** — Obtener todos los usuarios con sus roles. Útil para auditar el acceso.
- **get_activity_log** — Recuperar actividad reciente (ediciones, inicios de sesión, cambios de permisos).
- **get_sync_status** — Verificar el estado de sincronización git para un workspace — última hora de sincronización, cambios pendientes, cualquier conflicto.

## Configuración de Claude Desktop

Para conectar Claude Desktop a su instancia de Valoryx, añada una entrada de servidor MCP a su archivo de configuración. En macOS, este se encuentra en `~/Library/Application Support/Claude/claude_desktop_config.json`. En Windows, es `%APPDATA%\Claude\claude_desktop_config.json`.

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

Genere una clave de API desde el panel de administración de Valoryx en **Settings > API Keys**. La clave hereda los permisos del usuario que la creó, así que use una cuenta de servicio dedicada con el rol RBAC apropiado si desea limitar lo que la IA puede hacer.

Para la Community Edition ejecutándose localmente, la URL es típicamente `http://localhost:3000/api/mcp`.

## Ejemplos prácticos

Una vez conectado, estas son cosas concretas que puede hacer:

### Encontrar contenido obsoleto

```
"Encuentra todas las páginas en el workspace de Ingeniería que no se han
actualizado en los últimos 90 días"
```

El asistente llama a `search_recent` con una ventana de 90 días, invierte el resultado contra `get_page_tree`, y devuelve una lista de páginas potencialmente obsoletas. Obtiene rutas de páginas, fechas de última modificación y últimos editores — suficiente para asignar tareas de revisión.

### Auditar consistencia

```
"Busca en todas las páginas referencias a nuestro antiguo endpoint de API
api.example.com/v1 y lístalas"
```

Esto llama a `search_pages` con la cadena del endpoint antiguo. Obtiene una lista de cada página que todavía referencia la URL deprecada, con contexto circundante. Sin necesidad de hacer grep manual a través de un repositorio de documentación.

### Redactar y actualizar contenido

```
"Lee la guía de autenticación actual, luego actualízala para incluir
el nuevo flujo de inicio de sesión con passkey. Mantén la estructura existente."
```

El asistente llama a `get_page` para leer el contenido actual, redacta la actualización y llama a `update_page` para aplicarla. La versión anterior permanece en el historial. Si [la sincronización git](/docs/guides/git-integration/) está configurada, la edición aparece como un commit en su repositorio.

### Revisar cambios recientes

```
"Muéstrame todo lo que cambió en la última semana en todos
los workspaces"
```

Llama a `search_recent` con una ventana de 7 días. Devuelve un resumen de qué cambió, quién lo cambió y cuándo. Útil para revisiones semanales de documentación sin iniciar sesión en la interfaz web.

## Qué significa esto para el mantenimiento de documentación

El flujo de trabajo tradicional de mantenimiento de documentación es: alguien nota que la documentación está mal, registra un ticket, alguien más eventualmente actualiza la página. La brecha entre "notar" y "arreglar" es generalmente semanas.

Con MCP, el flujo de trabajo se convierte en: pedirle a la IA que audite una sección, revisar los hallazgos, aprobar los cambios. La brecha se reduce a minutos. No porque la IA escriba mejor documentación — no lo hace, no de forma confiable — sino porque el cuello de botella siempre fue encontrar qué está mal y hacer la edición, no componer el texto.

Esto funciona especialmente bien para actualizaciones mecánicas: cambios de URL, renombramientos de terminología, actualizaciones de números de versión, avisos de deprecación. El tipo de cambios que son tediosos para humanos y directos para una IA con acceso estructurado al contenido.

Para más información sobre cómo usar MCP para mantener la documentación actualizada, consulte [Cómo Mantener la Documentación Actualizada](/blog/keep-docs-up-to-date/).

## Limitaciones que vale la pena conocer

Las herramientas MCP operan sobre páginas individuales. No hay una herramienta para "reescribir todo el sitio de documentación" — por diseño. La reestructuración a gran escala todavía necesita juicio humano sobre la arquitectura de información.

Las herramientas de escritura crean cambios reales. Si configura Claude Desktop con una clave de API de nivel administrador, la IA puede eliminar páginas. Use RBAC para delimitar los permisos de la clave de API apropiadamente. Un rol "Editor" puede leer y escribir contenido pero no puede eliminar workspaces ni gestionar usuarios.

La calidad de la búsqueda depende de su contenido. Si su documentación usa terminología inconsistente, la IA encontrará resultados inconsistentes. MCP hace la búsqueda rápida, pero no arregla los problemas subyacentes del contenido.

## Primeros pasos

1. [Instale Valoryx](/install/) — binario único, sin dependencias, funcionando en menos de 2 minutos
2. Genere una clave de API desde el panel de administración
3. Añada la configuración del servidor MCP a Claude Desktop
4. Comience con un flujo de trabajo de solo lectura: busque y audite antes de habilitar las escrituras

La [documentación de MCP](/mcp/) cubre la referencia completa de la API para las 13 herramientas, incluyendo tipos de parámetros y esquemas de respuesta.

El mantenimiento de documentación no tiene que ser un proceso manual. Con un protocolo estructurado entre su asistente de IA y su plataforma de documentación, las partes tediosas — encontrar contenido obsoleto, verificar consistencia, hacer actualizaciones mecánicas — se convierten en algo que puede delegar con confianza.
