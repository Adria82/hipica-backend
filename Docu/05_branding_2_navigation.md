# 05_Branding2 — Navegación dinámica por cliente

## 🎯 Objetivo
Permitir que **cada hípica configure su propio menú lateral** sin modificar código ni recompilar la aplicación.

La navegación deja de estar "hardcodeada" en el frontend y pasa a formar parte de la configuración de cliente (`branding.json`).

---

## 🧠 Principio clave
El frontend define **qué funcionalidades existen** (router).
El branding decide **cuáles se muestran**.

```
Router → Define las rutas reales de la aplicación
Branding → Decide qué opciones ve cada cliente
```

Esto permite personalización sin comprometer seguridad.

---

## 📁 Configuración en `branding.json`

Cada cliente define su menú en su propio archivo:

```json
{
  "navigation": [
    {
      "titleKey": "menu.horses",
      "icon": "mdi-horse",
      "route": "/horses"
    }
  ]
}
```

### Campos

| Campo | Descripción |
|------|-------------|
`titleKey` | Clave de traducción (usa i18n, nunca texto literal)
`icon` | Icono Material Design Icons
`route` | Ruta Vue Router existente

---

## 🌍 Soporte multilenguaje

El texto visible NO se define en branding.
Se traduce mediante `vue-i18n`.

### `messages.ts`

```ts
menu: {
  horses: "Caballos"
}
```

Catalán:

```ts
menu: {
  horses: "Cavalls"
}
```

Inglés:

```ts
menu: {
  horses: "Horses"
}
```

El branding solo referencia:

```
"titleKey": "menu.horses"
```

---

## 🔄 Flujo de renderizado

1️⃣ `index.html` carga el branding del cliente.
2️⃣ Vue arranca con esa configuración disponible en `window.__APP_BRANDING__`.
3️⃣ `MainLayout` lee `branding.navigation`.
4️⃣ Se generan los items del menú dinámicamente.
5️⃣ `vue-i18n` traduce los títulos según idioma activo.

---

## 📐 Responsabilidades separadas

| Capa | Responsabilidad |
|------|-----------------|
Router | Define qué rutas existen realmente
Branding | Decide qué rutas se muestran
Backend (futuro) | Decide qué rutas están licenciadas

---

## ⚠️ Seguridad

Ocultar un menú NO es control de acceso.
La seguridad siempre debe estar en backend.

Aunque un usuario escriba manualmente:

```
/horses
```

El backend debe validar permisos.

---

## 🚀 Ventajas del enfoque

✔ Personalización por cliente sin despliegues nuevos
✔ Misma aplicación para todos los tenants
✔ Compatible con SaaS multi‑hípica
✔ Multilenguaje automático
✔ Fácil añadir/quitar módulos
✔ Preparado para licenciamiento futuro

---

## ➕ Posibles evoluciones

- Filtrar navegación según licencia backend
- Agrupar opciones en secciones (`groups`)
- Configurar orden o visibilidad avanzada
- Activar módulos por rol de usuario

---

## ✅ Resultado

La navegación deja de ser estática y pasa a ser **configuración dinámica del cliente**, alineada con el modelo multi‑tenant definido en el sistema de branding.

