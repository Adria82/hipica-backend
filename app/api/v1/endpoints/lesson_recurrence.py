from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timedelta

from app.db.session import get_session
from app.models.lesson_recurrence import LessonRecurrence
from app.models.lesson import Lesson
from app.models.booking import Booking, BookingStatus
from app.models.track import Track
from app.dependencies import require_role
from app.models import User
from app.schemas.lesson_recurrence import (
    LessonRecurrenceCreate,
    LessonRecurrenceRead,
    LessonRecurrenceUpdate,
)
from app.schemas.booking import AffectedLessonsResponse, AffectedLessonItem
from app.core.i18n import t

router = APIRouter(prefix="/lessons/recurrence", tags=["LessonRecurrence"])

MANAGE_ROLES = ["stable_admin", "app_admin"]


def _build_read(rec: LessonRecurrence, session: Session) -> LessonRecurrenceRead:
    instructor = session.get(User, rec.instructor_id)
    helper = session.get(User, rec.helper_id) if rec.helper_id else None
    track = session.get(Track, rec.track_id) if rec.track_id else None

    lessons = session.exec(
        select(Lesson).where(
            Lesson.recurrence_id == rec.id,
            Lesson.date_time >= datetime.utcnow(),
        )
    ).all()

    return LessonRecurrenceRead(
        id=rec.id,
        stable_id=rec.stable_id,
        instructor_id=rec.instructor_id,
        instructor_email=instructor.email if instructor else "—",
        helper_id=rec.helper_id,
        helper_email=helper.email if helper else None,
        track_id=rec.track_id,
        track_name=track.name if track else None,
        day_of_week=rec.day_of_week,
        start_time=rec.start_time,
        end_time=rec.end_time,
        from_date=rec.from_date,
        to_date=rec.to_date,
        max_students=rec.max_students,
        description=rec.description,
        lesson_ids=[lesson.id for lesson in lessons],
    )


def _generate_lessons(rec: LessonRecurrence, session: Session) -> List[int]:
    lesson_ids = []
    current = rec.from_date
    while current <= rec.to_date:
        if current.weekday() == rec.day_of_week:
            dt = datetime.combine(current, rec.start_time)
            end_dt = datetime.combine(current, rec.end_time) if rec.end_time else None
            lesson = Lesson(
                date_time=dt,
                end_time=end_dt,
                instructor_id=rec.instructor_id,
                helper_id=rec.helper_id,
                track_id=rec.track_id,
                description=rec.description,
                stable_id=rec.stable_id,
                max_students=rec.max_students,
                is_published=True,
                recurrence_id=rec.id,
            )
            session.add(lesson)
            session.flush()
            lesson_ids.append(lesson.id)
        current += timedelta(days=1)
    session.commit()
    return lesson_ids


@router.post("", response_model=LessonRecurrenceRead, status_code=201)
def create_lesson_recurrence(
    data: LessonRecurrenceCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(MANAGE_ROLES)),
):
    rec = LessonRecurrence(
        stable_id=current_user.stable_id,
        instructor_id=data.instructor_id,
        helper_id=data.helper_id,
        track_id=data.track_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        from_date=data.from_date,
        to_date=data.to_date,
        max_students=data.max_students,
        description=data.description,
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)
    _generate_lessons(rec, session)
    return _build_read(rec, session)


@router.get("/{rec_id}", response_model=LessonRecurrenceRead)
def get_lesson_recurrence(
    rec_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(MANAGE_ROLES)),
):
    rec = session.get(LessonRecurrence, rec_id)
    if not rec or rec.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "lesson.not_found"))
    return _build_read(rec, session)


