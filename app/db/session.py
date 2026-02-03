"""
Módulo para inicializar la sesión de base de datos con SQLAlchemy / SQLModel.

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import create_engine, Session
from app.core.config import DATABASE_URL

# -------------------------------------------------------------------------
# Motor de conexión
# -------------------------------------------------------------------------
engine = create_engine(DATABASE_URL, echo=True)  # echo=True muestra las queries en consola

# -------------------------------------------------------------------------
# Función para obtener sesión
# -------------------------------------------------------------------------
def get_session():
    """
    Crea y devuelve una sesión de base de datos.

    Uso recomendado:
        with get_session() as session:
            # Operaciones con la DB
    """
    with Session(engine) as session:
        yield session