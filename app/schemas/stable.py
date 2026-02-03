"""
Esquemas de la entidad Stable (hípica).

Define los modelos de entrada y salida utilizados por la API
para la gestión de hípicas.

Autor: Adrià Bofill
Fecha: 31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel
from typing import Optional


class StableBase(SQLModel):
    """
    Atributos base de una hípica.
    """
    name: str
    location: str
    is_active: bool = True


class StableCreate(StableBase):
    """
    Esquema para crear una nueva hípica.
    """
    pass


class StableUpdate(SQLModel):
    """
    Esquema para actualizar parcialmente una hípica.
    """
    name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class StableRead(StableBase):
    """
    Esquema de lectura de una hípica.
    """
    id: int