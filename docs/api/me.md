# API: Me

Base URL: `/api/v1/me`

Endpoints relacionados con el usuario autenticado. Permiten obtener informacion de contexto, gestionar el perfil (nombre, email, avatar) y consultar las funcionalidades activas de la hipica.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| GET | `/profile` | Obtener perfil del usuario autenticado | Cualquier usuario autenticado |
| PUT | `/profile` | Actualizar email y/o avatar | Cualquier usuario autenticado |
| GET | `/features` | Listar funcionalidades activas de la hipica | Cualquier usuario autenticado |

---

## Esquema de perfil

```json
{
  "id": 3,
  "name": "Monitor Juan",
  "email": "monitor@hipica.com",
  "role": "monitor",
  "stable_id": 1,
  "stable_name": "Hipica Can Bofill",
  "stable_theme": "default",
  "avatar": "data:image/png;base64,iVBORw0KGgo..."
}
```

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | integer | ID del usuario |
| `name` | string | Nombre del usuario |
| `email` | string | Email del usuario |
| `role` | string | Rol: `app_admin`, `stable_admin`, `monitor`, `client` |
| `stable_id` | integer \| null | ID de la hipica. `null` para `app_admin` global. |
| `stable_name` | string \| null | Nombre de la hipica. `null` si no tiene hipica. |
| `stable_theme` | string | Identificador del tema de branding. Default: `"default"`. |
| `avatar` | string \| null | Data URL base64 del avatar, o `null` si no hay ninguno. |

---

## Detalle de Endpoints

### GET /api/v1/me/profile

Devuelve el perfil completo del usuario autenticado.

**Autenticacion requerida:** Si.

**Response 200:** Objeto de perfil (ver esquema arriba).

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente, invalido o expirado |

---

### PUT /api/v1/me/profile

Actualiza el perfil. Solo se modifican los campos enviados.

**Autenticacion requerida:** Si.

**Request Body (todos opcionales):**
```json
{
  "email": "nuevo@ejemplo.com",
  "avatar": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `email` | string | No | Nuevo email. Debe ser unico en el sistema. |
| `avatar` | string | No | Data URL base64 de la imagen de perfil. Se almacena directamente en la columna `user.avatar` (character varying). |

**Response 200:** Objeto de perfil actualizado.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente, invalido o expirado |
| 409 | El email indicado ya esta en uso (`detail: "email.taken"`) |

---

### GET /api/v1/me/features

Devuelve los codigos de funcionalidad (`FeatureCode`) activos para la hipica del usuario.

Si el usuario es `app_admin` sin hipica asignada, devuelve todas las funcionalidades del sistema.

**Response 200:**
```json
{
  "features": ["HORSES", "CLIENTS", "LESSONS"]
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente, invalido o expirado |

---

## Notas de implementacion

- El avatar se guarda como data URL base64 directamente en la BD. Para imagenes grandes se recomienda comprimirlas en el cliente antes de enviarlas.
- El frontend (`profile.ts`) excluye el avatar del `localStorage` para evitar `QuotaExceededError`. El avatar se recarga desde la API en cada sesion via `fetchProfile()`.
- El campo `stable_theme` se usa en el frontend para cargar los assets de branding de la carpeta `public/branding/{theme}/`.
