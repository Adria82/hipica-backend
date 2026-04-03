"""
Tablas intermedias (link tables) para relaciones N:N en la hípica.

- LessonHorseLink: relación lecciones <-> caballos
- LessonUserLink: relación lecciones <-> usuarios (alumnos)
- HorseLevelLink: relación caballos <-> niveles

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field


class LessonHorseLink(SQLModel, table=True):
    """
    Tabla intermedia para relacionar Lecciones y Caballos.
    """
    lesson_id: int = Field(foreign_key="lesson.id", primary_key=True)
    horse_id: int = Field(foreign_key="horse.id", primary_key=True)


class LessonUserLink(SQLModel, table=True):
    """
    Tabla intermedia para relacionar Lecciones y Usuarios (alumnos).

    Sustituye a la antigua LessonClientLink que referenciaba la tabla client.
    """
    __tablename__ = "lessonuserlink"

    lesson_id: int = Field(foreign_key="lesson.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)


class HorseLevelLink(SQLModel, table=True):
    """
    Relación entre caballos y niveles de equitación.
    """
    horse_id: int = Field(foreign_key="horse.id", primary_key=True)
    level_id: int = Field(foreign_key="level.id", primary_key=True)

