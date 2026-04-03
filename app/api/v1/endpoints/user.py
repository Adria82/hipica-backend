"""
Endpoints CRUD para User (usuarios).

Autor:  Adrià Bofill
Fecha:  01/02/2026
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import Optional

from app.db.session import get_session
from app.models.user import User
from app.dependencies import get_current_user, require_role
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.security import hash_password
from app.core.i18n import t

router = APIRouter(prefix="/users", tags=["Users"])

# Roles elevados que solo app_admin puede asignar
_ELEVATED_ROLES = {"app_admin", "stable_admin"}


@router.post("/", response_model=UserRead, status_code=201)
def create_user(
    user_data: UserCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Crear un nuevo usuario.

    - app_admin puede crear usuarios con cualquier rol y en cualquier cuadra.
    - stable_admin solo puede crear usuarios con rol monitor o client,
      y dentro de su propia cuadra.
    """
    # stable_admin no puede crear usuarios con roles elevados
    if current_user.role == "stable_admin" and user_data.role in _ELEVATED_ROLES:
        raise HTTPException(
            status_code=403,
            detail=t(request, "auth.permission_denied"),
        )

    # stable_admin fuerza el stable_id de su cuadra
    if current_user.role == "stable_admin":
        user_data.stable_id = current_user.stable_id

    # Comprobar email duplicado
    existing = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=t(request, "user.email_exists"),
        )

    user = User(
        **user_data.model_dump(exclude={"password"}),
        hashed_password=hash_password(user_data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=list[UserRead])
def list_users(
    request: Request,
    role: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Listar usuarios.

    - app_admin ve todos los usuarios de todas las cuadras.
    - stable_admin ve solo los usuarios de su cuadra.

    Filtros opcionales:
    - role: filtra por rol (ej. 'client', 'monitor', 'assistant')
    """
    query = select(User)
    if current_user.role != "app_admin":
        query = query.where(User.stable_id == current_user.stable_id)
    if role:
        query = query.where(User.role == role)

    return session.exec(query).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Obtener un usuario por ID.

    stable_admin solo puede consultar usuarios de su cuadra.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=t(request, "user.not_found"))

    if current_user.role != "app_admin" and user.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Actualizar un usuario.

    - app_admin puede modificar cualquier campo de cualquier usuario.
    - stable_admin puede modificar usuarios de su cuadra, pero no puede
      asignarles roles elevados.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=t(request, "user.not_found"))

    if current_user.role != "app_admin" and user.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    # stable_admin no puede elevar roles
    if current_user.role == "stable_admin" and user_data.role in _ELEVATED_ROLES:
        raise HTTPException(
            status_code=403,
            detail=t(request, "auth.permission_denied"),
        )

    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["app_admin"])),
):
    """
    Eliminar un usuario.

    Solo accesible para app_admin.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=t(request, "user.not_found"))

    session.delete(user)
    session.commit()
    return {"ok": True}
