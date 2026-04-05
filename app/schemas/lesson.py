"""
Esquemas Pydantic para la entidad Lesson (clases).

Autor: Adrià Bofill
Fecha: 01/02/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel
from typing import List, Optional
from datetime import datetime


class StudentHorsePair(SQLModel):
    """
    Par alumno-caballo dentro de una lección.

    - student_id: ID del usuario (role=client)
    - horse_id: ID del caballo asignado a ese alumno (puede ser None)
    """
    student_id: int
    horse_id: Optional[int] = None


class LessonCreate(SQLModel):
    """
    Datos necesarios para crear una lección/clase.

    - student_ids: IDs de los usuarios (role=client) que asisten (retrocompatibilidad)
    - student_horse_pairs: pares alumno-caballo; si está presente, tiene preferencia sobre student_ids
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
    student_ids: List[int] = []
    horse_ids: List[int] = []
    student_horse_pairs: Optional[List[StudentHorsePair]] = None
    max_students: Optional[int] = None
    is_published: bool = False


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
    student_names: List[str] = []
    student_horse_pairs: List[StudentHorsePair] = []
    max_students: Optional[int] = None
    is_published: bool = False
    recurrence_id: Optional[int] = None


class LessonUpdate(SQLModel):
    """Datos para actualizar parcialmente una lección."""
    date_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    instructor_id: Optional[int] = None
    helper_id: Optional[int] = None
    track_id: Optional[int] = None
    description: Optional[str] = None
    stable_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    horse_ids: Optional[List[int]] = None
    student_horse_pairs: Optional[List[StudentHorsePair]] = None
    max_students: Optional[int] = None
    is_published: Optional[bool] = None
