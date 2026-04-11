---
title: "Documentación Autoalojada para Equipos Regulados"
description: "Cuando sus datos no pueden salir de su infraestructura, las opciones de documentación se reducen. Qué buscar y cómo las herramientas autoalojadas cumplen con los requisitos de cumplimiento."
date: "2026-03-23"
author: "Equipo Valoryx"
tags: ["compliance", "self-hosted", "security", "documentation"]
---

Si trabaja en salud, defensa, finanzas o cualquier industria donde la residencia de datos importa, ya ha tenido la conversación: "¿Podemos usar esta herramienta SaaS, o necesita pasar por una revisión de seguridad de seis meses?" Para la mayoría de las plataformas de documentación en la nube, la respuesta es la revisión — y a menudo termina con "no".

El problema no es que las herramientas en la nube sean inseguras. La mayoría son competentes en seguridad. El problema es el control. Los entornos regulados necesitan demostrar dónde viven los datos, quién puede acceder a ellos, cómo están cifrados y qué sucede cuando algo sale mal. Con una plataforma SaaS, confía en sus respuestas. Con autoalojamiento, puede verificar las suyas propias.

## Por qué la documentación se pasa por alto en el cumplimiento

Los equipos de seguridad auditan bases de datos, repositorios de código y herramientas de comunicación. Las plataformas de documentación a menudo pasan desapercibidas porque se ven como "solo documentación" — wikis internas con notas de reuniones y guías de incorporación.

Pero la documentación frecuentemente contiene:

- **Diagramas de arquitectura** con topología de red y rangos de IP
- **Especificaciones de API** con flujos de autenticación y formatos de tokens
- **Runbooks** con credenciales, cadenas de conexión y procedimientos de escalamiento
- **Documentación orientada al cliente** con capacidades del producto que están bajo control de exportación
- **Informes de incidentes** con detalles de vulnerabilidades

Este es material sensible. Si vive en un servidor de terceros en una jurisdicción que usted no controla, podría estar fuera de cumplimiento sin darse cuenta.

## La lista de verificación de cumplimiento

Al evaluar herramientas de documentación para entornos regulados, estos son los requisitos no negociables:

### Residencia de datos

¿Dónde viven físicamente los datos? Con herramientas autoalojadas, la respuesta es simple: en su infraestructura, en la región que elija. Con herramientas SaaS, necesita verificar las ubicaciones de centros de datos del proveedor y cualquier subprocesador de terceros.

