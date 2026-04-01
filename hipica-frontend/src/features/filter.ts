import type { FeatureCode, NavItem } from "@/types/api";

/**
 * Filtra sin modificar la referencia original de los items.
 * Esto mantiene el comportamiento de Vuetify navigation.
 */
export function filterNavigation(
  navigation: readonly NavItem[],
  enabled: readonly FeatureCode[]
): NavItem[] {
  const result: NavItem[] = [];

  for (const item of navigation) {
    // si no requiere licencia → se deja pasar tal cual (MISMA referencia)
    if (!item.feature) {
      result.push(item);
      continue;
    }

    if (enabled.includes(item.feature)) {
      result.push(item);
    }
  }

  return result;
}
