"""
MCP Server para la API de Gestión Hípica.

Expone herramientas (tools) para que Claude pueda interactuar
con el backend FastAPI de la hípica usando lenguaje natural.

Uso: python ./mcp/server.py
Requiere: pip install mcp httpx
"""

import httpx
from mcp.server.fastmcp import FastMCP

# ──────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────
BASE_URL = "http://localhost:8000/api/v1"

# Token JWT en memoria (se establece con la herramienta `login`)
_access_token: str | None = None


def _headers() -> dict:
    if not _access_token:
        raise ValueError(
            "No hay sesión activa. Llama primero a la herramienta `login`."
        )
    return {"Authorization": f"Bearer {_access_token}"}


def _get(path: str, params: dict | None = None) -> dict:
    r = httpx.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict) -> dict:
    r = httpx.post(f"{BASE_URL}{path}", headers=_headers(), json=body, timeout=10)
    r.raise_for_status()
    return r.json()


def _put(path: str, body: dict) -> dict:
    r = httpx.put(f"{BASE_URL}{path}", headers=_headers(), json=body, timeout=10)
    r.raise_for_status()
    return r.json()


def _patch(path: str, body: dict) -> dict:
    r = httpx.patch(f"{BASE_URL}{path}", headers=_headers(), json=body, timeout=10)
    r.raise_for_status()
    return r.json()


