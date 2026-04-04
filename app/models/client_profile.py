"""
Modelo de perfil extendido para usuarios con rol 'client'.

Contiene datos adicionales del alumno que no forman parte del User base.

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class ClientProfile(SQLModel, table=True):
    """
    Perfil extendido para usuarios con role='client'.

    Attributes:
        user_id (int): Clave primaria y FK a user.id.
        apellidos (Optional[str]): Apellidos del cliente.
        direccion (Optional[str]): Dirección postal.
        iban (Optional[str]): IBAN para pagos/domiciliación.
        notes (Optional[str]): Notas internas del administrador.
        user (User): Relación inversa al usuario propietario.
    """
    __tablename__ = "clientprofile"

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    apellidos: Optional[str] = Field(default=None)
    direccion: Optional[str] = Field(default=None)
    iban: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    level_id: Optional[int] = Field(default=None, foreign_key="level.id")

    user: Optional["User"] = Relationship(back_populates="client_profile")
