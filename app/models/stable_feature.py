"""
Tabla que relaciona una hípica con las funcionalidades activadas.

Cada registro indica que una Stable tiene habilitada una Feature concreta.

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field
from app.models.feature import FeatureCode


class StableFeature(SQLModel, table=True):
    """
    Relación entre Stable y funcionalidades activas.

    PK compuesta:
        - stable_id
        - feature

    Evita duplicados automáticamente.
    """

    stable_id: int = Field(foreign_key="stable.id", primary_key=True)
    feature: FeatureCode = Field(primary_key=True)