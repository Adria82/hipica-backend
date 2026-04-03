# API: Tracks

Base URL: `/api/v1/tracks`

Gestion de pistas de equitacion dentro de una hipica. Una pista (`Track`) es el espacio fisico donde se celebran las clases. Se asocia opcionalmente a una `Lesson` a traves del campo `track_id`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| GET | `/` | Listar pistas de la hipica | `monitor`, `stable_admin`, `app_admin` |
| POST | `/` | Crear una pista | `stable_admin`, `app_admin` |
| GET | `/{track_id}` | Obtener una pista por ID | `monitor`, `stable_admin`, `app_admin` |
| PUT | `/{track_id}` | Actualizar una pista | `stable_admin`, `app_admin` |
| DELETE | `/{track_id}` | Eliminar una pista | `stable_admin`, `app_admin` |

---

## Modelo de Datos

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | integer | Identificador unico |
| `name` | string | Nombre de la pista |
| `stable_id` | integer | FK a `stable.id`. Hipica a la que pertenece. |
| `is_active` | boolean | Si la pista esta activa (default: `true`) |

---

## Detalle de Endpoints

### GET /api/v1/tracks/

Lista todas las pistas de la hipica del usuario autenticado. El `app_admin` ve pistas de todas las hipicas.

**Rol requerido:** `monitor`, `stable_admin`, `app_admin`

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Pista Principal",
    "stable_id": 1,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Pista de Saltos",
    "stable_id": 1,
    "is_active": true
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente |

---

### POST /api/v1/tracks/

Crea una nueva pista. El `stable_id` se fuerza automaticamente al de la hipica del usuario autenticado (excepto para `app_admin`, que puede indicarlo libremente).

**Rol requerido:** `stable_admin`, `app_admin`

**Request Body:**
```json
{
  "name": "Pista de Dressage",
  "stable_id": 1
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `name` | string | Si | Nombre de la pista |
| `stable_id` | integer | Solo para `app_admin` | ID de la hipica. Para otros roles se ignora y se usa el del usuario. |

**Response 201:**
```json
{
  "id": 3,
  "name": "Pista de Dressage",
  "stable_id": 1,
  "is_active": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | No se pudo determinar el `stable_id` |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente |

---

### GET /api/v1/tracks/{track_id}

Obtiene una pista por su ID. Un usuario no puede acceder a pistas de otras hipicas (error 403).

**Rol requerido:** `monitor`, `stable_admin`, `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| track_id | integer | ID de la pista |

**Response 200:**
```json
{
  "id": 1,
  "name": "Pista Principal",
  "stable_id": 1,
  "is_active": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o pista de otra hipica |
| 404 | Pista no encontrada |

---

### PUT /api/v1/tracks/{track_id}

Actualiza los datos de una pista. Solo se modifican los campos incluidos en el body.

**Rol requerido:** `stable_admin`, `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| track_id | integer | ID de la pista a actualizar |

**Request Body (todos los campos son opcionales):**
```json
{
  "name": "Pista Norte",
  "is_active": false
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `name` | string | No | Nuevo nombre |
| `is_active` | boolean | No | Nuevo estado |

**Response 200:**
```json
{
  "id": 1,
  "name": "Pista Norte",
  "stable_id": 1,
  "is_active": false
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o pista de otra hipica |
| 404 | Pista no encontrada |

---

### DELETE /api/v1/tracks/{track_id}

Elimina una pista. No verifica si hay lecciones asociadas; la integridad referencial se gestiona a nivel de BD (la FK en `lesson.track_id` es nullable, por lo que las lecciones no se eliminan).

**Rol requerido:** `stable_admin`, `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| track_id | integer | ID de la pista a eliminar |

**Response 200:**
```json
{ "ok": true }
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o pista de otra hipica |
| 404 | Pista no encontrada |
