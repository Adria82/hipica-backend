# API: Auth

Base URL: `/api/v1/auth`

Endpoints de autenticación. Emiten y renuevan tokens JWT para acceder al resto de la API.

Los tokens siguen el esquema HS256:
- **Access token**: validez de 15 minutos. Se incluye en la cabecera `Authorization: Bearer <token>` en todas las peticiones protegidas.
- **Refresh token**: validez de 7 dias. Se usa exclusivamente para renovar el access token sin necesidad de introducir credenciales de nuevo.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Autenticacion requerida |
|--------|------|-------------|------------------------|
| POST | `/login` | Iniciar sesion y obtener tokens | No |
| POST | `/refresh` | Renovar el access token | No (requiere refresh token valido) |

---

## Detalle de Endpoints

### POST /api/v1/auth/login

Autentica al usuario con email y contrasena. Devuelve un access token y un refresh token.

El campo `username` del formulario corresponde al **email** del usuario (convencion OAuth2).

**Autenticacion requerida:** No

**Formato de la peticion:** `application/x-www-form-urlencoded` (formulario OAuth2)

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| username | string | Si | Email del usuario |
| password | string | Si | Contrasena del usuario |

**Ejemplo de peticion:**
```
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin%40hipica.com&password=secreto123
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| access_token | string | JWT de acceso. Expira en 15 minutos |
| refresh_token | string | JWT de refresco. Expira en 7 dias |
| token_type | string | Siempre `"bearer"` |

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Credenciales incorrectas (email o contrasena invalidos) |
| 422 | Campos del formulario ausentes o mal formados |

---

### POST /api/v1/auth/refresh

Genera un nuevo access token a partir de un refresh token valido. El refresh token no cambia.

**Autenticacion requerida:** No (el refresh token actua como credencial)

**Formato de la peticion:** `application/json`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| refresh_token | string | Si | JWT de refresco emitido previamente por `/login` |

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

El `refresh_token` devuelto es el mismo que se envio en la peticion.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Refresh token invalido, expirado o de tipo incorrecto |
| 422 | Cuerpo de la peticion mal formado (campo ausente) |

---

## Notas de Seguridad

- El access token debe enviarse en todas las peticiones protegidas como `Authorization: Bearer <access_token>`.
- Nunca se debe exponer el `SECRET_KEY` del servidor. Los tokens firmados con HS256 no son verificables por el cliente.
- Si el refresh token expira, el usuario debe volver a autenticarse con `/login`.
