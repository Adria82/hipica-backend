"""
Endpoints CRUD para Client (clientes).

Autor:  Adrià Bofill
Fecha:  01/02/2026
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.client import Client
from app.models.stable import Stable
from app.dependencies import require_role
from app.models import User
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.core.i18n import t

router = APIRouter(prefix="/clients", tags=["Clients"])


def _client_to_read(client: Client, session: Session | None = None) -> ClientRead:
    """Convierte un ORM Client en el schema ClientRead."""
    stable_name: str | None = None
    if session and client.stable_id:
        stable = session.get(Stable, client.stable_id)
        stable_name = stable.name if stable else None
    return ClientRead(
        id=client.id,
        name=client.name,
        email=client.email,
        phone=client.phone,
        is_active=client.is_active,
        stable_id=client.stable_id,
        stable_name=stable_name,
    )


@router.post("/", response_model=ClientRead, status_code=201)
def create_client(
    client_in: ClientCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Crear un nuevo cliente.

    Solo accesible para stable_admin y app_admin.
    El stable_id se fuerza al de la cuadra del usuario autenticado.
    """
    if current_user.role != "app_admin":
        client_in.stable_id = current_user.stable_id

    client = Client(**client_in.model_dump())
    session.add(client)
    session.commit()
    session.refresh(client)
    return _client_to_read(client, session)

@router.get("/", response_model=list[ClientRead])
def get_clients(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Obtener todos los clientes de la cuadra del usuario autenticado.

    app_admin ve clientes de todas las cuadras.
    """
    query = select(Client)
    if current_user.role != "app_admin":
        query = query.where(Client.stable_id == current_user.stable_id)

    clients = session.exec(query).all()
    return [_client_to_read(c, session) for c in clients]

@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Obtener un cliente por su ID.
    """
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail=t(request, "client.not_found"))

    if current_user.role != "app_admin" and client.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    return _client_to_read(client, session)

@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Actualizar los datos de un cliente.

    Solo accesible para stable_admin y app_admin.
    """
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail=t(request, "client.not_found"))

    if current_user.role != "app_admin" and client.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    for field, value in client_data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    session.add(client)
    session.commit()
    session.refresh(client)
    return _client_to_read(client, session)

@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Eliminar un cliente.

    Solo accesible para stable_admin y app_admin.
    """
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail=t(request, "client.not_found"))

    if current_user.role != "app_admin" and client.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    session.delete(client)
    session.commit()
    return {"ok": True}
