"""
Endpoints relacionados con el usuario autenticado (/me).

Incluye:
- Consulta de funcionalidades activas para la hípica del usuario.
- Consulta y edición del perfil del usuario autenticado.

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel

from app.db.session import get_session
from app.dependencies import get_current_user
from app.models import User
from app.models.client_profile import ClientProfile
from app.models.stable import Stable
from app.models.stable_feature import StableFeature
from app.models.feature import FeatureCode

router = APIRouter(prefix="/me", tags=["Me"])


@router.get("/profile")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Devuelve el perfil del usuario autenticado, incluyendo nombre e tema de su hípica.

    Returns:
        dict: { "id", "email", "role", "stable_id", "stable_name", "stable_theme" }
    """
    stable_name: Optional[str] = None
    stable_theme: Optional[str] = "default"

    if current_user.stable_id is not None:
        stable = session.get(Stable, current_user.stable_id)
        if stable:
            stable_name = stable.name
            stable_theme = stable.theme or "default"

    return {
        "id": current_user.id,
        "name": current_user.name,
        "apellidos": current_user.apellidos,
        "email": current_user.email,
        "dni": current_user.dni,
        "phone": current_user.phone,
        "role": current_user.role,
        "stable_id": current_user.stable_id,
        "stable_name": stable_name,
        "stable_theme": stable_theme,
        "avatar": current_user.avatar,
    }


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[str] = None
    dni: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


@router.put("/profile")
def update_my_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Actualiza el perfil del usuario autenticado.

    Returns:
        dict: Perfil actualizado.
    """
    if data.name is not None:
        current_user.name = data.name

    if data.apellidos is not None:
        current_user.apellidos = data.apellidos

    if data.email is not None:
        existing = session.exec(
            select(User).where(User.email == data.email, User.id != current_user.id)
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="email.taken")
        current_user.email = data.email

    if data.dni is not None:
        current_user.dni = data.dni

    if data.phone is not None:
        current_user.phone = data.phone

    if data.avatar is not None:
        current_user.avatar = data.avatar

    if current_user.role == "client" and data.apellidos is not None:
        profile = session.get(ClientProfile, current_user.id)
        if profile is None:
            profile = ClientProfile(user_id=current_user.id)
            session.add(profile)
        profile.apellidos = data.apellidos

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    stable_name: Optional[str] = None
    stable_theme: Optional[str] = "default"

    if current_user.stable_id is not None:
        stable = session.get(Stable, current_user.stable_id)
        if stable:
            stable_name = stable.name
            stable_theme = stable.theme or "default"

    return {
        "id": current_user.id,
        "name": current_user.name,
        "apellidos": current_user.apellidos,
        "email": current_user.email,
        "dni": current_user.dni,
        "phone": current_user.phone,
        "role": current_user.role,
        "stable_id": current_user.stable_id,
        "stable_name": stable_name,
        "stable_theme": stable_theme,
        "avatar": current_user.avatar,
    }


@router.get("/features")
def get_my_features(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Devuelve la lista de funcionalidades activas para la hípica del usuario autenticado.

    Returns:
        dict: { "features": ["HORSES", "CLIENTS", ...] }
    """
    if current_user.stable_id is None:
        return {"features": [feature.value for feature in FeatureCode]}

    results = session.exec(
        select(StableFeature.feature).where(
            StableFeature.stable_id == current_user.stable_id
        )
    ).all()

    return {"features": [feature.value for feature in results]}
