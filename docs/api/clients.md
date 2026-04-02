# API: Clients

Base URL: `/api/v1/clients`

Gestion de clientes (alumnos) de la hipica. Cada cliente pertenece a una hipica (`stable_id`) y puede estar asociado a multiples lecciones.

> **Alerta de seguridad:** Ningun endpoint de este recurso tiene control de acceso (`require_role`). Cualquier peticion puede ejecutarlos. Se recomienda revisar con `backend-dev`.

> **Nota arquitectonica:** Los endpoints `POST /` y `PUT /{id}` utilizan directamente el modelo ORM `Client` en lugar de los schemas `ClientCreate` / `ClientUpdate` definidos en `app/schemas/client.py`. Se recomienda corregir con `backend-dev`.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear un cliente | Sin control (ver alerta) |
| GET | `/` | Listar todos los clientes | Sin control (ver alerta) |
| GET | `/{client_id}` | Obtener un cliente por ID | Sin control (ver alerta) |
| PUT | `/{client_id}` | Actualizar un cliente | Sin control (ver alerta) |
| DELETE | `/{client_id}` | Eliminar un cliente | Sin control (ver alerta) |

---

## Detalle de Endpoints

### POST /api/v1/clients/

Crea un nuevo cliente en la hipica.

**Rol requerido:** Sin control de acceso

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
| stable_id | integer | Si | ID de la hipica a la que pertenece |
| is_active | boolean | No (default: `true`) | Si el cliente esta activo |

**Response 200:**
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
| 422 | Datos de entrada invalidos o campos obligatorios ausentes |

---

### GET /api/v1/clients/

Devuelve todos los clientes registrados en la base de datos, sin filtrar por hipica.

**Rol requerido:** Sin control de acceso

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
| — | Este endpoint no produce errores conocidos |

---

### GET /api/v1/clients/{client_id}

Obtiene un cliente por su ID.

**Rol requerido:** Sin control de acceso

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
| 404 | No existe un cliente con el ID indicado |

---

### PUT /api/v1/clients/{client_id}

Actualiza los datos de un cliente. La implementacion actual solo actualiza `name` y `email`; los demas campos se ignoran.

**Rol requerido:** Sin control de acceso

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
| name | string | Si | Nuevo nombre (aplicado) |
| email | string | No | Nuevo email (aplicado) |
| phone | string | No | Telefono (ignorado por la logica actual) |
| stable_id | integer | Si | ID de la hipica (ignorado por la logica actual) |
| is_active | boolean | No | Estado (ignorado por la logica actual) |

**Response 200:**
```json
{
  "id": 1,
  "name": "Joan Puig Nou",
  "email": "joan_nou@example.com",
  "phone": null,
  "stable_id": 1,
  "is_active": true
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe un cliente con el ID indicado |
| 422 | Datos de entrada invalidos |

---

### DELETE /api/v1/clients/{client_id}

Elimina un cliente por su ID.

**Rol requerido:** Sin control de acceso

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
| 404 | No existe un cliente con el ID indicado |
