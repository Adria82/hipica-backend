"""
Esquemas de la entidad User (usuario).

Define los modelos de entrada y salida utilizados por la API
para la gestión de usuarios de la hípica.

Un usuario puede tener rol:
- admin
- monitor
- client

Autor: Adrià Bofill
Fecha: 01/02/2026
Proyecto: Gestión de Hípica
"""

from typing import Optional
from sqlmodel import SQLModel


class UserBase(SQLModel):
    """
    Atributos base de un usuario (sin credenciales).
    """
    name: str
    apellidos: Optional[str] = None
    email: str
    dni: Optional[str] = None
    role: str = "client"
    phone: Optional[str] = None
    stable_id: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    """
    Esquema para crear un nuevo usuario.
    """
    password: str


class UserUpdate(SQLModel):
    """
    Esquema para actualizar parcialmente un usuario.
    """
    name: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[str] = None
    dni: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    stable_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """
    Esquema de lectura de un usuario.
    """
    id: int


class PasswordChange(SQLModel):
    """Payload para cambiar la contraseña de un usuario."""
    password: str
