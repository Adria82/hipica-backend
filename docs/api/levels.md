# API: Levels

Base URL: `/api/v1/levels`

Gestion del catalogo de niveles de equitacion disponibles en la plataforma. Los niveles se asignan a caballos mediante el endpoint `PUT /horses/{id}/levels`.

Los valores posibles del enum `NivelEquitacion` son:

| Valor | Descripcion |
|-------|-------------|
| `principiante` | Personas sin experiencia previa |
| `iniciado` | Personas con nociones basicas |
| `experto` | Jinetes avanzados |

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear un nivel | `app_admin` |
| GET | `/` | Listar todos los niveles | Sin autenticacion |
| GET | `/{level_id}` | Obtener un nivel por ID | Sin autenticacion |
| DELETE | `/{level_id}` | Eliminar un nivel | `app_admin` |

---

## Detalle de Endpoints

### POST /api/v1/levels/

Crea un nuevo nivel de equitacion en el catalogo. El nombre debe ser uno de los valores del enum `NivelEquitacion` y debe ser unico; no se permiten duplicados.

**Rol requerido:** `app_admin`

**Request Body:**
```json
{
  "name": "principiante"
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string (enum) | Si | Valor del enum: `principiante`, `iniciado` o `experto` |

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
| 422 | El valor de `name` no pertenece al enum `NivelEquitacion` |

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
