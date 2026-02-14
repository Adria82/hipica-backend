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
 * 
 * VUETIFY AZUL Y OK NO RECUADROS
 */

import "vuetify/styles"; // NECESARIO-> sin esto Vuetify se rompe

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
    layers: true,
    defaultTheme: "hipica",
    
    themes: {
      hipica: {
        dark: false,

        colors: {
          background: "var(--color-bg)",
          surface: "var(--color-surface)",

          primary: "var(--color-primary)",
          secondary: "var(--color-primary-dark)",
          accent: "var(--color-accent)",

          error: "#b00020",
          info: "var(--color-primary)",
          success: "#2e7d32",
          warning: "#ed6c02",
        },
      },
    },
  },

});




/**
 * Configuración centralizada de Vuetify.
 * Vuetify NO define colores propios:
 * usa las variables CSS del theme corporativo.
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
          background: "var(--color-bg)",
          surface: "var(--color-surface)",

          primary: "var(--color-primary)",
          secondary: "var(--color-primary-dark)",
          accent: "var(--color-accent)",

          error: "#b00020",
          info: "var(--color-primary)",
          success: "#2e7d32",
          warning: "#ed6c02",
        },
      },
    },
  },
});
*/