"""
Endpoints relacionados con el usuario autenticado (/me).

Incluye:
- Consulta de funcionalidades activas para la hípica del usuario.

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.dependencies import get_current_user
from app.models import User
from app.models.stable_feature import StableFeature
from app.models.feature import FeatureCode

router = APIRouter(prefix="/me", tags=["Me"])


@router.get("/features")
def get_my_features(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Devuelve la lista de funcionalidades activas para la hípica del usuario autenticado.

    Flujo:
        1. Se obtiene el usuario desde el JWT (get_current_user).
        2. Se identifica su stable_id.
        3. Se consultan las features activadas para esa hípica.
        4. Se devuelve la lista al frontend.

    Returns:
        dict: { "features": ["HORSES", "CLIENTS", ...] }

    Notas:
        - Si el usuario es 'app_admin' y no pertenece a ninguna stable,
          se podría devolver todas las features (modo super-admin).
    """

    # Usuario global sin hípica → acceso total a todas las funcionalidades
    if current_user.stable_id is None:
        return {"features": [feature.value for feature in FeatureCode]}

    results = session.exec(
        select(StableFeature.feature).where(
            StableFeature.stable_id == current_user.stable_id
        )
    ).all()

    return {"features": [feature.value for feature in results]}