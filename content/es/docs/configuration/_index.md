---
title: Configuración
description: Configure DocPlatform con variables de entorno, configuración del workspace, proveedores de autenticación y permisos basados en roles.
weight: 3
---

# Configuración

DocPlatform sigue un enfoque de convención sobre configuración. Funciona con valores predeterminados razonables de forma inmediata, pero cada aspecto es configurable para despliegues en producción.

## Capas de configuración

La configuración se aplica en tres capas, de la más amplia a la más específica:

| Capa | Ámbito | Método |
|---|---|---|
| **Variables de entorno** | Toda la plataforma | Archivo `.env` o entorno del shell |
| **Configuración del workspace** | Por workspace | `.docplatform/config.yaml` |
| **Frontmatter de la página** | Por página | Bloque YAML en cada archivo `.md` |

Las capas de mayor especificidad anulan a las inferiores. Por ejemplo, `access: restricted` de una página anula el predeterminado del workspace `access: public`.

## Guías

| Guía | Qué cubre |
|---|---|
| [Variables de entorno](environment.md) | Todas las configuraciones a nivel de plataforma: puerto, directorio de datos, git, SMTP, telemetría |
| [Configuración del workspace](workspace-config.md) | Configuración por workspace: repositorio git remoto, tema, navegación, valores predeterminados de publicación |
| [Autenticación](authentication.md) | Autenticación local, proveedores OIDC (Google, GitHub), configuración JWT, políticas de contraseña |
| [Roles y permisos](permissions.md) | Jerarquía RBAC de 6 niveles, control de acceso a nivel de página, configuración de Casbin |

## Referencia rápida

Las tareas de configuración más comunes:

| Tarea | Dónde |
|---|---|
| Cambiar el puerto del servidor | Variable de entorno `PORT` |
| Conectar un repositorio git | Configuración del workspace `git_remote` |
| Habilitar inicio de sesión con Google/GitHub | Variables de entorno `OIDC_*` |
| Configurar correo electrónico (invitaciones, restablecimiento de contraseña) | Variables de entorno `SMTP_*` |
| Cambiar el rol predeterminado para nuevos usuarios | Configuración del workspace `permissions.default_role` |
| Restringir documentación publicada solo a miembros del equipo | Variable de entorno `PUBLISH_REQUIRE_AUTH=true` |
| Restringir una página a roles específicos (editor web) | Frontmatter de la página `access: restricted` |
| Desactivar telemetría | `DOCPLATFORM_TELEMETRY=off` |
