# API: Levels

Base URL: `/api/v1/levels`

Gestion del catalogo de niveles de equitacion disponibles en la plataforma. Los niveles se asignan a caballos mediante el endpoint `PUT /horses/{id}/levels`.

Los valores posibles del enum `NivelEquitacion` son:

| Valor | Descripcion |
|-------|-------------|
| `principiante` | Personas sin experiencia previa |
| `iniciado` | Personas con nociones basicas |
| `experto` | Jinetes avanzados |

> **Nota de seguridad:** Los endpoints `POST /` y `DELETE /{id}` tienen el control de rol comentado en el codigo (`# current_user = Depends(require_role(["app_admin"]))`). Actualmente son accesibles sin autenticacion. Se recomienda revisar con `backend-dev`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear un nivel | Sin control (ver nota) |
| GET | `/` | Listar todos los niveles | Sin control |
| GET | `/{level_id}` | Obtener un nivel por ID | Sin control |
| DELETE | `/{level_id}` | Eliminar un nivel | Sin control (ver nota) |

---

## Detalle de Endpoints

### POST /api/v1/levels/

Crea un nuevo nivel de equitacion en el catalogo. El nombre debe ser uno de los valores del enum `NivelEquitacion` y debe ser unico; no se permiten duplicados.

**Rol requerido:** Sin control de acceso (deberia requerir `app_admin`)

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
| 422 | El valor de `name` no pertenece al enum `NivelEquitacion` |

---

### GET /api/v1/levels/

Lista todos los niveles de equitacion registrados en el catalogo.

**Rol requerido:** Sin control de acceso

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

**Rol requerido:** Sin control de acceso

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

**Rol requerido:** Sin control de acceso (deberia requerir `app_admin`)

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| level_id | integer | ID del nivel a eliminar |

**Response 204:** Sin contenido.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | El nivel tiene caballos asociados y no puede eliminarse |
| 404 | No existe un nivel con el ID indicado |
