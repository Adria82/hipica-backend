from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime
from app.models.booking import BookingStatus


class BookingCreate(SQLModel):
    lesson_id: int
    horse_request: Optional[str] = None
    notes: Optional[str] = None


class BookingRead(SQLModel):
    id: int
    lesson_id: int
    lesson_datetime: datetime
    lesson_end_time: Optional[datetime] = None
    user_id: int
    user_name: str
    status: BookingStatus
    horse_request: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    cancelled_at: Optional[datetime] = None


class BookingStatusUpdate(SQLModel):
    status: BookingStatus


class BulkBookingCreate(SQLModel):
    lesson_ids: List[int]
    horse_request: Optional[str] = None
    notes: Optional[str] = None


class AffectedLessonItem(SQLModel):
    id: int
    date_time: datetime
    booking_count: int


class AffectedLessonsResponse(SQLModel):
    affected_lessons: List[AffectedLessonItem]
