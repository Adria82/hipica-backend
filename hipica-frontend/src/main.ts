/**
 * Punto de entrada de la aplicación Vue.
 * Aquí se monta la app y se registra el router global.
 */

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { i18n } from "./i18n";
import "./style.css";

// Importar Vuetify
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { mdi } from "vuetify/iconsets/mdi";
import "@mdi/font/css/materialdesignicons.css";

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: "mdi",
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: "hipica",
    themes: {
      hipica: {
        dark: false,
        colors: {
          background: "#f4efe7",
          surface: "#ffffff",
          primary: "#8b5e3c",
          secondary: "#5c3d2e",
          accent: "#c8a27a",
          info: "#8b5e3c",
          "on-primary": "#ffffff",
          "on-secondary": "#ffffff",
        },
      },
    },
  },
});

createApp(App)
  .use(i18n)
  .use(router)
  .use(vuetify)
  .mount("#app");
