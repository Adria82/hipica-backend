"""
Endpoints CRUD para Horse (caballos).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.horse import Horse
from app.models.box import Box
from app.dependencies import get_current_user, require_role
from app.models import User
from app.models.level import Level
from app.models.stable import Stable
from app.schemas.horse import HorseCreate, HorseRead, HorseUpdate
from app.core.i18n import t, get_request_language

router = APIRouter(prefix="/horses", tags=["Horses"])


class BoxFullError(Exception):
    """Se lanza cuando un box no tiene capacidad disponible."""
    def __init__(self, box: Box, exclude_horse_id: int | None = None):
        self.box_name = box.name
        self.capacity = box.capacity
        self.horse_names = ", ".join(
            h.name for h in box.horses if h.id != exclude_horse_id
        )


def _check_box_capacity(session: Session, box_id: int, exclude_horse_id: int | None = None) -> Box:
    """Verifica que el box existe y tiene capacidad disponible. Lanza excepciones si no."""
    box = session.get(Box, box_id)
    if not box:
        raise ValueError("box.not_found")
    occupied = sum(1 for h in box.horses if h.id != exclude_horse_id)
    if occupied >= box.capacity:
        raise BoxFullError(box, exclude_horse_id)
    return box


def _horse_to_read(horse: Horse, session: Session | None = None, lang: str = "ca") -> HorseRead:
    """Convierte un ORM Horse en el schema HorseRead.

    lang: idioma para los nombres de niveles (ca/es/en).
    """
    stable_name: str | None = None
    if session and horse.stable_id:
        stable = session.get(Stable, horse.stable_id)
        stable_name = stable.name if stable else None

    def _level_name(lvl) -> str:
        names = lvl.names or {}
        return names.get(lang) or names.get("es") or names.get("ca") or next(iter(names.values()), str(lvl.id))

    return HorseRead(
        id=horse.id,
        name=horse.name,
        box_id=horse.box_id,
        box_name=horse.box.name if horse.box else None,
        is_active=horse.is_active,
        stable_id=horse.stable_id,
        stable_name=stable_name,
        levels=[_level_name(lvl) for lvl in horse.levels],
        level_ids=[lvl.id for lvl in horse.levels],
    )


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

    if horse_in.box_id is not None:
        try:
            _check_box_capacity(session, horse_in.box_id)
        except BoxFullError as e:
            raise HTTPException(status_code=409, detail=t(
                request, "box.full",
                box_name=e.box_name, capacity=e.capacity, horse_names=e.horse_names,
            ))
        except ValueError as e:
            raise HTTPException(status_code=409, detail=t(request, str(e)))

    horse = Horse(**horse_in.model_dump())
    session.add(horse)
    session.commit()
    session.refresh(horse)
    return _horse_to_read(horse, session, get_request_language(request))

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

    lang = get_request_language(request)
    horses = session.exec(query).all()
    return [_horse_to_read(h, session, lang) for h in horses]

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

    return _horse_to_read(horse, session, get_request_language(request))

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

    if "box_id" in update_data and update_data["box_id"] is not None:
        try:
            _check_box_capacity(session, update_data["box_id"], exclude_horse_id=horse.id)
        except BoxFullError as e:
            raise HTTPException(status_code=409, detail=t(
                request, "box.full",
                box_name=e.box_name, capacity=e.capacity, horse_names=e.horse_names,
            ))
        except ValueError as e:
            raise HTTPException(status_code=409, detail=t(request, str(e)))

    for field, value in update_data.items():
        setattr(horse, field, value)

    # Actualizar niveles si se proporcionaron (por IDs)
    if horse_data.levels is not None:
        db_levels = session.exec(
            select(Level).where(Level.id.in_(horse_data.levels))
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
    return _horse_to_read(horse, session, get_request_language(request))

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
    level_ids: list[int],
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Asignar o reemplazar los niveles de equitación de un caballo.
    Acepta una lista de IDs de niveles. Solo accesible para administradores.
    """
    horse = session.get(Horse, horse_id)
    if not horse:
        raise HTTPException(status_code=404, detail=t(request, "horse.not_found"))

    if current_user.role != "app_admin" and horse.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    db_levels = session.exec(
        select(Level).where(Level.id.in_(level_ids))
    ).all()

    if len(db_levels) != len(level_ids):
        raise HTTPException(
            status_code=400,
            detail=t(request, "horse.invalid_levels"),
        )

    horse.levels.clear()
    horse.levels.extend(db_levels)

    session.add(horse)
    session.commit()
    session.refresh(horse)

    return _horse_to_read(horse, session, get_request_language(request))
