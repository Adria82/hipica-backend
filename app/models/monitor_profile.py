"""
Modelo de perfil extendido para usuarios con rol 'monitor' o 'assistant'.

Contiene datos adicionales del monitor/ayudante que no forman parte del User base.

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class MonitorProfile(SQLModel, table=True):
    """
    Perfil extendido para usuarios con role='monitor' o role='assistant'.

    Attributes:
        user_id (int): Clave primaria y FK a user.id.
        especialidad (Optional[str]): Especialidad o disciplina ecuestre.
        disponibilidad (Optional[str]): Horario o disponibilidad habitual.
        certificados (Optional[str]): Certificaciones o títulos.
        experiencia (Optional[str]): Años o descripción de experiencia.
        telefono (Optional[str]): Teléfono de contacto profesional.
        iban (Optional[str]): IBAN para pago de nómina/honorarios.
        notas (Optional[str]): Notas internas del administrador.
        tarifa_hora (Optional[float]): Tarifa por hora en euros.
        user (User): Relación inversa al usuario propietario.
    """
    __tablename__ = "monitorprofile"

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    especialidad: Optional[str] = Field(default=None)
    disponibilidad: Optional[str] = Field(default=None)
    certificados: Optional[str] = Field(default=None)
    experiencia: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None)
    iban: Optional[str] = Field(default=None)
    notas: Optional[str] = Field(default=None)
    tarifa_hora: Optional[float] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="monitor_profile")
