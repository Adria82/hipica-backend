/**
 * Punto de entrada de la aplicación Vue.
 * Aquí solo montamos la app y registramos plugins globales.
 */

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { i18n } from "./i18n";

import "vuetify/styles";
import { vuetify } from "./plugins/vuetify";

// estilos globales (tokens visuales)
import "./assets/theme.css";

createApp(App)
  .use(i18n)
  .use(router)
  .use(vuetify)
  .mount("#app");
