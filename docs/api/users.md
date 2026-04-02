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

**Multi-tenant:** `app_admin` ve y opera sobre usuarios de todas las hipicas. `stable_admin` solo ve y gestiona usuarios de su propia hipica.

**Restriccion de roles elevados:** `stable_admin` no puede crear ni modificar usuarios con rol `app_admin` o `stable_admin`. Intentarlo devuelve 403.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear un usuario | `stable_admin` (solo roles `monitor`/`client`) o `app_admin` |
| GET | `/` | Listar usuarios | `stable_admin` (propia cuadra) o `app_admin` |
| GET | `/{user_id}` | Obtener un usuario por ID | `stable_admin` (propia cuadra) o `app_admin` |
| PUT | `/{user_id}` | Actualizar un usuario | `stable_admin` (sin escalar roles) o `app_admin` |
| DELETE | `/{user_id}` | Eliminar un usuario | `app_admin` |

---

## Detalle de Endpoints

### POST /api/v1/users/

Crea un nuevo usuario. La contrasena se almacena como hash bcrypt; nunca se guarda en texto plano. Si ya existe un usuario con el mismo email, la peticion falla con 400.

- `app_admin` puede crear usuarios con cualquier rol y en cualquier hipica.
- `stable_admin` solo puede crear usuarios con rol `monitor` o `client`, y el `stable_id` se fuerza al de su cuadra.

**Rol requerido:** `stable_admin` o `app_admin`

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
| role | string | No (default: `"client"`) | Rol del usuario: `app_admin`, `stable_admin`, `monitor`, `client`. `stable_admin` solo puede asignar `monitor` o `client` |
| stable_id | integer | No | ID de la hipica. Ignorado para `stable_admin` (se sobreescribe con el del token). Puede ser `null` para `app_admin` global |
| is_active | boolean | No (default: `true`) | Si el usuario puede autenticarse |

**Response 201:**
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
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente, o `stable_admin` intentando asignar un rol elevado (`app_admin` o `stable_admin`) |
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/users/

Lista usuarios del sistema. `stable_admin` ve solo los usuarios de su propia hipica. `app_admin` ve todos.

**Rol requerido:** `stable_admin` o `app_admin`

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
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `stable_admin` o `app_admin`) |

---

### GET /api/v1/users/{user_id}

Obtiene un usuario por su ID. `stable_admin` solo puede consultar usuarios de su propia hipica.

**Rol requerido:** `stable_admin` (propia cuadra) o `app_admin`

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
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o usuario de otra hipica |
| 404 | No existe un usuario con el ID indicado |

---

### PUT /api/v1/users/{user_id}

Actualiza un usuario existente. Solo se actualizan los campos incluidos en el cuerpo (`exclude_unset`). No permite cambiar la contrasena por este endpoint.

- `app_admin` puede modificar cualquier campo de cualquier usuario.
- `stable_admin` puede modificar usuarios de su cuadra, pero no puede asignarles roles elevados (`app_admin` o `stable_admin`).

**Rol requerido:** `stable_admin` (sin escalar roles) o `app_admin`

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
| role | string | No | Nuevo rol. `stable_admin` no puede asignar `app_admin` ni `stable_admin` |
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
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente, usuario de otra hipica, o `stable_admin` intentando escalar a rol elevado |
| 404 | No existe un usuario con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/users/{user_id}

Elimina un usuario por su ID. Solo accesible para `app_admin`.

**Rol requerido:** `app_admin`

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
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `app_admin`) |
| 404 | No existe un usuario con el ID indicado |
