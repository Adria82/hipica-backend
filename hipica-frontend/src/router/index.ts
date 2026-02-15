/**
 * Router principal de la aplicación.
 *
 * Funcionalidades:
 *  - Define las rutas disponibles en el frontend.
 *  - Protege las rutas que requieren autenticación.
 *  - Si el usuario no está logueado -> redirige automáticamente a /login.
 *
 * Más adelante se podrá ampliar para control de roles.
 *
 * Autor: Adrià Bofill
 * Proyecto: Gestión de Hípica
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import Login from "../views/Login.vue";
import Horses from "../views/Horses.vue";
import { isLoggedIn } from "../auth/tokens";
import MainLayout from "../layouts/MainLayout.vue";


/**
 * Definición de rutas de la aplicación.
 */
const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: Login,
  },

  /**
   * Zona protegida de la app (usa layout)
   */
  {
    path: "/",
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        redirect: "/horses",
      },
      {
        path: "horses",
        name: "horses",
        component: Horses,
      },
    ],
  },
];


/**
 * Creación del router usando history mode (URLs limpias).
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
});

/**
 * Navigation Guard global.
 *
 * Se ejecuta antes de cada cambio de ruta.
 */
router.beforeEach((to) => {
  const requiresAuth = to.meta.requiresAuth;

  // Si la ruta requiere login y NO estamos autenticados -> login
  if (requiresAuth && !isLoggedIn()) {
    return { name: "login" };
  }

  // Si ya estamos logueados e intentamos ir a /login -> redirigir
  if (to.name === "login" && isLoggedIn()) {
    return { name: "horses" };
  }
});

export default router;
