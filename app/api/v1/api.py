"""
Router principal de la API v1.

Autor:  Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from fastapi import APIRouter
from app.api.v1.endpoints import stable, horse, client, lesson, user

api_router = APIRouter()

api_router.include_router(stable.router, prefix="/stables", tags=["Stables"])
api_router.include_router(horse.router, prefix="/horses", tags=["Horses"])
api_router.include_router(client.router, prefix="/clients", tags=["Clients"])
api_router.include_router(lesson.router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(user.router, prefix="/users", tags=["Users"])