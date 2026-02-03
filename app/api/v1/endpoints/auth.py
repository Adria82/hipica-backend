from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from app.db.session import get_session
from app.models import User
from app.security import create_access_token, create_refresh_token, verify_password, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

router = APIRouter(tags=["auth"])

# ----------------- Schemas -----------------
class LoginRequest(BaseModel):
    """Datos de login."""
    email: str
    password: str

class TokenResponse(BaseModel):
    """Respuesta con access + refresh token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# ----------------- Endpoints -----------------
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    """
    Login de usuario: devuelve access + refresh tokens.

    Args:
        data (LoginRequest): email y contraseña del usuario.
        session (Session): sesión de SQLModel.

    Returns:
        TokenResponse: access_token y refresh_token.
    """
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    access_token = create_access_token({"sub": str(user.id), "role": user.role, "stable_id": user.stable_id})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str):
    """
    Genera un nuevo access token usando refresh token válido.

    Args:
        refresh_token (str): JWT de refresh.

    Returns:
        TokenResponse: nuevo access_token y el mismo refresh_token.
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Refresh token inválido")
        # Se podría verificar en DB que el usuario sigue activo
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    
    access_token = create_access_token({"sub": user_id})
    return {"access_token": access_token, "refresh_token": refresh_token}