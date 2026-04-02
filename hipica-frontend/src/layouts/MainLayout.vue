<template>
  <v-app>
    <!-- Menu Lateral -->
    <v-navigation-drawer v-model="drawer" app color="primary" dark>
      <v-list density="comfortable" nav>
        <v-list-item
          v-for="item in navigation"
          :key="item.route"
          :to="item.route"
          :value="item.route"
          :title="t(item.titleKey)"
          :prepend-icon="item.icon"
        />
          
        
      </v-list>
    </v-navigation-drawer>
    <!-- Barra superior -->
    <v-app-bar color="primary">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-app-bar-title class="d-flex align-center ga-3">
        <!-- Logo dinámico -->
        <v-img
            v-if="branding?.logo"
            :src="brandingLogoUrl"
            alt="logo"
            max-height="36"
            max-width="36"
            contain
        />

        <!-- Nombre de la hípica -->
        <span>{{ branding?.appName }}</span>
        </v-app-bar-title>

      <v-spacer />

      <language-selector />
      <v-btn
        icon="mdi-logout"
        variant="text"
        :title="t('layout.logout')"
        @click="logout"
      />
    </v-app-bar>

    <!-- Aquí irán vistas hijas -->
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import LanguageSelector from "@/components/LanguageSelector.vue";
import type { NavItem } from "@/types/features";

import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { getAccessToken, clearTokens } from "@/auth/tokens";
import { features, fetchFeatures } from "@/features/features";
import { fetchProfile, clearProfile } from "@/auth/profile";
import { filterNavigation } from "@/features/filter";

const { t } = useI18n();
const router = useRouter();
const drawer = ref(true);

function logout() {
  clearTokens();
  clearProfile();
  router.push({ name: "login" });
}

onMounted(async () => {
  // Si no hay token, no cargamos features (estás en login / público)
  if (!getAccessToken()) return;

  try {
    await Promise.all([fetchFeatures(), fetchProfile()]);
  } catch (e) {
    // Si falla, seguimos con lo cacheado (si hubiese), sin romper UI
    console.warn("No se pudieron cargar features/profile:", e);
  }
});

/**
 * Branding cargado previamente en index.html
 * Lo lee del fichero branding.json que tiene cada cliente en: public/branding/[cliente]/branding.json
 */
const branding = (window as any).__APP_BRANDING__ as
  | {
      appName: string;
      logo?: string;
      favicon?: string;
      navigation?: {
        titleKey: string;
        icon?: string;
        route: string;
        navigation?: NavItem[];
      }[];
    }
  | null;

const client = detectClient();

/**
 * Construir URL absoluta del logo
 */
const brandingLogoUrl = computed(() => {
  if (!branding?.logo) return undefined;
  return `/branding/${client}/${branding.logo}`;
});


/**
 * Creamos la navegación reactiva
 */
const navigation = computed(() =>
  filterNavigation(branding?.navigation ?? [], features.value)
);

/**
 * Detectar cliente igual que en index.html
 * (lo repetimos porque Vue no puede leer esa función)
 */
function detectClient(): string {
  const host = window.location.hostname;

  if (host.includes("localhost") || host.startsWith("127.0.0.1")) {
    return "demo";
  }

  const parts = host.split(".");
  return parts.length > 2 ? parts[0] : "demo";
}





</script>

