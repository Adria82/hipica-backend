# Feature: Menú Lateral Dinámico

## Descripción

El menú lateral de Hipica se construye de forma dinámica en tiempo de ejecución combinando dos fuentes de información:

1. **Branding por cliente** — un fichero `branding.json` específico de cada hípica define qué items de navegación existen, con qué iconos y a qué rutas apuntan.
2. **Licencias activas** — el sistema de features filtra esos items para mostrar únicamente los módulos que la hípica ha contratado.

La motivación es que Hipica es una plataforma multi-tenant. Cada hípica tiene su propia identidad visual y su propio conjunto de módulos contratados, y el menú debe reflejar ambas cosas sin necesidad de cambiar código.

---

## Flujo de Construcción del Menú

```mermaid
flowchart TD
    A[index.html se carga] --> B[Detecta cliente por subdominio]
    B --> C[Carga /branding/cliente/branding.json]
    C --> D[window.__APP_BRANDING__ = branding]
    D --> E[Vue monta MainLayout.vue]
    E --> F{¿Hay access token?}
    F -- No --> G[menú vacío / no se cargan features]
    F -- Sí --> H[fetchFeatures() → GET /api/v1/me/features]
    H --> I[features.value = [...] ref reactivo]
    I --> J[computed navigation = filterNavigation branding.navigation + features]
    J --> K[v-navigation-drawer renderiza los items filtrados]
```

---

## Detección del Cliente (Branding)

La detección ocurre en `index.html` antes de que Vue arranque, leyendo el subdominio de la URL:

| URL | Cliente detectado | Branding cargado |
|-----|-------------------|-----------------|
| `localhost` o `127.0.0.1` | `demo` | `public/branding/demo/branding.json` |
| `canvalls.hipica.com` | `canvalls` | `public/branding/canValls/branding.json` |
| `myhipica.hipica.com` | `myhipica` | `public/branding/myhipica/branding.json` |

La misma lógica de detección se replica en `MainLayout.vue` y `Login.vue` (funciones `detectClient()` locales) para construir URLs de imágenes.

El objeto de branding queda accesible globalmente como `window.__APP_BRANDING__` y se tipifica en `MainLayout.vue`.

---

## Estructura del fichero branding.json

```json
{
  "appName": "Hípica Abe Demo",
  "logo": "logo.png",
  "favicon": "favicon.ico",
  "loginImage": "login.png",
  "theme": {
    "primary": "#8b5e3c",
    "secondary": "#5c3d2e",
    "accent": "#c8a27a",
    "background": "#f4efe7",
    "surface": "#ffffff"
  },
  "navigation": [
    {
      "titleKey": "menu.horses",
      "icon": "mdi-horse",
      "route": "/horses",
      "feature": "HORSES"
    }
  ]
}
```

Campos de un item de navegación:

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `titleKey` | string | Sí | Clave i18n para el texto del item (`$t(titleKey)`) |
| `icon` | string | No | Nombre de icono Material Design Icons |
| `route` | string | Sí | Ruta Vue Router a la que apunta |
| `feature` | FeatureCode | No | Si se especifica, el item solo se muestra si la hípica tiene esa feature activa |

Si un item no tiene campo `feature`, aparece siempre (items de navegación libre como un dashboard general o ajustes de cuenta).

---

## Filtrado por Licencias

La función `filterNavigation` en `src/features/filter.ts` aplica el filtro sobre los items del branding:

```
branding.navigation  +  features.value  →  filterNavigation()  →  navigation (computed)
```

- Items **sin** campo `feature`: pasan siempre.
- Items **con** campo `feature`: solo pasan si ese código está incluido en `features.value`.

El resultado es un `computed` reactivo: si las features cambian (por ejemplo tras un refresh de sesión), el menú se actualiza automáticamente sin recargar la página.

---

## Branding Visual

Además del menú, el `branding.json` controla otros elementos visuales:

| Elemento | Campo en branding.json | Dónde se usa |
|----------|----------------------|--------------|
| Nombre en la barra superior | `appName` | `MainLayout.vue` — `v-app-bar-title` |
| Logo en la barra superior | `logo` | `MainLayout.vue` — `v-img` (URL: `/branding/<cliente>/logo.png`) |
| Imagen de fondo del login | `loginImage` | `Login.vue` — background-image en CSS |
| Favicon | `favicon` | `index.html` en tiempo de carga |
| Paleta de colores | `theme.*` | `index.html` aplica el tema a Vuetify antes de montar Vue |

---

## Componentes Involucrados

| Archivo | Responsabilidad |
|---------|----------------|
| `hipica-frontend/public/branding/<cliente>/branding.json` | Configuración por cliente: identidad visual y estructura de navegación |
| `hipica-frontend/index.html` | Carga el branding.json del cliente detectado antes de arrancar Vue |
| `src/layouts/MainLayout.vue` | Lee `window.__APP_BRANDING__`, carga features al montar, construye el `computed navigation` y renderiza el drawer |
| `src/features/features.ts` | Estado global reactivo de features activas; `fetchFeatures()` llama al backend |
| `src/features/filter.ts` | Función `filterNavigation(navigation, features)` — lógica de filtrado pura |
| `src/types/api.ts` | Tipos `FeatureCode` y `NavItem` |
| `src/views/Login.vue` | Lee el branding para la imagen de fondo; llama a `fetchFeatures()` tras login exitoso |

---

## Decisiones Técnicas

| Decisión | Justificación |
|----------|--------------|
| Branding en ficheros JSON estáticos por cliente | No requiere base de datos para la personalización visual; se despliega con la build del frontend |
| Detección de cliente por subdominio | Permite servir la misma aplicación a múltiples hípicas desde un único dominio base |
| `window.__APP_BRANDING__` como punto de transferencia | El branding se carga en `index.html` (antes de Vue) para evitar el parpadeo de tema; Vue lo consume desde la variable global |
| Items de navegación definidos en el branding | El menú es completamente configurable por cliente sin tocar código; añadir un item es solo editar el JSON |
| Filtrado como función pura separada (`filter.ts`) | Facilita los tests unitarios y desacopla la lógica de filtrado del componente de layout |
| `computed` reactivo para el menú | La reactividad de Vue garantiza que el menú refleja siempre el estado actual de features sin lógica adicional de sincronización |
| Duplicación de `detectClient()` en Login y MainLayout | Limitación temporal: `index.html` no puede compartir funciones con el código Vue directamente; se acepta la duplicación por simplicidad |

---

## Limitaciones Conocidas

- La navegación directa por URL a una ruta que requiere una feature no activa no está bloqueada. El item no aparecerá en el menú, pero si el usuario navega manualmente a `/lessons` sin tener `LESSONS`, la ruta se cargará (si existe en el router). La protección a nivel de ruta no está implementada en esta versión.
- Añadir un nuevo cliente requiere crear manualmente su directorio en `public/branding/<cliente>/` con el `branding.json` correspondiente y hacer un nuevo build del frontend.
