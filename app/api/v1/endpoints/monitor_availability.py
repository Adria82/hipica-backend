from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import List

from app.db.session import get_session
from app.models.monitor_availability import MonitorAvailability
from app.dependencies import require_role
from app.models import User
from app.schemas.monitor_availability import (
    MonitorAvailabilityCreate,
    MonitorAvailabilityRead,
    MonitorAvailabilityUpdate,
)
from app.core.i18n import t

router = APIRouter(prefix="/monitor-availability", tags=["MonitorAvailability"])

STAFF_ROLES = ["monitor", "assistant", "stable_admin", "app_admin"]


def _build_read(avail: MonitorAvailability, session: Session) -> MonitorAvailabilityRead:
    user = session.get(User, avail.user_id)
    user_name = user.name if user else "—"
    return MonitorAvailabilityRead(
        id=avail.id,
        stable_id=avail.stable_id,
        user_id=avail.user_id,
        user_name=user_name,
        is_recurring=avail.is_recurring,
        day_of_week=avail.day_of_week,
        specific_date=avail.specific_date,
        start_time=avail.start_time,
        end_time=avail.end_time,
        is_active=avail.is_active,
    )


@router.get("", response_model=List[MonitorAvailabilityRead])
def list_monitor_availability(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(STAFF_ROLES)),
):
    query = select(MonitorAvailability).where(MonitorAvailability.stable_id == current_user.stable_id)
    if current_user.role in ("monitor", "assistant"):
        query = query.where(MonitorAvailability.user_id == current_user.id)
    return [_build_read(a, session) for a in session.exec(query).all()]


@router.post("", response_model=MonitorAvailabilityRead, status_code=201)
def create_monitor_availability(
    data: MonitorAvailabilityCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(STAFF_ROLES)),
):
    if current_user.role in ("monitor", "assistant"):
        data.user_id = current_user.id

    target_user = session.get(User, data.user_id)
    if not target_user or target_user.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "user.not_found"))

    avail = MonitorAvailability(
        stable_id=current_user.stable_id,
        user_id=data.user_id,
        is_recurring=data.is_recurring,
        day_of_week=data.day_of_week,
        specific_date=data.specific_date,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    session.add(avail)
    session.commit()
    session.refresh(avail)
    return _build_read(avail, session)


@router.put("/{avail_id}", response_model=MonitorAvailabilityRead)
def update_monitor_availability(
    avail_id: int,
    data: MonitorAvailabilityUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(STAFF_ROLES)),
):
    avail = session.get(MonitorAvailability, avail_id)
    if not avail or avail.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "user.not_found"))
    if current_user.role in ("monitor", "assistant") and avail.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    for field in ("is_recurring", "day_of_week", "specific_date", "start_time", "end_time", "is_active"):
        val = getattr(data, field, None)
        if val is not None:
            setattr(avail, field, val)

    session.add(avail)
    session.commit()
    session.refresh(avail)
    return _build_read(avail, session)


@router.delete("/{avail_id}")
def delete_monitor_availability(
    avail_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(STAFF_ROLES)),
):
    avail = session.get(MonitorAvailability, avail_id)
    if not avail or avail.stable_id != current_user.stable_id:
        raise HTTPException(status_code=404, detail=t(request, "user.not_found"))
    if current_user.role in ("monitor", "assistant") and avail.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    session.delete(avail)
    session.commit()
    return {"ok": True}
