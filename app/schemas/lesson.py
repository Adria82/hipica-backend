"""
Esquemas Pydantic para la entidad Lesson (clases).

Autor: Adrià Bofill
Fecha: 01/02/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel
from typing import List, Optional
from datetime import datetime


class LessonCreate(SQLModel):
    """
    Datos necesarios para crear una lección/clase.

    - client_ids: IDs de los clientes que asisten
    - horse_ids: IDs de los caballos usados
    - helper_id: ID del monitor ayudante (opcional)
    - track_id: ID de la pista (opcional)
    - description: notas adicionales (opcional)
    """
    date_time: datetime
    end_time: Optional[datetime] = None
    instructor_id: int
    helper_id: Optional[int] = None
    track_id: Optional[int] = None
    description: Optional[str] = None
    stable_id: Optional[int] = None  # el endpoint lo fuerza al del usuario
    client_ids: List[int] = []
    horse_ids: List[int] = []


class LessonRead(SQLModel):
    """
    Respuesta completa de una lección/clase con datos desnormalizados
    para facilitar la presentación en el frontend.
    """
    id: int
    date_time: datetime
    end_time: Optional[datetime] = None
    instructor_id: int
    instructor_email: str
    helper_id: Optional[int] = None
    helper_email: Optional[str] = None
    track_id: Optional[int] = None
    track_name: Optional[str] = None
    description: Optional[str] = None
    stable_id: int
    horse_names: List[str] = []
    client_names: List[str] = []


class LessonUpdate(SQLModel):
    """Datos para actualizar parcialmente una lección."""
    date_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    instructor_id: Optional[int] = None
    helper_id: Optional[int] = None
    track_id: Optional[int] = None
    description: Optional[str] = None
    stable_id: Optional[int] = None
    client_ids: Optional[List[int]] = None
    horse_ids: Optional[List[int]] = None
