# 02_Vuetify — Integración de Vuetify 3 y sistema de temas

## 🎯 Objetivo
Dejar configurado Vuetify 3 como **fuente única de verdad de los colores** y usar un archivo `theme.css` como puente para exponer *design tokens* reutilizables en toda la aplicación.

---

## 🧠 Cambio de mentalidad respecto a Vuetify 2

### Antes (Vuetify 2)
```
CSS definía los colores → Vuetify los usaba
```

### Ahora (Vuetify 3)
```
Vuetify define los colores → CSS los reutiliza
```

👉 Vuetify genera automáticamente variables CSS internas (`--v-theme-*`).
👉 Nuestra app NO debe inventar colores por fuera.

---

## ⚙️ Cómo funciona internamente Vuetify 3

Si defines en `vuetify.ts`:

```ts
primary: "#8b5e3c"
```

Vuetify genera dinámicamente:

```css
--v-theme-primary: 139,94,60;
```

Eso permite que el framework calcule:
- Contrastes automáticos
- Hover
- Opacidades
- Dark mode
- Tonalidades Material Design 3

⚠️ Por eso Vuetify NO acepta `var(--mi-color)` como entrada.

---

## 🧩 Qué es `theme.css`

`theme.css` NO define colores.

Es un **adaptador** que traduce:

```
--v-theme-primary → --color-primary
```

Así nuestra app puede usar nombres semánticos:

```css
color: var(--color-primary);
```

Sin depender directamente de Vuetify.

Esto desacopla diseño y framework.

---

## 🏗️ Arquitectura final

```
vuetify.ts
   ↓ define colores reales (#hex)

Vuetify runtime
   ↓ genera --v-theme-*

theme.css
   ↓ expone tokens --color-*

componentes propios
   ↓ usan tokens de diseño
```

---

## 📁 Configuración correcta de archivos

---

# ✅ `src/plugins/vuetify.ts`

```ts
import "vuetify/styles";

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
          background: "#f4efe7",
          surface: "#ffffff",

          primary: "#8b5e3c",
          secondary: "#5c3d2e",
          accent: "#c8a27a",

          error: "#b00020",
          info: "#8b5e3c",
          success: "#2e7d32",
          warning: "#ed6c02",

          "on-surface": "#2b2b2b",
        },
      },
    },
  },
});
```

---

# ✅ `src/assets/theme.css`

```css
/* Bridge entre Vuetify y nuestros tokens de diseño */

:root {
  --color-bg: rgb(var(--v-theme-background));
  --color-surface: rgb(var(--v-theme-surface));
  --color-text: rgb(var(--v-theme-on-surface));

  --color-primary: rgb(var(--v-theme-primary));
  --color-primary-dark: rgb(var(--v-theme-secondary));
  --color-accent: rgb(var(--v-theme-accent));

  --color-border: rgba(var(--v-theme-on-surface), 0.12);
}
```

---

# ✅ `src/main.ts`

```ts
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { i18n } from "./i18n";

import "vuetify/styles";

import { vuetify } from "./plugins/vuetify";

import "./assets/theme.css";

createApp(App)
  .use(i18n)
  .use(router)
  .use(vuetify)
  .mount("#app");
```

---

# ✅ `src/App.vue`

```vue
<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>Hípica</v-app-bar-title>
      <v-spacer />
      <language-selector />
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import LanguageSelector from "./components/LanguageSelector.vue";
</script>
```

---

## 🧪 Cómo usar los colores ahora

### Dentro de Vuetify

```vue
<v-btn color="primary" />
```

### En CSS propio

```css
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}
```

---

## 🚀 Ventaja futura

Cuando añadamos modo oscuro, SOLO cambiaremos `vuetify.ts`.

Toda la aplicación —incluyendo CSS propio— cambiará automáticamente.

---

## ✅ Resultado

✔ Sistema desacoplado
✔ Compatible con dark mode
✔ Compatible con multi-brand
✔ Sin hacks
✔ 100% Vuetify 3 compliant

