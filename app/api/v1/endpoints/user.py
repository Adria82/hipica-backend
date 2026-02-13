"""
Endpoints CRUD para User (usuarios).

Autor:  Adrià Bofill
Fecha:  01/02/2026
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.security import hash_password
from app.core.i18n import t

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead)
def create_user(
    user_data: UserCreate,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Crear un nuevo usuario.
    """

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
    session: Session = Depends(get_session),
):
    """
    Listar todos los usuarios.
    """
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Obtener un usuario por ID.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=t(request, "user.not_found"))
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Actualizar un usuario.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=t(request, "user.not_found"))

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
):
    """
    Eliminar un usuario.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=t(request, "user.not_found"))

    session.delete(user)
    session.commit()
    return {"ok": True}
