from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from sqlalchemy import func
from typing import List
from datetime import datetime

from app.db.session import get_session
from app.models.booking import Booking, BookingStatus
from app.models.lesson import Lesson
from app.models.stable_config import StableConfig
from app.dependencies import require_role, get_current_user
from app.models import User
from app.schemas.booking import (
    BookingCreate,
    BookingRead,
    BookingStatusUpdate,
    BulkBookingCreate,
    AffectedLessonsResponse,
    AffectedLessonItem,
)
from app.core.i18n import t

router = APIRouter(tags=["Bookings"])

CLIENT_ROLES = ["client"]
STAFF_ROLES = ["stable_admin", "app_admin", "monitor", "assistant"]
ALL_ROLES = CLIENT_ROLES + STAFF_ROLES


def _get_config(stable_id: int, session: Session) -> StableConfig:
    config = session.exec(select(StableConfig).where(StableConfig.stable_id == stable_id)).first()
    if not config:
        config = StableConfig(stable_id=stable_id)
        session.add(config)
        session.commit()
        session.refresh(config)
    return config


def _count_bookings(lesson_id: int, session: Session) -> int:
    return session.exec(
        select(func.count()).where(
            Booking.lesson_id == lesson_id,
            Booking.status == BookingStatus.RESERVADO,
        )
    ).one()


def _build_booking_read(booking: Booking, session: Session) -> BookingRead:
    lesson = session.get(Lesson, booking.lesson_id)
    user = session.get(User, booking.user_id)
    return BookingRead(
        id=booking.id,
        lesson_id=booking.lesson_id,
        lesson_datetime=lesson.date_time if lesson else datetime.utcnow(),
        lesson_end_time=lesson.end_time if lesson else None,
        user_id=booking.user_id,
        user_name=user.name if user else "—",
        status=booking.status,
        horse_request=booking.horse_request,
        notes=booking.notes,
        created_at=booking.created_at,
        cancelled_at=booking.cancelled_at,
    )


# ---------------------------------------------------------------------------
# Client routes
# ---------------------------------------------------------------------------

@router.get("/bookings/available", response_model=List[dict])
def list_available_lessons(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(ALL_ROLES)),
):
    now = datetime.utcnow()
    query = select(Lesson).where(
        Lesson.stable_id == current_user.stable_id,
        Lesson.is_published == True,
        Lesson.date_time > now,
    )
    lessons = session.exec(query).all()

    result = []
    for lesson in lessons:
        booked = _count_bookings(lesson.id, session)
        if lesson.max_students is not None and booked >= lesson.max_students:
            continue
        instructor = session.get(User, lesson.instructor_id)
        from app.models.track import Track
        track = session.get(Track, lesson.track_id) if lesson.track_id else None
        result.append({
            "id": lesson.id,
            "date_time": lesson.date_time.isoformat(),
            "end_time": lesson.end_time.isoformat() if lesson.end_time else None,
            "instructor_name": instructor.name if instructor else "—",
            "track_name": track.name if track else None,
            "max_students": lesson.max_students,
            "booked_count": booked,
            "available_slots": (lesson.max_students - booked) if lesson.max_students else None,
            "description": lesson.description,
        })
    return result


