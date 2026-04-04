/**
 * Router principal de la aplicación.
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import Login from "../views/Login.vue";
import Horses from "../views/Horses.vue";
import Boxes from "../views/Boxes.vue";
import Lessons from "../views/Lessons.vue";
import Reports from "../views/Reports.vue";
import Stables from "../views/Stables.vue";
import Levels from "../views/Levels.vue";
import Features from "../views/Features.vue";
import Profile from "../views/Profile.vue";
import { isLoggedIn } from "../auth/tokens";
import MainLayout from "../layouts/MainLayout.vue";
import Users from "../views/Users.vue";
import Tracks from "../views/Tracks.vue";

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

      // Operativa
      { path: "horses",  name: "horses",  component: Horses  },
      { path: "boxes",   name: "boxes",   component: Boxes   },
      { path: "tracks",  name: "tracks",  component: Tracks  },
      { path: "lessons", name: "lessons", component: Lessons },

      // Administración (solo app_admin / stable_admin)
      { path: "users",    name: "users",    component: Users    },
      { path: "stables",  name: "stables",  component: Stables  },
      { path: "levels",   name: "levels",   component: Levels   },
      { path: "features", name: "features", component: Features },
      { path: "reports",  name: "reports",  component: Reports  },

      // Mi espacio
      { path: "profile", name: "profile", component: Profile },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    return { name: "login" };
  }
  if (to.name === "login" && isLoggedIn()) {
    return { name: "horses" };
  }
});

export default router;
