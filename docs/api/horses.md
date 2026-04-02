# API: Horses

Base URL: `/api/v1/horses`

Gestion de caballos de la hipica. Cada caballo pertenece a una hipica (`stable_id`) y puede tener niveles de equitacion asignados.

**Multi-tenant:** `app_admin` ve y opera sobre caballos de todas las hipicas. El resto de roles solo accede a los caballos de su propia hipica (`stable_id` del token).

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol minimo requerido |
|--------|------|-------------|----------------------|
| POST | `/` | Crear un caballo | `stable_admin` |
| GET | `/` | Listar caballos de la cuadra | `monitor` |
| GET | `/{horse_id}` | Obtener un caballo por ID | `monitor` |
| PUT | `/{horse_id}` | Actualizar un caballo | `stable_admin` |
| DELETE | `/{horse_id}` | Eliminar un caballo | `stable_admin` |
| PUT | `/{horse_id}/levels` | Asignar niveles de equitacion | `stable_admin` |

---

## Detalle de Endpoints

### POST /api/v1/horses/

Crea un nuevo caballo. El `stable_id` se fuerza al de la cuadra del usuario autenticado; `app_admin` puede indicarlo explicitamente en el cuerpo.

**Rol requerido:** `stable_admin` o `app_admin`

**Request Body:**
```json
{
  "name": "Tornado",
  "is_active": true,
  "stable_id": 1
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nombre del caballo |
| is_active | boolean | No (default: `true`) | Si el caballo esta disponible |
| stable_id | integer | Si | ID de la hipica. Ignorado para `stable_admin` (se sobreescribe con el del token) |

**Response 201:**
```json
{
  "id": 5,
  "name": "Tornado",
  "is_active": true,
  "stable_id": 1,
  "box_id": null,
  "box_name": null,
  "levels": []
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `stable_admin` o `app_admin`) |
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/horses/

Devuelve los caballos de la cuadra del usuario autenticado. `app_admin` recibe caballos de todas las hipicas.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Relampago",
    "is_active": true,
    "stable_id": 1,
    "box_id": 3,
    "box_name": "B1",
    "levels": ["principiante"]
  },
  {
    "id": 2,
    "name": "Tornado",
    "is_active": false,
    "stable_id": 1,
    "box_id": null,
    "box_name": null,
    "levels": []
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `monitor` o superior) |

---

### GET /api/v1/horses/{horse_id}

Obtiene un caballo por su ID. Si el caballo no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| horse_id | integer | ID del caballo |

**Response 200:**
```json
{
  "id": 1,
  "name": "Relampago",
  "is_active": true,
  "stable_id": 1,
  "box_id": 3,
  "box_name": "B1",
  "levels": ["principiante"]
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o caballo de otra hipica |
| 404 | No existe un caballo con el ID indicado |

---

### PUT /api/v1/horses/{horse_id}

Actualiza los datos de un caballo existente. Si se incluye el campo `levels`, reemplaza completamente los niveles asociados. Si el caballo no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| horse_id | integer | ID del caballo a actualizar |

**Request Body:**
```json
{
  "name": "Relampago II",
  "is_active": true,
  "stable_id": 2,
  "box_id": 5,
  "levels": ["iniciado"]
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | No | Nuevo nombre del caballo |
| stable_id | integer | No | ID de la hipica |
| is_active | boolean | No | Estado del caballo |
| box_id | integer | No | ID del box asignado (ver `/api/v1/boxes`) |
| levels | array[string] | No | Lista de valores del enum `NivelEquitacion`. Si se incluye, reemplaza todos los niveles anteriores |

**Response 200:**
```json
{
  "id": 1,
  "name": "Relampago II",
  "is_active": true,
  "stable_id": 2,
  "box_id": 5,
  "box_name": "C4",
  "levels": ["iniciado"]
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | Alguno de los niveles enviados no existe en el catalogo |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o caballo de otra hipica |
| 404 | No existe un caballo con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/horses/{horse_id}

Elimina un caballo por su ID. Si el caballo no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| horse_id | integer | ID del caballo a eliminar |

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
| 403 | Rol insuficiente o caballo de otra hipica |
| 404 | No existe un caballo con el ID indicado |

---

### PUT /api/v1/horses/{horse_id}/levels

Asigna o reemplaza los niveles de equitacion de un caballo. La lista enviada sustituye completamente los niveles anteriores. Si el caballo no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| horse_id | integer | ID del caballo |

**Request Body:**

Array de valores del enum `NivelEquitacion`:

```json
["principiante", "iniciado"]
```

Valores posibles del enum:

| Valor | Descripcion |
|-------|-------------|
| `principiante` | Personas sin experiencia previa |
| `iniciado` | Personas con nociones basicas |
| `experto` | Jinetes avanzados |

**Response 200:**
```json
{
  "id": 1,
  "name": "Relampago",
  "is_active": true,
  "stable_id": 1,
  "box_id": 3,
  "box_name": "B1",
  "levels": ["principiante", "iniciado"]
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | Alguno de los niveles enviados no existe en el catalogo |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o caballo de otra hipica |
| 404 | No existe un caballo con el ID indicado |
| 422 | Formato del cuerpo invalido |
