"""
Modelo de la entidad Track (pista de equitación).

Representa una pista física dentro de una hípica donde se realizan clases.

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.lesson import Lesson


class Track(SQLModel, table=True):
    """
    Pista de equitación perteneciente a una hípica.

    Attributes:
        id (int): Identificador único de la pista.
        name (str): Nombre de la pista.
        stable_id (int): Id de la hípica a la que pertenece.
        is_active (bool): Si la pista está activa.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    stable_id: int = Field(foreign_key="stable.id", index=True)
    is_active: bool = Field(default=True)

    # Relación inversa: lecciones celebradas en esta pista
    lessons: list["Lesson"] = Relationship(back_populates="track")