Bajo el [RGPD](https://commission.europa.eu/law/law-topic/data-protection_en), las transferencias de datos personales fuera de la UE requieren mecanismos legales específicos. Si su documentación contiene datos personales (nombres de empleados, información de clientes, investigación de usuarios), la ubicación del alojamiento importa.

### Autenticación y control de acceso

¿Quién puede acceder a la documentación y cómo lo demuestra? Los entornos regulados típicamente requieren:

- **Autenticación multifactor** — las contraseñas solas no son suficientes
- **Control de acceso basado en roles (RBAC)** — no todos deberían ver todo
- **Gestión de sesiones** — tiempos de expiración automáticos, límites de sesiones concurrentes
- **Registro de auditoría** — quién accedió a qué, cuándo, desde dónde

### Cifrado

Los datos deben estar cifrados en tránsito y en reposo. "Usamos HTTPS" cubre el tránsito. En reposo es la pregunta más difícil: ¿está cifrada la base de datos? ¿Están cifrados los archivos adjuntos? ¿Qué algoritmo y longitud de clave?

### Registro de auditoría

Los marcos de cumplimiento requieren evidencia. Cuando un auditor pregunte "quién accedió a este documento el 15 de marzo", necesita una respuesta. Los registros de auditoría deben capturar:

- Identidad del usuario (no solo "alguien")
- Acción realizada (lectura, escritura, eliminación, exportación)
- Marca de tiempo
- Dirección IP o identificador de sesión
- Éxito o fallo

### Portabilidad de datos

Si necesita cambiar de herramientas — o si un regulador solicita una exportación de datos — ¿puede extraer su contenido en un formato estándar? Los formatos propietarios crean dependencia del proveedor y riesgo de cumplimiento.

## Qué proporciona Valoryx

Así es como Valoryx aborda cada requisito. Estas no son afirmaciones de marketing — son detalles de implementación que puede verificar en la [documentación de seguridad](/security/) y el código fuente.

### Autenticación

Valoryx soporta autenticación WebAuthn/passkey y autenticación tradicional por contraseña. Las contraseñas se hashean con **Argon2id** — el ganador del Password Hashing Competition, diseñado para resistir ataques tanto de GPU como de ASIC. Argon2id es la recomendación actual de OWASP para almacenamiento de contraseñas.

RBAC está integrado con cinco roles: Owner, Admin, Editor, Viewer y Guest. Cada rol tiene permisos explícitos para acceso a workspaces, edición de páginas, gestión de usuarios y configuración del sistema. Los permisos se aplican a nivel de API, no solo de interfaz — por lo que incluso las llamadas directas a la API respetan los límites de roles.

### Cifrado

Todos los datos en reposo están cifrados con **AES-256-GCM**. Esto incluye la base de datos SQLite, archivos adjuntos y cualquier contenido en caché. AES-256-GCM proporciona tanto confidencialidad como integridad — los datos manipulados se detectan, no solo son ilegibles.

En tránsito, Valoryx sirve sobre HTTPS. Para instalaciones detrás de un proxy inverso (el patrón común), TLS termina en el proxy. La [guía de instalación](/install/) cubre tanto TLS directo como configuraciones de proxy inverso.

### Política de seguridad de contenido

Valoryx envía encabezados estrictos de **Content Security Policy (CSP)** que previenen cross-site scripting, clickjacking y exfiltración de datos mediante scripts en línea. Los encabezados CSP se configuran por defecto — sin configuración manual requerida.

### Registro de auditoría

Cada acción significativa se registra: vistas de páginas, ediciones, eliminaciones, intentos de inicio de sesión (exitosos y fallidos), cambios de permisos, operaciones de sincronización git y uso de claves de API. Los registros incluyen identidad del usuario, marca de tiempo, dirección IP y el recurso específico afectado.

Los registros se almacenan localmente en la misma base de datos SQLite, lo que significa que están cubiertos por las mismas políticas de cifrado y respaldo que su contenido. Para organizaciones que reenvían registros a un SIEM, el registro de actividad es accesible a través de la API de administración.

### Portabilidad de datos

Todo el contenido se almacena como markdown estándar. La sincronización git significa que su contenido ya existe en un repositorio git en archivos de texto plano. Si deja de usar Valoryx mañana, su documentación sigue ahí — en su repositorio, en formato estándar, con historial completo.

Sin paso de exportación propietario. Sin solución alternativa de "descargar como ZIP". Su contenido siempre es accesible en el formato en que lo escribió.

## Comparación: autoalojado vs. nube para cumplimiento

| Requisito | SaaS en la nube | Autoalojado (Valoryx) |
|------------|------------|----------------------|
| Residencia de datos | Centros de datos del proveedor (verificar regiones) | Su infraestructura, su región |
| Autenticación | Gestionada por el proveedor (generalmente OAuth/SAML) | Usted controla: WebAuthn, contraseñas Argon2id, RBAC |
| Cifrado en reposo | Gestionado por el proveedor (verificar algoritmo) | AES-256-GCM, claves en su servidor |
| Registros de auditoría | Formato de registro del proveedor, su retención | Sus registros, su retención, su SIEM |
| Subprocesadores | Cadena de proveedores (leer el DPA) | Ninguno — binario único, sin llamadas externas |
| Exportación de datos | Formato de exportación del proveedor (puede ser propietario) | Markdown estándar en un repositorio git |
| Respuesta a incidentes | El proveedor le notifica (verificar tiempo del SLA) | Usted detecta, usted responde, usted controla los plazos |

La fila de "subprocesadores" merece énfasis. Muchas herramientas de documentación SaaS usan servicios de terceros para búsqueda (Algolia), analítica (Segment), rastreo de errores (Sentry) y alojamiento (AWS, GCP). Cada subprocesador es un eslabón en la cadena de cumplimiento que necesita su propia evaluación. Valoryx es un único binario de Go con cero dependencias externas y cero llamadas de red salientes. No hay cadena de proveedores que auditar.

## Pasos prácticos

Si está evaluando herramientas de documentación para un entorno regulado:

1. **Mapee sus datos.** ¿Qué hay realmente en su documentación? ¿Detalles de arquitectura, credenciales, datos de clientes? Esto determina qué marcos de cumplimiento aplican.

2. **Verifique los requisitos de su marco.** RGPD, SOC 2, HIPAA, ITAR y FedRAMP tienen requisitos diferentes para residencia de datos, cifrado y control de acceso. Sepa cuáles aplican a su organización.

3. **Pruebe primero el autoalojamiento.** [Instale Valoryx](/install/) en su infraestructura, conéctelo a su proveedor de identidad y verifique los controles de seguridad usted mismo. La Community Edition es gratuita sin restricciones de funcionalidades — la misma autenticación, cifrado y registro de auditoría disponible en cada instalación.

4. **Documente sus controles.** Cuando llegue el auditor, necesitará mostrar: dónde viven los datos, cómo están cifrados, quién tiene acceso y qué muestra el registro de auditoría. Las herramientas autoalojadas hacen que cada una de estas preguntas sea respondible con evidencia de sus propios sistemas.

Lea nuestra [política de privacidad](/privacy/) y [términos de servicio](/terms/) para detalles sobre cómo Valoryx maneja datos en nuestra oferta en la nube. Para instalaciones autoalojadas, sus datos nunca tocan nuestra infraestructura.

El cumplimiento no debería dictar sus elecciones de herramientas — pero a menudo lo hace. La documentación autoalojada da a los equipos regulados una cosa menos que explicar al auditor y un sistema más completamente bajo su propio control.