def _delete(path: str) -> dict:
    r = httpx.delete(f"{BASE_URL}{path}", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json() if r.content else {"ok": True}


# ──────────────────────────────────────────────
# Servidor MCP
# ──────────────────────────────────────────────
mcp = FastMCP("hipica")


# ── Autenticación ──────────────────────────────

@mcp.tool()
def login(email: str, password: str) -> str:
    """
    Inicia sesión en la API de la hípica y guarda el token JWT.
    Debes llamar a esta herramienta antes de usar cualquier otra.
    """
    global _access_token
    r = httpx.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    _access_token = data["access_token"]
    return f"Sesión iniciada correctamente. Token obtenido."


# ── Hípicas (Stables) ──────────────────────────

@mcp.tool()
def listar_hipicas() -> list:
    """Devuelve todas las hípicas registradas en el sistema."""
    return _get("/stables/")


@mcp.tool()
def obtener_hipica(stable_id: int) -> dict:
    """Devuelve los datos de una hípica por su ID."""
    return _get(f"/stables/{stable_id}")


@mcp.tool()
def crear_hipica(name: str, location: str, is_active: bool = True) -> dict:
    """Crea una nueva hípica."""
    return _post("/stables/", {"name": name, "location": location, "is_active": is_active})


@mcp.tool()
def actualizar_hipica(
    stable_id: int,
    name: str | None = None,
    location: str | None = None,
    is_active: bool | None = None,
) -> dict:
    """Actualiza parcialmente los datos de una hípica."""
    body = {k: v for k, v in {"name": name, "location": location, "is_active": is_active}.items() if v is not None}
    return _patch(f"/stables/{stable_id}", body)


@mcp.tool()
def eliminar_hipica(stable_id: int) -> dict:
    """Elimina una hípica por su ID."""
    return _delete(f"/stables/{stable_id}")


# ── Caballos (Horses) ──────────────────────────

@mcp.tool()
def listar_caballos(stable_id: int | None = None) -> list:
    """
    Devuelve todos los caballos. Opcionalmente filtra por hípica (stable_id).
    """
    params = {"stable_id": stable_id} if stable_id is not None else None
    return _get("/horses/", params=params)


@mcp.tool()
def obtener_caballo(horse_id: int) -> dict:
    """Devuelve los datos de un caballo por su ID."""
    return _get(f"/horses/{horse_id}")


@mcp.tool()
def crear_caballo(name: str, stable_id: int, breed: str | None = None, is_active: bool = True) -> dict:
    """
    Crea un nuevo caballo en la hípica indicada.

    Parámetros:
    - name: nombre del caballo (obligatorio)
    - stable_id: ID de la hípica a la que pertenece (obligatorio)
    - breed: raza del caballo (opcional)
    - is_active: si está disponible (por defecto True)
    """
    body: dict = {"name": name, "stable_id": stable_id, "is_active": is_active}
    if breed:
        body["breed"] = breed
    return _post("/horses/", body)


@mcp.tool()
def actualizar_caballo(
    horse_id: int,
    name: str | None = None,
    breed: str | None = None,
    is_active: bool | None = None,
    stable_id: int | None = None,
) -> dict:
    """Actualiza parcialmente los datos de un caballo."""
    body = {
        k: v for k, v in {
            "name": name, "breed": breed, "is_active": is_active, "stable_id": stable_id
        }.items() if v is not None
    }
    return _put(f"/horses/{horse_id}", body)


@mcp.tool()
def eliminar_caballo(horse_id: int) -> dict:
    """Elimina un caballo por su ID."""
    return _delete(f"/horses/{horse_id}")


@mcp.tool()
def asignar_niveles_caballo(horse_id: int, levels: list[str]) -> dict:
    """
    Asigna niveles de equitación a un caballo.
    Valores válidos para levels: 'principiante', 'iniciado', 'experto'.
    Requiere rol stable_admin o app_admin.
    """
    return _put(f"/horses/{horse_id}/levels", {"levels": levels})


# ── Clientes ───────────────────────────────────

@mcp.tool()
def listar_clientes(stable_id: int | None = None) -> list:
    """Devuelve todos los clientes. Opcionalmente filtra por hípica."""
    params = {"stable_id": stable_id} if stable_id is not None else None
    return _get("/clients/", params=params)


@mcp.tool()
def obtener_cliente(client_id: int) -> dict:
    """Devuelve los datos de un cliente por su ID."""
    return _get(f"/clients/{client_id}")


@mcp.tool()
def crear_cliente(
    name: str,
    stable_id: int,
    phone: str | None = None,
    email: str | None = None,
    is_active: bool = True,
) -> dict:
    """Crea un nuevo cliente en la hípica indicada."""
    body: dict = {"name": name, "stable_id": stable_id, "is_active": is_active}
    if phone:
        body["phone"] = phone
    if email:
        body["email"] = email
    return _post("/clients/", body)


@mcp.tool()
def eliminar_cliente(client_id: int) -> dict:
    """Elimina un cliente por su ID."""
    return _delete(f"/clients/{client_id}")


# ── Usuarios ───────────────────────────────────

@mcp.tool()
def listar_usuarios() -> list:
    """Devuelve todos los usuarios del sistema."""
    return _get("/users/")


@mcp.tool()
def crear_usuario(
    name: str,
    email: str,
    password: str,
    role: str,
    stable_id: int | None = None,
) -> dict:
    """
    Crea un nuevo usuario.
    Roles válidos: 'app_admin', 'stable_admin', 'monitor', 'cliente'.
    """
    body: dict = {"name": name, "email": email, "password": password, "role": role}
    if stable_id is not None:
        body["stable_id"] = stable_id
    return _post("/users/", body)


# ── Clases (Lessons) ───────────────────────────

@mcp.tool()
def listar_clases(stable_id: int | None = None, instructor_id: int | None = None) -> list:
    """Devuelve todas las clases. Filtra opcionalmente por hípica o instructor."""
    params = {}
    if stable_id is not None:
        params["stable_id"] = stable_id
    if instructor_id is not None:
        params["instructor_id"] = instructor_id
    return _get("/lessons/", params=params or None)


@mcp.tool()
def crear_clase(
    date_time: str,
    stable_id: int,
    instructor_id: int,
    horse_ids: list[int],
    client_ids: list[int],
) -> dict:
    """
    Crea una nueva clase.
    - date_time: ISO 8601, ej. '2026-04-01T10:00:00'
    - horse_ids: lista de IDs de caballos
    - client_ids: lista de IDs de clientes
    """
    return _post("/lessons/", {
        "date_time": date_time,
        "stable_id": stable_id,
        "instructor_id": instructor_id,
        "horse_ids": horse_ids,
        "client_ids": client_ids,
    })


# ── Niveles ────────────────────────────────────

@mcp.tool()
def listar_niveles() -> list:
    """Devuelve todos los niveles de equitación disponibles."""
    return _get("/levels/")


# ── Entrada principal ──────────────────────────

if __name__ == "__main__":
    mcp.run()
