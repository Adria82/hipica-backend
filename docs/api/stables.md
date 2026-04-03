# API: Stables

Base URL: `/api/v1/stables`

Gestion de hipicas. Una hipica (`Stable`) es la entidad raiz del modelo multi-tenant: todos los usuarios, caballos, clientes y lecciones pertenecen a una hipica.

El campo `theme` determina que carpeta de branding usa el frontend para esta hipica (logo, assets). Ver `docs/features/branding-por-tema.md`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear una hipica | `app_admin` |
| GET | `/` | Listar todas las hipicas | `app_admin` |
| GET | `/{stable_id}` | Obtener una hipica por ID | `stable_admin` (solo la propia) o `app_admin` |
| PATCH | `/{stable_id}` | Actualizar parcialmente una hipica | `app_admin` |
| DELETE | `/{stable_id}` | Eliminar una hipica | `app_admin` |

---

## Detalle de Endpoints

### POST /api/v1/stables/

Crea una nueva hipica.

**Rol requerido:** `app_admin`

**Request Body:**
```json
{
  "name": "Hipica Can Bofill",
  "location": "Barcelona",
  "is_active": true,
  "theme": "default"
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nombre de la hipica |
| location | string | Si | Ubicacion o direccion |
| is_active | boolean | No (default: `true`) | Si la hipica esta operativa |
| theme | string | No (default: `"default"`) | Identificador de carpeta de branding |

**Response 201:**
```json
{
  "id": 1,
  "name": "Hipica Can Bofill",
  "location": "Barcelona",
  "is_active": true,
  "theme": "default"
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `app_admin`) |
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/stables/

Lista todas las hipicas registradas. No filtra por hipica del usuario.

**Rol requerido:** `app_admin`

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Hipica Can Bofill",
    "location": "Barcelona",
    "is_active": true,
    "theme": "default"
  },
  {
    "id": 2,
    "name": "Centre Equestre Garraf",
    "location": "Vilanova i la Geltru",
    "is_active": true,
    "theme": "garraf"
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `app_admin`) |

---

### GET /api/v1/stables/{stable_id}

Obtiene una hipica por su ID.

`stable_admin` puede consultar unicamente su propia hipica (aquella cuyo `id` coincide con su `stable_id`). Si intenta consultar otra hipica, recibe 403.

**Rol requerido:** `stable_admin` (solo la propia) o `app_admin`

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
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o `stable_admin` intentando acceder a una hipica que no es la suya |
| 404 | No existe una hipica con el ID indicado |

---

### PATCH /api/v1/stables/{stable_id}

Actualiza parcialmente una hipica. Solo se modifican los campos incluidos en el cuerpo; los campos omitidos conservan su valor actual.

**Rol requerido:** `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| stable_id | integer | ID de la hipica a actualizar |

**Request Body (todos los campos son opcionales):**
```json
{
  "name": "Hipica Can Bofill Renovada",
  "location": "Badalona",
  "is_active": false,
  "theme": "bofill"
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | No | Nuevo nombre |
| location | string | No | Nueva ubicacion |
| is_active | boolean | No | Nuevo estado operativo |
| theme | string | No | Identificador de carpeta de branding |

**Response 200:**
```json
{
  "id": 1,
  "name": "Hipica Can Bofill Renovada",
  "location": "Badalona",
  "is_active": false,
  "theme": "bofill"
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `app_admin`) |
| 404 | No existe una hipica con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/stables/{stable_id}

Elimina una hipica por su ID.

**Rol requerido:** `app_admin`

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
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `app_admin`) |
| 404 | No existe una hipica con el ID indicado |
