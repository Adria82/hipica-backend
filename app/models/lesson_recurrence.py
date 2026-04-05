from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date, time


class LessonRecurrence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stable_id: int = Field(foreign_key="stable.id", index=True)
    instructor_id: int = Field(foreign_key="user.id")
    helper_id: Optional[int] = Field(default=None, foreign_key="user.id")
    track_id: Optional[int] = Field(default=None, foreign_key="track.id")
    day_of_week: int  # 0=lunes…6=domingo
    start_time: time
    end_time: Optional[time] = None
    from_date: date
    to_date: date
    max_students: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
