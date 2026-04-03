from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from app.models.links import HorseLevelLink


class Level(SQLModel, table=True):
    """
    Tabla catálogo de niveles de equitación.
    El nombre es un texto libre (sin enum), gestionado por administradores.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    horses: List["Horse"] = Relationship(
        back_populates="levels",
        link_model=HorseLevelLink
    )
