---
title: "Cómo Funciona la Sincronización Bidireccional con Git"
description: "La mayoría de las herramientas de documentación afirman tener integración con git pero fallan con los conflictos. Así es como el patrón Content Ledger hace confiable la verdadera sincronización bidireccional."
date: "2026-03-19"
author: "Equipo Valoryx"
tags: ["git-sync", "architecture", "documentation"]
---

Toda plataforma de documentación con una página de integración con git hace la misma promesa: su documentación vive en git, su equipo edita en el navegador y todo se mantiene sincronizado. En la práctica, la mayoría de estas integraciones son espejos unidireccionales que se rompen en el momento en que dos personas editan desde direcciones diferentes.

Escribimos sobre [por qué esto sucede](/blog/why-git-sync-breaks/) en un artículo anterior. Este profundiza en la solución: cómo Valoryx implementa la sincronización bidireccional usando el patrón Content Ledger, y por qué este enfoque maneja los escenarios que rompen otras herramientas.

## El problema central

Un editor web y un repositorio git tienen modelos de consistencia fundamentalmente diferentes.

En un editor web, los guardados son inmediatos y atómicos. Usted hace clic en guardar, el contenido se persiste y cualquiera que cargue la página ve su versión. No hay concepto de "staging" o "commit" — la escritura es la publicación.

En git, los cambios se agrupan en commits, los commits se envían a un remoto y el remoto debe ser consultado y fusionado por otros participantes. Hay un retraso inherente entre "hice un cambio" y "todos ven mi cambio".

Cuando combina ambos modelos — un editor web y un repositorio git apuntando al mismo contenido — crea una ventana donde dos personas pueden hacer ediciones conflictivas sin saberlo. La Persona A edita en el navegador. La Persona B envía un commit desde VS Code. Ninguno sabe del otro hasta que se ejecuta la sincronización, y entonces algo tiene que ceder.

La mayoría de las plataformas manejan esto eligiendo un ganador: o la base de datos siempre gana (Wiki.js) o el repositorio git siempre gana (la mayoría de los generadores de sitios estáticos). Ambos enfoques pierden datos silenciosamente.

## El patrón Content Ledger

El Content Ledger es un registro de solo adición de cada mutación de contenido, independientemente de dónde se originó. Piense en él como un write-ahead log en una base de datos, pero para ediciones de documentación.

Cada cambio — ya sea que provenga del editor web, la API, una llamada a una herramienta MCP o un push de git — se registra como una entrada de ledger antes de aplicarse. Cada entrada contiene:

- **Marca de tiempo** — cuándo se hizo el cambio
- **Origen** — de dónde vino (web, git, api, mcp)
- **Ruta de la página** — qué página fue afectada
- **Operación** — crear, actualizar, mover, eliminar
- **Hash del contenido** — SHA-256 del nuevo contenido
- **Hash padre** — SHA-256 del contenido sobre el que se basó este cambio

El hash padre es la innovación clave. Crea una cadena de causalidad, similar a cómo [los commits de git referencian sus commits padre](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects). Cuando dos cambios tienen el mismo hash padre pero diferentes hashes de contenido, tiene un conflicto — y lo sabe antes de que se aplique cualquier cambio.

## Cómo funciona la sincronización: paso a paso

Esto es lo que sucede durante un ciclo de sincronización. Valoryx ejecuta esto automáticamente en un intervalo configurable (predeterminado: 30 segundos) o bajo demanda cuando un usuario lo activa.

### Paso 1: Recopilar cambios pendientes

El motor de sincronización lee todas las entradas de ledger desde la última sincronización exitosa. Estos son cambios locales que aún no se han enviado a git.

### Paso 2: Obtener cambios remotos

El motor ejecuta `git fetch` para obtener cualquier nuevo commit del repositorio remoto. Luego compara el HEAD remoto con el puntero de sincronización local para identificar cambios entrantes.

### Paso 3: Reconciliar

Para cada página que tiene cambios en ambos lados (entradas de ledger locales Y commits de git remotos), el motor verifica los hashes padre:

- **Sin superposición:** El cambio local se basó en la misma versión que tiene git. Merge fast-forward — aplicar ambos cambios en orden.
- **Divergente, sin conflicto:** Ambos lados cambiaron páginas diferentes. Aplicar ambos conjuntos de cambios independientemente.
- **Divergente, misma página:** Ambos lados cambiaron la misma página. Este es un conflicto real.

### Paso 4: Resolución de conflictos

Cuando se detecta un conflicto genuino, Valoryx no elige silenciosamente un ganador. En su lugar:

