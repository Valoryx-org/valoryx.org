---
title: Primeros pasos
description: Instale DocPlatform, cree su primer workspace y comience a escribir documentación en menos de 10 minutos.
weight: 1
---

# Primeros pasos

Esta sección le guía a través de la instalación de DocPlatform, su primera ejecución y la creación de un workspace donde su equipo pueda empezar a escribir.

## Elija su camino

| Camino | Tiempo | Ideal para |
|---|---|---|
| [Inicio rápido](quickstart.md) | 5 minutos | Evaluar el producto rápidamente — un solo comando, verlo en funcionamiento |
| [Instalación](installation.md) | 10 minutos | Configuración completa — elija su método (binario, Docker, código fuente), entienda lo que sucede |
| [Su primer workspace](first-workspace.md) | 10 minutos | Ya está en ejecución — aprenda a crear workspaces, conectar git e invitar a su equipo |

## Antes de comenzar

DocPlatform no tiene dependencias externas. No necesita instalar una base de datos, un motor de búsqueda ni un runtime de Node.js. El binario único incluye todo.

**Dependencias opcionales:**

- **Git 2.30+** — solo necesario si desea sincronizar con un repositorio git remoto
- **Clave SSH** — solo necesaria para repositorios git privados a través de SSH
- **Servidor SMTP** — solo necesario para invitaciones por correo electrónico y restablecimiento de contraseña (sin SMTP, los tokens de restablecimiento se imprimen en stdout)

## Arquitectura de un vistazo

Cuando ejecuta `docplatform serve`, se inicia un solo proceso que incluye:

- **Servidor HTTP** — sirve el editor web y la API en el puerto 3000
- **Base de datos SQLite** — almacena usuarios, workspaces, metadatos de páginas y registros de auditoría
- **Motor de búsqueda Bleve** — indexa todo el contenido para búsqueda instantánea de texto completo
- **Motor git** — sincroniza contenido bidireccionalmente con repositorios remotos
- **Frontend estático** — el editor web Next.js, integrado en el binario

Todos los datos residen en un solo directorio (por defecto: `.docplatform/`), lo que facilita las copias de seguridad y migraciones — solo copie el directorio.
