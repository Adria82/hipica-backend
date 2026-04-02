"""
Endpoints CRUD para Horse (caballos).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.horse import Horse
from app.dependencies import get_current_user, require_role
from app.models import User
from app.models.level import NivelEquitacion, Level
from app.schemas.horse import HorseCreate, HorseRead, HorseUpdate
from app.core.i18n import t

router = APIRouter(prefix="/horses", tags=["Horses"])

@router.post("/", response_model=HorseRead, status_code=201)
def create_horse(
    horse_in: HorseCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Crear un nuevo caballo.

    Solo accesible para stable_admin y app_admin.
    El stable_id se fuerza al de la cuadra del usuario autenticado
    (app_admin puede indicar stable_id explícitamente).
    """
    if current_user.role != "app_admin":
        horse_in.stable_id = current_user.stable_id

    horse = Horse(**horse_in.model_dump())
    session.add(horse)
    session.commit()
    session.refresh(horse)
    return HorseRead(
        id=horse.id,
        name=horse.name,
        box=horse.box,
        is_active=horse.is_active,
        stable_id=horse.stable_id,
        levels=[lvl.name for lvl in horse.levels],
    )

@router.get("/", response_model=list[HorseRead])
def get_horses(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Obtener todos los caballos de la cuadra del usuario autenticado.

    app_admin ve todos los caballos de todas las cuadras.
    """
    query = select(Horse)
    if current_user.role != "app_admin":
        query = query.where(Horse.stable_id == current_user.stable_id)

    horses = session.exec(query).all()
    return [
        HorseRead(
            id=h.id,
            name=h.name,
            box=h.box,
            is_active=h.is_active,
            stable_id=h.stable_id,
            levels=[lvl.name for lvl in h.levels],
        )
        for h in horses
    ]

@router.get("/{horse_id}", response_model=HorseRead)
def get_horse(
    horse_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Obtener un caballo por su ID.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail=t(request, "horse.not_found"))

    if current_user.role != "app_admin" and horse.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    return HorseRead(
        id=horse.id,
        name=horse.name,
        box=horse.box,
        is_active=horse.is_active,
        stable_id=horse.stable_id,
        levels=[lvl.name for lvl in horse.levels],
    )

@router.put("/{horse_id}", response_model=HorseRead)
def update_horse(
    horse_id: int,
    horse_data: HorseUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Actualizar los datos de un caballo.

    Solo accesible para stable_admin y app_admin.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail=t(request, "horse.not_found"))

    if current_user.role != "app_admin" and horse.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    update_data = horse_data.model_dump(exclude_unset=True, exclude={"levels"})
    for field, value in update_data.items():
        setattr(horse, field, value)

    # Actualizar niveles si se proporcionaron
    if horse_data.levels is not None:
        db_levels = session.exec(
            select(Level).where(Level.name.in_(horse_data.levels))
        ).all()
        if len(db_levels) != len(horse_data.levels):
            raise HTTPException(
                status_code=400,
                detail=t(request, "horse.invalid_levels"),
            )
        horse.levels.clear()
        horse.levels.extend(db_levels)

    session.add(horse)
    session.commit()
    session.refresh(horse)
    return HorseRead(
        id=horse.id,
        name=horse.name,
        box=horse.box,
        is_active=horse.is_active,
        stable_id=horse.stable_id,
        levels=[lvl.name for lvl in horse.levels],
    )

@router.delete("/{horse_id}")
def delete_horse(
    horse_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Eliminar un caballo.

    Solo accesible para stable_admin y app_admin.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail=t(request, "horse.not_found"))

    if current_user.role != "app_admin" and horse.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    session.delete(horse)
    session.commit()
    return {"ok": True}

@router.put(
    "/{horse_id}/levels",
    response_model=HorseRead,
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

    if current_user.role != "app_admin" and horse.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

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

    return HorseRead(
        id=horse.id,
        name=horse.name,
        box=horse.box,
        is_active=horse.is_active,
        stable_id=horse.stable_id,
        levels=[lvl.name for lvl in horse.levels],
    )
