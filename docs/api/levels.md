# API: Levels

Base URL: `/api/v1/levels`

Gestion del catalogo de niveles de equitacion disponibles en la plataforma. Los niveles son textos libres definidos por el `app_admin`; no estan limitados a un enum predefinido. Se asignan a caballos mediante el endpoint `PUT /horses/{id}/levels`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear un nivel | `app_admin` |
| GET | `/` | Listar todos los niveles | Sin autenticacion |
| GET | `/{level_id}` | Obtener un nivel por ID | Sin autenticacion |
| PUT | `/{level_id}` | Renombrar un nivel | `app_admin` |
| DELETE | `/{level_id}` | Eliminar un nivel | `app_admin` |

---

## Detalle de Endpoints

### POST /api/v1/levels/

Crea un nuevo nivel de equitacion en el catalogo. El nombre es texto libre y debe ser unico; no se permiten duplicados.

**Rol requerido:** `app_admin`

**Request Body:**
```json
{
  "name": "Nivel Basico"
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nombre libre del nivel. Unico en el sistema. |

**Response 201:**
```json
{
  "id": 1,
  "name": "principiante"
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | Ya existe un nivel con ese nombre |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `app_admin`) |
| 422 | Datos de entrada invalidos |

---

### GET /api/v1/levels/

Lista todos los niveles de equitacion registrados en el catalogo.

**Rol requerido:** Sin control de acceso (endpoint publico)

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "principiante"
  },
  {
    "id": 2,
    "name": "iniciado"
  },
  {
    "id": 3,
    "name": "experto"
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| — | Este endpoint no produce errores conocidos |

---

### GET /api/v1/levels/{level_id}

Obtiene un nivel de equitacion por su ID.

**Rol requerido:** Sin control de acceso (endpoint publico)

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| level_id | integer | ID del nivel |

**Response 200:**
```json
{
  "id": 2,
  "name": "iniciado"
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe un nivel con el ID indicado |

---

### PUT /api/v1/levels/{level_id}

Renombra un nivel existente. Comprueba que el nuevo nombre no este ya en uso por otro nivel.

**Rol requerido:** `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| level_id | integer | ID del nivel a renombrar |

**Request Body:**
```json
{
  "name": "Nivel Avanzado"
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | No | Nuevo nombre del nivel |

**Response 200:**
```json
{
  "id": 2,
  "name": "Nivel Avanzado"
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | Ya existe otro nivel con el nombre indicado |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `app_admin`) |
| 404 | No existe un nivel con el ID indicado |

---

### DELETE /api/v1/levels/{level_id}

Elimina un nivel del catalogo. No se permite eliminar un nivel que este asociado a algun caballo.

**Rol requerido:** `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| level_id | integer | ID del nivel a eliminar |

**Response 204:** Sin contenido.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | El nivel tiene caballos asociados y no puede eliminarse |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `app_admin`) |
| 404 | No existe un nivel con el ID indicado |
