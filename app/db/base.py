"""
Módulo para inicializar todas las tablas de la base de datos.

Importa todos los modelos y ejecuta create_all().

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel
from app.models.stable import Stable
from app.models.user import User
from app.models.horse import Horse
from app.models.client import Client
from app.models.lesson import Lesson, LessonHorseLink, LessonClientLink
from app.db.session import engine

def init_db():
    """
    Crea todas las tablas definidas en los modelos si no existen.
    """
    SQLModel.metadata.create_all(engine)
    print("Tablas creadas correctamente")