@router.put("/{rec_id}", response_model=LessonRecurrenceRead)
def update_lesson_recurrence(
    rec_id: int,
    data: LessonRecurrenceUpdate,
    request: Request,
    force: bool = Query(default=False),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(MANAGE_ROLES)),
):
    rec = session.get(LessonRecurrence, rec_id)
    if not rec or rec.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "lesson.not_found"))

    if not data.propagate:
        # Editar solo la clase indicada y desvincularla de la serie
        if not data.lesson_id:
            raise HTTPException(status_code=400, detail="lesson_id required when propagate=False")
        lesson = session.get(Lesson, data.lesson_id)
        if not lesson or lesson.recurrence_id != rec_id:
            raise HTTPException(status_code=404, detail=t(request, "lesson.not_found"))
        lesson.recurrence_id = None
        if data.instructor_id is not None:
            lesson.instructor_id = data.instructor_id
        if data.start_time is not None:
            lesson.date_time = datetime.combine(lesson.date_time.date(), data.start_time)
        if data.end_time is not None and lesson.end_time:
            lesson.end_time = datetime.combine(lesson.end_time.date(), data.end_time)
        if data.max_students is not None:
            lesson.max_students = data.max_students
        session.add(lesson)
        session.commit()
        return _build_read(rec, session)

    # propagate=True: afecta clases futuras
    now = datetime.utcnow()
    future_lessons = session.exec(
        select(Lesson).where(
            Lesson.recurrence_id == rec_id,
            Lesson.date_time > now,
        )
    ).all()

    future_lesson_ids = [l.id for l in future_lessons]
    affected_bookings = []
    if future_lesson_ids:
        affected_bookings = session.exec(
            select(Booking).where(
                Booking.lesson_id.in_(future_lesson_ids),
                Booking.status == BookingStatus.RESERVADO,
            )
        ).all()

    if affected_bookings and not force:
        from collections import Counter
        counts = Counter(b.lesson_id for b in affected_bookings)
        affected_list = [
            AffectedLessonItem(id=l.id, date_time=l.date_time, booking_count=counts.get(l.id, 0))
            for l in future_lessons
            if l.id in counts
        ]
        raise HTTPException(
            status_code=409,
            detail=AffectedLessonsResponse(affected_lessons=affected_list).model_dump(),
        )

    # Aplicar cambios al recurrence y a las clases futuras
    for field in ("instructor_id", "helper_id", "track_id", "day_of_week", "max_students", "description"):
        val = getattr(data, field, None)
        if val is not None:
            setattr(rec, field, val)

    session.add(rec)

    for lesson in future_lessons:
        if data.instructor_id is not None:
            lesson.instructor_id = data.instructor_id
        if data.helper_id is not None:
            lesson.helper_id = data.helper_id
        if data.track_id is not None:
            lesson.track_id = data.track_id
        if data.max_students is not None:
            lesson.max_students = data.max_students
        if data.start_time is not None:
            lesson.date_time = datetime.combine(lesson.date_time.date(), data.start_time)
        if data.end_time is not None and lesson.end_time:
            lesson.end_time = datetime.combine(lesson.end_time.date(), data.end_time)
        session.add(lesson)

    session.commit()
    return _build_read(rec, session)


@router.delete("/{rec_id}")
def delete_lesson_recurrence(
    rec_id: int,
    request: Request,
    force: bool = Query(default=False),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(MANAGE_ROLES)),
):
    rec = session.get(LessonRecurrence, rec_id)
    if not rec or rec.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "lesson.not_found"))

    now = datetime.utcnow()
    future_lessons = session.exec(
        select(Lesson).where(
            Lesson.recurrence_id == rec_id,
            Lesson.date_time > now,
        )
    ).all()
    future_lesson_ids = [l.id for l in future_lessons]

    lessons_with_bookings = []
    if future_lesson_ids:
        booked = session.exec(
            select(Booking.lesson_id).where(
                Booking.lesson_id.in_(future_lesson_ids),
                Booking.status == BookingStatus.RESERVADO,
            )
        ).all()
        lessons_with_bookings = list(set(booked))

    if lessons_with_bookings and not force:
        affected_list = [
            AffectedLessonItem(id=l.id, date_time=l.date_time, booking_count=0)
            for l in future_lessons
            if l.id in lessons_with_bookings
        ]
        raise HTTPException(
            status_code=409,
            detail=AffectedLessonsResponse(affected_lessons=affected_list).model_dump(),
        )

    for lesson in future_lessons:
        lesson.recurrence_id = None
        session.add(lesson)

    session.commit()
    return {"ok": True, "cancelled_lessons": len(future_lessons)}
