from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, time


class MonitorAvailability(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stable_id: int = Field(foreign_key="stable.id", index=True)
    user_id: int = Field(foreign_key="user.id")
    is_recurring: bool
    day_of_week: Optional[int] = None
    specific_date: Optional[date] = None
    start_time: time
    end_time: time
    is_active: bool = Field(default=True)
