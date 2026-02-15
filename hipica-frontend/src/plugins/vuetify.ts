import "vuetify/styles";

import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import { mdi } from "vuetify/iconsets/mdi";
import "@mdi/font/css/materialdesignicons.css";

/**
 * Crea la instancia de Vuetify usando el branding cargado en runtime.
 */
export function createVuetifyInstance() {
  const branding = (window as any).__APP_BRANDING__ ?? {};

  const themeColors = branding.theme ?? {};

  return createVuetify({
    components,
    directives,

    icons: {
      defaultSet: "mdi",
      sets: { mdi },
    },

    theme: {
      defaultTheme: "hipica",
      themes: {
        hipica: {
          dark: false,
          colors: {
            // defaults
            background: "#f4efe7",
            surface: "#ffffff",
            primary: "#8b5e3c",
            secondary: "#5c3d2e",
            accent: "#c8a27a",

            // branding overrides
            ...themeColors,
          },
        },
      },
    },
  });
}
