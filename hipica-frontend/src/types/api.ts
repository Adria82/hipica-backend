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
  horse_names: string[];
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
  levels: string[];       // nombres localizados (para mostrar)
  level_ids: number[];    // IDs de niveles asignados (para formularios)
};


/**
 * Entidad Level (nivel de equitación).
 * names contiene el nombre en cada idioma soportado: es, en, ca.
 */
export type Level = {
  id: number;
  names: { es: string; en: string; ca: string };
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
  name: string;
  apellidos: string | null;
  email: string;
  dni: string | null;
  phone: string | null;
  role: string;
  stable_id: number | null;
  stable_name: string | null;
  stable_theme: string | null;
  avatar: string | null;
};

export type ClientProfileData = {
  direccion: string | null;
  iban: string | null;
  notes: string | null;
  level_id: number | null;
};

export type MonitorProfileData = {
  especialidad: string | null;
  disponibilidad: string | null;
  certificados: string | null;
  experiencia: string | null;
  telefono: string | null;
  iban: string | null;
  notas: string | null;
  tarifa_hora: number | null;
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
 * Par alumno-caballo dentro de una lección.
 * horse_id puede ser null si el alumno está en la clase sin caballo asignado.
 */
export type StudentHorsePair = {
  student_id: number;
  horse_id: number | null;
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
  student_names: string[];
  student_horse_pairs: StudentHorsePair[];
};

/**
 * Payload para crear una lección.
 * Si student_horse_pairs está presente, tiene preferencia sobre student_ids.
 */
export type LessonCreate = {
  date_time: string;
  end_time?: string | null;
  instructor_id: number;
  helper_id?: number | null;
  track_id?: number | null;
  description?: string | null;
  horse_ids: number[];
  student_ids?: number[];
  student_horse_pairs?: StudentHorsePair[];
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
  name: string;
  email: string;
  hours: number;
  class_count: number;
};

export type HelperHours = {
  user_id: number;
  name: string;
  email: string;
  hours: number;
  class_count: number;
};

export type StudentClasses = {
  user_id: number;
  name: string;
  class_count: number;
  hours: number;
};

export type HorseHours = {
  horse_id: number;
  name: string;
  hours: number;
};

export type TrackHours = {
  track_id: number;
  name: string;
  class_count: number;
  hours: number;
};

export type LessonDetail = {
  lesson_id: number;
  date_time: string;
  end_time: string | null;
  duration_hours: number;
  track_name: string | null;
  instructor_name: string;
};

export type LessonReport = {
  instructor_hours: InstructorHours[];
  helper_hours: HelperHours[];
  student_classes: StudentClasses[];
  horse_hours: HorseHours[];
  track_hours: TrackHours[];
  from_date: string | null;
  to_date: string | null;
};

/**
 * Entidad User (usuario de la hípica).
 *
 * Devuelto por GET /api/v1/users y endpoints relacionados.
 */
export type UserRead = {
  id: number;
  name: string;
  apellidos: string | null;
  email: string;
  dni: string | null;
  role: string;
  phone: string | null;
  stable_id: number | null;
  is_active: boolean;
};

/**
 * Perfil extendido de un cliente (role=client).
 */
export type ClientProfile = {
  apellidos: string | null;
  direccion: string | null;
  iban: string | null;
  notes: string | null;
};

/**
 * Perfil extendido de monitor o ayudante (role=monitor|assistant).
 */
export type MonitorProfile = {
  especialidad: string | null;
  disponibilidad: string | null;
  certificados: string | null;
  experiencia: string | null;
  telefono: string | null;
  iban: string | null;
  notas: string | null;
  tarifa_hora: number | null;
};
