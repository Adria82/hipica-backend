"""
Modelo de la entidad Lesson (clase/lección).

Representa una lección de equitación que involucra:
- Varios caballos
- Varios clientes
- Un monitor (User)

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
from app.models.links import LessonHorseLink, LessonClientLink  # IMPORTAR LAS CLASES DE TABLAS INTERMEDIAS

class Lesson(SQLModel, table=True):
    """
    Clase que representa una lección.

    Attributes:
        id (int): Identificador único de la lección.
        date_time (datetime): Fecha y hora de la lección.
        instructor_id (int): Id del monitor/instructor.
        stable_id (int): Id de la hípica a la que pertenece.
        horses (List[Horse]): Caballos asignados a la lección.
        clients (List[Client]): Clientes participantes en la lección.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    date_time: datetime = Field(nullable=False)
    instructor_id: int = Field(foreign_key="user.id")
    stable_id: int = Field(foreign_key="stable.id")

    # Relaciones N:N usando strings
    horses: List["Horse"] = Relationship(
        back_populates="lessons",
        link_model=LessonHorseLink
    )
    clients: List["Client"] = Relationship(
        back_populates="lessons",
        link_model=LessonClientLink
    )
Lesson.model_rebuild()