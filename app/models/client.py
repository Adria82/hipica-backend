"""
Modelo de la entidad Client (cliente/alumno).

Representa un cliente que puede reservar lecciones y pertenecer
a una hípica.

Autor: Adrià Bofill
Fecha:  31/01/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from app.models.links import LessonClientLink

class Client(SQLModel, table=True):
    """
    Clase que representa un cliente.

    Attributes:
        id (int): Identificador único del cliente.
        name (str): Nombre completo del cliente.
        phone (Optional[str]): Número de teléfono.
        email (str): Correo electrónico.
        stable_id (int): Id de la hípica a la que pertenece.
        is_active (bool): Si el cliente está disponible.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    phone: Optional[str]
    email: Optional[str] = Field(default=None)
    stable_id: int = Field(foreign_key="stable.id")
    is_active: bool = Field(default=True)

    # Relación N:N con Lesson usando string -> evita circular import
    lessons: List["Lesson"] = Relationship(
        back_populates="clients",
        link_model=LessonClientLink
    )
Client.model_rebuild()