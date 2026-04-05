<template>
  <v-app>
    <!-- Menú lateral -->
    <v-navigation-drawer v-model="drawer" app color="primary" dark>
      <v-list density="comfortable" nav>

        <!-- Sección Administración (solo app_admin) -->
        <template v-if="isAppAdmin">
          <v-list-subheader class="text-uppercase font-weight-bold opacity-70">
            {{ t("nav.admin") }}
          </v-list-subheader>
          <v-list-item
            v-for="item in adminItems"
            :key="item.route"
            :to="item.route"
            :value="item.route"
            :title="t(item.titleKey)"
            :prepend-icon="item.icon"
            rounded="lg"
          />
          <v-divider class="my-2 opacity-30" />
        </template>

        <!-- Sección Operativa (filtrada por features) -->
        <v-list-subheader class="text-uppercase font-weight-bold opacity-70">
          {{ t("nav.operativa") }}
        </v-list-subheader>
        <v-list-item
          v-for="item in operativaItems"
          :key="item.route"
          :to="item.route"
          :value="item.route"
          :title="t(item.titleKey)"
          :prepend-icon="item.icon"
          rounded="lg"
        />
        <v-divider class="my-2 opacity-30" />

        <!-- Sección Mi espacio -->
        <v-list-subheader class="text-uppercase font-weight-bold opacity-70">
          {{ t("nav.myspace") }}
        </v-list-subheader>
        <v-list-item
          v-for="item in myspaceItems"
          :key="item.route"
          :to="item.route"
          :value="item.route"
          :title="t(item.titleKey)"
          :prepend-icon="item.icon"
          rounded="lg"
        />

      </v-list>
    </v-navigation-drawer>

    <!-- Barra superior -->
    <v-app-bar color="primary">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-app-bar-title class="d-flex align-center ga-3">
        <v-img
          v-if="branding?.logo"
          :src="brandingLogoUrl"
          alt="logo"
          max-height="36"
          max-width="36"
          contain
        />
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

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import LanguageSelector from "@/components/LanguageSelector.vue";
import { getAccessToken, clearTokens } from "@/auth/tokens";
import { features, fetchFeatures } from "@/features/features";
import { fetchProfile, clearProfile, isAppAdmin, userProfile } from "@/auth/profile";
import type { NavItem, FeatureCode } from "@/types/api";

const isMonitorOrAssistant = computed(() =>
  ["monitor", "assistant"].includes(userProfile.value?.role ?? "")
);

const { t } = useI18n();
const router = useRouter();
const drawer = ref(true);

// ---------------------------------------------------------------------------
// Branding
// ---------------------------------------------------------------------------
const branding = (window as any).__APP_BRANDING__ as { appName: string; logo?: string } | null;

const brandingLogoUrl = computed(() => {
  if (!branding?.logo) return undefined;
  const theme = userProfile.value?.stable_theme ?? "default";
  return `/branding/${theme}/${branding.logo}`;
});

// ---------------------------------------------------------------------------
// Navegación estática con gating
// ---------------------------------------------------------------------------

const ADMIN_ITEMS: NavItem[] = [
  { titleKey: "menu.users",        icon: "mdi-account-multiple",  route: "/users"         },
  { titleKey: "menu.reports",      icon: "mdi-chart-bar",         route: "/reports"       },
  { titleKey: "menu.stables",      icon: "mdi-home-group",        route: "/stables"       },
  { titleKey: "menu.levels",       icon: "mdi-stairs",            route: "/levels"        },
  { titleKey: "menu.features",     icon: "mdi-toggle-switch",     route: "/features"      },
  { titleKey: "menu.stableConfig", icon: "mdi-cog-outline",       route: "/stable-config" },
];

const OPERATIVA_ITEMS: (NavItem & { feature?: FeatureCode })[] = [
  { titleKey: "menu.users",     icon: "mdi-account-multiple",  route: "/users",    feature: "USERS"     },
  { titleKey: "menu.reports",   icon: "mdi-chart-bar",         route: "/reports",  feature: "REPORTING" },
  { titleKey: "menu.horses",    icon: "mdi-horse",             route: "/horses",   feature: "HORSES"    },
  { titleKey: "menu.boxes",     icon: "mdi-door",              route: "/boxes",    feature: "HORSES"    },
  { titleKey: "menu.tracks",    icon: "mdi-map-marker-path",   route: "/tracks",   feature: "LESSONS"   },
  { titleKey: "menu.lessons",   icon: "mdi-school",            route: "/lessons",  feature: "LESSONS"   },
  { titleKey: "menu.bookings",  icon: "mdi-calendar-check",    route: "/bookings", feature: "BOOKINGS"  },
];

const MYSPACE_ITEMS: NavItem[] = [
  { titleKey: "menu.profile",       icon: "mdi-account-circle-outline", route: "/profile"      },
  { titleKey: "menu.availability",  icon: "mdi-clock-outline",          route: "/availability" },
];

const adminItems = ADMIN_ITEMS;

const operativaItems = computed(() =>
  OPERATIVA_ITEMS.filter((item) =>
    !item.feature || features.value.includes(item.feature)
  )
);

const myspaceItems = computed(() =>
  MYSPACE_ITEMS.filter((item) => {
    if (item.route === "/availability") return isMonitorOrAssistant.value;
    return true;
  })
);

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
function logout() {
  clearTokens();
  clearProfile();
  router.push({ name: "login" });
}

onMounted(async () => {
  if (!getAccessToken()) return;
  try {
    await Promise.all([fetchFeatures(), fetchProfile()]);
  } catch (e) {
    console.warn("No se pudieron cargar features/profile:", e);
  }
});
</script>
