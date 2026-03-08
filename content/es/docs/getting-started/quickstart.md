---
title: Inicio rápido
description: Ponga en marcha DocPlatform en menos de 5 minutos con un workspace de documentación completamente funcional.
weight: 1
---

# Inicio rápido

Pase de cero a una plataforma de documentación en funcionamiento en menos de 5 minutos. Esta guía cubre la ruta más rápida; para opciones detalladas, consulte la guía de [Instalación](installation.md).

## Paso 1: Instalar

```bash
# Recommended (auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh
```

O descargue manualmente:

```bash
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform
```

O con Docker:

```bash
docker run -d --name docplatform -p 3000:3000 -v docplatform-data:/data ghcr.io/valoryx-org/docplatform:latest
```

Si usa Docker, vaya directamente al [Paso 3](#paso-3-registrar-su-cuenta): el contenedor se auto-inicializa.

## Paso 2: Inicializar un workspace

```bash
docplatform init --workspace-name "My Docs" --slug my-docs
```

Esto crea:

```
.docplatform/
├── data.db              # SQLite database
├── jwt-key.pem          # Auto-generated RS256 signing key
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Your documentation lives here
        └── .docplatform/
            └── config.yaml
```

### Con git (opcional)

Conecte a un repositorio git existente durante la inicialización:

```bash
docplatform init \
  --workspace-name "My Docs" \
  --slug my-docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

DocPlatform clona el repositorio y comienza a sincronizar. Los archivos `.md` existentes se indexan automáticamente.

## Paso 3: Iniciar el servidor

```bash
docplatform serve
```

```
INFO  Server starting            port=3000 version=v0.5.2
INFO  Database initialized       path=.docplatform/data.db
INFO  Search index ready         documents=0
INFO  Workspace loaded           name="My Docs" slug=my-docs
INFO  Listening on               http://localhost:3000
```

Abra [http://localhost:3000](http://localhost:3000) en su navegador.

## Paso 4: Registrar su cuenta

El primer usuario en registrarse se convierte automáticamente en **SuperAdmin** con acceso completo a la plataforma.

1. Haga clic en **Create Account**
2. Ingrese su nombre, correo electrónico y contraseña
3. Ha iniciado sesión y está listo para escribir

> **Nota de seguridad:** El flujo en que el primer usuario se convierte en administrador solo aplica cuando no existen usuarios. Después del primer registro, las cuentas nuevas reciben el rol predeterminado configurado para el workspace.

## Paso 5: Crear su primera página

1. Haga clic en **New Page** en la barra lateral
2. Asígnele un título — el slug de la URL se genera automáticamente a partir del título
3. Comience a escribir en el editor enriquecido
4. Los cambios se guardan automáticamente cada pocos segundos

La página se almacena como un archivo Markdown en el directorio `docs/` de su workspace. Si conectó git, se auto-confirma y se envía automáticamente.

## Paso 6: Pruébelo

Aquí hay algunas cosas que puede probar de inmediato:

| Acción | Cómo |
|---|---|
| **Cambiar a Markdown sin procesar** | Haga clic en el botón `</>` en la barra de herramientas del editor |
| **Buscar** | Presione `Cmd+K` (o `Ctrl+K`) para abrir la búsqueda instantánea |
| **Crear una subpágina** | Haga clic en el `+` junto a una página existente en la barra lateral |
| **Previsualizar el sitio publicado** | Navegue a `http://localhost:3000/p/my-docs/` |
| **Ejecutar diagnósticos** | Ejecute `docplatform doctor` en su terminal |

## Próximos pasos

| Objetivo | Guía |
|---|---|
| Conectar un repositorio git | [Integración con Git](../guides/git-integration.md) |
| Invitar a su equipo | [Equipos y colaboración](../guides/collaboration.md) |
| Publicar documentación públicamente | [Publicación](../guides/publishing.md) |
| Desplegar en producción | [Despliegue](../deployment/binary.md) |
| Configurar proveedores de autenticación | [Autenticación](../configuration/authentication.md) |
