---
title: "Documentación para Proyectos de Código Abierto"
description: "Los mantenedores de OSS necesitan documentación pero no pueden pagar herramientas de pago. Cómo configurar documentación gratuita y autoalojada con sincronización git en menos de 5 minutos."
date: "2026-04-06"
author: "Equipo Valoryx"
tags: ["open-source", "documentation", "free", "tutorial"]
---

Los proyectos de código abierto viven o mueren por su documentación. Una biblioteca con buena documentación se adopta. Una biblioteca con un README básico y una actitud de "mire el código" es bifurcada por alguien que escribe mejor documentación — o simplemente ignorada.

Pero la mayoría de las herramientas de documentación están construidas para empresas, no para mantenedores de OSS. Cobran por usuario, por página o por workspace. Para un proyecto mantenido por voluntarios con presupuesto cero, eso es inaceptable.

Construimos la Community Edition de DocPlatform para ser gratuita para siempre, sin límites. Usuarios ilimitados, páginas ilimitadas, workspaces ilimitados. Sin "plan gratuito" que le empuje a actualizar — la Community Edition es el producto completo sin alojamiento en la nube. Así es como configurarlo para su proyecto de código abierto.

## La configuración típica de documentación OSS

La mayoría de los proyectos de código abierto terminan con uno de estos enfoques:

