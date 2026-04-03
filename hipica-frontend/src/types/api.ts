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
  stable_name: string | null;
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
  stable_name: string | null;
  levels: string[];
};

/**
 * Entidad Client (cliente de una hípica).
 */
export type Client = {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  stable_id: number;
  stable_name: string | null;
};

/**
 * Entidad Level (nivel de equitación).
 */
export type Level = {
  id: number;
  name: string;
};

/**
 * Entidad Stable (hípica).
 */
export type Stable = {
  id: number;
  name: string;
  location: string;
  is_active: boolean;
  theme: string | null;
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
  stable_name: string | null;
  stable_theme: string | null;
  avatar: string | null;
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

/**
 * Sección del menú lateral.
 * Agrupa NavItems bajo un encabezado con control de visibilidad.
 *
 * - adminOnly: solo visible para app_admin
 * - items: filtrados por feature si tienen el campo `feature`
 */
export type NavSection = {
  titleKey: string;
  adminOnly?: boolean;
  items: NavItem[];
};

/**
 * Entidad Track (pista de equitación).
 *
 * Representa una pista física dentro de una hípica.
 */
export type Track = {
  id: number;
  name: string;
  stable_id: number;
  is_active: boolean;
};

/**
 * Entidad Lesson (clase/lección).
 *
 * Respuesta completa con datos desnormalizados: emails de instructor/ayudante,
 * nombre de pista, nombres de caballos y alumnos.
 */
export type Lesson = {
  id: number;
  date_time: string;
  end_time: string | null;
  instructor_id: number;
  instructor_email: string;
  helper_id: number | null;
  helper_email: string | null;
  track_id: number | null;
  track_name: string | null;
  description: string | null;
  stable_id: number;
  horse_names: string[];
  client_names: string[];
};

/**
 * Payload para crear una lección.
 */
export type LessonCreate = {
  date_time: string;
  end_time?: string | null;
  instructor_id: number;
  helper_id?: number | null;
  track_id?: number | null;
  description?: string | null;
  horse_ids: number[];
  client_ids: number[];
};

/**
 * Payload para actualizar una lección (todos los campos opcionales).
 */
export type LessonUpdate = Partial<LessonCreate>;

// ---------------------------------------------------------------------------
// Reports
// ---------------------------------------------------------------------------

export type InstructorHours = {
  user_id: number;
  email: string;
  hours: number;
};

export type HelperHours = {
  user_id: number;
  email: string;
  hours: number;
};

export type StudentClasses = {
  client_id: number;
  name: string;
  class_count: number;
};

export type HorseHours = {
  horse_id: number;
  name: string;
  hours: number;
};

export type LessonReport = {
  instructor_hours: InstructorHours[];
  helper_hours: HelperHours[];
  student_classes: StudentClasses[];
  horse_hours: HorseHours[];
  from_date: string | null;
  to_date: string | null;
};

/**
 * Entidad User (usuario de la hípica) — versión pública para selectores.
 */
export type UserRead = {
  id: number;
  email: string;
  role: string;
  stable_id: number | null;
};
