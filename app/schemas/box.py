"""
Esquemas de la entidad Box (box de una hípica).

Define los modelos de entrada y salida utilizados por la API
para la gestión de boxes de la hípica.

Autor: Adrià Bofill
Fecha: 02/04/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel
from typing import Optional


class BoxBase(SQLModel):
    """
    Atributos base de un box.

    Se reutiliza en los esquemas de creación y lectura.
    """

    name: str
    capacity: int = 1
    stable_id: int


class BoxCreate(BoxBase):
    """
    Esquema para crear un nuevo box.

    stable_id es opcional aquí porque el endpoint lo fuerza
    al stable_id del usuario autenticado (salvo app_admin).
    """

    stable_id: Optional[int] = None


class BoxUpdate(SQLModel):
    """
    Esquema para actualizar parcialmente un box.

    Todos los campos son opcionales.
    """

    name: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class BoxRead(SQLModel):
    """
    Esquema de salida de un box.

    Includes horses_count: número de caballos actualmente asignados,
    calculado en el endpoint (no es columna de DB).
    """

    id: int
    name: str
    capacity: int
    stable_id: int
    stable_name: Optional[str] = None
    is_active: bool
    horses_count: int
