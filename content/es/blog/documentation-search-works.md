---
title: "Cómo Funciona Realmente la Búsqueda en Documentación"
description: "La mayoría de las herramientas de documentación usan coincidencia básica de palabras clave o requieren Elasticsearch. DocPlatform integra Bleve para búsqueda de texto completo con stemming y coincidencia difusa — sin servicios adicionales."
date: "2026-04-02"
author: "Equipo Valoryx"
tags: ["search", "architecture", "documentation"]
---

Usted escribe una consulta en la barra de búsqueda de su documentación. Aparecen resultados. Pero, ¿qué sucedió entre la pulsación de tecla y los resultados? Para la mayoría de las plataformas de documentación, la respuesta es "no mucho" (coincidencia básica de palabras clave que no encuentra resultados obvios) o "mucha infraestructura" (un clúster de Elasticsearch que su equipo de operaciones tiene que mantener).

Hay un punto intermedio que la mayoría de los equipos desconoce: la búsqueda de texto completo embebida. DocPlatform usa [Bleve](https://blevesearch.com/), una biblioteca de búsqueda escrita en Go, compilada directamente en el binario. Sin servicios externos, sin llamadas de red, sin clúster que gestionar — pero con las funcionalidades que realmente necesita: stemming, coincidencia difusa, ponderación de campos y clasificación por relevancia.

Así es como funciona desde la base.

## Por qué falla la coincidencia de palabras clave

La implementación de búsqueda más simple es `LIKE '%query%'` en SQL. Es lo que obtiene cuando un desarrollador añade búsqueda como algo secundario. Funciona para coincidencias exactas pero falla en todos los demás casos:

- Buscar "install" no encuentra páginas que contengan "installation" o "installing"
- Buscar "authn" no encuentra páginas sobre "authentication"
- Un error tipográfico como "deploymnet" no devuelve nada
- Todos los resultados tienen la misma clasificación — una página titulada "Installation Guide" se clasifica igual que una página que menciona "install" una vez en el pie de página

Algunas plataformas mejoran esto con la extensión FTS5 de SQLite, que añade tokenización y clasificación básica. Es un paso adelante, pero todavía carece de stemming, coincidencia difusa y la capacidad de ponderar ciertos campos (como títulos) sobre otros.

## Qué hace realmente la búsqueda de texto completo

Un motor de búsqueda adecuado procesa texto en dos fases: indexación (cuando se escribe el contenido) y consulta (cuando alguien busca). Ambas fases hacen más trabajo del que esperaría.

### Indexación: qué sucede cuando guarda una página

Cuando crea o actualiza una página en DocPlatform, el contenido pasa por un pipeline de análisis antes de ser indexado:

**1. Tokenización** — El texto se divide en términos individuales. "Getting started with DocPlatform" se convierte en `["getting", "started", "with", "docplatform"]`.

**2. Conversión a minúsculas** — Todos los tokens se normalizan a minúsculas. "DocPlatform" y "docplatform" coinciden.

**3. Eliminación de palabras vacías** — Palabras comunes como "the", "is", "with", "a" se eliminan. Aparecen en casi todos los documentos y no ayudan a distinguir resultados relevantes.

**4. Stemming** — Las palabras se reducen a su forma raíz. "installing", "installation" e "installed" todas se convierten en "instal". Esto significa que una búsqueda de cualquiera de estas palabras encuentra todas ellas.

**5. Separación de campos** — Diferentes partes del documento se indexan por separado. El título, cuerpo, etiquetas y ruta obtienen cada uno su propio campo en el índice. Esto habilita la ponderación de campos en tiempo de consulta.

El índice resultante es una estructura de datos llamada índice invertido — un mapa de cada término a la lista de documentos que lo contienen, junto con información posicional (dónde en el documento aparece el término y con qué frecuencia).

```
"instal"     → [doc_3 (title, pos:0), doc_7 (body, pos:45), doc_12 (body, pos:102)]
"deploy"     → [doc_3 (body, pos:23), doc_5 (title, pos:0)]
"kubernetes" → [doc_5 (body, pos:15), doc_5 (body, pos:89)]
```

### Consulta: qué sucede cuando busca

Cuando un usuario escribe una consulta, el motor de búsqueda ejecuta el mismo pipeline de análisis en el texto de la consulta (tokenizar, minúsculas, stemming), luego busca cada término en el índice invertido.

Pero el valor real está en la clasificación. No todas las coincidencias son iguales. Bleve usa una variante de TF-IDF (frecuencia de término, frecuencia inversa de documento) combinada con ponderación de campos para producir una puntuación de relevancia:

- **Frecuencia de término:** Una página que menciona "deployment" 10 veces probablemente es más relevante que una que lo menciona una vez.
- **Frecuencia inversa de documento:** Un término que aparece en solo 3 de 500 documentos es más distintivo (y más útil para clasificar) que un término que aparece en 400 documentos.
- **Ponderación de campo:** Una coincidencia en el título vale más que una coincidencia en el cuerpo. En DocPlatform, las coincidencias en el título obtienen un multiplicador de 3x, las de etiquetas 2x y las del cuerpo 1x.

La fórmula produce una puntuación numérica para cada documento que coincide, y los resultados se devuelven ordenados por puntuación.

## Coincidencia difusa: manejando errores tipográficos

Los usuarios reales cometen errores tipográficos. "Kuberntes" en lugar de "Kubernetes." "Authentcation" en lugar de "Authentication." La búsqueda básica no devuelve nada para estas consultas.

Bleve soporta coincidencia difusa usando distancia de edición (distancia de Levenshtein). Un término de consulta coincide con un término del documento si difieren en N o menos operaciones de caracteres (inserciones, eliminaciones, sustituciones). DocPlatform usa una distancia de edición de 1 por defecto — suficiente para detectar errores tipográficos de un solo carácter sin producir demasiados falsos positivos.

```
Consulta: "authentcation"
Distancia de edición 1: coincide con "authentication" (falta una 'i')
Resultados: todos los documentos que contienen "authentication"
```

Esto sucede de forma transparente. Los usuarios no necesitan saber sobre coincidencia difusa ni configurar nada. Simplemente buscan y obtienen resultados incluso cuando escriben mal.

## Cómo DocPlatform mantiene el índice sincronizado

La parte complicada de la búsqueda embebida no es la búsqueda en sí — es mantener el índice consistente con el contenido. DocPlatform tiene dos fuentes de contenido: el editor web y git. Ambos pueden crear, actualizar y eliminar páginas.

Este es el flujo de indexación:

**Guardado del editor web:** El usuario hace clic en guardar → el contenido se escribe en la base de datos → el indexador de búsqueda actualiza el índice Bleve → el motor de sincronización git hace commit del cambio.

**Push de git recibido:** Se dispara el webhook de git → el motor de sincronización obtiene los cambios → las páginas nuevas/modificadas se escriben en la base de datos → el indexador de búsqueda actualiza el índice Bleve.

**Operaciones masivas:** Cuando importa un repositorio con cientos de archivos markdown, el indexador los procesa en lotes. Una importación de 500 páginas toma aproximadamente 3 segundos en indexarse completamente en hardware modesto.

**Eliminaciones:** Cuando se elimina una página (desde la interfaz web o git), el documento correspondiente se elimina del índice Bleve. Sin resultados de búsqueda huérfanos.

El detalle importante: la indexación es síncrona con la operación de escritura. Cuando el guardado/sincronización se completa, el índice de búsqueda ya está actualizado. No hay demora de "esperar la reindexación". Esto es posible porque Bleve se ejecuta en el mismo proceso — no hay salto de red a un clúster de Elasticsearch separado.

Para más información sobre cómo funciona el motor de sincronización, consulte nuestro artículo sobre [por qué la sincronización git se rompe](/blog/why-git-sync-breaks/) y el patrón Content Ledger que lo resuelve.

## Comparación: búsqueda embebida vs. externa

| Capacidad | SQL LIKE | SQLite FTS5 | Bleve (embebido) | Elasticsearch |
|---|---|---|---|---|
| Tokenización | No | Sí | Sí | Sí |
| Stemming | No | Limitado | Sí | Sí |
| Coincidencia difusa | No | No | Sí | Sí |
| Ponderación de campos | No | No | Sí | Sí |
| Clasificación por relevancia | No | Básica | TF-IDF | BM25 |
| Servicio adicional | No | No | No | Sí |
| Sobrecarga de memoria | Ninguna | ~1MB | ~10MB | 1-4 GB (JVM) |
| Complejidad operativa | Ninguna | Ninguna | Ninguna | Alta |

Elasticsearch gana en funcionalidades avanzadas: agregaciones, consultas de documentos anidados, analizadores personalizados, búsqueda distribuida en clústeres. Si está construyendo un producto de búsqueda, probablemente lo necesite.

Pero para búsqueda de documentación — donde el corpus son miles de páginas, no millones de registros — Bleve embebido cubre los requisitos con cero sobrecarga operativa. No necesita un clúster separado para buscar en su documentación.

Como cubrimos en [el artículo sobre la arquitectura de binario único](/blog/single-binary-architecture/), mantener todo en un proceso elimina toda una clase de problemas operativos.

## Qué buscan realmente los usuarios

Construimos nuestra configuración de búsqueda en torno a cómo la gente realmente busca en la documentación:

**Nombres exactos de funcionalidades:** "RBAC", "WebAuthn", "git sync" — estos necesitan coincidir precisamente en títulos y etiquetas.

**Consultas conceptuales:** "cómo configurar permisos" — estas dependen del stemming y la coincidencia en el texto del cuerpo.

**Recuerdo parcial:** "esa página sobre despliegue..." — la coincidencia difusa y la ponderación de títulos ayudan a mostrar el resultado correcto incluso con consultas incompletas.

**Mensajes de error:** Los usuarios pegan mensajes de error en la búsqueda. Estos se benefician de la coincidencia exacta con secuencias largas de tokens.

La configuración predeterminada maneja bien todos estos casos. Sin ajustes requeridos.

## Pruébelo

Si desea ver esto en acción, [instale DocPlatform](/install/) y cree algunas páginas. La barra de búsqueda en el sitio de documentación publicado usa exactamente el sistema descrito aquí. Escriba una consulta, cometa un error tipográfico intencionalmente, y observe cómo aún encuentra lo que necesita.

La Community Edition incluye capacidades completas de búsqueda — sin restricciones de funcionalidades, sin "actualice para mejor búsqueda." La [guía de configuración de búsqueda](/docs/guides/search/) cubre los detalles de personalización del comportamiento de búsqueda si lo necesita.
