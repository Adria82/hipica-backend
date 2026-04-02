# API: Users

Base URL: `/api/v1/users`

Gestion de usuarios del sistema. Un usuario pertenece a una hipica (`stable_id`, opcional para `app_admin`) y tiene un rol que determina sus permisos en la API.

Los roles disponibles son:

| Rol | Descripcion |
|-----|-------------|
| `app_admin` | Administrador global. Puede gestionar todas las hipicas |
| `stable_admin` | Administrador de una hipica concreta |
| `monitor` | Monitor/instructor. Acceso de lectura avanzado |
| `client` | Cliente/alumno. Acceso minimo |

> **Alerta de seguridad:** Ningun endpoint de este recurso tiene control de acceso (`require_role`). Cualquier peticion puede crear, listar, modificar o eliminar usuarios, incluyendo la asignacion de roles privilegiados. Se recomienda proteger estos endpoints urgentemente con `backend-dev`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear un usuario | Sin control (ver alerta) |
| GET | `/` | Listar todos los usuarios | Sin control (ver alerta) |
| GET | `/{user_id}` | Obtener un usuario por ID | Sin control (ver alerta) |
| PUT | `/{user_id}` | Actualizar un usuario | Sin control (ver alerta) |
| DELETE | `/{user_id}` | Eliminar un usuario | Sin control (ver alerta) |

---

## Detalle de Endpoints

### POST /api/v1/users/

Crea un nuevo usuario. La contrasena se almacena como hash bcrypt; nunca se guarda en texto plano. Si ya existe un usuario con el mismo email, la peticion falla con 400.

**Rol requerido:** Sin control de acceso

**Request Body:**
```json
{
  "name": "Adria Bofill",
  "email": "adria@hipica.com",
  "password": "contrasena_segura",
  "role": "stable_admin",
  "stable_id": 1,
  "is_active": true
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nombre completo del usuario |
| email | string | Si | Correo electronico (unico en el sistema) |
| password | string | Si | Contrasena en texto plano (se hashea internamente) |
| role | string | No (default: `"client"`) | Rol del usuario: `app_admin`, `stable_admin`, `monitor`, `client` |
| stable_id | integer | No | ID de la hipica. Puede ser `null` para `app_admin` global |
| is_active | boolean | No (default: `true`) | Si el usuario puede autenticarse |

**Response 200:**
```json
{
  "id": 4,
  "name": "Adria Bofill",
  "email": "adria@hipica.com",
  "role": "stable_admin",
  "stable_id": 1,
  "is_active": true
}
```

La contrasena nunca se incluye en la respuesta.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | Ya existe un usuario con ese email |
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/users/

Lista todos los usuarios del sistema, sin filtrar por hipica.

**Rol requerido:** Sin control de acceso

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Admin Global",
    "email": "admin@hipica.com",
    "role": "app_admin",
    "stable_id": null,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Monitor Joan",
    "email": "joan@hipica.com",
    "role": "monitor",
    "stable_id": 1,
    "is_active": true
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| — | Este endpoint no produce errores conocidos |

---

### GET /api/v1/users/{user_id}

Obtiene un usuario por su ID.

**Rol requerido:** Sin control de acceso

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| user_id | integer | ID del usuario |

**Response 200:**
```json
{
  "id": 2,
  "name": "Monitor Joan",
  "email": "joan@hipica.com",
  "role": "monitor",
  "stable_id": 1,
  "is_active": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe un usuario con el ID indicado |

---

### PUT /api/v1/users/{user_id}

Actualiza un usuario existente. Solo se actualizan los campos incluidos en el cuerpo (actualizacion parcial mediante `exclude_unset`). No permite cambiar la contrasena por este endpoint.

**Rol requerido:** Sin control de acceso

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| user_id | integer | ID del usuario a actualizar |

**Request Body (todos los campos son opcionales):**
```json
{
  "name": "Monitor Joan Actualizado",
  "email": "joan_nou@hipica.com",
  "role": "stable_admin",
  "stable_id": 2,
  "is_active": false
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | No | Nuevo nombre |
| email | string | No | Nuevo email |
| role | string | No | Nuevo rol |
| stable_id | integer | No | Nueva hipica asignada |
| is_active | boolean | No | Nuevo estado de activacion |

**Response 200:**
```json
{
  "id": 2,
  "name": "Monitor Joan Actualizado",
  "email": "joan_nou@hipica.com",
  "role": "stable_admin",
  "stable_id": 2,
  "is_active": false
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe un usuario con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/users/{user_id}

Elimina un usuario por su ID.

**Rol requerido:** Sin control de acceso

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| user_id | integer | ID del usuario a eliminar |

**Response 200:**
```json
{
  "ok": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe un usuario con el ID indicado |
