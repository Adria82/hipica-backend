"""
Esquemas de la entidad Level (nivel de equitación).

Define los modelos de entrada y salida utilizados por la API
para la gestión del catálogo de niveles de equitación.

Autor: Adrià Bofill
Fecha: 04/02/2026
Proyecto: Gestión de Hípica
"""

from typing import Optional
from sqlmodel import SQLModel


class LevelBase(SQLModel):
    """
    Atributos base de un nivel de equitación.
    """
    name: str


class LevelCreate(LevelBase):
    """
    Esquema para crear un nivel de equitación.
    """
    pass


class LevelUpdate(SQLModel):
    """
    Esquema para renombrar un nivel de equitación.
    """
    name: Optional[str] = None


class LevelRead(LevelBase):
    """
    Esquema de salida de un nivel de equitación.
    """
    id: int
