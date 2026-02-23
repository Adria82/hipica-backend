"""
Definición de funcionalidades (features) disponibles en el sistema.

Representa los módulos que una hípica puede tener activados.
NO es un sistema de permisos, sino de licenciamiento funcional.

Autor: Adrià Bofill
Proyecto: Gestión de Hípica
"""

from enum import Enum


class FeatureCode(str, Enum):
    """
    Catálogo de funcionalidades disponibles.

    Se usa como contrato entre backend y frontend.
    El frontend mostrará u ocultará módulos según esta lista.
    """

    HORSES = "HORSES"
    CLIENTS = "CLIENTS"
    LESSONS = "LESSONS"
    BOOKINGS = "BOOKINGS"
    BILLING = "BILLING"
    REPORTING = "REPORTING"