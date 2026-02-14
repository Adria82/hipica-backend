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
});

createApp(App)
  .use(i18n)
  .use(router)
  .use(vuetify)
  .mount("#app");
