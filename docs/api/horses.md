# API: Horses

Base URL: `/api/v1/horses`

Gestion de caballos de la hipica. Cada caballo pertenece a una hipica (`stable_id`) y puede tener niveles de equitacion asignados.

> **Alerta de seguridad:** Los endpoints `POST /`, `GET /`, `GET /{id}`, `PUT /{id}` y `DELETE /{id}` no tienen ningun control de acceso (`require_role`) en su implementacion actual. Cualquier peticion, autenticada o no, puede ejecutarlos. Se recomienda revisar con `backend-dev`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear un caballo | Sin control (ver alerta) |
| GET | `/` | Listar todos los caballos | Sin control (ver alerta) |
| GET | `/{horse_id}` | Obtener un caballo por ID | Sin control (ver alerta) |
| PUT | `/{horse_id}` | Actualizar un caballo | Sin control (ver alerta) |
| DELETE | `/{horse_id}` | Eliminar un caballo | Sin control (ver alerta) |
| PUT | `/{horse_id}/levels` | Asignar niveles de equitacion | `stable_admin` o `app_admin` |

---

## Detalle de Endpoints

### POST /api/v1/horses/

Crea un nuevo caballo. El cuerpo de la peticion usa directamente el modelo ORM `Horse`.

**Rol requerido:** Sin control de acceso

**Request Body:**
```json
{
  "name": "Tornado",
  "is_active": true,
  "stable_id": 1,
  "box": "A3"
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nombre del caballo |
| is_active | boolean | No (default: `true`) | Si el caballo esta disponible |
| stable_id | integer | Si | ID de la hipica a la que pertenece |
| box | string | No | Numero o codigo del box |

**Response 200:**
```json
{
  "id": 5,
  "name": "Tornado",
  "is_active": true,
  "stable_id": 1,
  "box": "A3"
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/horses/

Devuelve todos los caballos registrados en la base de datos, sin filtrar por hipica.

**Rol requerido:** Sin control de acceso

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Relampago",
    "is_active": true,
    "stable_id": 1,
    "box": "B1"
  },
  {
    "id": 2,
    "name": "Tornado",
    "is_active": false,
    "stable_id": 1,
    "box": null
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| — | Este endpoint no produce errores conocidos |

---

### GET /api/v1/horses/{horse_id}

Obtiene un caballo por su ID.

**Rol requerido:** Sin control de acceso

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
  "box": "B1"
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe un caballo con el ID indicado |

---

### PUT /api/v1/horses/{horse_id}

Actualiza los datos de un caballo existente. Solo actualiza `name` y `stable_id`; el campo `box` no se actualiza por este endpoint.

**Rol requerido:** Sin control de acceso

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
  "box": "C4"
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nuevo nombre del caballo |
| stable_id | integer | Si | ID de la hipica |
| is_active | boolean | No | Estado del caballo |
| box | string | No | Box (ignorado por la logica actual del endpoint) |

**Response 200:**
```json
{
  "id": 1,
  "name": "Relampago II",
  "is_active": true,
  "stable_id": 2,
  "box": "B1"
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe un caballo con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/horses/{horse_id}

Elimina un caballo por su ID.

**Rol requerido:** Sin control de acceso

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
| 404 | No existe un caballo con el ID indicado |

---

### PUT /api/v1/horses/{horse_id}/levels

Asigna o reemplaza los niveles de equitacion de un caballo. La lista enviada sustituye completamente los niveles anteriores.

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
  "box": "B1"
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | Alguno de los niveles enviados no existe en el catalogo |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `stable_admin` o `app_admin`) |
| 404 | No existe un caballo con el ID indicado |
| 422 | Formato del cuerpo invalido |
