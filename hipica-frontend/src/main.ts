/**
 * Punto de entrada de la aplicación Vue.
 * Aquí se monta la app y se registra el router global.
 */

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

createApp(App)
  .use(router)
  .mount("#app");
