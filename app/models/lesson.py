"""
Modelo de la entidad Lesson (clase/lección).

Representa una lección de equitación que involucra:
- Varios caballos
- Varios usuarios (alumnos, role='client')
- Un monitor/instructor (User)
- Un ayudante opcional (User)
- Una pista opcional (Track)

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from app.models.links import LessonHorseLink, LessonUserLink

if TYPE_CHECKING:
    from app.models.track import Track
    from app.models.user import User


class Lesson(SQLModel, table=True):
    """
    Clase que representa una lección.

    Attributes:
        id (int): Identificador único de la lección.
        date_time (datetime): Fecha y hora de inicio de la lección.
        end_time (datetime | None): Fecha y hora de fin de la lección.
        instructor_id (int): Id del monitor/instructor principal.
        helper_id (int | None): Id del ayudante (monitor secundario).
        track_id (int | None): Id de la pista donde se celebra.
        description (str | None): Descripción o notas adicionales.
        stable_id (int): Id de la hípica a la que pertenece.
        horses (List[Horse]): Caballos asignados a la lección.
        students (List[User]): Usuarios alumnos participantes en la lección.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    date_time: datetime = Field(nullable=False)
    end_time: Optional[datetime] = Field(default=None, nullable=True)
    instructor_id: int = Field(foreign_key="user.id")
    helper_id: Optional[int] = Field(default=None, foreign_key="user.id", nullable=True)
    track_id: Optional[int] = Field(default=None, foreign_key="track.id", nullable=True)
    description: Optional[str] = Field(default=None, nullable=True)
    stable_id: int = Field(foreign_key="stable.id", index=True)

    # Relaciones N:N usando strings
    horses: List["Horse"] = Relationship(
        back_populates="lessons",
        link_model=LessonHorseLink
    )
    students: List["User"] = Relationship(
        link_model=LessonUserLink
    )

    # Relación con Track
    track: Optional["Track"] = Relationship(back_populates="lessons")


Lesson.model_rebuild()
