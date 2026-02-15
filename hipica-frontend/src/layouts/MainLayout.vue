<template>
  <v-app>
    <!-- Barra superior -->
    <v-app-bar color="primary">
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

      <!-- aquí luego pondremos usuario/logout -->
      <language-selector />
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
import { computed } from "vue";
import LanguageSelector from "@/components/LanguageSelector.vue";

/**
 * Branding cargado previamente en index.html
 */
const branding = (window as any).__APP_BRANDING__ as
  | {
      appName: string;
      logo?: string;
      favicon?: string;
    }
  | null;

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

const client = detectClient();

/**
 * Construir URL absoluta del logo
 */
const brandingLogoUrl = computed(() => {
  if (!branding?.logo) return undefined;
  return `/branding/${client}/${branding.logo}`;
});
</script>

