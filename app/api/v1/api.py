"""
Router principal de la API v1.

Autor:  Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, level, stable, horse, lesson, user, me, box, track, reports,
    stable_config, monitor_availability, lesson_recurrence, bookings,
)

api_router = APIRouter()

api_router.include_router(stable.router)
api_router.include_router(box.router)
api_router.include_router(horse.router)
api_router.include_router(me.router)
api_router.include_router(lesson.router)
api_router.include_router(track.router)
api_router.include_router(reports.router)
api_router.include_router(user.router)
api_router.include_router(level.router)
api_router.include_router(auth.router)
api_router.include_router(stable_config.router)
api_router.include_router(monitor_availability.router)
api_router.include_router(lesson_recurrence.router)
api_router.include_router(bookings.router)
