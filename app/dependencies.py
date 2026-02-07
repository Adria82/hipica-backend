"""
Este módulo contiene las dependencias de seguridad para FastAPI, que permiten:
1. Autenticación: obtener el usuario actual a partir de un JWT.
2. Autorización: restringir el acceso a endpoints según roles del usuario.

Funciones principales:

- get_current_user(token, session) -> User
    Obtiene el usuario autenticado a partir del token JWT. Lanza excepción 401 si no es válido o el usuario no existe.
    
- require_role(required_roles) -> función dependiente
    Valida que el usuario tenga uno de los roles indicados. Lanza excepción 403 si no tiene permisos.
    
Uso típico:

from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, require_role
from app.models import User

router = APIRouter()

# Ejemplo 1: endpoint protegido que devuelve información del usuario logueado
@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

# Ejemplo 2: endpoint protegido por roles
@router.get("/lessons")
def list_lessons(current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"]))):
    '''
    Lista lessons según permisos:
    - monitor: solo sus lecciones/clases
    - stable_admin: todas las lecciones/clases de su hípica
    - app_admin: todas las lecciones/clases de todas las hípicas
    '''
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from jose import JWTError, jwt
from app.models import User
from app.security import SECRET_KEY, ALGORITHM
from app.db.session import get_session


# Dependencia para leer el token Bearer desde la cabecera Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Obtiene el usuario actual a partir del JWT.

    Args:
        token (str): Token JWT enviado en la cabecera Authorization.
        session (Session): Sesión de SQLModel.

    Returns:
        User: Usuario autenticado.

    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 🔐 Validar tipo de token
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    user = session.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_role(required_roles: list[str]):
    """
    Dependencia que asegura que el usuario tenga uno de los roles indicados.

    Args:
        required_roles (list[str]): Lista de roles permitidos.

    Returns:
        User: Usuario autenticado si cumple con los roles.

    Raises:
        HTTPException 403: Si el usuario no tiene permisos.
    
    Uso:
        @router.get("/lessons")
        def list_lessons(current_user: User = Depends(require_role(["stable_admin", "app_admin"]))):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )
        return current_user

    return role_checker