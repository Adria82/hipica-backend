/**
 * ============================================================
 * Auth Storage Helpers
 * ============================================================
 * Utilidades para gestionar los tokens de autenticación en
 * el almacenamiento local del navegador.
 *
 * Este módulo encapsula el acceso a localStorage para:
 *  - Guardar los tokens tras el login
 *  - Recuperarlos para las llamadas a la API
 *  - Eliminarlos al hacer logout
 *  - Saber si el usuario tiene sesión activa
 *
 * Centralizar esta lógica evita duplicaciones y facilita
 * futuros cambios (por ejemplo, migrar a cookies seguras).
 * ============================================================
 */

/** Nombres de las claves en localStorage del navegador
 * simples etiquetas.
 */
const ACCESS_KEY = "hipica_access_token";
const REFRESH_KEY = "hipica_refresh_token";

/**
 * Obtiene el access token almacenado en el navegador.
 *
 * @returns El JWT de acceso si existe, o null si el usuario no está autenticado.
 */
export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}

/**
 * Obtiene el refresh token almacenado.
 *
 * @returns El refresh token si existe, o null si no hay sesión.
 */
export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}


/**
 * Guarda los tokens de autenticación tras un login o refresh exitoso.
 *
 * @param tokens Objeto con el access_token y refresh_token devueltos por la API.
 */
export function setTokens(tokens: { access_token: string; refresh_token: string }): void {
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

/**
 * Elimina los tokens del almacenamiento.
 *
 * Debe llamarse en:
 *  - Logout explícito del usuario
 *  - Expiración definitiva de sesión
 *  - Error de refresh token
 */
export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

/**
 * Indica si el usuario tiene una sesión activa en el frontend.
 *
 * !!Solo comprueba existencia del token, no su validez.
 * La verificación real depende del backend.
 *
 * @returns true si hay access token almacenado, false en caso contrario.
 */
export function isLoggedIn(): boolean {
  return !!getAccessToken();
}
