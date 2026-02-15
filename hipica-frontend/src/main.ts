/**
 * Punto de entrada de la aplicación Vue.
 */

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { i18n } from "./i18n";

import "vuetify/styles";
import { createVuetifyInstance } from "./plugins/vuetify";

// estilos globales (tokens visuales)
import "./assets/theme.css";

/**
 * Crear Vuetify YA con el branding cargado en index.html
 */
const vuetify = createVuetifyInstance();

const app = createApp(App);

app.use(i18n);
app.use(router);
app.use(vuetify);

app.mount("#app");
