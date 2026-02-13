"""
Endpoints CRUD para Horse (caballos).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.horse import Horse
from app.dependencies import require_role
from app.models import User
from app.models.level import NivelEquitacion, Level
from app.core.i18n import t

router = APIRouter(prefix="/horses", tags=["Horses"])

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
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Obtener un caballo por su ID.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail=t(request, "horse.not_found"))
    return horse

@router.put("/{horse_id}", response_model=Horse)
def update_horse(
    horse_id: int,
    horse_data: Horse,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Actualizar los datos de un caballo.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail=t(request, "horse.not_found"))

    horse.name = horse_data.name
    horse.stable_id = horse_data.stable_id

    session.add(horse)
    session.commit()
    session.refresh(horse)
    return horse

@router.delete("/{horse_id}")
def delete_horse(
    horse_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Eliminar un caballo.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail=t(request, "horse.not_found"))

    session.delete(horse)
    session.commit()
    return {"ok": True}

@router.put(
    "/{horse_id}/levels",
    response_model=Horse,
    summary="Asignar niveles de equitación a un caballo",
)
def set_horse_levels(
    horse_id: int,
    levels: list[NivelEquitacion],
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Asignar o reemplazar los niveles de equitación de un caballo.
    Solo accesible para administradores.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail=t(request, "horse.not_found"))

    db_levels = session.exec(
        select(Level).where(Level.name.in_(levels))
    ).all()

    if len(db_levels) != len(levels):
        raise HTTPException(
            status_code=400,
            detail=t(request, "horse.invalid_levels"),
        )

    horse.levels.clear()
    horse.levels.extend(db_levels)

    session.add(horse)
    session.commit()
    session.refresh(horse)

    return horse

