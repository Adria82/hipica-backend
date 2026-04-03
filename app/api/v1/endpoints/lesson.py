"""
Endpoints CRUD para Lesson (clases).

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from sqlalchemy import delete
from typing import List, Optional

from app.db.session import get_session
from app.models.lesson import Lesson
from app.models.horse import Horse
from app.models.track import Track
from app.models.links import LessonUserLink, LessonHorseLink
from app.dependencies import require_role
from app.models import User
from app.schemas.lesson import LessonCreate, LessonRead, LessonUpdate
from app.core.i18n import t

router = APIRouter(prefix="/lessons", tags=["Lessons"])

# Roles con acceso a gestión de clases (instructor y ayudante)
STAFF_ROLES = ["monitor", "assistant"]


def _build_lesson_read(lesson: Lesson, session: Session) -> LessonRead:
    """
    Construye un LessonRead con todos los campos desnormalizados:
    instructor_email, helper_email, track_name, horse_names, student_names.
    """
    instructor = session.get(User, lesson.instructor_id)
    instructor_email = instructor.email if instructor else "—"

    helper_email: Optional[str] = None
    if lesson.helper_id:
        helper = session.get(User, lesson.helper_id)
        helper_email = helper.email if helper else None

    track_name: Optional[str] = None
    if lesson.track_id:
        track = session.get(Track, lesson.track_id)
        track_name = track.name if track else None

    horse_links = session.exec(
        select(LessonHorseLink).where(LessonHorseLink.lesson_id == lesson.id)
    ).all()
    horse_names = []
    for hl in horse_links:
        horse = session.get(Horse, hl.horse_id)
        if horse:
            horse_names.append(horse.name)

    student_links = session.exec(
        select(LessonUserLink).where(LessonUserLink.lesson_id == lesson.id)
    ).all()
    student_names = []
    for sl in student_links:
        student = session.get(User, sl.user_id)
        if student:
            student_names.append(student.name)

    return LessonRead(
        id=lesson.id,
        date_time=lesson.date_time,
        end_time=lesson.end_time,
        instructor_id=lesson.instructor_id,
        instructor_email=instructor_email,
        helper_id=lesson.helper_id,
        helper_email=helper_email,
        track_id=lesson.track_id,
        track_name=track_name,
        description=lesson.description,
        stable_id=lesson.stable_id,
        horse_names=horse_names,
        student_names=student_names,
    )


@router.get("/", response_model=List[LessonRead])
def list_lessons(
    request: Request,
    instructor_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "assistant", "stable_admin", "app_admin"])),
):
    """
    Listar todas las lecciones de la cuadra del usuario autenticado.

    app_admin ve lecciones de todas las cuadras.
    Filtros opcionales:
    - instructor_id: devuelve solo lecciones de este instructor
    """
    query = select(Lesson)
    if current_user.role != "app_admin":
        query = query.where(Lesson.stable_id == current_user.stable_id)
    if instructor_id:
        query = query.where(Lesson.instructor_id == instructor_id)

    lessons = session.exec(query).all()
    return [_build_lesson_read(lesson, session) for lesson in lessons]


@router.post("/", response_model=LessonRead, status_code=201)
def create_lesson(
    lesson_data: LessonCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Crear una nueva lección/clase y asociar alumnos y caballos.

    El stable_id se fuerza al de la cuadra del usuario autenticado.
    Solo accesible para stable_admin y app_admin.
    """
    if current_user.role != "app_admin":
        lesson_data.stable_id = current_user.stable_id

    if not lesson_data.stable_id:
        raise HTTPException(status_code=400, detail=t(request, "lesson.stable_required"))

    lesson = Lesson(
        date_time=lesson_data.date_time,
        end_time=lesson_data.end_time,
        instructor_id=lesson_data.instructor_id,
        helper_id=lesson_data.helper_id,
        track_id=lesson_data.track_id,
        description=lesson_data.description,
        stable_id=lesson_data.stable_id,
    )
    session.add(lesson)
    session.commit()
    session.refresh(lesson)

    # Asociar alumnos (usuarios con role=client)
    for student_id in lesson_data.student_ids:
        student = session.get(User, student_id)
        if not student:
            raise HTTPException(
                status_code=404,
                detail=t(request, "lesson.client_not_found", client_id=student_id),
            )
        session.add(LessonUserLink(lesson_id=lesson.id, user_id=student_id))

    # Asociar caballos
    for horse_id in lesson_data.horse_ids:
        horse = session.get(Horse, horse_id)
        if not horse:
            raise HTTPException(
                status_code=404,
                detail=t(request, "lesson.horse_not_found", horse_id=horse_id),
            )
        session.add(LessonHorseLink(lesson_id=lesson.id, horse_id=horse_id))

    session.commit()

    return _build_lesson_read(lesson, session)


@router.get("/{lesson_id}", response_model=LessonRead)
def get_lesson(
    lesson_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "assistant", "stable_admin", "app_admin"])),
):
    """Obtener una lección/clase con todos sus datos."""
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail=t(request, "lesson.not_found"))

    if current_user.role != "app_admin" and lesson.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    return _build_lesson_read(lesson, session)


@router.put("/{lesson_id}", response_model=LessonRead)
def update_lesson(
    lesson_id: int,
    lesson_update: LessonUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Actualizar una lección existente.

    Solo accesible para stable_admin y app_admin.
    """
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail=t(request, "lesson.not_found"))

    if current_user.role != "app_admin" and lesson.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    # Actualizar campos escalares
    if lesson_update.date_time is not None:
        lesson.date_time = lesson_update.date_time
    if lesson_update.end_time is not None:
        lesson.end_time = lesson_update.end_time
    if lesson_update.instructor_id is not None:
        lesson.instructor_id = lesson_update.instructor_id
    # helper_id y track_id pueden setearse a None explícitamente
    if "helper_id" in lesson_update.model_fields_set:
        lesson.helper_id = lesson_update.helper_id
    if "track_id" in lesson_update.model_fields_set:
        lesson.track_id = lesson_update.track_id
    if "description" in lesson_update.model_fields_set:
        lesson.description = lesson_update.description
    if lesson_update.stable_id is not None:
        lesson.stable_id = lesson_update.stable_id

    session.add(lesson)
    session.commit()

    # Actualizar relaciones N:N
    if lesson_update.student_ids is not None:
        session.exec(
            delete(LessonUserLink).where(LessonUserLink.lesson_id == lesson.id)
        )
        session.add_all(
            [LessonUserLink(lesson_id=lesson.id, user_id=uid) for uid in lesson_update.student_ids]
        )

    if lesson_update.horse_ids is not None:
        session.exec(
            delete(LessonHorseLink).where(LessonHorseLink.lesson_id == lesson.id)
        )
        session.add_all(
            [LessonHorseLink(lesson_id=lesson.id, horse_id=hid) for hid in lesson_update.horse_ids]
        )

    session.commit()
    session.refresh(lesson)
    return _build_lesson_read(lesson, session)


@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Eliminar una lección y sus relaciones N:N.

    Solo accesible para stable_admin y app_admin.
    """
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail=t(request, "lesson.not_found"))

    if current_user.role != "app_admin" and lesson.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    # Borrar relaciones N:N antes de borrar la lección
    session.exec(delete(LessonUserLink).where(LessonUserLink.lesson_id == lesson_id))
    session.exec(delete(LessonHorseLink).where(LessonHorseLink.lesson_id == lesson_id))

    session.delete(lesson)
    session.commit()
    return {"ok": True}
