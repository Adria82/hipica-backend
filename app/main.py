"""
Módulo principal de la API de Gestión de la Hípica.

Este módulo es el punto de entrada de la aplicación FastAPI.
Define la creación de la aplicación, la conexión a la base de datos
y algunos endpoints básicos de comprobación de estado.

Autor:  Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""
import os

from fastapi import FastAPI, Request
from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL
from app.db.base import init_db
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.i18n import t




# Creación del motor de conexión de SQLAlchemy.
# El engine se reutilizará en toda la aplicación.
engine = create_engine(DATABASE_URL)


# -------------------------------------------------------------------------
# Creación de la aplicación FastAPI
# -------------------------------------------------------------------------

app = FastAPI(
    title="Gestión Hípica API",
    description="API para la gestión de una hípica (caballos, clientes, clases, etc.)",
    version="1.0.0"
)

# ---------------------------------------------------------
# CORS (permite que el frontend Vue se comunique con FastAPI)
# ---------------------------------------------------------
origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos los endpoints versión 1
app.include_router(api_router, prefix="/api/v1")


# -------------------------------------------------------------------------
# Inicialización de la base de datos
# -------------------------------------------------------------------------
init_db()


# -------------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------------

@app.get("/")
def read_root(request: Request):
    """
    Endpoint raíz de la API.

    Se utiliza como comprobación básica para verificar que
    la aplicación está levantada y respondiendo correctamente.

    :return: Diccionario con el estado de la API.
    """
    return {
        "status": "ok",
        "message": t(request, "api.running"),
    }


@app.get("/health/db")
def db_health():
    """
    Endpoint de comprobación del estado de la base de datos.

    Realiza una consulta simple (`SELECT 1`) contra la base de datos
    para verificar que la conexión con PostgreSQL es correcta.

    Este endpoint es muy útil para:
    - Health checks
    - Monitorización
    - Diagnóstico de problemas de conexión

    :return: Diccionario indicando el estado de la base de datos.
    """
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        return {
            "db": "ok",
            "result": result.scalar()
        }
