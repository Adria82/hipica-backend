# API: Boxes

Base URL: `/api/v1/boxes`

Gestion de boxes (cuadras/compartimentos) de la hipica. Cada box pertenece a una hipica (`stable_id`) y puede tener caballos asignados hasta su capacidad maxima.

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

## Esquema BoxRead

```json
{
  "id": 1,
  "name": "A1",
  "capacity": 2,
  "stable_id": 1,
  "stable_name": "Hipica Can Bofill",
  "is_active": true,
  "horses_count": 1,
  "horse_names": ["Trueno"]
}
```

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | integer | Identificador unico |
| `name` | string | Nombre o codigo del box |
| `capacity` | integer | Numero maximo de caballos |
| `stable_id` | integer | ID de la hipica |
| `stable_name` | string \| null | Nombre de la hipica |
| `is_active` | boolean | Si el box esta operativo |
| `horses_count` | integer | Numero de caballos actualmente asignados |
| `horse_names` | array[string] | Nombres de los caballos asignados al box |

---

## Detalle de Endpoints

### POST /api/v1/boxes/

Crea un nuevo box. El `stable_id` se fuerza al de la cuadra del usuario autenticado; `app_admin` puede indicarlo explicitamente.

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
| stable_id | integer | Si | ID de la hipica. Ignorado para `stable_admin` |

**Response 201:** Objeto `BoxRead`.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente |
| 422 | Datos de entrada invalidos |

---

### GET /api/v1/boxes/

Devuelve los boxes de la cuadra del usuario autenticado. `app_admin` recibe boxes de todas las hipicas.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Response 200:** Array de `BoxRead`.

---

### GET /api/v1/boxes/{box_id}

Obtiene un box por su ID.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Response 200:** Objeto `BoxRead`.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o box de otra hipica |
| 404 | No existe un box con el ID indicado |

---

### PUT /api/v1/boxes/{box_id}

Actualiza los datos de un box.

**Rol requerido:** `stable_admin` o `app_admin`

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

**Response 200:** Objeto `BoxRead` actualizado.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o box de otra hipica |
| 404 | No existe un box con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/boxes/{box_id}

Elimina un box. Devuelve 409 si tiene caballos asignados.

**Rol requerido:** `stable_admin` o `app_admin`

**Response 200:**
```json
{ "ok": true }
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o box de otra hipica |
| 404 | No existe un box con el ID indicado |
| 409 | El box tiene caballos asignados. El mensaje de error incluye sus nombres. |
