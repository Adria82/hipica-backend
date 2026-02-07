"""
Endpoints CRUD para Client (clientes).

Autor:  Adrià Bofill
Fecha:  01/02/2026
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.client import Client

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("/", response_model=Client)
def create_client(
    client: Client,
    session: Session = Depends(get_session),
):
    """
    Crear un nuevo cliente.
    """
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@router.get("/", response_model=list[Client])
def get_clients(
    session: Session = Depends(get_session),
):
    """
    Obtener todos los clientes.
    """
    return session.exec(select(Client)).all()

@router.get("/{client_id}", response_model=Client)
def get_client(
    client_id: int,
    session: Session = Depends(get_session),
):
    """
    Obtener un cliente por su ID.
    """
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client

@router.put("/{client_id}", response_model=Client)
def update_client(
    client_id: int,
    client_data: Client,
    session: Session = Depends(get_session),
):
    """
    Actualizar los datos de un cliente.
    """
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    client.name = client_data.name
    client.email = client_data.email

    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    session: Session = Depends(get_session),
):
    """
    Eliminar un cliente.
    """
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    session.delete(client)
    session.commit()
    return {"ok": True}
