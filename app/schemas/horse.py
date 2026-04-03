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

    stable_id es opcional aquí porque el endpoint lo fuerza
    al stable_id del usuario autenticado (salvo app_admin).
    """
    stable_id: Optional[int] = None
    box_id: Optional[int] = None


class HorseUpdate(SQLModel):
    """
    Esquema para actualizar parcialmente un caballo.

    Puede ser utilizado por administradores para modificar
    los niveles de equitación asignados o el box asignado.
    levels acepta una lista de IDs de nivel.
    """
    name: Optional[str] = None
    breed: Optional[str] = None
    box_id: Optional[int] = None
    is_active: Optional[bool] = None
    stable_id: Optional[int] = None
    levels: Optional[List[int]] = None

class HorseRead(SQLModel):
    """
    Esquema de salida de un caballo.
    levels: nombres localizados según Accept-Language de la request.
    level_ids: IDs de los niveles asignados (para edición en formularios).
    """
    id: int
    name: str
    box_id: Optional[int] = None
    box_name: Optional[str] = None
    is_active: bool
    stable_id: int
    stable_name: Optional[str] = None
    levels: List[str]
    level_ids: List[int] = []
