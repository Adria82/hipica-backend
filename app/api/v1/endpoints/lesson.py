"""
Endpoints CRUD para Lesson (clases).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import delete
from typing import List, Optional

from app.db.session import get_session
from app.models.lesson import Lesson
from app.models.client import Client
from app.models.horse import Horse
from app.models.links import LessonClientLink, LessonHorseLink
from app.schemas.client import ClientRead
from app.schemas.horse import HorseRead
from app.schemas.lesson import LessonCreate, LessonRead, LessonUpdate

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.post("/", response_model=LessonRead)
def create_lesson(
    lesson_data: LessonCreate,
    session: Session = Depends(get_session),
):
    """
    Crear una nueva lección/clase y asociar clientes y caballos.
    """

    # Crear la lección
    lesson = Lesson(
        date_time=lesson_data.date_time,
        stable_id=lesson_data.stable_id,
        instructor_id=lesson_data.instructor_id,
    )
    session.add(lesson)
    session.commit()
    session.refresh(lesson)

    # Asociar clientes
    for client_id in lesson_data.client_ids:
        client = session.get(Client, client_id)
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente {client_id} no encontrado"
            )
        session.add(
            LessonClientLink(
                lesson_id=lesson.id,
                client_id=client_id
            )
        )

    # Asociar caballos
    for horse_id in lesson_data.horse_ids:
        horse = session.get(Horse, horse_id)
        if not horse:
            raise HTTPException(
                status_code=404,
                detail=f"Caballo {horse_id} no encontrado"
            )
        session.add(
            LessonHorseLink(
                lesson_id=lesson.id,
                horse_id=horse_id
            )
        )

    session.commit()

    return get_lesson(lesson.id, session)

@router.get("/{lesson_id}", response_model=LessonRead)
def get_lesson(
    lesson_id: int,
    session: Session = Depends(get_session),
):
    """
    Obtener una lección/clase con clientes y caballos.
    """
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Clientes
    client_links = session.exec(
        select(LessonClientLink).where(LessonClientLink.lesson_id == lesson.id)
    ).all()
    clients = [ClientRead.model_validate(session.get(Client, cl.client_id)) for cl in client_links]

    # Caballos
    horse_links = session.exec(
        select(LessonHorseLink).where(LessonHorseLink.lesson_id == lesson.id)
    ).all()
    horses = [HorseRead.model_validate(session.get(Horse, hl.horse_id)) for hl in horse_links]

    # Devolver la lección completa
    return LessonRead(
        id=lesson.id,
        date_time=lesson.date_time,
        instructor_id=lesson.instructor_id,
        stable_id=lesson.stable_id,
        clients=clients,
        horses=horses
    )



# ----------------------------
# Listar lecciones con filtros
# ----------------------------
@router.get("/", response_model=List[LessonRead])
def list_lessons(
    stable_id: Optional[int] = None,
    instructor_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """
    Listar todas las lecciones.

    Filtros opcionales:
    - stable_id: devuelve solo lecciones de esta hípica
    - instructor_id: devuelve solo lecciones de este instructor
    """
    query = select(Lesson)
    if stable_id:
        query = query.where(Lesson.stable_id == stable_id)
    if instructor_id:
        query = query.where(Lesson.instructor_id == instructor_id)

    lessons = session.exec(query).all()
    result = []

    for lesson in lessons:
        # Obtener clientes
        client_links = session.exec(
            select(LessonClientLink).where(LessonClientLink.lesson_id == lesson.id)
        ).all()
        clients = [session.get(Client, cl.client_id) for cl in client_links]

        # Obtener caballos
        horse_links = session.exec(
            select(LessonHorseLink).where(LessonHorseLink.lesson_id == lesson.id)
        ).all()
        horses = [session.get(Horse, hl.horse_id) for hl in horse_links]

        result.append(
            LessonRead(
                id=lesson.id,
                date_time=lesson.date_time,
                instructor_id=lesson.instructor_id,
                stable_id=lesson.stable_id,
                clients=clients,
                horses=horses
            )
        )

    return result

# ----------------------------
# Borrar lección
# ----------------------------
@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    session: Session = Depends(get_session),
):
    """
    Eliminar una lección y sus relaciones N:N.
    """
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    # Borrar relaciones N:N
    session.exec(
        delete(LessonClientLink).where(LessonClientLink.lesson_id == lesson_id)
    )
    session.exec(
        delete(LessonHorseLink).where(LessonHorseLink.lesson_id == lesson_id)
    )

    session.delete(lesson)
    session.commit()
    return {"ok": True}

@router.put("/{lesson_id}", response_model=LessonRead, summary="Modificar una lección")
def update_lesson(
    lesson_id: int,
    lesson_update: LessonUpdate,
    session: Session = Depends(get_session)
):
    """
    Actualiza una lección existente.

    - **lesson_id**: ID de la lección a modificar
    - **date_time**: nueva fecha y hora (opcional)
    - **instructor_id**: ID del instructor (opcional)
    - **stable_id**: ID de la hípica (opcional)
    - **client_ids**: lista de IDs de clientes asociados (opcional)
    - **horse_ids**: lista de IDs de caballos asociados (opcional)

    Devuelve la lección actualizada con clientes y caballos.
    """
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Actualizar campos básicos
    if lesson_update.date_time is not None:
        lesson.date_time = lesson_update.date_time
    if lesson_update.instructor_id is not None:
        lesson.instructor_id = lesson_update.instructor_id
    if lesson_update.stable_id is not None:
        lesson.stable_id = lesson_update.stable_id

    session.add(lesson)
    session.commit()

    # Actualizar relaciones N:N
    if lesson_update.client_ids is not None:
        # Borrar relaciones actuales
        session.exec(
            select(LessonClientLink).where(LessonClientLink.lesson_id == lesson.id)
        ).all()
        session.exec(
            delete(LessonClientLink).where(LessonClientLink.lesson_id == lesson.id)
        )
        # Añadir nuevas relaciones
        session.add_all([LessonClientLink(lesson_id=lesson.id, client_id=cid) for cid in lesson_update.client_ids])

    if lesson_update.horse_ids is not None:
        session.exec(
            delete(LessonHorseLink).where(LessonHorseLink.lesson_id == lesson.id)
        )
        session.add_all([LessonHorseLink(lesson_id=lesson.id, horse_id=hid) for hid in lesson_update.horse_ids])

    session.commit()

    # Traer relaciones con JOIN para optimizar
    client_rows = session.exec(
        select(Client)
        .join(LessonClientLink, Client.id == LessonClientLink.client_id)
        .where(LessonClientLink.lesson_id == lesson.id)
    ).all()

    horse_rows = session.exec(
        select(Horse)
        .join(LessonHorseLink, Horse.id == LessonHorseLink.horse_id)
        .where(LessonHorseLink.lesson_id == lesson.id)
    ).all()

    # Preparar respuesta
    clients = [ClientRead.model_validate(c) for c in client_rows]
    horses = [HorseRead.model_validate(h) for h in horse_rows]

    return LessonRead(
        id=lesson.id,
        date_time=lesson.date_time,
        instructor_id=lesson.instructor_id,
        stable_id=lesson.stable_id,
        clients=clients,
        horses=horses
    )
