"""
Módulo base para modelos SQLModel.

Define la clase Base para que todas las entidades hereden
de ella y compartan configuración común.

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel

class Base(SQLModel):
    """
    Clase base para todos los modelos SQLModel.

    Se usa para aplicar configuraciones comunes y mantener
    consistencia en los modelos de la base de datos.
    """
    pass