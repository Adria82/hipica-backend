# API: Clients

Base URL: `/api/v1/clients`

Gestion de clientes (alumnos) de la hipica. Cada cliente pertenece a una hipica (`stable_id`) y puede estar asociado a multiples lecciones.

**Multi-tenant:** `app_admin` ve y opera sobre clientes de todas las hipicas. El resto de roles solo accede a los clientes de su propia hipica (`stable_id` del token).

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol minimo requerido |
|--------|------|-------------|----------------------|
| POST | `/` | Crear un cliente | `stable_admin` |
| GET | `/` | Listar clientes de la cuadra | `monitor` |
| GET | `/{client_id}` | Obtener un cliente por ID | `monitor` |
| PUT | `/{client_id}` | Actualizar un cliente | `stable_admin` |
| DELETE | `/{client_id}` | Eliminar un cliente | `stable_admin` |

---

## Detalle de Endpoints

### POST /api/v1/clients/

Crea un nuevo cliente en la hipica. El `stable_id` se fuerza al de la cuadra del usuario autenticado; `app_admin` puede indicarlo explicitamente en el cuerpo.

**Rol requerido:** `stable_admin` o `app_admin`

**Request Body:**
```json
{
  "name": "Maria Garcia",
  "email": "maria@example.com",
  "phone": "612345678",
  "stable_id": 1,
  "is_active": true
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | Si | Nombre completo del cliente |
| email | string | No | Correo electronico |
| phone | string | No | Numero de telefono |
| stable_id | integer | Si | ID de la hipica. Ignorado para `stable_admin` (se sobreescribe con el del token) |
| is_active | boolean | No (default: `true`) | Si el cliente esta activo |

**Response 201:**
```json
{
  "id": 3,
  "name": "Maria Garcia",
  "email": "maria@example.com",
  "phone": "612345678",
  "stable_id": 1,
  "is_active": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `stable_admin` o `app_admin`) |
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/clients/

Devuelve los clientes de la cuadra del usuario autenticado. `app_admin` recibe clientes de todas las hipicas.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Joan Puig",
    "email": "joan@example.com",
    "phone": null,
    "stable_id": 1,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Maria Garcia",
    "email": "maria@example.com",
    "phone": "612345678",
    "stable_id": 1,
    "is_active": false
  }
]
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `monitor` o superior) |

---

### GET /api/v1/clients/{client_id}

Obtiene un cliente por su ID. Si el cliente no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `monitor`, `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| client_id | integer | ID del cliente |

**Response 200:**
```json
{
  "id": 1,
  "name": "Joan Puig",
  "email": "joan@example.com",
  "phone": null,
  "stable_id": 1,
  "is_active": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o cliente de otra hipica |
| 404 | No existe un cliente con el ID indicado |

---

### PUT /api/v1/clients/{client_id}

Actualiza los datos de un cliente. Solo se modifican los campos incluidos en el cuerpo (`exclude_unset`). Si el cliente no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| client_id | integer | ID del cliente a actualizar |

**Request Body:**
```json
{
  "name": "Joan Puig Nou",
  "email": "joan_nou@example.com",
  "phone": "699000111",
  "stable_id": 1,
  "is_active": true
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| name | string | No | Nuevo nombre |
| email | string | No | Nuevo email |
| phone | string | No | Nuevo telefono |
| stable_id | integer | No | Nueva hipica asignada |
| is_active | boolean | No | Nuevo estado |

**Response 200:**
```json
{
  "id": 1,
  "name": "Joan Puig Nou",
  "email": "joan_nou@example.com",
  "phone": "699000111",
  "stable_id": 1,
  "is_active": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente o cliente de otra hipica |
| 404 | No existe un cliente con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/clients/{client_id}

Elimina un cliente por su ID. Si el cliente no pertenece a la hipica del usuario autenticado (y este no es `app_admin`), devuelve 403.

**Rol requerido:** `stable_admin` o `app_admin`

**Parametros de ruta:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| client_id | integer | ID del cliente a eliminar |

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
| 403 | Rol insuficiente o cliente de otra hipica |
| 404 | No existe un cliente con el ID indicado |
