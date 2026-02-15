# 03_Layouts — Arquitectura de Layouts y Vistas

## 🎯 Objetivo
Separar la **estructura visual global (Layout)** de las **pantallas funcionales (Views)**.

Esto permite:
- Tener zonas públicas (login) sin UI de aplicación.
- Tener zonas privadas con navegación, app-bar, etc.
- Cambiar layouts sin tocar las vistas.
- Escalar a roles, multi-layout o white‑label sin refactor.

---

## 🧠 Idea clave
`App.vue` deja de contener UI.
El **router decide qué layout usar**.

```
App.vue
  └─ <router-view>
        ├─ Login (sin layout)
        └─ MainLayout
              └─ <router-view>
                     ├─ Horses
                     ├─ (futuras vistas)
```

---

## 📁 Estructura recomendada

```
src/
 ├─ layouts/
 │    └─ MainLayout.vue
 ├─ views/
 │    ├─ Login.vue
 │    └─ Horses.vue
 ├─ router/
 │    └─ index.ts
 └─ App.vue
```

---

## 🏗️ ¿Qué es un Layout?
Un Layout es un **contenedor estructural** que define:
- Cabecera
- Navegación
- Márgenes
- Slots donde se renderizan vistas

⚠️ No contiene lógica de negocio.
⚠️ No llama APIs.
⚠️ No conoce datos.

Solo organiza la UI.

---

## ✅ `MainLayout.vue`

```vue
<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>Hípica</v-app-bar-title>
      <v-spacer />
      <language-selector />
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import LanguageSelector from "@/components/LanguageSelector.vue";
</script>
```

El `<router-view />` interno es donde se renderizan las **vistas hijas**.

---

## 🔀 Router como orquestador de Layouts

El router ahora define qué rutas usan layout y cuáles no.

```ts
const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: Login,
  },
  {
    path: "/",
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "", redirect: "/horses" },
      {
        path: "horses",
        name: "horses",
        component: Horses,
      },
    ],
  },
];
```

---

## 🧩 ¿Por qué el `meta.requiresAuth` está en el padre?

Porque así todas las vistas hijas heredan la protección.

```
/MainLayout
   ├─ /horses
   ├─ /lessons
   └─ /users
```

Un solo control protege todo el "área privada".

---

## 🪶 `App.vue` ahora es mínimo

```vue
<template>
  <router-view />
</template>
```

Su única responsabilidad es montar el router.

---

## 🧠 Ventajas de esta arquitectura

### ✔ Escalable
Añadir nuevas secciones no rompe nada.

### ✔ Reutilizable
Podemos crear más layouts:
- `AdminLayout`
- `PublicLayout`
- `EmbeddedLayout`

### ✔ Compatible con roles
Un layout distinto según permisos.

### ✔ Compatible con theming dinámico
El layout permanece estable aunque cambie Vuetify theme.

### ✔ Testable
Las vistas se prueban aisladas.

---

## 🚀 Cómo añadir una nueva pantalla ahora

1️⃣ Crear la vista:
```
views/Lessons.vue
```

2️⃣ Añadirla como hija del layout:

```ts
{
  path: "lessons",
  name: "lessons",
  component: Lessons,
}
```

No se toca nada más.

---

## 📌 Regla de oro

👉 Las **Views muestran datos**.
👉 Los **Layouts organizan la aplicación**.
👉 El **Router decide cómo se ensamblan**.

Nunca mezclar responsabilidades.

---

## 🏁 Resultado

Tenemos una base profesional preparada para crecer sin deuda técnica.

