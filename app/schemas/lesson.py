"""
Esquemas Pydantic para la entidad Lesson (clases).

Autor: Adrià Bofill
Fecha: 01/02/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel
from typing import List, Optional
from datetime import datetime

from app.schemas.client import ClientRead
from app.schemas.horse import HorseRead


class LessonBase(SQLModel):
    date_time: datetime
    stable_id: int
    instructor_id: Optional[int] = None


class LessonCreate(LessonBase):
    """
    Datos necesarios para crear una lección/clase.

    - client_ids: IDs de los clientes que asisten
    - horse_ids: IDs de los caballos usados
    """
    client_ids: List[int]
    horse_ids: List[int]

class LessonRead(SQLModel):
    """
    Respuesta completa de una lección/clase.
    """
    id: int
    date_time: datetime
    instructor_id: int
    stable_id: int
    clients: List[ClientRead] = []
    horses: List[HorseRead] = []

class LessonUpdate(SQLModel):
    date_time: Optional[datetime] = None
    instructor_id: Optional[int] = None
    stable_id: Optional[int] = None
    client_ids: Optional[List[int]] = None
    horse_ids: Optional[List[int]] = None