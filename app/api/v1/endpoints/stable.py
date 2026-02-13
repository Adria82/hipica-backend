"""
Endpoints CRUD para Stables (hípicas).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.stable import Stable
from app.schemas.stable import StableCreate, StableRead, StableUpdate
from app.core.i18n import t

router = APIRouter(prefix="/stables", tags=["Stables"])


@router.post("/", response_model=StableRead)
def create_stable(
    stable: StableCreate,
    session: Session = Depends(get_session),
):
    """
    Crear una nueva hípica.
    """
    db_stable = Stable.model_validate(stable)
    session.add(db_stable)
    session.commit()
    session.refresh(db_stable)
    return db_stable


@router.get("/", response_model=list[StableRead])
def list_stables(
    session: Session = Depends(get_session),
):
    """
    Listar todas las hípicas.
    """
    return session.exec(select(Stable)).all()


@router.get("/{stable_id}", response_model=StableRead)
def get_stable(
    stable_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Obtener una hípica por ID.
    """
    stable = session.get(Stable, stable_id)
    if not stable:
        raise HTTPException(status_code=404, detail=t(request, "stable.not_found"))
    return stable


@router.patch("/{stable_id}", response_model=StableRead)
def update_stable(
    stable_id: int,
    stable_data: StableUpdate,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Actualizar una hípica.
    """
    stable = session.get(Stable, stable_id)
    if not stable:
        raise HTTPException(status_code=404, detail=t(request, "stable.not_found"))

    for key, value in stable_data.model_dump(exclude_unset=True).items():
        setattr(stable, key, value)

    session.add(stable)
    session.commit()
    session.refresh(stable)
    return stable


@router.delete("/{stable_id}")
def delete_stable(
    stable_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Eliminar una hípica.
    """
    stable = session.get(Stable, stable_id)
    if not stable:
        raise HTTPException(status_code=404, detail=t(request, "stable.not_found"))

    session.delete(stable)
    session.commit()
    return {"ok": True}
