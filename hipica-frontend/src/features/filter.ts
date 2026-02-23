import type { FeatureCode, NavItem } from "@/types/api";

/**
 * Filtra navegación según features activas.
 */
export function filterNavigationByFeatures(
  navigation: NavItem[],
  enabled: FeatureCode[]
): NavItem[] {
  return navigation.filter((item) => {
    // Si el item no define feature → siempre visible
    if (!item.feature) return true;

    // Si define feature → visible solo si está habilitada
    return enabled.includes(item.feature);
  });
}


