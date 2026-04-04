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
from app.models.track import Track
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
    name: str
    email: str
    hours: float
    class_count: int


class HelperHours(SQLModel):
    """Horas como ayudante en el rango de fechas."""
    user_id: int
    name: str
    email: str
    hours: float
    class_count: int


class StudentClasses(SQLModel):
    """Número de clases asistidas por un alumno (usuario) en el rango de fechas."""
    user_id: int
    name: str
    class_count: int
    hours: float


class HorseHours(SQLModel):
    """Horas de trabajo de un caballo en el rango de fechas."""
    horse_id: int
    name: str
    hours: float


class TrackHours(SQLModel):
    """Horas de uso de una pista en el rango de fechas."""
    track_id: int
    name: str
    class_count: int
    hours: float


class LessonReport(SQLModel):
    """Informe completo de clases para un rango de fechas."""
    instructor_hours: list[InstructorHours]
    helper_hours: list[HelperHours]
    student_classes: list[StudentClasses]
    horse_hours: list[HorseHours]
    track_hours: list[TrackHours]
    from_date: Optional[str] = None
    to_date: Optional[str] = None


class LessonDetail(SQLModel):
    """Detalle de una lección individual para drill-down."""
    lesson_id: int
    date_time: str
    end_time: Optional[str]
    duration_hours: float
    track_name: Optional[str]
    instructor_name: str


def _lesson_duration_hours(lesson: Lesson) -> float:
    """Calcula la duración de una lección en horas. Devuelve 1.0 si no hay end_time."""
    if lesson.end_time and lesson.end_time > lesson.date_time:
        delta = lesson.end_time - lesson.date_time
        return delta.total_seconds() / 3600
    return 1.0


