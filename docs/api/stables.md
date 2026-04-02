# API: Stables

Base URL: `/api/v1/stables`

Gestion de hipicas. Una hipica (`Stable`) es la entidad raiz del modelo multi-tenant: todos los usuarios, caballos, clientes y lecciones pertenecen a una hipica.

> **Alerta de seguridad:** Ningun endpoint de este recurso tiene control de acceso (`require_role`). Cualquier peticion puede crear, modificar o eliminar hipicas. Se recomienda proteger al menos `POST /`, `PATCH /{id}` y `DELETE /{id}` con el rol `app_admin`. Revisar con `backend-dev`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear una hipica | Sin control (ver alerta) |
| GET | `/` | Listar todas las hipicas | Sin control (ver alerta) |
| GET | `/{stable_id}` | Obtener una hipica por ID | Sin control (ver alerta) |
| PATCH | `/{stable_id}` | Actualizar parcialmente una hipica | Sin control (ver alerta) |
| DELETE | `/{stable_id}` | Eliminar una hipica | Sin control (ver alerta) |

---

## Detalle de Endpoints

### POST /api/v1/stables/

Crea una nueva hipica.

**Rol requerido:** Sin control de acceso

**Request Body:**
```json
{
  "name": "Hipica Can Bofill",
  "location": "Barcelona",
  "is_active": true
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nombre de la hipica |
| location | string | Si | Ubicacion o direccion |
| is_active | boolean | No (default: `true`) | Si la hipica esta operativa |

**Response 200:**
```json
{
  "id": 1,
  "name": "Hipica Can Bofill",
  "location": "Barcelona",
  "is_active": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/stables/

Lista todas las hipicas registradas.

**Rol requerido:** Sin control de acceso

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Hipica Can Bofill",
    "location": "Barcelona",
    "is_active": true
  },
  {
    "id": 2,
    "name": "Centre Equestre Garraf",
    "location": "Vilanova i la Geltru",
    "is_active": true
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| — | Este endpoint no produce errores conocidos |

---

### GET /api/v1/stables/{stable_id}

Obtiene una hipica por su ID.

**Rol requerido:** Sin control de acceso

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| stable_id | integer | ID de la hipica |

**Response 200:**
```json
{
  "id": 1,
  "name": "Hipica Can Bofill",
  "location": "Barcelona",
  "is_active": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe una hipica con el ID indicado |

---

### PATCH /api/v1/stables/{stable_id}

Actualiza parcialmente una hipica. Solo se modifican los campos incluidos en el cuerpo; los campos omitidos conservan su valor actual.

**Rol requerido:** Sin control de acceso

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| stable_id | integer | ID de la hipica a actualizar |

**Request Body (todos los campos son opcionales):**
```json
{
  "name": "Hipica Can Bofill Renovada",
  "location": "Badalona",
  "is_active": false
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | No | Nuevo nombre |
| location | string | No | Nueva ubicacion |
| is_active | boolean | No | Nuevo estado operativo |

**Response 200:**
```json
{
  "id": 1,
  "name": "Hipica Can Bofill Renovada",
  "location": "Badalona",
  "is_active": false
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe una hipica con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/stables/{stable_id}

Elimina una hipica por su ID.

**Rol requerido:** Sin control de acceso

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| stable_id | integer | ID de la hipica a eliminar |

**Response 200:**
```json
{
  "ok": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe una hipica con el ID indicado |
