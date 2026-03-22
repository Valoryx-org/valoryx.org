---
title: GitHub Sync
description: Conecte su workspace a GitHub para respaldo, edicion en IDE y control de versiones.
weight: 4
---

# GitHub Sync

Valoryx Cloud puede sincronizar su documentacion con un repositorio de GitHub. Esto le da lo mejor de ambos mundos: un editor web atractivo Y toda la potencia de git.

## Por que conectar GitHub?

- **Respaldo** — sus documentos siempre estan seguros en GitHub, incluso si cancela su cuenta
- **Edicion en IDE** — los desarrolladores de su equipo pueden editar documentos en VS Code, Vim o cualquier editor
- **Pull requests** — use el flujo de trabajo de PR de GitHub para revisar documentos antes de publicar
- **Historial de versiones** — git blame, diff y rollback completo para cada cambio
- **Integracion CI/CD** — ejecute builds o pruebas cuando los documentos cambien

## Como funciona

```
Edita en el navegador → autoguardado → auto-commit → push a GitHub
                                                        ↕
Un companero hace push desde IDE → GitHub → webhook → pull a Valoryx
```

Los cambios fluyen en ambas direcciones automaticamente. No tiene que preocuparse por la sincronizacion.

## Configuracion

1. Vaya a **Workspace Settings** → **Git Sync**
2. Haga clic en **Connect GitHub**
3. Autorice a Valoryx para acceder a sus repositorios
4. Seleccione el repositorio y la rama con la que desea sincronizar
5. Listo — su workspace ahora esta conectado

## Que se sincroniza

Cada pagina de su workspace corresponde a un archivo `.md` en el repositorio:

```
your-repo/
├── getting-started.md
├── api/
│   ├── authentication.md
│   └── endpoints.md
├── guides/
│   ├── deployment.md
│   └── troubleshooting.md
└── .docplatform.yaml     ← metadatos del workspace
```

## Necesito GitHub?

**No.** GitHub sync es completamente opcional. Valoryx Cloud funciona perfectamente sin el. Sus documentos se almacenan de forma segura en nuestros servidores. GitHub agrega respaldo y acceso desde IDE — pero no es necesario para que ninguna funcion opere.
