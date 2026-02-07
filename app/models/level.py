from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from app.models.links import HorseLevelLink


class NivelEquitacion(str, Enum):
    """
    Enum que define los niveles de equitación.

    - PRINCIPIANTE: Personas sin experiencia previa.
    - INICIADO: Personas con nociones básicas.
    - EXPERTO: Jinetes avanzados.
    """
    PRINCIPIANTE = "principiante"
    INICIADO = "iniciado"
    EXPERTO = "experto"


class Level(SQLModel, table=True):
    """
    Tabla catálogo de niveles de equitación.
    Gestionada por administradores.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: NivelEquitacion = Field(index=True, unique=True)

    horses: List["Horse"] = Relationship(
        back_populates="levels",
        link_model=HorseLevelLink
    )