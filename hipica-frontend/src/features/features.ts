/**
 * Estado de features activas de la sesión.
 * No define tipos: usa los de types/api.ts
 */

import { ref } from "vue";
import { http } from "@/api/http";
import type { FeatureCode } from "@/types/api";

const STORAGE_KEY = "hipica_features";

/**
 * Estado global reactivo
 */
export const features = ref<FeatureCode[]>(load());

function load(): FeatureCode[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

/**
 * Cargar desde backend
 */
export async function fetchFeatures(): Promise<void> {
  const { data } = await http.get<{ features: FeatureCode[] }>("/api/v1/me/features");

  features.value = data.features ?? [];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(features.value));
}

/**
 * Limpiar sesión
 */
export function clearFeatures(): void {
  features.value = [];
  localStorage.removeItem(STORAGE_KEY);
}