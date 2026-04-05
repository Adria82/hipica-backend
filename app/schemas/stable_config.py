from sqlmodel import SQLModel
from typing import Optional


class StableConfigRead(SQLModel):
    stable_id: int
    cancel_deadline_hours: int
    auto_attendance: bool


class StableConfigUpdate(SQLModel):
    cancel_deadline_hours: Optional[int] = None
    auto_attendance: Optional[bool] = None
