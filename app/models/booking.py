from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint
from typing import Optional
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    RESERVADO = "RESERVADO"
    CANCELADO = "CANCELADO"
    ASISTIO = "ASISTIO"
    NO_ASISTIO = "NO_ASISTIO"


class Booking(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("lesson_id", "user_id", name="uq_booking_lesson_user"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    stable_id: int = Field(foreign_key="stable.id", index=True)
    lesson_id: int = Field(foreign_key="lesson.id")
    user_id: int = Field(foreign_key="user.id")
    status: BookingStatus = Field(default=BookingStatus.RESERVADO)
    horse_request: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
