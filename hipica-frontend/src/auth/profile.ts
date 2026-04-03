/**
 * Estado reactivo del perfil del usuario autenticado.
 *
 * Persiste en localStorage para sobrevivir recargas.
 * Se carga tras el login y se limpia en el logout.
 */

import { ref, computed } from "vue";
import { http } from "@/api/http";
import type { UserProfile } from "@/types/api";

const STORAGE_KEY = "hipica_user_profile";

export const userProfile = ref<UserProfile | null>(loadProfile());

function loadProfile(): UserProfile | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export async function fetchProfile(): Promise<void> {
  const { data } = await http.get<UserProfile>("/api/v1/me/profile");
  userProfile.value = data;
  // El avatar (base64) se excluye de localStorage para evitar QuotaExceededError.
  // Se recarga desde la API en cada sesión (MainLayout lo llama en onMounted).
  const { avatar: _avatar, ...rest } = data;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(rest));
}

export function clearProfile(): void {
  userProfile.value = null;
  localStorage.removeItem(STORAGE_KEY);
}

/** true si el usuario puede crear/editar/eliminar registros */
export const canManage = computed(
  () =>
    userProfile.value?.role === "app_admin" ||
    userProfile.value?.role === "stable_admin"
);

/** true si el usuario es app_admin (acceso global a todas las hípicas) */
export const isAppAdmin = computed(
  () => userProfile.value?.role === "app_admin"
);
