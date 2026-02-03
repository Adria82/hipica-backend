"""
Tablas intermedias (link tables) para relaciones N:N en la hípica.

- LessonHorseLink: relación lecciones <-> caballos
- LessonClientLink: relación lecciones <-> clientes

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field

class LessonHorseLink(SQLModel, table=True):
    """
    Tabla intermedia para relacionar Lecciones y Caballos
    """
    lesson_id: int = Field(foreign_key="lesson.id", primary_key=True)
    horse_id: int = Field(foreign_key="horse.id", primary_key=True)


class LessonClientLink(SQLModel, table=True):
    """
    Tabla intermedia para relacionar Lecciones y Clientes
    """
    lesson_id: int = Field(foreign_key="lesson.id", primary_key=True)
    client_id: int = Field(foreign_key="client.id", primary_key=True)