# API: Me

Base URL: `/api/v1/me`

Endpoints relacionados con el usuario autenticado. Permiten al frontend obtener informacion de contexto del usuario actual, gestionar su perfil y consultar las funcionalidades activas para su hipica.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| GET | `/profile` | Obtener perfil del usuario autenticado | Cualquier usuario autenticado |
| PUT | `/profile` | Actualizar email y/o avatar del usuario | Cualquier usuario autenticado |
| GET | `/features` | Listar funcionalidades activas de la hipica del usuario | Cualquier usuario autenticado |

---

## Detalle de Endpoints

### GET /api/v1/me/profile

Devuelve el perfil completo del usuario autenticado, incluyendo datos de su hipica y avatar.

**Autenticacion requerida:** Si. Token Bearer en la cabecera `Authorization`.

**Rol requerido:** Cualquier usuario autenticado.

**Response 200:**
```json
{
  "id": 3,
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
| `email` | string | Email del usuario |
| `role` | string | Rol del usuario (`app_admin`, `stable_admin`, `monitor`, `client`) |
| `stable_id` | integer \| null | ID de la hipica asociada. `null` para `app_admin` sin hipica. |
| `stable_name` | string \| null | Nombre legible de la hipica. `null` si no tiene hipica asociada. |
| `stable_theme` | string | Identificador del tema de branding. Default: `"default"`. |
| `avatar` | string \| null | Data URL base64 del avatar o `null` si no se ha subido ninguno. |

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente, invalido o expirado |

---

### PUT /api/v1/me/profile

Actualiza el perfil del usuario autenticado. Solo se modifican los campos enviados; los omitidos conservan su valor.

**Autenticacion requerida:** Si. Token Bearer en la cabecera `Authorization`.

**Rol requerido:** Cualquier usuario autenticado.

**Request Body (todos los campos son opcionales):**
```json
{
  "email": "nuevo@ejemplo.com",
  "avatar": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `email` | string | No | Nuevo email. Debe ser unico en el sistema. |
| `avatar` | string | No | Data URL en base64 de la imagen de perfil. |

**Response 200:** Misma estructura que `GET /me/profile` con los datos actualizados.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente, invalido o expirado |
| 409 | El email indicado ya esta en uso por otro usuario (`detail: "email.taken"`) |

---

### GET /api/v1/me/features

Devuelve la lista de codigos de funcionalidad (`FeatureCode`) activados para la hipica del usuario autenticado.

El flujo interno es:
1. Se obtiene el usuario desde el JWT.
2. Se identifica su `stable_id`.
3. Se consulta la tabla `StableFeature` para esa hipica.
4. Se devuelve la lista de codigos de funcionalidad activos.

**Caso especial:** Si el usuario es `app_admin` y no pertenece a ninguna hipica (`stable_id` es `null`), se devuelven **todas** las funcionalidades disponibles en el sistema.

**Autenticacion requerida:** Si. Token Bearer en la cabecera `Authorization`.

**Rol requerido:** Cualquier usuario autenticado (no hay restriccion de rol adicional).

**Response 200:**
```json
{
  "features": ["HORSES", "CLIENTS", "LESSONS"]
}
```

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| features | array[string] | Lista de codigos de funcionalidad activos para la hipica |

**Ejemplo — usuario app_admin sin hipica asignada (acceso total):**
```json
{
  "features": ["HORSES", "CLIENTS", "LESSONS", "LEVELS", "USERS"]
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente, invalido o expirado |

---

## Notas de Uso

Este endpoint es el mecanismo principal por el que el frontend decide que secciones del menu lateral mostrar. Se consulta tras el login y se almacena en el store reactivo de features (`src/features/features.ts`).

El catalogo de codigos posibles (`FeatureCode`) esta definido en `app/models/feature.py`.
