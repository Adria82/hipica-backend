"""
Esquemas Pydantic para la entidad Track (pista de equitación).

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel
from typing import Optional


class TrackCreate(SQLModel):
    """Datos para crear una nueva pista."""
    name: str
    stable_id: Optional[int] = None  # el endpoint lo fuerza al del usuario


class TrackUpdate(SQLModel):
    """Datos para actualizar una pista. Todos los campos son opcionales."""
    name: Optional[str] = None
    is_active: Optional[bool] = None


class TrackRead(SQLModel):
    """Respuesta completa de una pista."""
    id: int
    name: str
    stable_id: int
    is_active: bool
