---
title: "El Costo Real de las Plataformas de Documentación"
description: "Los precios por usuario penalizan la adopción de documentación. Aquí tiene una comparación de TCO con 5, 15, 50 y 100 usuarios — con números reales."
date: "2026-04-09"
author: "Equipo Valoryx"
tags: ["pricing", "comparison", "documentation"]
---

Los precios por usuario parecen razonables a primera vista. ¿Cinco usuarios a $8/mes? Son $40. Su equipo puede pagar $40.

Pero la documentación es una de esas herramientas donde el número de personas que *deberían* tener acceso sigue creciendo. Los ingenieros necesitan escribir. Los gerentes de producto necesitan revisar. El personal de soporte necesita consultar. Los nuevos empleados necesitan leer y anotar. De repente no está en 5 puestos — está en 50, y esos "asequibles" $8/puesto son $400/mes por una herramienta que almacena archivos de texto.

Los precios por usuario para documentación tienen un incentivo perverso: penalizan a las empresas por dejar que más personas contribuyan a la documentación. Los gerentes empiezan a controlar el acceso. La gente comparte contraseñas. La documentación se convierte en problema de otro. Y luego se pregunta por qué su documentación siempre está desactualizada.

## Los números

Comparemos el costo mensual real de cuatro plataformas de documentación a diferentes tamaños de equipo. Estos son precios de lista a principios de 2026.

