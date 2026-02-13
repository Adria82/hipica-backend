"""
Endpoints de autenticación.

Incluye:
- Login con OAuth2 (username/password)
- Emisión de access token + refresh token
- Refresh de access token

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from jose import jwt, JWTError
from app.schemas.auth import TokenResponse, RefreshRequest

from app.db.session import get_session
from app.models import User
from app.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    SECRET_KEY,
    ALGORITHM,
)
from app.core.i18n import t

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Login de usuario: devuelve access + refresh tokens.

    Args:
        data (LoginRequest): email y contraseña del usuario.
        session (Session): sesión de SQLModel.

    Returns:
        TokenResponse: access_token y refresh_token.
    """
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t(request, "auth.credentials_invalid"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(data: RefreshRequest, request: Request):
    """
    Genera un nuevo access token usando refresh token válido.

    Args:
        refresh_token (str): JWT de refresh.

    Returns:
        TokenResponse: nuevo access_token y el mismo refresh_token.
    """
    try:
        payload = jwt.decode(
            data.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=t(request, "auth.refresh_token_invalid"),
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=t(request, "auth.refresh_token_invalid"),
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t(request, "auth.refresh_token_invalid"),
        )

    new_access_token = create_access_token(
        data={"sub": str(user_id)}
    )

    return {
        "access_token": new_access_token,
        "refresh_token": data.refresh_token,
        "token_type": "bearer",
    }
