---
title: "Por Qué Todas las Herramientas de Documentación con Git Rompen la Sincronización (y Cómo Lo Resolvimos)"
description: "Todas las plataformas de documentación afirman tener integración con Git. La mayoría mienten. Aquí explicamos qué sale mal realmente y el patrón Content Ledger que por fin lo soluciona."
date: "2026-02-22"
author: "Equipo Valoryx"
tags: ["git-sync", "documentation", "architecture"]
---

Conectas tu repositorio, haces push de un commit desde el IDE y todo se rompe. Conflictos de merge. Ediciones perdidas. Reversiones silenciosas. Esto no es un bug: es un fallo de diseño fundamental.

## Las Tres Formas en Que Git Sync Falla

**1. Espejo Unidireccional.** La mayoría de las plataformas tratan Git como una copia de seguridad. Los cambios desde el IDE generan conflictos. El "Git Sync" de GitBook es el ejemplo más visible.

**2. Base de Datos Primero, Git Después.** Wiki.js almacena el contenido en la base de datos. La sincronización con Git es opcional. La base de datos siempre gana. No puedes hacer `git clone`, hacer push y ver los resultados reflejados en la interfaz.

**3. Resolución Destructiva de Conflictos.** Cuando la sincronización falla, las plataformas sobrescriben silenciosamente, crean duplicados o marcan la sincronización como "fallida".

## Por Qué Esto Es Difícil
Las interfaces web esperan escrituras atómicas e inmediatas. Git opera sobre instantáneas. La brecha temporal genera divergencia cuando dos personas editan el mismo archivo.

## El Patrón Content Ledger

Valoryx resuelve esto con un registro de eventos de solo anexado y ordenado totalmente:

- **Cada mutación es un evento** en el registro (no una escritura directa a Git o a la base de datos)
- **Los eventos se aplican a ambos destinos**: la base de datos (interfaz web) y el repositorio Git convergen al mismo estado
- **Los pushes de Git se convierten en entradas del registro** mediante webhook: la interfaz web se actualiza en segundos
- **Los conflictos son imposibles por diseño**: todas las mutaciones se serializan, sin ventana de divergencia

## En la Práctica
- Editas en el navegador → `git log` muestra el commit en segundos
- Haces push desde VS Code → la interfaz web se actualiza sin sincronización manual
- CI modifica documentación → los resultados aparecen en el editor web
- Ejecutas `git revert` → la interfaz web lo refleja de inmediato

Sin estado de sincronización. Sin interfaz de conflictos. Sin divergencia.
