"""
Endpoints CRUD para Track (pistas de equitación).

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.track import Track
from app.dependencies import require_role
from app.models import User
from app.schemas.track import TrackCreate, TrackRead, TrackUpdate
from app.core.i18n import t

router = APIRouter(prefix="/tracks", tags=["Tracks"])


def _track_to_read(track: Track) -> TrackRead:
    """Convierte un ORM Track en el schema TrackRead."""
    return TrackRead(
        id=track.id,
        name=track.name,
        stable_id=track.stable_id,
        is_active=track.is_active,
    )


@router.get("/", response_model=list[TrackRead])
def list_tracks(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Listar todas las pistas de la cuadra del usuario autenticado.

    app_admin ve las pistas de todas las cuadras.
    """
    query = select(Track)
    if current_user.role != "app_admin":
        query = query.where(Track.stable_id == current_user.stable_id)

    tracks = session.exec(query).all()
    return [_track_to_read(tr) for tr in tracks]


@router.post("/", response_model=TrackRead, status_code=201)
def create_track(
    track_in: TrackCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Crear una nueva pista.

    Solo accesible para stable_admin y app_admin.
    El stable_id se fuerza al de la cuadra del usuario autenticado.
    """
    if current_user.role != "app_admin":
        track_in.stable_id = current_user.stable_id

    if not track_in.stable_id:
        raise HTTPException(status_code=400, detail=t(request, "track.stable_required"))

    track = Track(
        name=track_in.name,
        stable_id=track_in.stable_id,
    )
    session.add(track)
    session.commit()
    session.refresh(track)
    return _track_to_read(track)


@router.get("/{track_id}", response_model=TrackRead)
def get_track(
    track_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """Obtener una pista por su ID."""
    track = session.get(Track, track_id)
    if not track:
        raise HTTPException(status_code=404, detail=t(request, "track.not_found"))

    if current_user.role != "app_admin" and track.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    return _track_to_read(track)


@router.put("/{track_id}", response_model=TrackRead)
def update_track(
    track_id: int,
    track_data: TrackUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Actualizar los datos de una pista.

    Solo accesible para stable_admin y app_admin.
    """
    track = session.get(Track, track_id)
    if not track:
        raise HTTPException(status_code=404, detail=t(request, "track.not_found"))

    if current_user.role != "app_admin" and track.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    update_data = track_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(track, field, value)

    session.add(track)
    session.commit()
    session.refresh(track)
    return _track_to_read(track)


@router.delete("/{track_id}")
def delete_track(
    track_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Eliminar una pista.

    Solo accesible para stable_admin y app_admin.
    """
    track = session.get(Track, track_id)
    if not track:
        raise HTTPException(status_code=404, detail=t(request, "track.not_found"))

    if current_user.role != "app_admin" and track.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    session.delete(track)
    session.commit()
    return {"ok": True}
