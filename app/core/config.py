"""
Módulo de configuración de la aplicación de Gestión de Hípica.

Este módulo centraliza todas las variables de entorno y la construcción
de la URL de conexión a la base de datos.

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

import os

# -------------------------------------------------------------------------
# Variables de entorno de la base de datos PostgreSQL
# -------------------------------------------------------------------------

POSTGRES_USER = os.getenv("POSTGRES_USER", "hipica")
"""
Usuario de la base de datos PostgreSQL.
Por defecto 'hipica' si no está definido en el entorno.
"""

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hipica")
"""
Contraseña del usuario de PostgreSQL.
Por defecto 'hipica' si no está definido en el entorno.
"""

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
"""
Host donde se encuentra la base de datos.
Por defecto 'db' (nombre del servicio en Docker Compose).
"""

POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
"""
Puerto de conexión a PostgreSQL.
Por defecto '5432'.
"""

POSTGRES_DB = os.getenv("POSTGRES_DB", "hipica")
"""
Nombre de la base de datos.
Por defecto 'hipica'.
"""

# -------------------------------------------------------------------------
# URL de conexi?n completa
# -------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")
"""
URL de conexi?n completa para SQLAlchemy / FastAPI.

Si existe la variable de entorno DATABASE_URL se usa directamente.
"""

if not DATABASE_URL:
    DATABASE_URL = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    """
    URL de conexi?n completa para SQLAlchemy / FastAPI.

    Ejemplo resultante:
    postgresql://hipica:hipica@db:5432/hipica
    """
