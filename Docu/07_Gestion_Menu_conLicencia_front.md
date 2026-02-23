# 07 - Gestión del Menú con Licencia (Frontend)

## 1. Objetivo

Conectar Vuetify con el endpoint `/api/v1/me/features` para que la
navegación visible dependa dinámicamente de las funcionalidades
licenciadas.

El frontend no decide qué existe, solo muestra lo permitido por backend.

------------------------------------------------------------------------

## 2. Flujo

Login → Guardar JWT → Consultar /me/features → Guardar features →
Construir menú filtrado

------------------------------------------------------------------------

## 3. Respuesta Backend

``` json
{ "features": ["HORSES","CLIENTS","LESSONS"] }
```

------------------------------------------------------------------------

## 4. Tipos (types/api.ts)

``` ts
export type FeatureCode =
  | "HORSES"
  | "CLIENTS"
  | "LESSONS"
  | "BOOKINGS"
  | "BILLING"
  | "REPORTING";

export type NavItem = {
  titleKey: string;
  icon?: string;
  route: string;
  feature?: FeatureCode;
};
```

------------------------------------------------------------------------

## 5. Branding Define la UI

`branding.json` define navegación potencial:

``` json
{
  "titleKey": "menu.horses",
  "icon": "mdi-horse",
  "route": "/horses",
  "feature": "HORSES"
}
```

------------------------------------------------------------------------

## 6. Estado Runtime de Features

Se cargan desde backend y se cachean en localStorage para evitar
parpadeos.

------------------------------------------------------------------------

## 7. Filtrado de Navegación

Regla: - Sin `feature` → visible - Con `feature` habilitada → visible -
No habilitada → oculto

------------------------------------------------------------------------

## 8. Integración en MainLayout.vue

``` ts
const navigation = computed(() =>
  filterNavigation(branding.navigation, features.value)
);
```

------------------------------------------------------------------------

## 9. Carga Tras Login

``` ts
setTokens(res.data);
await fetchFeatures();
router.push(...);
```

------------------------------------------------------------------------

## 10. Interceptor Axios

Añade automáticamente: Authorization: Bearer `<token>`{=html}

------------------------------------------------------------------------

## 11. Seguridad

Esto es licenciamiento visual. La seguridad real sigue en backend (JWT +
roles).

------------------------------------------------------------------------

## 12. Beneficios

-   Arquitectura SaaS real
-   Un único build
-   Activación sin redeploy
-   Escalable a planes comerciales

------------------------------------------------------------------------

## 13. Estado Actual

✔ Backend conectado\
✔ Features dinámicas\
✔ Menú filtrado automáticamente\
✔ Sistema preparado para crecer
