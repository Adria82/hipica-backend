"""
Esquemas para los perfiles extendidos de usuario: ClientProfile y MonitorProfile.

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from typing import Optional
from sqlmodel import SQLModel


class ClientProfileRead(SQLModel):
    """Perfil extendido de un cliente de la hípica (lectura).

    Contiene los campos adicionales que complementan el registro base
    de usuario para los alumnos de la hípica.

    Attributes:
        apellidos: Apellidos del cliente.
        direccion: Dirección postal completa.
        iban: Número de cuenta bancaria para domiciliación de pagos.
        notes: Observaciones libres (alergias, preferencias, etc.).
        level_id: FK al nivel de equitación del alumno (tabla Level).
            Puede ser None si el cliente aún no tiene nivel asignado.
    """
    apellidos: Optional[str] = None
    direccion: Optional[str] = None
    iban: Optional[str] = None
    notes: Optional[str] = None
    level_id: Optional[int] = None


class ClientProfileUpdate(SQLModel):
    apellidos: Optional[str] = None
    direccion: Optional[str] = None
    iban: Optional[str] = None
    notes: Optional[str] = None


class MonitorProfileRead(SQLModel):
    especialidad: Optional[str] = None
    disponibilidad: Optional[str] = None
    certificados: Optional[str] = None
    experiencia: Optional[str] = None
    telefono: Optional[str] = None
    iban: Optional[str] = None
    notas: Optional[str] = None
    tarifa_hora: Optional[float] = None


class MonitorProfileUpdate(SQLModel):
    especialidad: Optional[str] = None
    disponibilidad: Optional[str] = None
    certificados: Optional[str] = None
    experiencia: Optional[str] = None
    telefono: Optional[str] = None
    iban: Optional[str] = None
    notas: Optional[str] = None
    tarifa_hora: Optional[float] = None


class UserProfileUpdate(SQLModel):
    """Payload unificado para PUT /users/{id}/profile. El endpoint ignora los campos
    que no correspondan al rol del usuario."""
    # client fields
    apellidos: Optional[str] = None
    direccion: Optional[str] = None
    notes: Optional[str] = None
    level_id: Optional[int] = None
    # monitor/assistant fields
    especialidad: Optional[str] = None
    disponibilidad: Optional[str] = None
    certificados: Optional[str] = None
    experiencia: Optional[str] = None
    telefono: Optional[str] = None
    notas: Optional[str] = None
    tarifa_hora: Optional[float] = None
    # shared
    iban: Optional[str] = None
