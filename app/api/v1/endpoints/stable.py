"""
Endpoints CRUD para Stables (hípicas).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.stable import Stable
from app.models.stable_feature import StableFeature
from app.models.feature import FeatureCode
from app.dependencies import require_role
from app.models import User
from app.schemas.stable import StableCreate, StableRead, StableUpdate
from app.core.i18n import t

router = APIRouter(prefix="/stables", tags=["Stables"])


@router.post("/", response_model=StableRead, status_code=201)
def create_stable(
    stable: StableCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["app_admin"])),
):
    """
    Crear una nueva hípica.

    Solo accesible para app_admin.
    """
    db_stable = Stable.model_validate(stable)
    session.add(db_stable)
    session.commit()
    session.refresh(db_stable)
    return db_stable


@router.get("/", response_model=list[StableRead])
def list_stables(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["app_admin"])),
):
    """
    Listar todas las hípicas.

    Solo accesible para app_admin.
    """
    return session.exec(select(Stable)).all()


@router.get("/{stable_id}", response_model=StableRead)
def get_stable(
    stable_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Obtener una hípica por ID.

    stable_admin solo puede consultar su propia hípica.
    """
    stable = session.get(Stable, stable_id)
    if not stable:
        raise HTTPException(status_code=404, detail=t(request, "stable.not_found"))

    if current_user.role != "app_admin" and stable.id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    return stable


@router.patch("/{stable_id}", response_model=StableRead)
def update_stable(
    stable_id: int,
    stable_data: StableUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["app_admin"])),
):
    """
    Actualizar una hípica.

    Solo accesible para app_admin.
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
    current_user: User = Depends(require_role(["app_admin"])),
):
    """
    Eliminar una hípica.

    Solo accesible para app_admin.
    """
    stable = session.get(Stable, stable_id)
    if not stable:
        raise HTTPException(status_code=404, detail=t(request, "stable.not_found"))

    session.delete(stable)
    session.commit()
    return {"ok": True}


@router.get("/{stable_id}/features", response_model=list[str])
def get_stable_features(
    stable_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["app_admin"])),
):
    """
    Obtener las features activadas para una hípica.
    """
    stable = session.get(Stable, stable_id)
    if not stable:
        raise HTTPException(status_code=404, detail=t(request, "stable.not_found"))

    results = session.exec(
        select(StableFeature).where(StableFeature.stable_id == stable_id)
    ).all()
    return [sf.feature.value for sf in results]


@router.put("/{stable_id}/features", response_model=list[str])
def set_stable_features(
    stable_id: int,
    features: list[str],
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["app_admin"])),
):
    """
    Reemplaza el conjunto de features de una hípica.

    Recibe la lista completa de features activas; elimina las que ya no
    estén y añade las nuevas.
    """
    stable = session.get(Stable, stable_id)
    if not stable:
        raise HTTPException(status_code=404, detail=t(request, "stable.not_found"))

    # Validar que todos los valores son FeatureCode válidos
    valid_codes = {f.value for f in FeatureCode}
    for f in features:
        if f not in valid_codes:
            raise HTTPException(status_code=400, detail=f"Feature '{f}' no válida")

    # Eliminar las existentes
    existing = session.exec(
        select(StableFeature).where(StableFeature.stable_id == stable_id)
    ).all()
    for sf in existing:
        session.delete(sf)

    # Insertar las nuevas
    for f in features:
        session.add(StableFeature(stable_id=stable_id, feature=FeatureCode(f)))

    session.commit()

    return features