1. Preserva ambas versiones en el ledger
2. Marca la página como "en conflicto" en la interfaz
3. Muestra un diff entre las dos versiones
4. Permite que un humano elija qué versión conservar, o las fusione manualmente

Este es el mismo modelo que `git merge` con conflictos — excepto que funciona a través de la interfaz web, para que los editores no técnicos puedan resolver conflictos sin aprender comandos de git.

### Paso 5: Commit y push

Después de la reconciliación, los cambios locales se hacen commit al repositorio git y se envían. El mensaje de commit incluye el origen de cada cambio (edición web, llamada API, etc.) para que su historial de git le diga no solo qué cambió, sino cómo.

## Cómo se ve esto en la práctica

Considere este escenario real. Un desarrollador actualiza la documentación de autenticación de API desde VS Code y hace push al repositorio. Mientras tanto, un escritor técnico edita la introducción de la misma página en el editor web de Valoryx.

Con una herramienta de sincronización unidireccional, una edición sobrescribe la otra. Con el Content Ledger:

1. El push del desarrollador crea un cambio remoto (nuevo commit en el lado de git)
2. El guardado del escritor crea una entrada de ledger local (nueva mutación en el lado web)
3. La sincronización se ejecuta, detecta que ambos cambios tocan la misma página
4. Los hashes padre divergen — es un conflicto real
5. La página se marca, ambas versiones se preservan
6. El escritor ve una notificación: "Esta página tiene un conflicto de sincronización" con una vista de diff
7. El escritor fusiona los cambios (el desarrollador arregló un bloque de código, el escritor reescribió la introducción — ambas ediciones son válidas)
8. La versión fusionada se hace commit y se envía

Sin pérdida de datos. Sin sobrescrituras silenciosas. La fusión ocurrió a través de una interfaz web, no un terminal.

## Comparación con enfoques unidireccionales

| Escenario | Unidireccional (BD gana) | Unidireccional (Git gana) | Content Ledger |
|----------|-------------------|---------------------|---------------|
| Edición web + push git (misma página) | Cambio de git perdido | Cambio web perdido | Conflicto detectado, ambos preservados |
| Edición web + push git (páginas diferentes) | Funciona | Funciona | Funciona |
| Ediciones web rápidas | Funciona | Funciona | Funciona (agrupadas en un solo commit) |
| Ediciones git offline, push masivo | Algunos cambios perdidos | Funciona | Funciona |
| Merge de rama git en main | Impredecible | Funciona | Funciona (trata el commit de merge como cualquier otro) |
| Renombrar/mover en web + editar en git | Desajuste de ruta, sincronización rota | Desajuste de ruta, sincronización rota | El ledger rastrea movimientos, reconcilia rutas |

La última fila importa más de lo que parece. Renombrar o mover una página en una interfaz web mientras alguien edita la ruta antigua en git es uno de los casos límite más difíciles. La mayoría de las herramientas se rinden aquí. El Content Ledger rastrea las operaciones de movimiento explícitamente, por lo que sabe que `/docs/auth.md` se convirtió en `/docs/authentication.md` y puede aplicar la edición entrante de git a la nueva ruta correcta.

## ¿Por qué no usar git directamente?

Si git es tan central en este diseño, ¿por qué no omitir el editor web y usar git directamente? Dos razones:

Primero, no todos en un equipo de documentación usan git. Los gerentes de producto, ingenieros de soporte y escritores técnicos a menudo prefieren un editor web. Forzarlos a un flujo de trabajo de git crea fricción y reduce la contribución.

Segundo, git por sí solo no le da documentación publicada. Todavía necesita una capa de renderizado, indexación de búsqueda, control de acceso y una estructura de navegación. Valoryx proporciona todo eso mientras mantiene git como la capa de almacenamiento canónica.

El Content Ledger conecta estos dos mundos. Los usuarios de git trabajan en git. Los usuarios web trabajan en el navegador. Ambos flujos de trabajo son de primera clase, y el ledger los mantiene consistentes.

## Configuración de la sincronización git

Si desea probar esto con su propio repositorio:

1. [Instale Valoryx](/install/) — binario único, sin dependencias externas
2. Cree un workspace y conéctelo a un repositorio git en la configuración del workspace
3. Configure la URL remota, la rama y el intervalo de sincronización
4. Comience a editar desde ambos lados

La [guía de integración git](/docs/guides/git-integration/) cubre la configuración completa, incluyendo configuración de claves SSH, estrategias de ramas y ajuste del intervalo de sincronización.

Para equipos que ya gestionan documentación en repositorios git, esto significa que no tienen que elegir entre una buena experiencia de edición y un flujo de trabajo nativo de git. El Content Ledger hace ambos posibles sin los compromisos que afectan a todos los demás enfoques que hemos probado.
