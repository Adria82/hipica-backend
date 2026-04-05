from sqlmodel import SQLModel, Field


class StableConfig(SQLModel, table=True):
    stable_id: int = Field(foreign_key="stable.id", primary_key=True)
    cancel_deadline_hours: int = Field(default=24)
    auto_attendance: bool = Field(default=False)
