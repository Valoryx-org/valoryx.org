---
title: Autenticación
description: Configure la autenticación local, inicio de sesión OIDC con Google y GitHub, configuración JWT y políticas de contraseña.
weight: 2
---

# Autenticación

DocPlatform soporta autenticación local (correo electrónico + contraseña) de forma predeterminada, con inicio de sesión OIDC opcional de Google y GitHub para equipos que usan esos proveedores.

## Autenticación local (predeterminada)

La autenticación local funciona sin ninguna configuración. Los usuarios se registran con un correo electrónico y contraseña, e inician sesión con las mismas credenciales.

### Cómo funciona

1. **Registro** — El usuario envía correo electrónico + contraseña. La contraseña se hashea con argon2id (algoritmo recomendado por OWASP 2024).
2. **Inicio de sesión** — El usuario envía credenciales. El servidor verifica el hash de la contraseña y devuelve tokens JWT.
3. **Sesión** — El token de acceso (RS256, 15 minutos de vida) se envía con cada solicitud a la API. El token de actualización (30 días de vida) se usa para obtener nuevos tokens de acceso sin re-autenticación.

### Hashing de contraseñas

DocPlatform usa argon2id con los siguientes parámetros (estándar OWASP 2024):

| Parámetro | Valor |
|---|---|
| **Algoritmo** | argon2id |
| **Memoria** | 64 MB |
| **Iteraciones** | 3 |
| **Paralelismo** | 4 |
| **Longitud del salt** | 16 bytes |
| **Longitud de la clave** | 32 bytes |

Estos parámetros no son configurables — siguen las mejores prácticas de seguridad. Los hashes de contraseña se almacenan en la base de datos SQLite y nunca salen del servidor.

### Restablecimiento de contraseña

Cuando un usuario solicita un restablecimiento de contraseña:

- **Con SMTP configurado** — se envía un enlace de restablecimiento de un solo uso por correo electrónico al usuario
- **Sin SMTP** — el token de restablecimiento se imprime en stdout (logs del servidor)

```bash
# Check server logs for the reset token
docplatform serve 2>&1 | grep "password reset"
```

El token expira después de 1 hora y solo puede usarse una vez.

## Tokens JWT

DocPlatform emite JSON Web Tokens RS256 (RSA-SHA256) para autenticación.

### Ciclo de vida del token

```
User logs in
    │
    ▼
┌─────────────────────────────────┐
│ Access Token (15 min)            │  ──►  Sent with every API request
│ Refresh Token (30 days)          │  ──►  Used to get new access tokens
└─────────────────────────────────┘
    │
    │  Access token expires
    ▼
┌─────────────────────────────────┐
│ POST /api/v1/auth/refresh        │
│ Body: { refresh_token: "..." }   │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ New Access Token (15 min)        │  ──►  Old refresh token rotated
│ New Refresh Token (30 days)      │  ──►  Old one invalidated
└─────────────────────────────────┘
```

### Rotación de token de actualización

Cada vez que se usa un token de actualización, se emite uno nuevo y el anterior se invalida. Esto limita la ventana de exposición si un token se ve comprometido.

### Configuración

| Variable | Predeterminado | Descripción |
|---|---|---|
| `JWT_SECRET_PATH` | `{DATA_DIR}/jwt-key.pem` | Ruta a la clave privada RS256 |
| `JWT_ACCESS_TTL` | `900` | Tiempo de vida del token de acceso (segundos) |
| `JWT_REFRESH_TTL` | `2592000` | Tiempo de vida del token de actualización (segundos) |

### Gestión de claves

El par de claves RS256 se auto-genera en el primer inicio si el archivo no existe. Para rotar las claves:

1. Detenga el servidor
2. Elimine el archivo de clave (`{DATA_DIR}/jwt-key.pem`)
3. Inicie el servidor — se genera una nueva clave

Todas las sesiones existentes se invalidan al rotar la clave. Los usuarios deben iniciar sesión nuevamente.

## Inicio de sesión con Google OIDC (opcional)

Permita a los usuarios iniciar sesión con su cuenta de Google.

### Configuración

