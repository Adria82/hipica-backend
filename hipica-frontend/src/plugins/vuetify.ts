/**
 * Configuración centralizada de Vuetify.
 * Aquí definimos:
 *  - Componentes y directivas
 *  - Iconos (MDI)
 *  - Theme corporativo de la Hípica
 */

/*

import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import { mdi } from "vuetify/iconsets/mdi";
import "@mdi/font/css/materialdesignicons.css";

export const vuetify = createVuetify({
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
          background: "#f4efe7",     // arena
          surface: "#ffffff",        // tarjetas

          primary: "#8b5e3c",        // madera media
          secondary: "#5c3d2e",      // madera oscura
          accent: "#c8a27a",         // cuero

          info: "#8b5e3c",

          "on-primary": "#ffffff",
          "on-secondary": "#ffffff",
        },
      },
    },
  },
});
*/


/**
 * Configuración centralizada de Vuetify
 */

import "vuetify/styles"; // NECESARIO

import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import { mdi } from "vuetify/iconsets/mdi";
import "@mdi/font/css/materialdesignicons.css";

export const vuetify = createVuetify({
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
          // AQUÍ VAN LOS COLORES REALES (no CSS vars)
          background: "#f4efe7",
          surface: "#ffffff",

          primary: "#8b5e3c",
          secondary: "#5c3d2e",
          accent: "#c8a27a",

          error: "#b00020",
          info: "#8b5e3c",
          success: "#2e7d32",
          warning: "#ed6c02",

          // importante para el color del texto base
          "on-surface": "#2b2b2b",
        },
      },
    },
  },
});
