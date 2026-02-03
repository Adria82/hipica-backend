"""
Endpoints CRUD para Horse (caballos).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.horse import Horse

router = APIRouter(tags=["horses"])

@router.post("/", response_model=Horse)
def create_horse(
    horse: Horse,
    session: Session = Depends(get_session),
):
    """
    Crear un nuevo caballo.
    """
    session.add(horse)
    session.commit()
    session.refresh(horse)
    return horse

@router.get("/", response_model=list[Horse])
def get_horses(
    session: Session = Depends(get_session),
):
    """
    Obtener todos los caballos.
    """
    return session.exec(select(Horse)).all()

@router.get("/{horse_id}", response_model=Horse)
def get_horse(
    horse_id: int,
    session: Session = Depends(get_session),
):
    """
    Obtener un caballo por su ID.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail="Caballo no encontrado")
    return horse

@router.put("/{horse_id}", response_model=Horse)
def update_horse(
    horse_id: int,
    horse_data: Horse,
    session: Session = Depends(get_session),
):
    """
    Actualizar los datos de un caballo.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail="Caballo no encontrado")

    horse.name = horse_data.name
    horse.stable_id = horse_data.stable_id

    session.add(horse)
    session.commit()
    session.refresh(horse)
    return horse

@router.delete("/{horse_id}")
def delete_horse(
    horse_id: int,
    session: Session = Depends(get_session),
):
    """
    Eliminar un caballo.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail="Caballo no encontrado")

    session.delete(horse)
    session.commit()
    return {"ok": True}

