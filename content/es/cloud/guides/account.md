---
title: Su cuenta
description: Administre su perfil, contrasena, facturacion y datos.
weight: 6
---

# Su cuenta

## Registro

Visite [app.valoryx.dev](https://app.valoryx.dev/#/register) y cree una cuenta con su correo electronico y una contrasena. Debera aceptar los [Terminos de servicio](/terms/) y la [Politica de privacidad](/privacy/).

Tambien puede iniciar sesion con **Google** o **GitHub** si esas opciones estan disponibles.

## Configuracion del perfil

Haga clic en su avatar en la esquina superior izquierda, luego en **Profile** para:

- Cambiar su nombre para mostrar
- Actualizar su correo electronico
- Cambiar su contrasena
- Configurar una passkey (WebAuthn) para inicio de sesion sin contrasena

## Facturacion

Vaya a **Workspace Settings** → **Billing** para:

- Ver su plan actual y uso
- Actualizar a Team ($29/mes) o Business ($79/mes)
- Gestionar su suscripcion a traves del portal de Stripe
- Ver facturas e historial de pagos

## Sus datos

### Que almacenamos

- Su correo electronico, nombre y contrasena (con hash Argon2id)
- El contenido de su documentacion (en workspaces)
- Registros de actividad (quien edito que y cuando)

### Que no almacenamos

- Numeros de tarjeta de credito (gestionados completamente por Stripe)
- Sus credenciales de Git (tokens OAuth, no se almacenan a largo plazo)
- Cookies de rastreo (las analiticas son opcionales, compatibles con GDPR)

### Exportar sus datos

Su contenido siempre es portable:

- **Con GitHub sync** — sus documentos ya estan en su repositorio de GitHub como archivos Markdown
- **Sin GitHub sync** — use el boton **Export** en la configuracion del workspace para descargar un ZIP con todos sus archivos Markdown
- **Datos de la cuenta** — solicite una exportacion completa de datos contactandonos

### Eliminar su cuenta

Contactenos en valoryxeu@gmail.com para solicitar la eliminacion de su cuenta. Eliminaremos todos sus datos en un plazo de 30 dias segun lo requiere el GDPR.

## Seguridad

- Las contrasenas se almacenan con hash Argon2id (recomendado por OWASP)
- Las sesiones usan cookies HttpOnly (no accesibles por JavaScript)
- Todo el trafico esta cifrado con TLS
- Passkey/WebAuthn opcional para inicio de sesion sin contrasena
- Historial de auditoria completo de todas las acciones de la cuenta
