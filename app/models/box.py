"""
Modelo de la entidad Box (box de una hípica).

Representa un box físico dentro de una hípica donde se alojan
los caballos.

Autor: Adrià Bofill
Fecha: 02/04/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class Box(SQLModel, table=True):
    """
    Clase que representa un box de una hípica.

    Attributes:
        id (int): Identificador único del box.
        name (str): Nombre o número del box (ej: "Box 1", "A3").
        capacity (int): Número máximo de caballos que puede albergar.
        stable_id (int): Id de la hípica a la que pertenece.
        is_active (bool): Si el box está disponible.
        horses (List[Horse]): Caballos actualmente asignados a este box.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    capacity: int = Field(default=1, ge=1)
    stable_id: int = Field(foreign_key="stable.id", index=True)
    is_active: bool = Field(default=True)

    # Relación inversa con Horse
    horses: List["Horse"] = Relationship(back_populates="box")
