---
title: "Por Qué Distribuimos un Único Binario de Go"
description: "DocPlatform es un binario con cero dependencias. Sin Docker, sin Postgres, sin Redis. Esta es la arquitectura detrás de una instalación de 30 segundos."
date: "2026-03-30"
author: "Equipo Valoryx"
tags: ["architecture", "golang", "self-hosted", "documentation"]
---

La mayoría de las plataformas de documentación se distribuyen como un stack. Obtiene una aplicación Node.js, una base de datos PostgreSQL, una caché Redis, un clúster de Elasticsearch para búsqueda y un proxy inverso Nginx para unirlo todo. Cinco servicios, cinco cosas que pueden fallar, cinco cosas que monitorear, parchear y actualizar.

DocPlatform se distribuye como un archivo. Descárguelo, ejecútelo, listo.

Esto no es un truco de marketing. Es una decisión de arquitectura que tomamos desde el día uno, y cada decisión de diseño desde entonces se deriva de ella. Aquí explica por qué.

## El stack típico de documentación

Veamos qué realmente despliega cuando configura una plataforma de documentación moderna:

```
┌─────────────┐
│   Nginx     │  ← proxy inverso, terminación TLS
├─────────────┤
│   Node.js   │  ← servidor de aplicación
├─────────────┤
│  PostgreSQL │  ← almacenamiento de contenido
├─────────────┤
│    Redis    │  ← caché de sesiones, cola de trabajos
├─────────────┤
│Elasticsearch│  ← búsqueda de texto completo
└─────────────┘
```

Son cinco procesos, cada uno con sus propios archivos de configuración, requisitos de versión y modos de fallo. Docker Compose ayuda a gestionar la orquestación, pero no reduce la superficie. Todavía necesita:

- Monitorear cada servicio por caídas y uso de recursos
- Ejecutar migraciones de base de datos en las actualizaciones
- Ajustar tamaños de heap de Elasticsearch y configuraciones de índice
- Manejar políticas de desalojo de Redis cuando se llena la memoria
- Rotar logs de Nginx y renovar certificados TLS

Para una empresa Fortune 500 con un equipo de plataforma, esto es rutina. Para una startup de 10 personas que solo quiere documentación interna, es una sobrecarga que nunca termina.

## Cómo se ve un binario único

Esta es la arquitectura de despliegue de DocPlatform:

```
┌──────────────────────────┐
│      docplatform          │  ← binario único de Go
│  ┌────────┐ ┌──────────┐ │
│  │ SQLite │ │  Bleve   │ │
│  │  (BD)  │ │(búsqueda)│ │
│  └────────┘ └──────────┘ │
└──────────────────────────┘
```