def _apply_date_and_stable_filters(
    query,
    current_user: User,
    stable_id: Optional[int],
    from_date: Optional[date],
    to_date: Optional[date],
):
    """Aplica filtros de stable_id y rango de fechas a una query de Lesson."""
    if current_user.role == "app_admin":
        if stable_id is not None:
            query = query.where(Lesson.stable_id == stable_id)
    else:
        query = query.where(Lesson.stable_id == current_user.stable_id)
    if from_date:
        query = query.where(Lesson.date_time >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.where(Lesson.date_time <= datetime.combine(to_date, datetime.max.time()))
    return query


@router.get("/lessons", response_model=LessonReport)
def lessons_report(
    request: Request,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    stable_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Informe agregado de clases para un rango de fechas.

    Devuelve:
    - instructor_hours: horas impartidas por cada instructor (con name y class_count)
    - helper_hours: horas como ayudante por cada usuario (con name y class_count)
    - student_classes: número de clases y horas de cada alumno
    - horse_hours: horas trabajadas por cada caballo
    - track_hours: horas de uso y número de clases por pista

    Filtros opcionales:
    - from_date: fecha de inicio (inclusive)
    - to_date: fecha de fin (inclusive)
    - stable_id: solo para app_admin; si se omite devuelve datos de todas las hípicas
    """
    query = select(Lesson)
    query = _apply_date_and_stable_filters(query, current_user, stable_id, from_date, to_date)
    lessons = session.exec(query).all()

    # Aggregations
    instructor_hours_map: dict[int, float] = {}
    instructor_count_map: dict[int, int] = {}
    helper_hours_map: dict[int, float] = {}
    helper_count_map: dict[int, int] = {}
    student_hours_map: dict[int, float] = {}
    student_count_map: dict[int, int] = {}
    horse_map: dict[int, float] = {}
    track_hours_map: dict[int, float] = {}
    track_count_map: dict[int, int] = {}

    for lesson in lessons:
        duration = _lesson_duration_hours(lesson)

        # Instructor hours + class_count
        instructor_hours_map[lesson.instructor_id] = instructor_hours_map.get(lesson.instructor_id, 0) + duration
        instructor_count_map[lesson.instructor_id] = instructor_count_map.get(lesson.instructor_id, 0) + 1

        # Helper hours + class_count
        if lesson.helper_id:
            helper_hours_map[lesson.helper_id] = helper_hours_map.get(lesson.helper_id, 0) + duration
            helper_count_map[lesson.helper_id] = helper_count_map.get(lesson.helper_id, 0) + 1

        # Student classes + hours
        student_links = session.exec(
            select(LessonUserLink).where(LessonUserLink.lesson_id == lesson.id)
        ).all()
        for sl in student_links:
            student_count_map[sl.user_id] = student_count_map.get(sl.user_id, 0) + 1
            student_hours_map[sl.user_id] = student_hours_map.get(sl.user_id, 0) + duration

        # Horse hours
        horse_links = session.exec(
            select(LessonHorseLink).where(LessonHorseLink.lesson_id == lesson.id)
        ).all()
        for hl in horse_links:
            horse_map[hl.horse_id] = horse_map.get(hl.horse_id, 0) + duration

        # Track hours + class_count
        if lesson.track_id:
            track_hours_map[lesson.track_id] = track_hours_map.get(lesson.track_id, 0) + duration
            track_count_map[lesson.track_id] = track_count_map.get(lesson.track_id, 0) + 1

    # Build response lists
    instructor_hours: list[InstructorHours] = []
    for user_id, hours in instructor_hours_map.items():
        user = session.get(User, user_id)
        if user:
            instructor_hours.append(InstructorHours(
                user_id=user_id,
                name=user.name,
                email=user.email,
                hours=round(hours, 2),
                class_count=instructor_count_map.get(user_id, 0),
            ))

    helper_hours: list[HelperHours] = []
    for user_id, hours in helper_hours_map.items():
        user = session.get(User, user_id)
        if user:
            helper_hours.append(HelperHours(
                user_id=user_id,
                name=user.name,
                email=user.email,
                hours=round(hours, 2),
                class_count=helper_count_map.get(user_id, 0),
            ))

    student_classes: list[StudentClasses] = []
    for user_id, count in student_count_map.items():
        student = session.get(User, user_id)
        if student:
            student_classes.append(StudentClasses(
                user_id=user_id,
                name=student.name,
                class_count=count,
                hours=round(student_hours_map.get(user_id, 0), 2),
            ))

    horse_hours: list[HorseHours] = []
    for horse_id, hours in horse_map.items():
        horse = session.get(Horse, horse_id)
        if horse:
            horse_hours.append(HorseHours(horse_id=horse_id, name=horse.name, hours=round(hours, 2)))

    track_hours: list[TrackHours] = []
    for track_id, hours in track_hours_map.items():
        track = session.get(Track, track_id)
        if track:
            track_hours.append(TrackHours(
                track_id=track_id,
                name=track.name,
                class_count=track_count_map.get(track_id, 0),
                hours=round(hours, 2),
            ))

    return LessonReport(
        instructor_hours=sorted(instructor_hours, key=lambda x: x.hours, reverse=True),
        helper_hours=sorted(helper_hours, key=lambda x: x.hours, reverse=True),
        student_classes=sorted(student_classes, key=lambda x: x.class_count, reverse=True),
        horse_hours=sorted(horse_hours, key=lambda x: x.hours, reverse=True),
        track_hours=sorted(track_hours, key=lambda x: x.hours, reverse=True),
        from_date=str(from_date) if from_date else None,
        to_date=str(to_date) if to_date else None,
    )


@router.get("/lessons/by-user/{user_id}", response_model=list[LessonDetail])
def lessons_by_user(
    user_id: int,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    stable_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Detalle de clases de un usuario (instructor, ayudante o alumno) para drill-down.

    Devuelve las lecciones donde el usuario participó como instructor, ayudante o alumno
    dentro del rango de fechas indicado.
    """
    # Lecciones donde el usuario es instructor o ayudante
    query_direct = select(Lesson).where(
        (Lesson.instructor_id == user_id) | (Lesson.helper_id == user_id)
    )
    query_direct = _apply_date_and_stable_filters(query_direct, current_user, stable_id, from_date, to_date)
    direct_lessons = session.exec(query_direct).all()
    direct_ids = {l.id for l in direct_lessons}

    # Lecciones donde el usuario es alumno
    student_links = session.exec(
        select(LessonUserLink).where(LessonUserLink.user_id == user_id)
    ).all()
    student_lesson_ids = [sl.lesson_id for sl in student_links]

    if student_lesson_ids:
        query_student = select(Lesson).where(Lesson.id.in_(student_lesson_ids))  # type: ignore[attr-defined]
        query_student = _apply_date_and_stable_filters(query_student, current_user, stable_id, from_date, to_date)
        student_lessons = session.exec(query_student).all()
    else:
        student_lessons = []

    # Combinar y deduplicar
    all_lessons = list(direct_lessons)
    for lesson in student_lessons:
        if lesson.id not in direct_ids:
            all_lessons.append(lesson)

    all_lessons.sort(key=lambda l: l.date_time)

    result: list[LessonDetail] = []
    for lesson in all_lessons:
        instructor = session.get(User, lesson.instructor_id)
        track = session.get(Track, lesson.track_id) if lesson.track_id else None
        result.append(LessonDetail(
            lesson_id=lesson.id,
            date_time=lesson.date_time.isoformat(),
            end_time=lesson.end_time.isoformat() if lesson.end_time else None,
            duration_hours=round(_lesson_duration_hours(lesson), 2),
            track_name=track.name if track else None,
            instructor_name=instructor.name if instructor else "",
        ))

    return result


@router.get("/lessons/by-horse/{horse_id}", response_model=list[LessonDetail])
def lessons_by_horse(
    horse_id: int,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    stable_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Detalle de clases de un caballo para drill-down.

    Devuelve las lecciones donde el caballo participó dentro del rango de fechas indicado.
    """
    horse_links = session.exec(
        select(LessonHorseLink).where(LessonHorseLink.horse_id == horse_id)
    ).all()
    lesson_ids = [hl.lesson_id for hl in horse_links]

    if not lesson_ids:
        return []

    query = select(Lesson).where(Lesson.id.in_(lesson_ids))  # type: ignore[attr-defined]
    query = _apply_date_and_stable_filters(query, current_user, stable_id, from_date, to_date)
    lessons = session.exec(query).all()
    lessons = sorted(lessons, key=lambda l: l.date_time)

    result: list[LessonDetail] = []
    for lesson in lessons:
        instructor = session.get(User, lesson.instructor_id)
        track = session.get(Track, lesson.track_id) if lesson.track_id else None
        result.append(LessonDetail(
            lesson_id=lesson.id,
            date_time=lesson.date_time.isoformat(),
            end_time=lesson.end_time.isoformat() if lesson.end_time else None,
            duration_hours=round(_lesson_duration_hours(lesson), 2),
            track_name=track.name if track else None,
            instructor_name=instructor.name if instructor else "",
        ))

    return result


@router.get("/lessons/by-track/{track_id}", response_model=list[LessonDetail])
def lessons_by_track(
    track_id: int,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    stable_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Detalle de clases de una pista para drill-down.

    Devuelve las lecciones realizadas en la pista indicada dentro del rango de fechas.
    """
    query = select(Lesson).where(Lesson.track_id == track_id)
    query = _apply_date_and_stable_filters(query, current_user, stable_id, from_date, to_date)
    lessons = session.exec(query).all()
    lessons = sorted(lessons, key=lambda l: l.date_time)

    result: list[LessonDetail] = []
    for lesson in lessons:
        instructor = session.get(User, lesson.instructor_id)
        trk = session.get(Track, lesson.track_id) if lesson.track_id else None
        result.append(LessonDetail(
            lesson_id=lesson.id,
            date_time=lesson.date_time.isoformat(),
            end_time=lesson.end_time.isoformat() if lesson.end_time else None,
            duration_hours=round(_lesson_duration_hours(lesson), 2),
            track_name=trk.name if trk else None,
            instructor_name=instructor.name if instructor else "",
        ))

    return result
