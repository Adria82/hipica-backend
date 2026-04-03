# API: Lessons

Base URL: `/api/v1/lessons`

Gestion de lecciones/clases de la hipica. Cada leccion tiene una fecha y hora, un instructor, una hipica de referencia, y esta asociada a multiples alumnos y caballos mediante relaciones N:N.

Los alumnos ya no son entidades `Client` independientes: son usuarios con `role="client"` consultados via `GET /api/v1/users?role=client`. Ver `docs/features/unificacion-client-user.md`.

**Multi-tenant:** El `stable_id` de la leccion se fuerza siempre al del usuario autenticado (salvo `app_admin`). El filtrado en el listado se aplica automaticamente desde el token; ya no existe un query param `stable_id`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol minimo requerido |
|--------|------|-------------|----------------------|
| POST | `/` | Crear una leccion | `stable_admin` |
| GET | `/` | Listar lecciones de la cuadra | `monitor` / `assistant` |
| GET | `/{lesson_id}` | Obtener una leccion por ID | `monitor` / `assistant` |
| PUT | `/{lesson_id}` | Actualizar una leccion | `stable_admin` |
| DELETE | `/{lesson_id}` | Eliminar una leccion | `stable_admin` |

---

## Schemas de referencia

### LessonRead (respuesta)

La respuesta devuelve nombres desnormalizados para facilitar la presentacion en el frontend, sin necesidad de consultas adicionales.

```json
{
  "id": 1,
  "date_time": "2026-03-15T10:00:00",
  "end_time": null,
  "instructor_id": 2,
  "instructor_email": "juan@hipica.com",
  "helper_id": null,
  "helper_email": null,
  "track_id": null,
  "track_name": null,
  "description": null,
  "stable_id": 1,
  "student_names": ["Carlos", "Ana"],
  "horse_names": ["Trueno", "Rayo"]
}
```

---

## Detalle de Endpoints

### POST /api/v1/lessons/

Crea una nueva leccion y asocia alumnos y caballos. Si alguno de los IDs de alumnos o caballos no existe, la peticion falla con 404. El `stable_id` se fuerza al del usuario autenticado; `app_admin` puede indicarlo en el cuerpo.

**Rol requerido:** `stable_admin` o `app_admin`

**Request Body:**
```json
{
  "date_time": "2026-03-15T10:00:00",
  "end_time": "2026-03-15T11:00:00",
  "stable_id": 1,
  "instructor_id": 2,
  "helper_id": null,
  "track_id": null,
  "description": null,
  "student_ids": [3, 4],
  "horse_ids": [1, 2]
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| date_time | datetime (ISO 8601) | Si | Fecha y hora de inicio de la leccion |
| end_time | datetime (ISO 8601) | No | Fecha y hora de fin |
| stable_id | integer | No | ID de la hipica. Ignorado para roles distintos de `app_admin` (se sobreescribe con el del token) |
| instructor_id | integer | Si | ID del usuario instructor principal |
| helper_id | integer | No | ID del usuario ayudante (`role=assistant`) |
| track_id | integer | No | ID de la pista donde se celebra |
| description | string | No | Notas adicionales |
| student_ids | array[integer] | No (default: `[]`) | IDs de usuarios con `role=client` que asisten |
| horse_ids | array[integer] | No (default: `[]`) | IDs de caballos usados |

**Response 201:** Objeto `LessonRead` completo (ver schema de referencia arriba).

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `stable_admin` o `app_admin`) |
| 404 | Alguno de los `student_ids` o `horse_ids` no existe |
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
    "instructor_email": "juan@hipica.com",
    "stable_id": 1,
    "student_names": ["Carlos", "Ana"],
    "horse_names": ["Trueno"]
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

Actualiza una leccion existente. Todos los campos son opcionales; solo se actualizan los que se incluyan en el cuerpo. Si se proporcionan `student_ids` o `horse_ids`, las relaciones anteriores se eliminan y se reemplazan por las nuevas. Si la leccion no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

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
  "student_ids": [3, 5],
  "horse_ids": [1]
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| date_time | datetime (ISO 8601) | No | Nueva fecha y hora de inicio |
| end_time | datetime (ISO 8601) | No | Nueva fecha y hora de fin (puede ser `null` para limpiar) |
| instructor_id | integer | No | Nuevo instructor |
| helper_id | integer | No | Nuevo ayudante (puede ser `null` para limpiar) |
| track_id | integer | No | Nueva pista (puede ser `null` para limpiar) |
| description | string | No | Nueva descripcion (puede ser `null` para limpiar) |
| stable_id | integer | No | Nueva hipica |
| student_ids | array[integer] | No | Sustituye la lista de alumnos. Si se omite, no cambia |
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
