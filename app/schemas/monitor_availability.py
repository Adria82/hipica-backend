from sqlmodel import SQLModel
from typing import Optional
from datetime import date, time


class MonitorAvailabilityCreate(SQLModel):
    user_id: int
    is_recurring: bool
    day_of_week: Optional[int] = None
    specific_date: Optional[date] = None
    start_time: time
    end_time: time


class MonitorAvailabilityRead(SQLModel):
    id: int
    stable_id: int
    user_id: int
    user_name: str
    is_recurring: bool
    day_of_week: Optional[int] = None
    specific_date: Optional[date] = None
    start_time: time
    end_time: time
    is_active: bool


class MonitorAvailabilityUpdate(SQLModel):
    is_recurring: Optional[bool] = None
    day_of_week: Optional[int] = None
    specific_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: Optional[bool] = None
