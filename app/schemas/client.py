"""
Esquemas de la entidad Client (cliente).

Define los modelos de entrada y salida utilizados por la API
para la gestión de clientes de la hípica.

Autor: Adrià Bofill
Fecha: 01/02/2026
Proyecto: Gestión de Hípica
"""

from sqlmodel import SQLModel
from typing import Optional


class ClientBase(SQLModel):
    """
    Atributos base de un cliente.
    """
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    stable_id: int


class ClientCreate(ClientBase):
    """
    Esquema para crear un nuevo cliente.
    """
    pass


class ClientUpdate(SQLModel):
    """
    Esquema para actualizar parcialmente un cliente.
    """
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    stable_id: Optional[int] = None


class ClientRead(SQLModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    stable_id: int
    stable_name: Optional[str] = None