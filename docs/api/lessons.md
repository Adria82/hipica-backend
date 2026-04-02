# API: Lessons

Base URL: `/api/v1/lessons`

Gestion de lecciones/clases de la hipica. Cada leccion tiene una fecha y hora, un instructor, una hipica de referencia, y esta asociada a multiples clientes y caballos mediante relaciones N:N.

**Multi-tenant:** El `stable_id` de la leccion se fuerza siempre al del usuario autenticado (salvo `app_admin`). El filtrado en el listado se aplica automaticamente desde el token; ya no existe un query param `stable_id`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol minimo requerido |
|--------|------|-------------|----------------------|
| POST | `/` | Crear una leccion | `monitor` |
| GET | `/` | Listar lecciones de la cuadra | `monitor` |
| GET | `/{lesson_id}` | Obtener una leccion por ID | `monitor` |
| PUT | `/{lesson_id}` | Actualizar una leccion | `monitor` |
| DELETE | `/{lesson_id}` | Eliminar una leccion | `monitor` |

---

## Schemas de referencia

### LessonRead (respuesta)

```json
{
  "id": 1,
  "date_time": "2026-03-15T10:00:00",
  "instructor_id": 2,
  "stable_id": 1,
  "clients": [
    {
      "id": 3,
      "name": "Joan Puig",
      "email": "joan@example.com",
      "phone": null,
      "is_active": true,
      "stable_id": 1
    }
  ],
  "horses": [
    {
      "id": 1,
      "name": "Relampago",
      "box": "B1",
      "is_active": true,
      "stable_id": 1,
      "levels": ["principiante"]
    }
  ]
}
```

---

## Detalle de Endpoints

### POST /api/v1/lessons/

Crea una nueva leccion y asocia clientes y caballos. Si alguno de los IDs de clientes o caballos no existe, la peticion falla con 404. El `stable_id` se fuerza al del usuario autenticado; `app_admin` puede indicarlo en el cuerpo.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Request Body:**
```json
{
  "date_time": "2026-03-15T10:00:00",
  "stable_id": 1,
  "instructor_id": 2,
  "client_ids": [3, 4],
  "horse_ids": [1, 2]
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| date_time | datetime (ISO 8601) | Si | Fecha y hora de la leccion |
| stable_id | integer | Si | ID de la hipica. Ignorado para roles distintos de `app_admin` (se sobreescribe con el del token) |
| instructor_id | integer | No | ID del usuario instructor |
| client_ids | array[integer] | Si | Lista de IDs de clientes que asisten |
| horse_ids | array[integer] | Si | Lista de IDs de caballos usados |

**Response 201:** Objeto `LessonRead` completo (ver schema de referencia arriba).

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `monitor` o superior) |
| 404 | Alguno de los `client_ids` o `horse_ids` no existe |
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/lessons/

Lista las lecciones de la cuadra del usuario autenticado. `app_admin` ve lecciones de todas las hipicas. El filtrado por hipica es automatico y no aceptable como query param.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Query Parameters:**

| Parametro | Tipo | Requerido | Descripcion |
|-----------|------|-----------|-------------|
| instructor_id | integer | No | Filtra lecciones de un instructor concreto |

**Ejemplo de peticion con filtro:**
```
GET /api/v1/lessons/?instructor_id=2
```

**Response 200:** Array de objetos `LessonRead`.

```json
[
  {
    "id": 1,
    "date_time": "2026-03-15T10:00:00",
    "instructor_id": 2,
    "stable_id": 1,
    "clients": [...],
    "horses": [...]
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `monitor` o superior) |

---

### GET /api/v1/lessons/{lesson_id}

Obtiene una leccion por su ID, incluyendo la lista completa de clientes y caballos asociados. Si la leccion no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| lesson_id | integer | ID de la leccion |

**Response 200:** Objeto `LessonRead` completo (ver schema de referencia).

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o leccion de otra hipica |
| 404 | No existe una leccion con el ID indicado |

---

### PUT /api/v1/lessons/{lesson_id}

Actualiza una leccion existente. Todos los campos son opcionales; solo se actualizan los que se incluyan en el cuerpo. Si se proporcionan `client_ids` o `horse_ids`, las relaciones anteriores se eliminan y se reemplazan por las nuevas. Si la leccion no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| lesson_id | integer | ID de la leccion a actualizar |

**Request Body:**
```json
{
  "date_time": "2026-03-15T11:00:00",
  "instructor_id": 3,
  "stable_id": 1,
  "client_ids": [3, 5],
  "horse_ids": [1]
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| date_time | datetime (ISO 8601) | No | Nueva fecha y hora |
| instructor_id | integer | No | Nuevo instructor |
| stable_id | integer | No | Nueva hipica |
| client_ids | array[integer] | No | Sustituye la lista de clientes. Si se omite, no cambia |
| horse_ids | array[integer] | No | Sustituye la lista de caballos. Si se omite, no cambia |

**Response 200:** Objeto `LessonRead` actualizado con las relaciones actuales.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o leccion de otra hipica |
| 404 | No existe una leccion con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/lessons/{lesson_id}

Elimina una leccion y todas sus relaciones N:N con clientes y caballos. Si la leccion no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| lesson_id | integer | ID de la leccion a eliminar |

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
| 403 | Rol insuficiente o leccion de otra hipica |
| 404 | No existe una leccion con el ID indicado |