**GitHub Pages + generador de sitios estáticos.** Escribe archivos markdown, configura un pipeline de compilación y despliega en GitHub Pages. El stack más común es [Docusaurus](https://docusaurus.io/) (basado en React) o MkDocs (basado en Python).

**Ventajas:** Alojamiento gratuito, contenido con control de versiones, flujo de trabajo git familiar.

**Desventajas:** Sin editor web (los contribuidores deben conocer git, markdown y el sistema de compilación), sin vista previa en tiempo real, sin búsqueda sin servicios de terceros (Algolia DocSearch tiene lista de espera y proceso de aprobación), sin funcionalidades de colaboración.

**Plataforma alojada con plan gratuito.** GitBook, ReadMe o Notion con una página pública. Obtiene un editor web y búsqueda alojada.

**Ventajas:** Fácil de empezar, el editor web reduce la barrera para contribuidores no técnicos.

**Desventajas:** Los planes gratuitos son limitados (GitBook: 1 espacio, integraciones limitadas; ReadMe: referencias de API limitadas). Su contenido vive en el servidor de alguien más. Si cambian los precios o cierran, estará migrando bajo presión.

**Markdown puro en el repositorio.** Una carpeta `docs/` con archivos markdown. Sin paso de compilación, sin alojamiento, sin búsqueda.

**Ventajas:** Cero configuración. Contenido con control de versiones.

**Desventajas:** Los usuarios no pueden navegar la documentación sin ir a GitHub. Sin búsqueda. Sin estructura de navegación más allá de los nombres de archivo.

## Un mejor enfoque

DocPlatform le da lo mejor de los tres: contenido almacenado como markdown en su repositorio git, un editor web para contribuidores no técnicos, búsqueda de texto completo y un sitio de documentación publicado — todo desde un único binario que puede alojar en cualquier lugar.

Esta es la configuración.

### Paso 1: Instalar DocPlatform

En cualquier máquina Linux, macOS o Windows:

```bash
curl -fsSL https://get.valoryx.org | sh
```

O descargue el binario directamente desde la [página de instalación](/install/). No hay nada más que instalar — sin base de datos, sin Docker, sin runtime.

### Paso 2: Iniciar el servidor

```bash
docplatform serve
```

Abra `http://localhost:3000`. Cree su cuenta de administrador. Eso es su servidor funcionando.

Para una configuración permanente, use un servicio systemd:

```ini
[Unit]
Description=DocPlatform
After=network.target

[Service]
ExecStart=/opt/docplatform/bin/docplatform serve
WorkingDirectory=/opt/docplatform
Restart=always

[Install]
WantedBy=multi-user.target
```

### Paso 3: Crear un workspace

Un workspace en DocPlatform es un proyecto de documentación. Para un proyecto de código abierto, típicamente tendrá un workspace para su documentación pública.

1. Vaya a Settings → Workspaces → Create
2. Nómbrelo con el nombre de su proyecto (ej., "MyProject Docs")
3. Elija un tema — hay 7 temas integrados, todos diseñados para documentación técnica

### Paso 4: Conectar su repositorio de GitHub

Aquí es donde se pone interesante. DocPlatform soporta sincronización bidireccional con git — las ediciones realizadas en la interfaz web se hacen commit en su repositorio, y los cambios enviados al repositorio aparecen en la interfaz.

1. Vaya a Workspace Settings → Git Sync
2. Añada la URL de su repositorio: `https://github.com/yourorg/yourproject.git`
3. Configure la ruta de documentación (ej., `docs/` si su markdown vive en una subcarpeta)
4. Añada una clave de despliegue o token de acceso personal para acceso de escritura

Una vez conectado, DocPlatform obtiene sus archivos markdown existentes y los indexa para búsqueda. Cualquier archivo `.md` en la ruta configurada se convierte en una página.

### Paso 5: Publicar su documentación

Active "Publish" en la configuración del workspace. DocPlatform genera un sitio de documentación navegable con:

- Árbol de navegación basado en la estructura de carpetas
- Búsqueda de texto completo con tolerancia a errores tipográficos
- Diseño responsivo que funciona en móvil
- Resaltado de sintaxis para bloques de código
- Modo oscuro

Su documentación publicada es accesible en `http://yourserver:3000/docs/workspace-slug/`.

## El flujo de trabajo git

Así es como se ve el flujo de trabajo en la práctica para un proyecto de código abierto con múltiples contribuidores:

**Los mantenedores** usan el editor web para correcciones rápidas — correcciones de errores tipográficos, reestructuración de páginas, actualización de capturas de pantalla. Cada guardado crea un commit de git automáticamente.

**Los contribuidores externos** envían PRs al directorio de documentación en su repositorio de GitHub, exactamente como lo harían con el código. Cuando fusiona el PR, DocPlatform recoge los cambios vía sincronización git y actualiza el sitio publicado.

**Los contribuidores no técnicos** (community managers, escritores técnicos) usan el editor WYSIWYG en el navegador. No necesitan conocer git ni la sintaxis de markdown. Sus ediciones igualmente se hacen commit en el repositorio.

Esto significa que su documentación tiene el mismo proceso de revisión que su código. ¿Quiere que alguien revise un cambio de documentación antes de que se publique? Que envíe un PR. ¿Quiere permitir que contribuidores de confianza editen directamente? Déles acceso de editor en DocPlatform.

## Comparación: DocPlatform vs. Docusaurus

Dado que Docusaurus es la herramienta de documentación OSS más popular, aquí tiene una comparación directa:

| Funcionalidad | Docusaurus | DocPlatform CE |
|---|---|---|
| Editor web | No — editar markdown, commit, esperar la compilación | Sí — WYSIWYG, cambios en vivo inmediatamente |
| Búsqueda | Requiere Algolia DocSearch (lista de espera) o Lunr.js (del lado del cliente, limitado) | Búsqueda de texto completo integrada (Bleve) |
| Paso de compilación | Sí — compilación React, puede tomar 30+ segundos | No — las páginas se renderizan al guardar |
| Integración git | Nativa (es un generador de sitios estáticos) | Sincronización bidireccional (web ↔ git) |
| Múltiples versiones | Sí (documentación versionada) | Basado en workspaces (un workspace por versión) |
| Tiempo de configuración | 10-30 minutos (Node.js, npm, configuración) | 2 minutos (descargar binario, ejecutar) |
| Alojamiento | GitHub Pages, Netlify, Vercel (gratis) | Autoalojado (necesita un servidor) |
| RBAC | Ninguno (es una herramienta de compilación) | 5 roles (admin, manager, editor, reviewer, viewer) |
| i18n | Basado en plugins | Basado en workspaces |

Docusaurus gana si desea alojamiento sin costo en GitHub Pages y todos sus contribuidores se sienten cómodos con git y React. DocPlatform gana si desea un editor web, búsqueda integrada, control de acceso, o si sus contribuidores no son todos desarrolladores.

## Alojamiento con presupuesto

Una objeción común: "Docusaurus es gratis porque GitHub Pages lo aloja. Autoalojado significa que necesito un servidor."

Cierto. Pero los servidores son económicos:

- **Hetzner CX22:** 2 vCPU, 4GB RAM, 40GB disco — EUR 3.99/mes
- **Oracle Cloud Free Tier:** instancia ARM, 24GB RAM — gratis para siempre
- **Portátil viejo en un armario:** Gratis si ya tiene uno

DocPlatform usa aproximadamente 50MB de RAM en reposo y 100-200MB bajo carga. Cualquier servidor que pueda ejecutar un binario de Go puede ejecutarlo.

Si ya está ejecutando un servidor de CI, un bot de Discord u otro servicio para su proyecto, DocPlatform puede ejecutarse en la misma máquina.

## Configuración real: de cero a documentación publicada

Veamos un ejemplo concreto. Usted mantiene una herramienta CLI llamada `fastgrep` y quiere pasar de un README a documentación completa.

```bash
# Instalar DocPlatform
curl -fsSL https://get.valoryx.org | sh

# Iniciar el servidor
docplatform serve &

# Abrir navegador, crear cuenta de admin, crear workspace
# Conectar a github.com/yourname/fastgrep, ruta de docs: docs/

# Crear sus primeras páginas en el editor web:
# - Primeros Pasos
# - Instalación
# - Configuración
# - Referencia CLI
# - Contribuir
```

Cada página que cree en el editor web se hace commit en `docs/` en su repositorio. Sus archivos markdown existentes en `docs/` (si los hay) se importan automáticamente.

Publique el workspace, apunte su dominio al servidor, y su proyecto tiene documentación con búsqueda y editor web — configurado en menos de 5 minutos.

Para la configuración completa de publicación, consulte la [guía de publicación](/docs/guides/publishing/).

## Gratuito significa gratuito

La [Community Edition](/open-source/) no es una prueba. No es un plan gratuito limitado. Es el producto completo:

- Usuarios y editores ilimitados
- Workspaces y páginas ilimitados
- Búsqueda de texto completo
- Sincronización git
- RBAC con 5 roles
- Los 7 temas
- Autenticación WebAuthn/passkey
- Servidor MCP con 26 herramientas de IA

Lo único que la Community Edition no incluye es alojamiento en la nube — usted lo ejecuta en su propia infraestructura. Para proyectos de código abierto que ya gestionan su propia infraestructura, eso no es una limitación; es una ventaja.

[Descargue DocPlatform](/install/) y dele a su proyecto la documentación que merece.
