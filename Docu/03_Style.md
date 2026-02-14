# Style - Paleta madera/cuero y ajustes de UI

## Resumen
En este cambio he aplicado la paleta de colores propuesta (madera y cuero) y adaptado la UI para usar componentes de Vuetify con esos colores. También se actualizó el `Login.vue` para usar componentes de Vuetify y se añadieron reglas CSS para forzar texto blanco en fondos oscuros.

## Archivos modificados
- `hipica-frontend/src/main.ts`
  - Añadida configuración de tema Vuetify `hipica` con la paleta:
    - Fondo principal: `#f4efe7`
    - Madera oscura: `#5c3d2e`
    - Madera media: `#8b5e3c`
    - Acento: `#c8a27a`
    - Texto: `#2b2b2b`
    - Hover botón: `#6e4a33`
  - Ajustado `on-primary` y `on-secondary` a blanco para asegurar contraste en fondos oscuros.

- `hipica-frontend/src/style.css`
  - Definidas variables CSS bajo `:root` para la paleta (`--hipica-bg`, `--hipica-wood`, etc.).
  - Aplicado `background-color` y `color` por defecto usando las variables.
  - Añadidos estilos reutilizables:
    - `.v-btn.hipica` — clase para botones que usan color `--hipica-wood` y cambio `--hipica-hover` al pasar el ratón.
    - `.hipica-card` — estilo ligero para tarjetas.
  - Añadidas reglas que fuerzan texto blanco (`color: #ffffff`) en elementos con tema oscuro (por ejemplo `.theme--dark`, `.v-card.theme--dark`, `.v-app-bar.theme--dark`) para garantizar legibilidad.

- `hipica-frontend/src/views/Login.vue`
  - Reescrito para usar componentes Vuetify: `v-card`, `v-text-field`, `v-btn`, `v-alert`, `v-container`, `v-row`, `v-col`.
  - Botón de envío usa la clase `hipica` para aplicar la paleta.
  - `LanguageSelector` integrado en la cabecera de la tarjeta.

## Motivo y beneficios
- Cohesión visual: la paleta madera/cuero encaja con la temática ecuestre.
- Accesibilidad: texto blanco asegurado en fondos oscuros para contraste suficiente.
- Reutilización: variables y clases permiten aplicar el estilo fácilmente en más componentes.

## Cómo probar localmente
1. Ir al frontend:

```bash
cd hipica-frontend
npm install    # si no está instalado
npm run dev
```

2. Abrir `http://localhost:5173` (por defecto) y revisar la pantalla de login.

## Nota
Se incluyeron cambios mínimos en otros archivos para integrar Vuetify (configuración en `vite.config.ts` y registro en `main.ts`).

---
Generado automáticamente por el flujo de integración de UI; archivo: `Docu/03_Style.md`.
