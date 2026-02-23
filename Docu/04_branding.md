# 04_Branding — Personalización dinámica (multi‑hípica)

## 🎯 Objetivo
Permitir que **una única build** del frontend se personalice por cliente (hípica) sin recompilar:
- Logo
- Favicon
- Nombre de la aplicación
- Colores del tema (Vuetify)
- Imagen de fondo del login (opcional)

La personalización se carga **en runtime** desde archivos estáticos por cliente.

---

## 🧠 Enfoque
No se usan `.env` ni builds separadas.
La app detecta el cliente por **subdominio** y carga su configuración:

```
https://can-vila.midominio.com  →  /public/branding/can-vila/*
https://demo.midominio.com      →  /public/branding/demo/*
localhost                        →  demo (fallback)
```

---

## 📁 Estructura de carpetas

```
public/
  branding/
    demo/
      branding.json
      logo.png
      favicon.ico
      login.jpg (opcional)

    can-vila/
      branding.json
      logo.png
      favicon.ico
      login.jpg (opcional)
```

Añadir un cliente nuevo = crear una carpeta nueva.

---

## 📄 Formato de `branding.json`

```json
{
  "appName": "Hípica Abe Demo",
  "logo": "logo.png",
  "favicon": "favicon.ico",
  "loginImage": "login.jpg",

  "theme": {
    "primary": "#5A3E2B",
    "secondary": "#2F2218",
    "accent": "#C89F6A",
    "background": "#000000",
    "surface": "#ffffff"
  }
}
```

- `appName` → título del navegador
- `logo` → logo mostrado en la app
- `favicon` → icono de pestaña
- `loginImage` → fondo del login (opcional)
- `theme` → sobrescribe colores base de Vuetify

---

## 🚀 Bootstrap en `index.html`

Antes de arrancar Vue, se carga el branding del cliente:

1. Detectar cliente por `hostname`
2. Cargar `/branding/{cliente}/branding.json`
3. Aplicar título y favicon
4. Inyectar dinámicamente `main.ts`

Esto garantiza que Vuetify se cree **ya con los colores correctos**.

---

## 🎨 Creación dinámica del tema (Vuetify)

`vuetify.ts` exporta una **factory** en lugar de una instancia fija:

```ts
export function createVuetifyInstance() {
  const branding = (window as any).__APP_BRANDING__ ?? {};
  const themeColors = branding.theme ?? {};

  return createVuetify({
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
            ...themeColors
          }
        }
      }
    }
  });
}
```

➡️ El tema nace ya personalizado (sin mutaciones posteriores).

---

## 🔌 Uso en `main.ts`

```ts
const vuetify = createVuetifyInstance();

const app = createApp(App);
app.use(router);
app.use(i18n);
app.use(vuetify);
app.mount("#app");
```

---

## 🖼️ Consumo del branding en Layout

El layout lee la configuración ya cargada:

```ts
const branding = (window as any).__APP_BRANDING__;
```

Y construye rutas a los assets:

```
/branding/{cliente}/logo.png
```

---

## 🔐 Ventajas de esta arquitectura

✔ Un solo despliegue para todos los clientes
✔ Cambios de branding sin tocar código
✔ Escalable a SaaS multi‑tenant
✔ Compatible con Docker/CDN
✔ Sin rebuilds
✔ Separación clara entre marca y funcionalidad

---

## 🧪 Forzar cliente en desarrollo (local)

En local (`localhost`) no hay subdominio, por lo que por defecto se carga `demo`.

Para probar otros clientes sin cambiar hosts ni recompilar, se permite un **override por query param**:

```
http://localhost:5173/?client=canValls
```

El `index.html` comprueba primero si existe `?client=` y, si está presente, lo usa en lugar de detectar por subdominio. En producción no se usa este parámetro y la detección sigue siendo automática por hostname.

**Ventajas**
- Cambiar de cliente en 1 clic (favoritos del navegador).
- No requiere reiniciar Vite.
- No afecta a producción.

## ➕ Posibles extensiones futuras

- Módulos habilitados por licencia
- Colores por modo oscuro
- Configuración funcional desde backend
- Plantillas visuales por cliente

---

## ✅ Resultado

La aplicación queda preparada para venderse como producto multi‑hípica con personalización inmediata mediante archivos estáticos.

