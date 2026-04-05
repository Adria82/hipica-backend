"""
Utilidades i18n para mensajes de la API.

Define:
- Idiomas soportados.
- Resolución de idioma a partir de la cabecera Accept-Language.
- Traducción de mensajes por clave.
"""

from __future__ import annotations

from fastapi import Request

DEFAULT_LANGUAGE = "ca"
SUPPORTED_LANGUAGES = {"ca", "es", "en"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        "api.running": "API Hípica en marcha",
        "auth.credentials_not_validated": "No se pudo validar las credenciales",
        "auth.permission_denied": "No tienes permisos para realizar esta acción",
        "auth.credentials_invalid": "Credenciales incorrectas",
        "auth.refresh_token_invalid": "Refresh token inválido",
        "client.not_found": "Cliente no encontrado",
        "horse.not_found": "Caballo no encontrado",
        "horse.invalid_levels": "Uno o más niveles no son válidos",
        "level.exists": "El nivel ya existe",
        "level.not_found": "Nivel no encontrado",
        "level.delete_associated": "No se puede eliminar un nivel asociado a caballos",
        "stable.not_found": "Hípica no encontrada",
        "user.email_exists": "Ya existe un usuario con este email",
        "user.not_found": "Usuario no encontrado",
        "lesson.stable_required": "Debes seleccionar una hípica",
        "lesson.client_not_found": "Cliente {client_id} no encontrado",
        "lesson.horse_not_found": "Caballo {horse_id} no encontrado",
        "lesson.not_found": "Lección no encontrada",
        "box.not_found": "Box no encontrado",
        "box.has_horses": "No se puede eliminar el box porque tiene caballos asignados: {horse_names}",
        "box.full": "El box '{box_name}' está lleno (capacidad: {capacity}). Caballos asignados: {horse_names}",
        "booking.not_found": "Reserva no encontrada",
        "booking.not_published": "Esta clase no está publicada para reservas",
        "booking.lesson_started": "Esta clase ya ha comenzado o ha pasado",
        "booking.duplicate": "Ya tienes una reserva para esta clase",
        "booking.full": "Esta clase está completa",
        "booking.not_cancellable": "Esta reserva no se puede cancelar",
        "booking.cancel_deadline_passed": "El plazo de cancelación ha pasado",
    },
    "ca": {
        "api.running": "API Hípica en marxa",
        "auth.credentials_not_validated": "No s'han pogut validar les credencials",
        "auth.permission_denied": "No tens permisos per fer aquesta acció",
        "auth.credentials_invalid": "Credencials incorrectes",
        "auth.refresh_token_invalid": "Refresh token invàlid",
        "client.not_found": "Client no trobat",
        "horse.not_found": "Cavall no trobat",
        "horse.invalid_levels": "Un o més nivells no són vàlids",
        "level.exists": "El nivell ja existeix",
        "level.not_found": "Nivell no trobat",
        "level.delete_associated": "No es pot eliminar un nivell associat a cavalls",
        "stable.not_found": "Hípica no trobada",
        "user.email_exists": "Ja existeix un usuari amb aquest email",
        "user.not_found": "Usuari no trobat",
        "lesson.stable_required": "Has de seleccionar una hipica",
        "lesson.client_not_found": "Client {client_id} no trobat",
        "lesson.horse_not_found": "Cavall {horse_id} no trobat",
        "lesson.not_found": "Lliçó no trobada",
        "box.not_found": "Box no trobat",
        "box.has_horses": "No es pot eliminar el box perquè té cavalls assignats: {horse_names}",
        "box.full": "El box '{box_name}' està ple (capacitat: {capacity}). Cavalls assignats: {horse_names}",
        "booking.not_found": "Reserva no trobada",
        "booking.not_published": "Aquesta classe no està publicada per a reserves",
        "booking.lesson_started": "Aquesta classe ja ha començat o ha passat",
        "booking.duplicate": "Ja tens una reserva per a aquesta classe",
        "booking.full": "Aquesta classe és plena",
        "booking.not_cancellable": "Aquesta reserva no es pot cancel·lar",
        "booking.cancel_deadline_passed": "El termini de cancel·lació ha passat",
    },
    "en": {
        "api.running": "Hipica API is running",
        "auth.credentials_not_validated": "Could not validate credentials",
        "auth.permission_denied": "You do not have permission to perform this action",
        "auth.credentials_invalid": "Invalid credentials",
        "auth.refresh_token_invalid": "Invalid refresh token",
        "client.not_found": "Client not found",
        "horse.not_found": "Horse not found",
        "horse.invalid_levels": "One or more levels are invalid",
        "level.exists": "Level already exists",
        "level.not_found": "Level not found",
        "level.delete_associated": "Cannot delete a level associated with horses",
        "stable.not_found": "Stable not found",
        "user.email_exists": "A user with this email already exists",
        "user.not_found": "User not found",
        "lesson.stable_required": "You must select a stable",
        "lesson.client_not_found": "Client {client_id} not found",
        "lesson.horse_not_found": "Horse {horse_id} not found",
        "lesson.not_found": "Lesson not found",
        "box.not_found": "Box not found",
        "box.has_horses": "Cannot delete the box because it has horses assigned: {horse_names}",
        "box.full": "Box '{box_name}' is full (capacity: {capacity}). Assigned horses: {horse_names}",
        "booking.not_found": "Booking not found",
        "booking.not_published": "This lesson is not published for bookings",
        "booking.lesson_started": "This lesson has already started or passed",
        "booking.duplicate": "You already have a booking for this lesson",
        "booking.full": "This lesson is full",
        "booking.not_cancellable": "This booking cannot be cancelled",
        "booking.cancel_deadline_passed": "The cancellation deadline has passed",
    },
}


def _normalize_language(raw_language: str | None) -> str:
    """Normaliza Accept-Language y devuelve ca/es/en con fallback a ca."""
    if not raw_language:
        return DEFAULT_LANGUAGE

    for entry in raw_language.split(","):
        language_tag = entry.split(";")[0].strip().lower()
        if not language_tag:
            continue

        base_language = language_tag.split("-")[0]
        if base_language in SUPPORTED_LANGUAGES:
            return base_language

    return DEFAULT_LANGUAGE


def get_request_language(request: Request) -> str:
    """Devuelve el idioma resuelto para la request actual."""
    return _normalize_language(request.headers.get("Accept-Language"))


def t(request: Request, key: str, **kwargs: object) -> str:
    """Traduce una clave de mensaje usando el idioma de la request."""
    language = get_request_language(request)
    template = (
        TRANSLATIONS.get(language, {}).get(key)
        or TRANSLATIONS[DEFAULT_LANGUAGE].get(key)
        or key
    )
    return template.format(**kwargs)
