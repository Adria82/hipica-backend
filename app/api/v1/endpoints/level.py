"""
Endpoints CRUD para Level (niveles de equitación).

Gestiona el catálogo de niveles disponibles en la hípica.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.level import Level
from app.dependencies import require_role
from app.models import User
from app.schemas.level import LevelCreate, LevelRead
from app.core.i18n import t

router = APIRouter(prefix="/levels", tags=["levels"])


@router.post(
    "/",
    response_model=LevelRead,
    status_code=status.HTTP_201_CREATED,
)
def create_level(
    level: LevelCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["app_admin"])),
):
    """
    Crear un nuevo nivel de equitación.
    """
    exists = session.exec(
        select(Level).where(Level.name == level.name)
    ).first()

    if exists:
        raise HTTPException(
            status_code=400,
            detail=t(request, "level.exists"),
        )

    db_level = Level(name=level.name)
    session.add(db_level)
    session.commit()
    session.refresh(db_level)
    return db_level


@router.get(
    "/",
    response_model=list[LevelRead],
)
def list_levels(
    session: Session = Depends(get_session),
):
    """
    Listar todos los niveles de equitación.
    """
    return session.exec(select(Level)).all()


@router.get(
    "/{level_id}",
    response_model=LevelRead,
)
def get_level(
    level_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Obtener un nivel de equitación por ID.
    """
    level = session.get(Level, level_id)
    if not level:
        raise HTTPException(
            status_code=404,
            detail=t(request, "level.not_found"),
        )
    return level


@router.delete(
    "/{level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_level(
    level_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["app_admin"])),
):
    """
    Eliminar un nivel de equitación.

    No se permite eliminar niveles asociados a caballos.
    """
    level = session.get(Level, level_id)
    if not level:
        raise HTTPException(
            status_code=404,
            detail=t(request, "level.not_found"),
        )

    if level.horses:
        raise HTTPException(
            status_code=400,
            detail=t(request, "level.delete_associated"),
        )

    session.delete(level)
    session.commit()
