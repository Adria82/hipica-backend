from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from typing import Optional, List
from app.models.links import HorseLevelLink


class Level(SQLModel, table=True):
    """
    Tabla catálogo de niveles de equitación.
    Los nombres están almacenados como dict JSON {es, en, ca}
    para soportar múltiples idiomas.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    names: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

    horses: List["Horse"] = Relationship(
        back_populates="levels",
        link_model=HorseLevelLink
    )
