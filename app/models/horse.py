"""
Modelo de la entidad Horse (caballo).

Representa un caballo que pertenece a una hípica y puede ser
asignado a una clase.

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from app.models.links import LessonHorseLink


class Horse(SQLModel, table=True):
    """
    Clase que representa un caballo.

    Attributes:
        id (int): Identificador único del caballo.
        name (str): Nombre del caballo.
        is_active (bool): Si el caballo está disponible.
        stable_id (int): Id de la hípica a la que pertenece.
        box (Optional[str]): Número de box/cuadra del caballo.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    stable_id: int = Field(foreign_key="stable.id")
    box: Optional[str]

    # Relación N:N con Lesson usando string -> evita circular import
    lessons: List["Lesson"] = Relationship(
        back_populates="horses",
        link_model=LessonHorseLink
    )

Horse.model_rebuild()
