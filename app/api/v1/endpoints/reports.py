"""
Endpoints de informes agregados para la hípica.

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime, date

from app.db.session import get_session
from app.models.lesson import Lesson
from app.models.horse import Horse
from app.models.links import LessonUserLink, LessonHorseLink
from app.dependencies import require_role
from app.models import User
from sqlmodel import SQLModel

router = APIRouter(prefix="/reports", tags=["Reports"])


# ---------------------------------------------------------------------------
# Schemas de respuesta para informes
# ---------------------------------------------------------------------------

class InstructorHours(SQLModel):
    """Horas impartidas por un instructor en el rango de fechas."""
    user_id: int
    email: str
    hours: float


class HelperHours(SQLModel):
    """Horas como ayudante en el rango de fechas."""
    user_id: int
    email: str
    hours: float


class StudentClasses(SQLModel):
    """Número de clases asistidas por un alumno (usuario) en el rango de fechas."""
    user_id: int
    name: str
    class_count: int


class HorseHours(SQLModel):
    """Horas de trabajo de un caballo en el rango de fechas."""
    horse_id: int
    name: str
    hours: float


class LessonReport(SQLModel):
    """Informe completo de clases para un rango de fechas."""
    instructor_hours: list[InstructorHours]
    helper_hours: list[HelperHours]
    student_classes: list[StudentClasses]
    horse_hours: list[HorseHours]
    from_date: Optional[str] = None
    to_date: Optional[str] = None


def _lesson_duration_hours(lesson: Lesson) -> float:
    """Calcula la duración de una lección en horas. Devuelve 1.0 si no hay end_time."""
    if lesson.end_time and lesson.end_time > lesson.date_time:
        delta = lesson.end_time - lesson.date_time
        return delta.total_seconds() / 3600
    return 1.0


@router.get("/lessons", response_model=LessonReport)
def lessons_report(
    request: Request,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Informe agregado de clases para un rango de fechas.

    Devuelve:
    - instructor_hours: horas impartidas por cada instructor
    - helper_hours: horas como ayudante por cada usuario
    - student_classes: número de clases de cada alumno
    - horse_hours: horas trabajadas por cada caballo

    Filtros opcionales:
    - from_date: fecha de inicio (inclusive)
    - to_date: fecha de fin (inclusive)
    """
    query = select(Lesson)
    if current_user.role != "app_admin":
        query = query.where(Lesson.stable_id == current_user.stable_id)
    if from_date:
        query = query.where(Lesson.date_time >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.where(Lesson.date_time <= datetime.combine(to_date, datetime.max.time()))

    lessons = session.exec(query).all()

    # Aggregations
    instructor_map: dict[int, float] = {}
    helper_map: dict[int, float] = {}
    student_map: dict[int, int] = {}
    horse_map: dict[int, float] = {}

    for lesson in lessons:
        duration = _lesson_duration_hours(lesson)

        # Instructor hours
        instructor_map[lesson.instructor_id] = instructor_map.get(lesson.instructor_id, 0) + duration

        # Helper hours
        if lesson.helper_id:
            helper_map[lesson.helper_id] = helper_map.get(lesson.helper_id, 0) + duration

        # Student classes
        student_links = session.exec(
            select(LessonUserLink).where(LessonUserLink.lesson_id == lesson.id)
        ).all()
        for sl in student_links:
            student_map[sl.user_id] = student_map.get(sl.user_id, 0) + 1

        # Horse hours
        horse_links = session.exec(
            select(LessonHorseLink).where(LessonHorseLink.lesson_id == lesson.id)
        ).all()
        for hl in horse_links:
            horse_map[hl.horse_id] = horse_map.get(hl.horse_id, 0) + duration

    # Build response lists
    instructor_hours: list[InstructorHours] = []
    for user_id, hours in instructor_map.items():
        user = session.get(User, user_id)
        if user:
            instructor_hours.append(InstructorHours(user_id=user_id, email=user.email, hours=round(hours, 2)))

    helper_hours: list[HelperHours] = []
    for user_id, hours in helper_map.items():
        user = session.get(User, user_id)
        if user:
            helper_hours.append(HelperHours(user_id=user_id, email=user.email, hours=round(hours, 2)))

    student_classes: list[StudentClasses] = []
    for user_id, count in student_map.items():
        student = session.get(User, user_id)
        if student:
            student_classes.append(StudentClasses(user_id=user_id, name=student.name, class_count=count))

    horse_hours: list[HorseHours] = []
    for horse_id, hours in horse_map.items():
        horse = session.get(Horse, horse_id)
        if horse:
            horse_hours.append(HorseHours(horse_id=horse_id, name=horse.name, hours=round(hours, 2)))

    return LessonReport(
        instructor_hours=sorted(instructor_hours, key=lambda x: x.hours, reverse=True),
        helper_hours=sorted(helper_hours, key=lambda x: x.hours, reverse=True),
        student_classes=sorted(student_classes, key=lambda x: x.class_count, reverse=True),
        horse_hours=sorted(horse_hours, key=lambda x: x.hours, reverse=True),
        from_date=str(from_date) if from_date else None,
        to_date=str(to_date) if to_date else None,
    )
