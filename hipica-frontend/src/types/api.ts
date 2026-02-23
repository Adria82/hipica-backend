/**
 * ============================================================
 * API Types
 * ============================================================
 * Definiciones de tipos utilizadas para la comunicación
 * con el backend (DTOs de request y response).
 *
 * Este fichero centraliza los contratos tipados entre
 * frontend y backend.
 * ============================================================
 */


/**
 * Respuesta devuelta por el endpoint de autenticación.
 *
 * Se obtiene tras realizar login correctamente.
 */
export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer" | string;
};

/**
 * Payload utilizado para solicitar un nuevo access_token
 * cuando el actual ha expirado.
 */
export type RefreshRequest = {
  refresh_token: string;
};

/**
 * Entidad Horse.
 *
 * Representa un caballo dentro de una hípica.
 * Se corresponde con el modelo Horse del backend.
 */
export type Horse = {
  id: number;
  name: string;
  box?: string | null;
  is_active: boolean;
  stable_id: number;
};

export type FeatureCode =
  | "HORSES"
  | "CLIENTS"
  | "LESSONS"
  | "BOOKINGS"
  | "BILLING"
  | "REPORTING";

export type NavItem = {
  titleKey: string;
  icon?: string;
  route: string;
  feature?: FeatureCode; // si existe, se filtra por licencia
};