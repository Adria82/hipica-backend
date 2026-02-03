"""
Modelo de la entidad User (usuario).

Representa un usuario de la aplicación, que puede ser:
- Admin (dueño de la hípica)
- Monitor (instructor de clases)

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from datetime import datetime, timezone
from sqlmodel import Field, SQLModel,  Relationship
from typing import Optional
from app.models.stable import Stable

class User(SQLModel, table=True):
    """
    Clase que representa un usuario de la aplicación.

    Attributes:
        id (int): Identificador único del usuario.
        name (str): Nombre del usuario.
        email (str): Correo electrónico único.
        hashed_password (str): Contraseña hasheada del usuario.
        role (str): Rol del usuario ('app_admin', 'stable_admin', 'monitor', 'cliente').
        stable_id (Optional[int]): Id de la hípica a la que pertenece. None si es 'app_admin'.
        stable (Optional[Stable]): Objeto de la hípica asociada, accesible desde ORM.
        is_active (bool): Indica si el usuario está activo.
        created_at (datetime): Fecha de creación del usuario.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False, index=True, unique=True)
    hashed_password: str = Field(nullable=False)
    role: str = Field(nullable=False, default="cliente")  # 'app_admin', 'stable_admin', 'monitor', 'cliente'
    stable_id: Optional[int] = Field(default=None, foreign_key="stable.id")  # None para app_admin
    stable: Optional[Stable] = Relationship(back_populates="users")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))