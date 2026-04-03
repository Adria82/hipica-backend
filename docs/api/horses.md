# API: Horses

Base URL: `/api/v1/horses`

Gestion de caballos de la hipica. Cada caballo pertenece a una hipica (`stable_id`) y puede tener niveles de equitacion asignados mediante sus IDs.

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

## Esquema HorseRead

```json
{
  "id": 1,
  "name": "Relampago",
  "is_active": true,
  "stable_id": 1,
  "stable_name": "Hipica Can Bofill",
  "box_id": 3,
  "box_name": "B1",
  "levels": ["Principiant", "Iniciat"],
  "level_ids": [1, 2]
}
```

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | integer | Identificador unico |
| `name` | string | Nombre del caballo |
| `is_active` | boolean | Si el caballo esta disponible |
| `stable_id` | integer | ID de la hipica |
| `stable_name` | string \| null | Nombre de la hipica |
| `box_id` | integer \| null | ID del box asignado |
| `box_name` | string \| null | Nombre del box |
| `levels` | array[string] | Nombres de los niveles localizados segun `Accept-Language` de la request |
| `level_ids` | array[integer] | IDs de los niveles asignados (para uso en formularios del frontend) |

> **Nota sobre `levels`:** El endpoint resuelve el nombre de cada nivel en el idioma indicado por la cabecera `Accept-Language` (ca/es/en). Si el idioma solicitado no tiene traduccion, hace fallback a `es` y luego a `ca`.

---

## Detalle de Endpoints

### POST /api/v1/horses/

Crea un nuevo caballo. El `stable_id` se fuerza al de la cuadra del usuario autenticado; `app_admin` puede indicarlo explicitamente.

**Rol requerido:** `stable_admin` o `app_admin`

**Request Body:**
```json
{
  "name": "Tornado",
  "is_active": true,
  "stable_id": 1,
  "box_id": 2
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nombre del caballo |
| is_active | boolean | No (default: `true`) | Si el caballo esta disponible |
| stable_id | integer | Si | ID de la hipica. Ignorado para `stable_admin` |
| box_id | integer | No | ID del box a asignar |

**Response 201:** Objeto `HorseRead`.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente |
| 409 | El box esta lleno |
| 422 | Datos de entrada invalidos |

---

### GET /api/v1/horses/

Devuelve los caballos de la cuadra del usuario autenticado. `app_admin` recibe caballos de todas las hipicas.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Cabeceras:**

| Cabecera | Descripcion |
|----------|-------------|
| `Accept-Language` | Idioma para los nombres de niveles (`ca`, `es`, `en`). Default: `ca`. |

**Response 200:** Array de `HorseRead`.

---

### GET /api/v1/horses/{horse_id}

Obtiene un caballo por su ID.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Response 200:** Objeto `HorseRead`.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o caballo de otra hipica |
| 404 | No existe un caballo con el ID indicado |

---

### PUT /api/v1/horses/{horse_id}

Actualiza los datos de un caballo. Si se incluye `levels`, reemplaza completamente los niveles asociados (acepta lista de IDs).

**Rol requerido:** `stable_admin` o `app_admin`

**Request Body:**
```json
{
  "name": "Relampago II",
  "is_active": true,
  "box_id": 5,
  "levels": [1, 3]
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | No | Nuevo nombre del caballo |
| stable_id | integer | No | ID de la hipica |
| is_active | boolean | No | Estado del caballo |
| box_id | integer | No | ID del box asignado |
| levels | array[integer] | No | Lista de IDs de niveles. Si se incluye, reemplaza todos los niveles anteriores |

**Response 200:** Objeto `HorseRead`.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | Alguno de los IDs de niveles no existe |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o caballo de otra hipica |
| 404 | No existe un caballo con el ID indicado |
| 409 | El box esta lleno |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/horses/{horse_id}

Elimina un caballo por su ID.

**Rol requerido:** `stable_admin` o `app_admin`

**Response 200:**
```json
{ "ok": true }
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o caballo de otra hipica |
| 404 | No existe un caballo con el ID indicado |

---

### PUT /api/v1/horses/{horse_id}/levels

Asigna o reemplaza los niveles de equitacion de un caballo. Acepta una lista de IDs de nivel.

**Rol requerido:** `stable_admin` o `app_admin`

**Request Body:**

Array de IDs de nivel:

```json
[1, 2]
```

**Response 200:** Objeto `HorseRead` con los niveles actualizados.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | Alguno de los IDs de niveles no existe |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o caballo de otra hipica |
| 404 | No existe un caballo con el ID indicado |
| 422 | Formato del cuerpo invalido |