Un binario. Un directorio de datos. SQLite maneja el almacenamiento de contenido, sesiones y configuración. [Bleve](https://blevesearch.com/) maneja la búsqueda de texto completo. Ambos son bibliotecas embebidas compiladas directamente en el binario — sin procesos externos, sin llamadas de red entre servicios.

La instalación toma 30 segundos:

```bash
curl -fsSL https://get.valoryx.org | sh
docplatform serve
```

Eso es todo. Sin `docker-compose up`, sin inicialización de base de datos, sin variables de entorno para cadenas de conexión. El binario crea su directorio de datos en la primera ejecución y comienza a servir en el puerto 3000.

Para más opciones de instalación, consulte la [guía de instalación](/install/).

## Por qué Go hace esto posible

Elegimos Go específicamente porque habilita esta arquitectura. Tres propiedades importan:

### Compilación estática

Go compila a un único binario estáticamente enlazado. Sin dependencias en tiempo de ejecución, sin bibliotecas compartidas, sin JVM, sin `node_modules`. El binario se ejecuta en un servidor Linux básico sin nada más instalado.

```bash
# Compilación cruzada para Linux desde cualquier SO
GOOS=linux GOARCH=amd64 go build -o docplatform ./cmd/server/
```

Ese único comando produce un binario que puede enviar por `scp` a un servidor y ejecutar. Compare esto con desplegar una aplicación Node.js, donde necesita instalar Node, ejecutar `npm install`, esperar que las dependencias nativas compilen correctamente en la arquitectura de destino y configurar un gestor de procesos.

### Goroutines para concurrencia

Una plataforma de documentación necesita manejar solicitudes concurrentes (vistas de página, consultas de búsqueda, guardados del editor), ejecutar trabajos en segundo plano (sincronización git, indexación de búsqueda) y gestionar conexiones WebSocket (colaboración en tiempo real) — todo simultáneamente.

Las goroutines de Go hacen esto económico. Cada conexión WebSocket obtiene su propia goroutine, costando aproximadamente 2KB de memoria. Un servidor Node.js manejando las mismas conexiones necesita gestionarlas en un único event loop, o descargarlas a worker threads con complejidad de memoria compartida.

El motor de sincronización git, que consulta y reconcilia cambios entre el editor web y los repositorios git, se ejecuta como un conjunto de goroutines dentro del mismo proceso. Sin servicio worker separado, sin cola de trabajos, sin Redis.

### Bases de datos embebidas

Tanto SQLite como Bleve están escritos en C y Go respectivamente, y ambos compilan directamente en el binario vía `cgo` (SQLite) y Go puro (Bleve). Esto significa:

- Sin servidor de base de datos que instalar, configurar o monitorear
- Sin latencia de red entre la aplicación y sus datos
- Las copias de seguridad son copias de archivos — `cp data.db data.db.bak`
- Las actualizaciones preservan datos automáticamente — el nuevo binario lee los archivos de datos antiguos

SQLite maneja [miles de millones de filas](https://www.sqlite.org/whentouse.html) en producción en empresas mucho más grandes que la nuestra. Para una plataforma de documentación sirviendo cientos de usuarios concurrentes, es más que suficiente.

## La ventaja operativa

El enfoque de binario único paga dividendos en operaciones:

**Las actualizaciones** son reemplazar un archivo. Detenga el binario antiguo, copie el nuevo, inícielo. Sin migraciones de base de datos de las que preocuparse — la aplicación maneja los cambios de esquema en el arranque.

**Las copias de seguridad** son copiar dos archivos: la base de datos SQLite y el índice Bleve. O solo la base de datos — el índice de búsqueda se puede reconstruir desde el contenido.

**El monitoreo** es observar un proceso. Si está corriendo, todo funciona. Si se cae, reinícielo. No hay fallos parciales donde la base de datos está activa pero la búsqueda no.

**El uso de recursos** es predecible. Un proceso, una huella de memoria. Sin picos de memoria sorpresa del heap de JVM de Elasticsearch o Redis acumulando claves.

**La superficie de seguridad** es mínima. Un binario, un puerto de escucha. Sin comunicación entre servicios que asegurar, sin Redis expuesto en un puerto de red, sin clúster de Elasticsearch con su propia capa de autenticación. Consulte nuestra [documentación de seguridad](/security/) para el modelo completo.

## Compromisos que aceptamos

Esta arquitectura tiene límites, y somos honestos al respecto:

**Solo escalado vertical.** SQLite se ejecuta en una máquina. No puede distribuir la base de datos a través de un clúster. Para la mayoría de los casos de uso de documentación — incluso grandes con miles de páginas — un único servidor moderno maneja la carga fácilmente. Pero si necesita escalado horizontal a través de centros de datos, esta no es la arquitectura correcta.

**Escritor único para SQLite.** SQLite soporta lectores concurrentes pero serializa las escrituras. En la práctica, las plataformas de documentación son de lectura intensiva (muchas vistas de página, pocas ediciones), por lo que esto rara vez es un cuello de botella. Pero un equipo de 200 personas guardando páginas simultáneamente vería algo de contención de escritura.

**Sin intercambio de componentes.** No puede reemplazar Bleve con Elasticsearch si quiere funcionalidades de búsqueda más avanzadas. El motor de búsqueda está embebido, no es intercambiable. Creemos que el compromiso vale la pena — Bleve soporta stemming, coincidencia difusa y ponderación de campos, lo cual cubre lo que necesita la búsqueda de documentación.

## Ejemplos de despliegue

El binario único se ejecuta en cualquier lugar donde pueda correr un proceso Linux/macOS/Windows:

**Servidor bare metal o VM:**
```bash
# Descargar, ejecutar, listo
curl -fsSL https://get.valoryx.org | sh
docplatform serve --port 3000
```

**Servicio systemd:**
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

**Docker (si lo desea):**
```dockerfile
FROM scratch
COPY docplatform /docplatform
ENTRYPOINT ["/docplatform", "serve"]
```

Note el `FROM scratch` — dado que el binario no tiene dependencias, la imagen Docker no contiene literalmente nada excepto el binario en sí. La imagen pesa menos de 30MB.

Para opciones detalladas de despliegue, consulte la [guía de despliegue de binarios](/docs/deployment/binary/).

## Qué significa esto para su equipo

Cada servicio adicional en su stack es un servicio que alguien tiene que entender, monitorear y arreglar a las 2 AM cuando se rompe. La infraestructura de documentación debería pasar a segundo plano — debería ser algo que configura una vez y se olvida.

Un binario único que incluye todo lo que necesita es lo más cercano que hemos encontrado a ese ideal. Sin contenedores que orquestar, sin bases de datos que ajustar, sin clústeres de búsqueda que monitorear. Solo un archivo que ejecuta su documentación.

[Instale DocPlatform](/install/) en 30 segundos y compruébelo usted mismo. La Community Edition es gratuita — usuarios ilimitados, páginas ilimitadas, sin límite de tiempo.