@router.post("/bookings", response_model=BookingRead, status_code=201)
def create_booking(
    data: BookingCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(CLIENT_ROLES)),
):
    lesson = session.get(Lesson, data.lesson_id)
    if not lesson or lesson.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "lesson.not_found"))
    if not lesson.is_published:
        raise HTTPException(status_code=400, detail=t(request, "booking.not_published"))
    if lesson.date_time <= datetime.utcnow():
        raise HTTPException(status_code=400, detail=t(request, "booking.lesson_started"))

    existing = session.exec(
        select(Booking).where(
            Booking.lesson_id == data.lesson_id,
            Booking.user_id == current_user.id,
            Booking.status == BookingStatus.RESERVADO,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=t(request, "booking.duplicate"))

    if lesson.max_students is not None:
        booked = _count_bookings(lesson.id, session)
        if booked >= lesson.max_students:
            raise HTTPException(status_code=409, detail=t(request, "booking.full"))

    booking = Booking(
        stable_id=current_user.stable_id,
        lesson_id=data.lesson_id,
        user_id=current_user.id,
        horse_request=data.horse_request,
        notes=data.notes,
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return _build_booking_read(booking, session)


@router.post("/bookings/bulk")
def bulk_create_bookings(
    data: BulkBookingCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(CLIENT_ROLES)),
):
    results = []
    for lesson_id in data.lesson_ids:
        try:
            lesson = session.get(Lesson, lesson_id)
            if not lesson or lesson.stable_id != current_user.stable_id:
                results.append({"lesson_id": lesson_id, "success": False, "error": "not_found"})
                continue
            if not lesson.is_published:
                results.append({"lesson_id": lesson_id, "success": False, "error": "not_published"})
                continue
            if lesson.date_time <= datetime.utcnow():
                results.append({"lesson_id": lesson_id, "success": False, "error": "lesson_started"})
                continue

            existing = session.exec(
                select(Booking).where(
                    Booking.lesson_id == lesson_id,
                    Booking.user_id == current_user.id,
                    Booking.status == BookingStatus.RESERVADO,
                )
            ).first()
            if existing:
                results.append({"lesson_id": lesson_id, "success": False, "error": "duplicate"})
                continue

            if lesson.max_students is not None:
                booked = _count_bookings(lesson.id, session)
                if booked >= lesson.max_students:
                    results.append({"lesson_id": lesson_id, "success": False, "error": "full"})
                    continue

            booking = Booking(
                stable_id=current_user.stable_id,
                lesson_id=lesson_id,
                user_id=current_user.id,
                horse_request=data.horse_request,
                notes=data.notes,
            )
            session.add(booking)
            session.flush()
            results.append({"lesson_id": lesson_id, "success": True, "booking_id": booking.id})
        except Exception as e:
            results.append({"lesson_id": lesson_id, "success": False, "error": str(e)})

    session.commit()
    return results


@router.post("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    booking = session.get(Booking, booking_id)
    if not booking or booking.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "booking.not_found"))

    is_staff = current_user.role in STAFF_ROLES
    if not is_staff and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    if booking.status != BookingStatus.RESERVADO:
        raise HTTPException(status_code=400, detail=t(request, "booking.not_cancellable"))

    if not is_staff:
        lesson = session.get(Lesson, booking.lesson_id)
        config = _get_config(current_user.stable_id, session)
        from datetime import timedelta
        if lesson and (lesson.date_time - datetime.utcnow()).total_seconds() < config.cancel_deadline_hours * 3600:
            raise HTTPException(status_code=400, detail=t(request, "booking.cancel_deadline_passed"))

    booking.status = BookingStatus.CANCELADO
    booking.cancelled_at = datetime.utcnow()
    booking.updated_at = datetime.utcnow()
    session.add(booking)
    session.commit()
    return {"ok": True}


@router.get("/bookings/mine", response_model=List[BookingRead])
def my_bookings(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(CLIENT_ROLES)),
):
    bookings = session.exec(
        select(Booking)
        .where(
            Booking.user_id == current_user.id,
            Booking.stable_id == current_user.stable_id,
        )
        .join(Lesson, Booking.lesson_id == Lesson.id)
        .order_by(Lesson.date_time.desc())
    ).all()
    return [_build_booking_read(b, session) for b in bookings]


# ---------------------------------------------------------------------------
# Staff routes
# ---------------------------------------------------------------------------

@router.get("/lessons/{lesson_id}/bookings", response_model=List[BookingRead])
def list_lesson_bookings(
    lesson_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(STAFF_ROLES)),
):
    lesson = session.get(Lesson, lesson_id)
    if not lesson or lesson.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "lesson.not_found"))

    bookings = session.exec(
        select(Booking).where(Booking.lesson_id == lesson_id)
    ).all()
    return [_build_booking_read(b, session) for b in bookings]


@router.put("/bookings/{booking_id}/status", response_model=BookingRead)
def update_booking_status(
    booking_id: int,
    data: BookingStatusUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(STAFF_ROLES)),
):
    booking = session.get(Booking, booking_id)
    if not booking or booking.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "booking.not_found"))

    booking.status = data.status
    booking.updated_at = datetime.utcnow()
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return _build_booking_read(booking, session)


@router.post("/admin/attendance/process")
def process_attendance(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    now = datetime.utcnow()

    query = (
        select(Booking)
        .join(Lesson, Booking.lesson_id == Lesson.id)
        .join(StableConfig, StableConfig.stable_id == Booking.stable_id)
        .where(
            Booking.status == BookingStatus.RESERVADO,
            Lesson.end_time < now,
        )
    )

    if current_user.role != "app_admin":
        query = query.where(
            Booking.stable_id == current_user.stable_id,
            StableConfig.auto_attendance == True,
        )
    else:
        query = query.where(StableConfig.auto_attendance == True)

    bookings = session.exec(query).all()
    count = 0
    for booking in bookings:
        booking.status = BookingStatus.ASISTIO
        booking.updated_at = now
        session.add(booking)
        count += 1

    session.commit()
    return {"processed": count}