| Usuarios | [GitBook](https://www.gitbook.com/pricing) ($8/usuario) | Notion ($10/usuario) | Confluence ($6/usuario) | Valoryx Cloud | Valoryx CE |
|------:|------:|------:|------:|------:|------:|
| 5 | $40 | $50 | $30 | $29 | $0 |
| 15 | $120 | $150 | $90 | $29 | $0 |
| 50 | $400 | $500 | $300 | $29 | $0 |
| 100 | $800 | $1,000 | $600 | $29 | $0 |

Algunas notas sobre estos números:

**GitBook** cobra $8/usuario/mes en el plan Plus. El plan gratuito está limitado a 1 espacio con funcionalidades básicas. La documentación publicada solo está disponible en planes de pago.

**Notion** cobra $10/usuario/mes en el plan Plus. Notion es una herramienta de workspace general, no una plataforma de documentación — carece de documentación publicada, sincronización git y funcionalidades específicas de documentación. Pero muchos equipos lo usan para documentación, así que es una comparación justa de precio.

**Confluence** cobra $6.05/usuario/mes (Standard) para la nube. Este es el precio actual de Atlassian para 1-100 usuarios. La versión Data Center (autoalojada) comienza en $27,000/año para 500 usuarios.

**Valoryx Cloud** es $29/mes tarifa plana para el plan Team — 3 workspaces, 15 editores, 150 páginas. No por usuario. El [plan Free](/pricing/) le da 1 workspace, 3 editores, 50 páginas a $0.

**Valoryx Community Edition** es $0. Para siempre. Todo ilimitado. Usted lo aloja.

## El problema de escalabilidad

Mire la columna de 5 usuarios. Cada plataforma es asequible. GitBook a $40/mes es menos que un almuerzo de equipo. Nadie va a pelear por $40.

Ahora mire la columna de 100 usuarios. GitBook es $800/mes — $9,600/año por una herramienta que almacena y renderiza markdown. A ese punto, está en una revisión de presupuesto, alguien pregunta "¿realmente necesitamos esto?" y la respuesta generalmente es "limitemos el acceso a las personas que realmente escriben documentación".

Esa decisión — limitar el acceso — es donde muere la calidad de la documentación.

La buena documentación sucede cuando todos pueden contribuir. El ingeniero que acaba de depurar un problema de despliegue debería poder actualizar la guía de despliegue. El agente de soporte que encontró una solución alternativa debería poder añadirla a la página de resolución de problemas. El nuevo empleado que luchó con la incorporación debería poder mejorar la documentación de incorporación.

Los precios por usuario hacen que cada una de esas contribuciones cueste $6-10/mes. Entonces en su lugar, obtiene: "Envíe un correo al equipo de documentación y pídales que lo actualicen." El equipo de documentación tiene un backlog. La actualización nunca sucede. El conocimiento queda en la cabeza de alguien hasta que deja la empresa.

## Costo total de propiedad

El precio de suscripción mensual es solo parte del costo. El TCO real incluye:

### Costo de infraestructura (solo autoalojado)

Si elige Valoryx Community Edition, necesita un servidor. Un Hetzner CX22 (2 vCPU, 4GB RAM) cuesta EUR 3.99/mes. DocPlatform usa ~100MB de RAM bajo carga normal. Ese servidor también puede ejecutar otras cosas.

Costo anual de infraestructura para autoalojado: **~$50/año.**

### Tiempo de administración

**Las plataformas SaaS** requieren casi nada de tiempo de administración para uso básico, pero consumen horas en configuración de SSO, aprovisionamiento/desaprovisionamiento de usuarios y luchando con modelos de permisos que no coinciden con la estructura de su organización.

**DocPlatform autoalojado** requiere configuración inicial (30 minutos), actualizaciones ocasionales (descargar nuevo binario, reiniciar — 5 minutos) y verificación de copias de seguridad (automatizada, pero vale la pena verificar mensualmente).

### Costo de migración

El costo oculto de cualquier plataforma es qué sucede cuando quiere irse. La exportación de Confluence es famosamente dolorosa — años de contenido bloqueado en un formato de almacenamiento propietario. GitBook exporta a markdown pero pierde metadatos.

DocPlatform almacena todo como markdown en un repositorio git. Su contenido siempre es accesible fuera de la plataforma, en un formato estándar, con historial de versiones completo. El costo de migración es cero porque no hay nada que migrar — su contenido ya vive en git.

## El argumento de la tarifa plana

Valoryx Cloud usa precios de tarifa plana en lugar de por usuario:

| Plan | Precio | Workspaces | Editores | Páginas |
|------|------:|------:|------:|------:|
| Free | $0/mes | 1 | 3 | 50 |
| Team | $29/mes | 3 | 15 | 150 |
| Business | Próximamente | Más | Más | Más |

Los límites son en workspaces y páginas, no en usuarios. El plan Team a $29/mes soporta 15 editores — en cualquier plataforma por usuario, 15 usuarios costarían $90-150/mes.

Más importante, los lectores son gratuitos. Si su empresa tiene 200 personas que necesitan leer documentación pero solo 15 que la escriben, no paga por 200 puestos. Paga por el plan Team.

Esto alinea los incentivos correctamente: usted quiere que la mayor cantidad de personas posible lean y contribuyan a su documentación. El modelo de precios no debería penalizar eso.

## Cuándo el precio por usuario tiene sentido

Los precios por usuario no siempre son incorrectos. Para herramientas donde cada usuario genera un costo significativo (cargas de trabajo intensivas en cómputo, aplicaciones intensivas en almacenamiento), cobrar por usuario refleja el uso real de recursos.

Las plataformas de documentación no tienen esta característica. Renderizar markdown es barato. Almacenar texto es barato. El costo marginal de añadir el usuario 51 a una plataforma de documentación es aproximadamente cero. Cobrar $6-10/mes por ese usuario 51 es una elección de modelo de negocio, no un reflejo de costos.

## El cálculo de la Community Edition

Para equipos que pueden autoalojar, la Community Edition cambia el cálculo completamente:

| Gasto | Costo anual |
|---|---:|
| Servidor (Hetzner CX22) | $50 |
| Nombre de dominio | $12 |
| Certificado TLS (Let's Encrypt) | $0 |
| Licencia DocPlatform CE | $0 |
| **Total** | **$62/año** |

Son $62/año por usuarios ilimitados, páginas ilimitadas, workspaces ilimitados, búsqueda de texto completo, sincronización git, RBAC, WebAuthn e integración MCP. Sin tarifas por usuario, sin restricciones de funcionalidades, sin "contacte a ventas para precios empresariales".

Con 100 usuarios, son $0.62/usuario/año versus $72-120/usuario/año para plataformas alojadas con precios por usuario.

## Tomando la decisión

Aquí tiene un marco simple:

**Elija Valoryx Cloud ($29/mes)** si no quiere gestionar infraestructura pero quiere precios de tarifa plana. Bueno para equipos pequeños a medianos que quieren una solución alojada sin escalamiento de costos por usuario.

**Elija Valoryx Community Edition ($0)** si su equipo puede gestionar un servidor Linux. Mejor para equipos que se preocupan por la soberanía de datos, quieren costo recurrente cero o tienen requisitos de cumplimiento que exigen autoalojamiento. Consulte la [guía de instalación](/install/).

**Elija una plataforma por usuario** si su organización tiene menos de 10 usuarios, su equipo no escribe mucha documentación y ya están integrados en el ecosistema de ese proveedor (ej., Confluence si están completamente en Atlassian).

**No elija basándose en el precio de 5 usuarios.** Elija basándose en el precio de 50 usuarios, porque ahí es hacia donde se dirige. Las herramientas de documentación tienen la tendencia de expandirse a través de las organizaciones — si la herramienta es buena, más personas quieren acceso. Su modelo de precios debería recompensar eso, no penalizarlo.

Compare todos los planes en la [página de precios](/pricing/) o consulte la [página de código abierto](/open-source/) para la lista completa de funcionalidades de la Community Edition.
