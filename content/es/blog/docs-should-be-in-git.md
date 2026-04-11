---
title: "Su Documentación Debería Estar en Git. Punto."
description: "El código vive en git. La infraestructura vive en git. ¿Por qué su documentación sigue viviendo en una wiki? Un argumento a favor de la documentación con control de versiones."
date: "2026-03-09"
author: "Equipo Valoryx"
tags: ["git", "documentation", "opinion"]
---

Este es un inventario de lo que un equipo de ingeniería típico mantiene en git:

- Código fuente de la aplicación
- Definiciones de infraestructura (Terraform, Pulumi, CloudFormation)
- Configuraciones de pipelines de CI/CD
- Scripts de migración de base de datos
- Especificaciones de API (OpenAPI, protobuf)
- Manifiestos de despliegue (Kubernetes, Docker Compose)
- Plantillas de configuración de entornos

Y esto es lo que generalmente vive fuera de git:

- Documentación

Esto es extraño. La documentación describe el sistema. Cambia cuando el sistema cambia. Necesita revisión, versionado, atribución y la capacidad de revertir. Todos los demás artefactos que comparten estas propiedades viven en git. La documentación no — y nadie puede dar una buena razón de por qué.

## Las excusas habituales

### "Las personas no técnicas necesitan editar documentación"

Este es el argumento más común para mantener la documentación en Confluence o Notion. Y es válido — no se puede pedir a un gerente de producto que aprenda git branching para corregir un error tipográfico. Pero no es un argumento en contra de git. Es un argumento a favor de mejores herramientas sobre git.

Git es un backend de almacenamiento y versionado. Nada requiere que los humanos interactúen con él directamente. Un editor web puede crear commits y enviar cambios de la misma manera que un pipeline de CI lo hace. El usuario escribe en un navegador; el sistema maneja las operaciones de git.

El planteamiento de "git vs. usuarios no técnicos" es una falsa dicotomía. Se pueden tener ambos.

### "La documentación cambia demasiado frecuentemente para PRs"

Algunos equipos sienten que requerir pull requests para documentación ralentizaría la escritura. Y si su proceso de PR requiere dos revisores, una verificación de CI y una cola de merge — sí, eso es demasiada fricción para corregir un error tipográfico.

Pero nada en git obliga a un proceso de revisión pesado. Puede hacer push directamente a main para cambios menores y usar ramas para reescrituras estructurales. El punto es que el historial existe. Cada cambio se rastrea, se atribuye y es reversible. Si revisa cada cambio es una decisión de proceso, no una restricción de herramientas.

### "Nuestra plataforma de documentación no soporta git"

Esto solía ser cierto y solía importar. Confluence, Notion y la mayoría de las wikis almacenan contenido en una base de datos propietaria sin integración real con git. Exportar a markdown tiene pérdidas y es unidireccional.

Pero esto es una limitación de productos específicos, no una restricción fundamental. Las plataformas de documentación que tratan git como la fuente de verdad — mientras proporcionan un editor web por comodidad — existen ahora. La tecnología alcanzó a la necesidad.

### "Markdown es limitante"

Crítica válida para ciertos tipos de contenido. Markdown no soporta nativamente tablas complejas, diagramas incrustados o elementos interactivos. Pero para el 90% de la documentación interna — guías, runbooks, decisiones de arquitectura, documentación de API, materiales de incorporación — markdown es más que suficiente.

Y markdown en git le da algo que ningún formato propietario puede: portabilidad. Si decide cambiar de herramienta en dos años, su contenido son archivos de texto plano en un formato estándar. Intente exportar cinco años de contenido de Confluence a algo útil.

## Lo que pierde sin git

Si su documentación vive fuera de git, pierde capacidades que los ingenieros dan por sentadas con el código:

### Blame

¿Quién escribió este párrafo afirmando que la API soporta paginación? ¿Cuándo? ¿En respuesta a qué? Con `git blame`, puede rastrear cada línea hasta su autor, marca de tiempo y mensaje de commit. En una wiki, podría obtener "última edición por Sara, hace 6 meses" — sin contexto de por qué.

### Ramas

Está reescribiendo la guía de despliegue para una nueva infraestructura. La guía antigua necesita seguir siendo precisa hasta que la migración esté completa. En git, crea una rama. Ambas versiones coexisten. Hace merge cuando la migración se completa. En una wiki, o mantiene dos páginas (que inevitablemente divergen) o edita en su lugar y espera que nadie siga las instrucciones a medio actualizar.

