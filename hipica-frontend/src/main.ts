/**
 * Punto de entrada de la aplicación Vue.
 * Aquí se monta la app y se registra el router global.
 */

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { i18n } from "./i18n";

createApp(App)
  .use(i18n)
  .use(router)
  .mount("#app");
