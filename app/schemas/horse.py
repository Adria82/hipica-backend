"""
Esquemas de la entidad Horse (caballo).

Define los modelos de entrada y salida utilizados por la API
para la gestión de caballos de la hípica.

Autor: Adrià Bofill
Fecha: 01/02/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel
from typing import List, Optional

from app.models.level import NivelEquitacion


class HorseBase(SQLModel):
    """
    Atributos base de un caballo.

    Se reutiliza en los esquemas de creación y lectura.
    """
    name: str
    breed: Optional[str] = None
    is_active: bool = True
    stable_id: int


class HorseCreate(HorseBase):
    """
    Esquema para crear un nuevo caballo.
    """
    pass


class HorseUpdate(SQLModel):
    """
    Esquema para actualizar parcialmente un caballo.

    Puede ser utilizado por administradores para modificar
    los niveles de equitación asignados.
    """
    name: Optional[str] = None
    breed: Optional[str] = None
    is_active: Optional[bool] = None
    stable_id: Optional[int] = None
    levels: Optional[List[NivelEquitacion]] = None

class HorseRead(SQLModel):
    """
    Esquema de salida de un caballo.
    """
    id: int
    name: str
    box: Optional[str] = None
    is_active: bool
    stable_id: int
    levels: List[NivelEquitacion]