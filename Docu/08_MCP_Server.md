# 08 — MCP Server para la API de la Hípica

## Objetivo

Crear un servidor MCP (Model Context Protocol) propio que expone la lógica de negocio del backend FastAPI como **herramientas que Claude puede invocar directamente**.

Esto permite interactuar con la aplicación en lenguaje natural:

> "Crea 5 caballos en la hípica 1"

→ Claude llama automáticamente a `crear_caballo(name=..., stable_id=1)` × 5 via la API REST.

---

## Estructura de archivos

```
hipica-backend/
├── hipica_mcp/
│   ├── __init__.py
│   └── server.py       ← Servidor MCP
└── .mcp.json           ← Registro de servidores MCP para Claude Code
```

---

## Configuración (.mcp.json)

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://hipica:hipica@localhost:5432/hipica"]
    },
    "hipica": {
      "command": "python",
      "args": ["-m", "hipica_mcp.server"],
      "cwd": "c:/abe/Hipica/app/hipica-backend"
    }
  }
}
```

> El directorio se llama `hipica_mcp` (no `mcp`) para evitar colisión de nombres con el paquete Python `mcp`.

---

## Dependencias

El servidor requiere dos paquetes Python:

```bash
pip install "mcp[cli]" httpx
```

- `mcp` — SDK de Model Context Protocol (Anthropic)
- `httpx` — cliente HTTP síncrono (ya incluido en `requirements.txt`)

---

## Arquitectura del servidor

```
Claude Code
    │
    │  stdio (MCP protocol)
    ▼
hipica_mcp/server.py  (FastMCP)
    │
    │  HTTP REST (JWT Bearer)
    ▼
FastAPI  →  http://localhost:8000/api/v1
    │
    ▼
PostgreSQL
```

### Autenticación

El servidor mantiene un token JWT en memoria (`_access_token`). El flujo es:

1. Claude llama a `login(email, password)`
2. El servidor hace `POST /api/v1/auth/login` y guarda el `access_token`
3. Todas las llamadas siguientes incluyen `Authorization: Bearer <token>`

---

## Herramientas disponibles

### Autenticación

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `login` | `email`, `password` | Inicia sesión y guarda el JWT en memoria |

### Hípicas

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `listar_hipicas` | — | Lista todas las hípicas |
| `obtener_hipica` | `stable_id` | Detalle de una hípica |
| `crear_hipica` | `name`, `location`, `is_active?` | Crea una hípica |
| `actualizar_hipica` | `stable_id`, campos opcionales | Actualización parcial |
| `eliminar_hipica` | `stable_id` | Elimina una hípica |

### Caballos

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `listar_caballos` | `stable_id?` | Lista caballos (filtrable por hípica) |
| `obtener_caballo` | `horse_id` | Detalle de un caballo |
| `crear_caballo` | `name`, `stable_id`, `breed?`, `is_active?` | Crea un caballo |
| `actualizar_caballo` | `horse_id`, campos opcionales | Actualización parcial |
| `eliminar_caballo` | `horse_id` | Elimina un caballo |
| `asignar_niveles_caballo` | `horse_id`, `levels[]` | Asigna niveles de equitación (`principiante`, `iniciado`, `experto`) |

### Clientes

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `listar_clientes` | `stable_id?` | Lista clientes |
| `obtener_cliente` | `client_id` | Detalle de un cliente |
| `crear_cliente` | `name`, `stable_id`, `phone?`, `email?` | Crea un cliente |
| `eliminar_cliente` | `client_id` | Elimina un cliente |

### Usuarios

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `listar_usuarios` | — | Lista todos los usuarios |
| `crear_usuario` | `name`, `email`, `password`, `role`, `stable_id?` | Crea un usuario. Roles: `app_admin`, `stable_admin`, `monitor`, `cliente` |

### Clases

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `listar_clases` | `stable_id?`, `instructor_id?` | Lista clases con filtros opcionales |
| `crear_clase` | `date_time`, `stable_id`, `instructor_id`, `horse_ids[]`, `client_ids[]` | Crea una clase. `date_time` en ISO 8601 |

### Niveles

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `listar_niveles` | — | Lista los niveles de equitación disponibles |

---

## Ejemplo de uso en lenguaje natural

```
Usuario: "Crea 5 caballos en la hípica 1"

Claude:
  1. login("admin@hipica.com", "password")
  2. crear_caballo("Caballo 1", stable_id=1)
  3. crear_caballo("Caballo 2", stable_id=1)
  4. crear_caballo("Caballo 3", stable_id=1)
  5. crear_caballo("Caballo 4", stable_id=1)
  6. crear_caballo("Caballo 5", stable_id=1)
```

```
Usuario: "Lista todos los caballos de la hípica 2 y desactiva los que sean de raza Árabe"

Claude:
  1. listar_caballos(stable_id=2)
  2. actualizar_caballo(horse_id=X, is_active=False)  ← para cada Árabe
```

---

## Activación

Reinicia Claude Code para que detecte el nuevo servidor MCP. A partir de ese momento el servidor `hipica` aparece disponible junto al servidor `postgres`.
