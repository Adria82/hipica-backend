"""
Modelo de la entidad Stable (hípica).

Representa una hípica dentro de la aplicación.
Cada stable puede tener usuarios, caballos, clientes y lecciones.

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List

class Stable(SQLModel, table=True):
    """
    Clase que representa una hípica.

    Attributes:
        id (int): Identificador único de la hípica.
        name (str): Nombre de la hípica.
        location (Optional[str]): Ubicación física de la hípica.
        is_active (bool): Indica si la hípica está activa.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    location: Optional[str] = None
    is_active: bool = Field(default=True)
    theme: Optional[str] = Field(default="default")

    # Relación con usuarios
    users: List["User"] = Relationship(back_populates="stable")