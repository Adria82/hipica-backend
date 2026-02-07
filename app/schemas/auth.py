"""
Esquemas de autenticación y autorización.

Define los modelos de entrada y salida utilizados por los endpoints
de autenticación (login y refresh de tokens) de la API.

Incluye:
- TokenResponse: respuesta estándar con access token y refresh token.
- RefreshRequest: modelo de entrada para la renovación del access token.

Autor: Adrià Bofill
Fecha: 04/02/2026
Proyecto: Gestión de Hípica
"""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """
    Respuesta estándar de autenticación.

    Se devuelve tras un login correcto o una renovación de sesión.

    Attributes:
        access_token (str): JWT de acceso, usado para autenticar
            las peticiones protegidas de la API.
        refresh_token (str): JWT de refresco, usado para obtener
            un nuevo access token cuando el actual ha expirado.
        token_type (str): Tipo de token. Por defecto "bearer".
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """
    Modelo de entrada para refrescar el access token.

    Contiene el refresh token previamente emitido por el sistema.

    Attributes:
        refresh_token (str): JWT de refresco válido.
    """
    refresh_token: str