### Cambios atómicos entre repositorios

Los mejores cambios de documentación ocurren junto con cambios de código. Un PR que añade un endpoint de API debería incluir la documentación para ese endpoint. Un commit que depreca una funcionalidad debería actualizar la documentación en el mismo commit — o al menos en el mismo PR. Cuando la documentación vive en una wiki, este acoplamiento es imposible. El código se publica, y alguien crea un ticket para "actualizar la documentación" que se queda en un backlog durante semanas.

### Diffs

¿Qué cambió en las últimas notas de versión? Muéstreme el diff. En git, `git diff v1.4..v1.5 -- docs/` le da exactamente lo que cambió. En una wiki, hace clic a través de historiales de página uno a uno, comparando la salida renderizada y esperando detectar cada edición.

### Automatización

Con la documentación en git, puede construir automatización:

```bash
# Encontrar documentación no actualizada en 90 días
git log --all --diff-filter=M --name-only --since="90 days ago" -- docs/ \
  | sort -u > recently_modified.txt

# Comparar con todos los archivos de documentación
find docs/ -name "*.md" | sort > all_docs.txt

# Archivos NO modificados en 90 días
comm -23 all_docs.txt recently_modified.txt
```

Intente hacer esto con una wiki. Necesitaría consultar una API, analizar marcas de tiempo y manejar paginación — si la API siquiera expone fechas de modificación.

## La verdadera razón por la que la documentación no está en git

No es técnica. Es histórica. La documentación precede a las prácticas modernas de DevOps. Las wikis surgieron a principios de los 2000 cuando "infraestructura como código" no existía y el control de versiones significaba SVN. El modelo wiki — editar en el navegador, guardar en la base de datos — tenía sentido cuando la alternativa era enviar documentos de Word por correo electrónico.

Pero las prácticas de ingeniería avanzaron. La infraestructura pasó de servidores configurados manualmente a código declarativo en git. CI/CD pasó de trabajos de Jenkins configurados a través de una interfaz web a pipeline-as-code en archivos YAML. La configuración pasó de páginas de ajustes de aplicación a variables de entorno y archivos de configuración en repositorios.

La documentación es el último reducto. No porque sea diferente, sino porque las herramientas no evolucionaron. Los generadores de sitios estáticos resolvieron el problema de "documentación en git" para desarrolladores pero excluyeron a todos los que no usan un terminal. Las wikis resolvieron el problema de "cualquiera puede escribir" pero abandonaron el control de versiones. Ningún lado cerró la brecha — hasta hace poco.

## Cómo debería verse

Un flujo de trabajo de documentación que respete git debería verse así:

1. Los escritores crean y editan contenido a través de una interfaz web — sin terminal requerido
2. Cada guardado crea un commit de git — automáticamente, de forma invisible
3. Los desarrolladores pueden editar el mismo contenido en su IDE y hacer push al mismo repositorio
4. Ambos lados se mantienen sincronizados — sin conflictos, sin merge manual
5. Los pull requests funcionan para documentación de la misma manera que funcionan para código
6. El historial completo de git está disponible: blame, diff, log, branch

Esto no es hipotético. El [patrón Content Ledger](/blog/why-git-sync-breaks/) resuelve el problema de sincronización. Las plataformas que lo implementan le dan una experiencia de edición tipo wiki con un repositorio git como backend.

Si está construyendo un nuevo flujo de trabajo de documentación — o reconstruyendo uno que no funciona — comience con git como base. Elija herramientas que traten el repositorio como la fuente de verdad, no como un destino de exportación. Su yo futuro, auditando qué cambió y por qué, se alegrará de que el historial exista.

Como [la propia documentación de Git lo expresa](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control): el control de versiones registra cambios en archivos a lo largo del tiempo para que pueda recuperar versiones específicas más adelante. Eso aplica a la documentación tanto como al código. Quizás más — porque el código tiene tests para detectar regresiones, pero la documentación solo tiene la memoria humana.

Si su documentación vale la pena escribirse, vale la pena versionarse. Póngala en git.

---

*Si desea probar una plataforma de documentación donde git es la fuente de verdad — no un añadido posterior — [DocPlatform](/install/) es gratuita y autoalojada. Un binario, sin base de datos que gestionar, sincronización bidireccional con git integrada.*
