---
title: "Autoaloje Su Documentación en 5 Minutos"
description: "Un tutorial paso a paso: descargue DocPlatform, ejecute un solo binario, cree su primer workspace y publique documentación. Sin Docker, sin base de datos."
date: "2026-03-02"
author: "Equipo Valoryx"
tags: ["self-hosted", "tutorial", "documentation"]
---

La mayoría de las herramientas de documentación autoalojadas requieren una base de datos, un proxy inverso y media tarde de edición de YAML antes de ver una pantalla de bienvenida. DocPlatform es un único binario de Go sin dependencias externas. Este tutorial le lleva desde cero hasta documentación publicada en aproximadamente cinco minutos.

## Requisitos previos

Necesita una máquina con Linux, macOS o Windows. Eso es todo. Sin Docker, sin PostgreSQL, sin runtime de Node.js. DocPlatform se compila en un único binario estático — el runtime de Go está integrado. Si tiene curiosidad sobre el lenguaje de implementación, [Go](https://go.dev/) produce ejecutables autocontenidos que funcionan sin instalar nada en el host.

## Paso 1: Descargar e instalar

En Linux o macOS, el script de instalación se encarga de todo:

```bash
curl -fsSL https://valoryx.org/install.sh | bash
```

Esto descarga el binario de la última versión a `/usr/local/bin/docplatform` (o `~/.local/bin/` si no tiene acceso root). En macOS con Homebrew, también puede ejecutar:

```bash
brew install valoryx/tap/docplatform
```

En Windows, descargue el `.exe` desde la [página de descargas](/install/) y añádalo a su PATH.

Verifique la instalación:

```bash
docplatform version
# DocPlatform v1.x.x (linux/amd64)
```

## Paso 2: Iniciar el servidor

Ejecute el servidor con la configuración predeterminada:

```bash
docplatform serve
```

Verá una salida como esta:

```
INFO  Starting DocPlatform server
INFO  Data directory: ./data
INFO  Listening on http://localhost:3000
INFO  Full-text search index: ready
INFO  Admin setup required — visit http://localhost:3000 to create your account
```

Abra `http://localhost:3000` en su navegador. DocPlatform sirve tanto el editor como el sitio publicado desde el mismo binario en el mismo puerto. Sin paso de compilación de frontend separado.

En el primer inicio, verá la pantalla de configuración de administrador. Elija un nombre de usuario y contraseña. Esto crea la cuenta de super administrador — la que puede gestionar todo. Puede añadir más usuarios después a través del panel de administración.

## Paso 3: Crear su primer workspace

Después de iniciar sesión, el panel muestra una lista de workspaces vacía. Haga clic en **New Workspace** y complete:

- **Nombre:** `engineering-handbook` (o lo que esté documentando)
- **Slug:** `engineering-handbook` (esto se convierte en la ruta de la URL)
- **Tema:** Elija uno de los 5 temas integrados — puede cambiarlo después

Haga clic en **Create**. Ahora tiene un workspace con una página raíz lista para editar.

## Paso 4: Escribir documentación

Haga clic en su nuevo workspace y llegará al [editor WYSIWYG](/docs/getting-started/first-workspace/). Soporta atajos de markdown — escriba `##` seguido de un espacio para crear un H2, use acentos graves para código en línea, triple acento grave para bloques de código. Todo lo que esperaría de un editor moderno, pero renderizado como texto enriquecido mientras escribe.

Cree algunas páginas para familiarizarse:

1. Haga clic en **New Page** en la barra lateral
2. Dele un título: "Primeros Pasos"
3. Escriba contenido — pegue markdown existente si lo tiene
4. Presione **Ctrl+S** (o Cmd+S en macOS) para guardar

La página se guarda en la base de datos SQLite local de DocPlatform (integrada en el binario — sin base de datos externa que gestionar). Cada guardado crea una versión a la que puede regresar.

Pruebe a crear una página hija: pase el cursor sobre "Primeros Pasos" en la barra lateral y haga clic en el icono **+**. Ahora tiene una jerarquía de páginas.

## Paso 5: Publicar su documentación

Para hacer su documentación accesible públicamente, vaya a **Workspace Settings > Publishing** y active el estado de publicación a **On**. Su documentación ahora está disponible en:

```
http://localhost:3000/s/engineering-handbook
```

El prefijo `/s/` sirve la vista publicada de solo lectura. Usa el tema que seleccionó, tiene búsqueda de texto completo impulsada por Bleve, e incluye un árbol de navegación lateral construido a partir de su jerarquía de páginas.

Eso es todo. Cinco comandos, sin archivos de configuración, y tiene un sitio de documentación funcionando.

## Qué está ejecutándose internamente

Cuando ejecutó `docplatform serve`, inició un único proceso que maneja:

- **Servidor HTTP** — sirve la interfaz del editor, la API y el sitio de documentación publicado
- **Base de datos SQLite** — almacena usuarios, workspaces, páginas y versiones
- **Índice de búsqueda Bleve** — búsqueda de texto completo con tolerancia a errores tipográficos y clasificación por relevancia
- **Autenticación WebAuthn/passkey** — autenticación moderna sin contraseña junto con usuario/contraseña tradicional
- **RBAC** — 5 roles (super admin, admin, editor, visor, invitado) con permisos granulares

Todo esto se ejecuta en un único proceso usando aproximadamente 50–80 MB de RAM. Sin workers en segundo plano, sin colas de mensajes, sin microservicios.

## Paso 6: Conectar Git (opcional)

Si desea que su documentación se almacene en un repositorio git — con control de versiones, revisable, editable desde su IDE — DocPlatform soporta sincronización bidireccional con git. Lea la [guía de inicio rápido](/docs/getting-started/quickstart/) para la configuración completa, pero la versión corta es:

1. Vaya a **Workspace Settings > Git Sync**
2. Pegue la URL de su repositorio y la clave de despliegue
3. Elija una rama
4. Haga clic en **Enable Sync**

A partir de ese momento, cada guardado en el editor crea un commit de git, y cada push al repositorio desde un IDE o pipeline de CI se refleja en el editor. Esto no es un espejo unidireccional — es verdadera sincronización bidireccional usando el patrón Content Ledger (consulte [Por Qué las Herramientas de Documentación con Git Rompen la Sincronización](/blog/why-git-sync-breaks/) para la explicación técnica).

## Ejecución en producción

Para un despliegue en producción, querrá configurar algunas variables de entorno:

```bash
export DOCPLATFORM_PORT=3000
export DOCPLATFORM_DATA_DIR=/var/lib/docplatform
export DOCPLATFORM_BASE_URL=https://docs.yourcompany.com

docplatform serve
```

Colóquelo detrás de un proxy inverso (Nginx, Caddy o Cloudflare Tunnel) para la terminación HTTPS. Use una unidad systemd o similar para mantenerlo en ejecución:

```ini
[Unit]
Description=DocPlatform Documentation Server
After=network.target

[Service]
ExecStart=/usr/local/bin/docplatform serve
WorkingDirectory=/var/lib/docplatform
Restart=always
User=docplatform

[Install]
WantedBy=multi-user.target
```

Haga copias de seguridad del directorio de datos periódicamente — contiene la base de datos SQLite y el índice de búsqueda. Un simple `cp` o `rsync` mientras el servidor está ejecutándose funciona bien (SQLite maneja lecturas concurrentes).

## Próximos pasos

Ahora tiene una plataforma de documentación funcionando. Aquí tiene hacia dónde continuar:

- [Guía completa de inicio rápido](/docs/getting-started/quickstart/) — cubre sincronización git, temas y gestión de usuarios
- [Creando su primer workspace](/docs/getting-started/first-workspace/) — configuración detallada del workspace
- [Opciones de instalación](/install/) — todos los métodos de descarga, incluyendo builds para ARM

La Community Edition de DocPlatform es gratuita, sin límites de usuarios, sin límites de páginas y sin restricciones de funcionalidades. Descargue el binario y comience a escribir. Todo lo que necesita viene en ese único archivo.
