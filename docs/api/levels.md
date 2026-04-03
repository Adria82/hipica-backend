# API: Levels

Base URL: `/api/v1/levels`

Gestion del catalogo de niveles de equitacion. Cada nivel almacena su nombre en tres idiomas (`es`, `en`, `ca`) mediante una columna JSON. Los niveles son gestionados por `app_admin` y se asignan a caballos mediante sus IDs.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| POST | `/` | Crear un nivel | `app_admin` |
| GET | `/` | Listar todos los niveles | Sin autenticacion |
| GET | `/{level_id}` | Obtener un nivel por ID | Sin autenticacion |
| PUT | `/{level_id}` | Actualizar nombres de un nivel | `app_admin` |
| DELETE | `/{level_id}` | Eliminar un nivel | `app_admin` |

---

## Esquema LevelRead

```json
{
  "id": 1,
  "names": {
    "es": "Principiante",
    "en": "Beginner",
    "ca": "Principiant"
  }
}
```

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | integer | Identificador unico |
| `names` | object | Nombre del nivel en cada idioma soportado (`es`, `en`, `ca`) |

---

## Detalle de Endpoints

### POST /api/v1/levels/

Crea un nuevo nivel de equitacion con nombres en los tres idiomas.

**Rol requerido:** `app_admin`

**Request Body:**
```json
{
  "names": {
    "es": "Avanzado",
    "en": "Advanced",
    "ca": "Avançat"
  }
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| names | object | Si | Nombres del nivel. Debe incluir al menos `es`. |

**Response 201:** Objeto `LevelRead`.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente (requiere `app_admin`) |
| 422 | Datos de entrada invalidos |

---

### GET /api/v1/levels/

Lista todos los niveles del catalogo.

**Rol requerido:** Sin control de acceso.

**Response 200:** Array de `LevelRead`.

---

### GET /api/v1/levels/{level_id}

Obtiene un nivel por su ID.

**Response 200:** Objeto `LevelRead`.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 404 | No existe un nivel con el ID indicado |

---

### PUT /api/v1/levels/{level_id}

Actualiza los nombres de un nivel existente.

**Rol requerido:** `app_admin`

**Request Body:**
```json
{
  "names": {
    "es": "Experto",
    "en": "Expert",
    "ca": "Expert"
  }
}
```

**Response 200:** Objeto `LevelRead` actualizado.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente |
| 404 | No existe un nivel con el ID indicado |

---

### DELETE /api/v1/levels/{level_id}

Elimina un nivel. No se permite si tiene caballos asociados.

**Rol requerido:** `app_admin`

**Response 204:** Sin contenido.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 400 | El nivel tiene caballos asociados |
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente |
| 404 | No existe un nivel con el ID indicado |
