from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.stable_config import StableConfig
from app.dependencies import require_role
from app.models import User
from app.schemas.stable_config import StableConfigRead, StableConfigUpdate

router = APIRouter(prefix="/stable-config", tags=["StableConfig"])


def _get_or_create_config(stable_id: int, session: Session) -> StableConfig:
    config = session.exec(select(StableConfig).where(StableConfig.stable_id == stable_id)).first()
    if not config:
        config = StableConfig(stable_id=stable_id)
        session.add(config)
        session.commit()
        session.refresh(config)
    return config


@router.get("", response_model=StableConfigRead)
def get_stable_config(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    stable_id = current_user.stable_id
    config = _get_or_create_config(stable_id, session)
    return config


@router.put("", response_model=StableConfigRead)
def update_stable_config(
    data: StableConfigUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    stable_id = current_user.stable_id
    config = _get_or_create_config(stable_id, session)

    if data.cancel_deadline_hours is not None:
        config.cancel_deadline_hours = data.cancel_deadline_hours
    if data.auto_attendance is not None:
        config.auto_attendance = data.auto_attendance

    session.add(config)
    session.commit()
    session.refresh(config)
    return config
