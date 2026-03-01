---
title: Búsqueda
description: Búsqueda instantánea de texto completo en toda su documentación con resultados filtrados por permisos.
weight: 6
---

# Búsqueda

DocPlatform incluye un motor de búsqueda de texto completo integrado (Bleve) que indexa todo el contenido automáticamente. Sin servicio externo que configurar — la búsqueda funciona de forma inmediata.

## Uso de la búsqueda

### Diálogo Cmd+K

Presione `Cmd+K` (macOS) o `Ctrl+K` (Windows/Linux) en cualquier lugar del editor web para abrir el diálogo de búsqueda.

```
┌──────────────────────────────────────────┐
│  🔍  Search documentation...             │
├──────────────────────────────────────────┤
│                                          │
│  📄 Getting Started                      │
│     Install and configure DocPlatform... │
│                                          │
│  📄 API Authentication                   │
│     JWT tokens, OAuth2, and session...   │
│                                          │
│  📄 Docker Deployment                    │
│     Run DocPlatform as a container...    │
│                                          │
│  ↑↓ Navigate   ↵ Open   Esc Close       │
└──────────────────────────────────────────┘
```

### Qué se indexa

El motor de búsqueda indexa:

- **Título de la página** (peso aumentado para clasificación)
- **Descripción de la página** (peso aumentado)
- **Contenido completo de la página** (texto del cuerpo, bloques de código, listas, etc.)
- **Etiquetas** (aumento por coincidencia exacta)
- **Metadatos de frontmatter**

### Sintaxis de búsqueda

| Sintaxis | Ejemplo | Descripción |
|---|---|---|
| Palabras clave | `git sync` | Páginas que contienen tanto "git" como "sync" |
| Frase exacta | `"bidirectional sync"` | Páginas con la frase exacta |
| Prefijo | `auth*` | Páginas con palabras que comienzan con "auth" |
| Filtro por etiqueta | `tag:api` | Páginas etiquetadas con "api" |

## Filtrado por permisos

Los resultados de búsqueda se filtran automáticamente según los permisos del usuario actual:

- **Páginas públicas** — visibles en los resultados de búsqueda para todos los usuarios autenticados
- **Páginas del workspace** — visibles solo para miembros del workspace
- **Páginas restringidas** — visibles solo para usuarios con el rol requerido

Un Viewer no puede encontrar páginas restringidas solo para administradores a través de la búsqueda, incluso si el contenido coincide con su consulta. Este filtrado ocurre a nivel del motor de búsqueda, no después de la consulta.

## Indexación

### Indexación automática

El contenido se indexa incrementalmente mediante una cola de trabajos asíncrona:

1. Se crea o actualiza una página (mediante el editor o sincronización git)
2. El Content Ledger emite un evento
3. Se encola un trabajo de indexación de búsqueda
4. El indexador Bleve procesa el trabajo y actualiza el índice

Hay un breve retraso (típicamente menos de 1 segundo) entre guardar una página y que el contenido actualizado aparezca en los resultados de búsqueda.

### Reconstruir el índice de búsqueda

Si el índice de búsqueda se desincroniza (raro — generalmente después de un fallo o manipulación manual de archivos), reconstrúyalo:

```bash
docplatform rebuild
```

Esto elimina el índice de búsqueda existente y re-indexa todas las páginas desde el sistema de archivos. El proceso se ejecuta en segundo plano — el servidor permanece disponible durante la reconstrucción.

### Salud del índice

Verifique la salud del índice de búsqueda con el comando doctor:

```bash
docplatform doctor
```

El doctor reporta:

- Número de documentos indexados vs. conteo de páginas en la base de datos
- Entradas huérfanas del índice (indexadas pero sin página correspondiente)
- Entradas faltantes del índice (página existe pero no está indexada)
- Tamaño del archivo de índice y marca de tiempo de la última actualización

## Búsqueda en documentación publicada

Los sitios de documentación publicada incluyen una interfaz de búsqueda para visitantes. La entrada de búsqueda aparece en el encabezado del sitio y usa el mismo motor Bleve.

La búsqueda del sitio público está limitada solo a páginas publicadas — el contenido no publicado o restringido nunca aparece en los resultados de búsqueda pública.

## Aspectos internos del motor de búsqueda

Para usuarios que desean comprender cómo funciona la búsqueda internamente:

### Analizador

Bleve usa el **analizador de inglés** por defecto, que incluye:

- **Tokenización** — divide el texto en espacios en blanco y puntuación
- **Conversión a minúsculas** — coincidencia sin distinción de mayúsculas/minúsculas
- **Eliminación de palabras vacías** — filtra palabras comunes (the, is, at, etc.)
- **Stemming** — coincide con variantes de palabras (running → run, documented → document)

### Ponderación de campos

No todos los campos tienen el mismo peso en la puntuación de relevancia:

| Campo | Peso | Descripción |
|---|---|---|
| `title` | Alto | Título de la página (señal más relevante) |
| `description` | Alto | Descripción / resumen de la página |
| `tags` | Coincidencia exacta | Campo de palabras clave — coincidencias exactas de etiquetas aumentadas |
| `body` | Normal | Contenido completo de la página |
| `path` | Palabra clave | Ruta del archivo — solo coincidencia exacta |

Esto significa que una consulta que coincide con el título de una página tiene mayor clasificación que la misma consulta coincidiendo profundamente en el texto del cuerpo.

### Almacenamiento

El índice Bleve se almacena en `{DATA_DIR}/search-index/` usando bbolt (una base de datos B+ tree de Go puro). El índice es independiente de la base de datos SQLite y puede eliminarse y reconstruirse de forma segura con `docplatform rebuild`.

## Rendimiento

| Métrica | Valor |
|---|---|
| **Latencia de consulta** | < 8ms (p99) |
| **Tamaño del índice** | ~1 KB por página (aproximado) |
| **Máximo corpus probado** | 1.000 páginas |
| **Consultas concurrentes** | Soportadas (thread-safe) |
| **Latencia de indexación** | < 1 segundo después de guardar (asíncrono) |

El rendimiento de búsqueda escala linealmente con el volumen de contenido. Para workspaces que excedan 10.000 páginas, una versión futura ofrecerá integración opcional con Meilisearch.
