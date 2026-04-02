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
 * Entidad Box.
 *
 * Representa un box físico de una hípica donde se alojan caballos.
 * Se corresponde con el modelo Box del backend.
 */
export type Box = {
  id: number;
  name: string;
  capacity: number;
  stable_id: number;
  is_active: boolean;
  horses_count: number;
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
  box_id: number | null;
  box_name: string | null;
  is_active: boolean;
  stable_id: number;
  levels: string[];
};

/**
 * Entidad Stable (hípica).
 */
export type Stable = {
  id: number;
  name: string;
  location: string;
  is_active: boolean;
};

/**
 * Perfil del usuario autenticado.
 *
 * Devuelto por GET /api/v1/me/profile.
 */
export type UserProfile = {
  id: number;
  email: string;
  role: string;
  stable_id: number | null;
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
