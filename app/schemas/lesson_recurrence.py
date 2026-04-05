from sqlmodel import SQLModel
from typing import Optional, List
from datetime import date, time


class LessonRecurrenceCreate(SQLModel):
    instructor_id: int
    helper_id: Optional[int] = None
    track_id: Optional[int] = None
    day_of_week: int
    start_time: time
    end_time: Optional[time] = None
    from_date: date
    to_date: date
    max_students: Optional[int] = None
    description: Optional[str] = None


class LessonRecurrenceRead(SQLModel):
    id: int
    stable_id: int
    instructor_id: int
    instructor_email: str
    helper_id: Optional[int] = None
    helper_email: Optional[str] = None
    track_id: Optional[int] = None
    track_name: Optional[str] = None
    day_of_week: int
    start_time: time
    end_time: Optional[time] = None
    from_date: date
    to_date: date
    max_students: Optional[int] = None
    description: Optional[str] = None
    lesson_ids: List[int] = []


class LessonRecurrenceUpdate(SQLModel):
    instructor_id: Optional[int] = None
    helper_id: Optional[int] = None
    track_id: Optional[int] = None
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    max_students: Optional[int] = None
    description: Optional[str] = None
    propagate: bool = False
    lesson_id: Optional[int] = None  # requerido si propagate=False para desvincular una sola clase