1. Vaya a la [Google Cloud Console](https://console.cloud.google.com/)
2. Cree un nuevo proyecto (o use uno existente)
3. Navegue a **APIs & Services** → **Credentials**
4. Haga clic en **Create Credentials** → **OAuth 2.0 Client ID**
5. Tipo de aplicación: **Web application**
6. Agregue la URI de redirección autorizada: `https://your-domain.com/api/v1/auth/callback/google`
7. Copie el Client ID y el Client Secret

Establezca las variables de entorno:

```bash
export OIDC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
export OIDC_GOOGLE_CLIENT_SECRET=your-client-secret
```

Reinicie el servidor. Un botón **Sign in with Google** aparece en la página de inicio de sesión.

### Aprovisionamiento de usuarios

Cuando un usuario inicia sesión mediante Google por primera vez:

- Se crea una cuenta DocPlatform con su correo electrónico de Google
- Se le asigna el rol predeterminado (`permissions.default_role`) en cualquier workspace al que sea invitado
- No se establece contraseña (puede agregar una más tarde desde su perfil)

## Inicio de sesión con GitHub OIDC (opcional)

Permita a los usuarios iniciar sesión con su cuenta de GitHub.

### Configuración

1. Vaya a [GitHub Developer Settings](https://github.com/settings/developers)
2. Haga clic en **New OAuth App**
3. Establezca la URL de callback de autorización: `https://your-domain.com/api/v1/auth/callback/github`
4. Copie el Client ID y genere un Client Secret

Establezca las variables de entorno:

```bash
export OIDC_GITHUB_CLIENT_ID=your-client-id
export OIDC_GITHUB_CLIENT_SECRET=your-client-secret
```

Reinicie el servidor. Un botón **Sign in with GitHub** aparece en la página de inicio de sesión.

### Aprovisionamiento de usuarios

Igual que con Google — se crea una cuenta DocPlatform usando el correo electrónico principal de GitHub. Si la cuenta de GitHub no tiene correo electrónico público, se solicita al usuario que ingrese uno.

## Gestión de sesiones

DocPlatform rastrea las sesiones activas por usuario:

| Campo | Descripción |
|---|---|
| **Device** | Cadena de user-agent |
| **IP address** | IP del cliente (para fines de auditoría) |
| **Created** | Cuándo se estableció la sesión |
| **Last active** | Solicitud a la API más reciente |

Los usuarios pueden ver y revocar sesiones desde su página de perfil. Los administradores pueden ver todas las sesiones desde el panel de administración.

### Revocación de sesiones

- **Iniciada por el usuario** — Profile → Sessions → Revoke
- **Iniciada por el administrador** — Admin → Users → seleccionar usuario → Revoke All Sessions
- **Rotación de clave** — Eliminar la clave JWT invalida todas las sesiones globalmente

## Política de contraseñas

| Restricción | Valor |
|---|---|
| Longitud mínima | 8 caracteres |
| Longitud máxima | 128 caracteres |
| Hashing | argon2id (64 MB de memoria, 3 iteraciones, paralelismo 4) |

Las contraseñas se validan en el registro y el restablecimiento de contraseña. DocPlatform no impone requisitos de clases de caracteres (mayúsculas, caracteres especiales) — la longitud es la medida de seguridad principal según las directrices actuales del NIST.

## Autenticación WebSocket

Las conexiones WebSocket usan un patrón de ticket de un solo uso para evitar exponer tokens JWT en URLs (que aparecerían en los logs del servidor y el historial del navegador).

**Flujo:**

1. El cliente llama a `POST /api/v1/auth/ws-ticket` con un JWT válido
2. El servidor devuelve un ticket aleatorio (válido durante **30 segundos**, de un solo uso)
3. El cliente se conecta a `ws://host/ws?ticket={ticket}`
4. El servidor valida el ticket, establece el WebSocket y descarta el ticket

Esto es transparente para los usuarios — el editor web maneja la adquisición de tickets automáticamente.

## Recomendaciones de seguridad

- **Habilite OIDC** para equipos con cuentas de Google o GitHub — delega la gestión de contraseñas a proveedores establecidos
- **Use HTTPS** en producción — los tokens JWT son tokens de portador; los tokens interceptados otorgan acceso completo
- **Mantenga cortos los tiempos de vida de los tokens** — tokens de acceso de 15 minutos limitan la exposición
- **Monitorice las sesiones** — revise las sesiones activas periódicamente en busca de dispositivos o IPs inesperados
- **Rote las claves** anualmente o después de cualquier compromiso sospechado
- **Use cookies HttpOnly** — DocPlatform almacena tokens en cookies HttpOnly + Secure + SameSite=Strict, previniendo el robo de tokens por XSS
