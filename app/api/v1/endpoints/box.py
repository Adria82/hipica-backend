"""
Endpoints CRUD para Box (boxes de una hípica).

Autor: Adrià Bofill
Fecha: 02/04/2026
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.box import Box
from app.dependencies import require_role
from app.models import User
from app.schemas.box import BoxCreate, BoxRead, BoxUpdate
from app.core.i18n import t

router = APIRouter(prefix="/boxes", tags=["Boxes"])


def _box_to_read(box: Box) -> BoxRead:
    """Convierte un ORM Box en el schema BoxRead."""
    return BoxRead(
        id=box.id,
        name=box.name,
        capacity=box.capacity,
        stable_id=box.stable_id,
        is_active=box.is_active,
        horses_count=len(box.horses),
    )


@router.get("/", response_model=list[BoxRead])
def get_boxes(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Listar todos los boxes de la cuadra del usuario autenticado.

    app_admin ve los boxes de todas las cuadras.
    """
    query = select(Box)
    if current_user.role != "app_admin":
        query = query.where(Box.stable_id == current_user.stable_id)

    boxes = session.exec(query).all()
    return [_box_to_read(b) for b in boxes]


@router.post("/", response_model=BoxRead, status_code=201)
def create_box(
    box_in: BoxCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Crear un nuevo box.

    Solo accesible para stable_admin y app_admin.
    El stable_id se fuerza al de la cuadra del usuario autenticado
    (app_admin puede indicar stable_id explícitamente).
    """
    if current_user.role != "app_admin":
        box_in.stable_id = current_user.stable_id

    box = Box(**box_in.model_dump())
    session.add(box)
    session.commit()
    session.refresh(box)
    return _box_to_read(box)


@router.get("/{box_id}", response_model=BoxRead)
def get_box(
    box_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["monitor", "stable_admin", "app_admin"])),
):
    """
    Obtener un box por su ID.

    Devuelve 403 si el box pertenece a otra cuadra (cross-tenant).
    """
    box = session.get(Box, box_id)
    if not box:
        raise HTTPException(status_code=404, detail=t(request, "box.not_found"))

    if current_user.role != "app_admin" and box.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    return _box_to_read(box)


@router.put("/{box_id}", response_model=BoxRead)
def update_box(
    box_id: int,
    box_data: BoxUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Actualizar los datos de un box.

    Solo accesible para stable_admin y app_admin.
    """
    box = session.get(Box, box_id)
    if not box:
        raise HTTPException(status_code=404, detail=t(request, "box.not_found"))

    if current_user.role != "app_admin" and box.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    update_data = box_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(box, field, value)

    session.add(box)
    session.commit()
    session.refresh(box)
    return _box_to_read(box)


@router.delete("/{box_id}")
def delete_box(
    box_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["stable_admin", "app_admin"])),
):
    """
    Eliminar un box.

    Devuelve 409 si el box tiene caballos asignados.
    Solo accesible para stable_admin y app_admin.
    """
    box = session.get(Box, box_id)
    if not box:
        raise HTTPException(status_code=404, detail=t(request, "box.not_found"))

    if current_user.role != "app_admin" and box.stable_id != current_user.stable_id:
        raise HTTPException(status_code=403, detail=t(request, "auth.permission_denied"))

    if box.horses:
        raise HTTPException(status_code=409, detail=t(request, "box.has_horses"))

    session.delete(box)
    session.commit()
    return {"ok": True}
