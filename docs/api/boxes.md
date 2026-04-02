# API: Boxes

Base URL: `/api/v1/boxes`

Gestion de boxes (cuadras/compartimentos) de la hipica. Cada box pertenece a una hipica (`stable_id`) y puede tener caballos asignados.

**Multi-tenant:** `app_admin` ve y opera sobre boxes de todas las hipicas. El resto de roles solo accede a los boxes de su propia hipica (`stable_id` del token).

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol minimo requerido |
|--------|------|-------------|----------------------|
| POST | `/` | Crear un box | `stable_admin` |
| GET | `/` | Listar boxes de la cuadra | `monitor` |
| GET | `/{box_id}` | Obtener un box por ID | `monitor` |
| PUT | `/{box_id}` | Actualizar un box | `stable_admin` |
| DELETE | `/{box_id}` | Eliminar un box | `stable_admin` |

---

## Detalle de Endpoints

### POST /api/v1/boxes/

Crea un nuevo box. El `stable_id` se fuerza al de la cuadra del usuario autenticado; `app_admin` puede indicarlo explicitamente en el cuerpo.

**Rol requerido:** `stable_admin` o `app_admin`

**Request Body:**
```json
{
  "name": "A1",
  "capacity": 1,
  "stable_id": 1
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nombre o codigo del box |
| capacity | integer | No (default: `1`) | Capacidad maxima de caballos |
| stable_id | integer | Si | ID de la hipica. Ignorado para `stable_admin` (se sobreescribe con el del token) |

**Response 201:**
```json
{
  "id": 1,
  "name": "A1",
  "capacity": 1,
  "stable_id": 1,
  "is_active": true,
  "horses_count": 0
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `stable_admin` o `app_admin`) |
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/boxes/

Devuelve los boxes de la cuadra del usuario autenticado. `app_admin` recibe boxes de todas las hipicas.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "A1",
    "capacity": 1,
    "stable_id": 1,
    "is_active": true,
    "horses_count": 2
  },
  {
    "id": 2,
    "name": "B3",
    "capacity": 2,
    "stable_id": 1,
    "is_active": true,
    "horses_count": 0
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `monitor` o superior) |

---

### GET /api/v1/boxes/{box_id}

Obtiene un box por su ID. Si el box no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| box_id | integer | ID del box |

**Response 200:**
```json
{
  "id": 1,
  "name": "A1",
  "capacity": 1,
  "stable_id": 1,
  "is_active": true,
  "horses_count": 2
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o box de otra hipica |
| 404 | No existe un box con el ID indicado |

---

### PUT /api/v1/boxes/{box_id}

Actualiza los datos de un box. Si el box no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| box_id | integer | ID del box a actualizar |

**Request Body:**
```json
{
  "name": "A1-bis",
  "capacity": 2,
  "is_active": false
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | No | Nuevo nombre del box |
| capacity | integer | No | Nueva capacidad |
| is_active | boolean | No | Estado del box |

**Response 200:**
```json
{
  "id": 1,
  "name": "A1-bis",
  "capacity": 2,
  "stable_id": 1,
  "is_active": false,
  "horses_count": 1
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o box de otra hipica |
| 404 | No existe un box con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/boxes/{box_id}

Elimina un box por su ID. Devuelve 409 si el box tiene caballos asignados.

**Rol requerido:** `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| box_id | integer | ID del box a eliminar |

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
| 403 | Rol insuficiente o box de otra hipica |
| 404 | No existe un box con el ID indicado |
| 409 | El box tiene caballos asignados y no puede eliminarse |
