Genera el scaffolding completo y opinionado de una nueva vista Vue 3 para el proyecto Hipica.

## Entrada esperada del usuario

El usuario debe indicar:
- **Entidad/Feature**: qué gestiona la vista (ej. "horses", "lessons")
- **Ruta**: path de la vista (ej. `/horses`)
- **Funcionalidad**: listar, crear, editar, eliminar, o combinación
- **Roles que pueden acceder**: quién puede ver esta vista
- **Endpoint(s) de backend**: qué endpoints consume

Si falta algún dato, pregúntalo antes de generar.

## Pasos a ejecutar

### 1. Tipos TypeScript — `src/types/api.ts`

Añadir las interfaces que correspondan al response_model del backend:

```typescript
// Verificar coherencia con el schema Pydantic:
// Python int → TypeScript number
// Python str → TypeScript string
// Python bool → TypeScript boolean
// Python datetime → TypeScript string (ISO 8601)
// Python Optional[X] → TypeScript X | null
// Python list[X] → TypeScript X[]

export interface <Entity>Read {
  id: number
  // ... campos del response_model
  stable_id: number
  is_active: boolean
}

export interface <Entity>Create {
  // ... campos del schema Create (sin id, sin stable_id)
}
```

### 2. Traducciones — `src/i18n/messages.ts`

Añadir las claves para los **tres idiomas** (ca/es/en):

```typescript
// Estructura de claves a añadir en cada idioma:
<entity>: {
  title: '...',
  create: '...',
  edit: '...',
  delete: '...',
  // campos del formulario
  name: '...',
  // mensajes de feedback
  created: '...',
  updated: '...',
  deleted: '...',
  confirmDelete: '...',
}
```

### 3. Vista — `src/views/<Entity>.vue`

Estructura base con Composition API + Vuetify:

```vue
<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-h5 mb-4">{{ $t('<entity>.title') }}</h1>
      </v-col>
    </v-row>

    <!-- Lista con v-data-table si es listado -->
    <v-data-table
      :headers="headers"
      :items="items"
      :loading="loading"
    />

    <!-- FAB o botón de creación si tiene permisos -->
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/api/http'
import type { <Entity>Read } from '@/types/api'

const { t } = useI18n()
const items = ref<<Entity>Read[]>([])
const loading = ref(false)

const headers = [
  // columnas con t() para i18n
]

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await http.get<<Entity>Read[]>('/api/v1/<entities>/')
    items.value = data
  } finally {
    loading.value = false
  }
})
</script>
```

### 4. Ruta — `src/router/index.ts`

Añadir con `meta.requiresAuth: true` **siempre**:

```typescript
{
  path: '/<entities>',
  name: '<entities>',
  component: () => import('@/views/<Entity>.vue'),
  meta: { requiresAuth: true }
}
```

## Guardrails de Verificación

Antes de entregar el código generado, verificar:

- [ ] ¿Los tipos TypeScript coinciden con el `response_model` del backend?
- [ ] ¿Todos los textos usan `$t('key')` — sin texto hardcodeado?
- [ ] ¿Las claves i18n están añadidas en los tres idiomas (ca/es/en)?
- [ ] ¿HTTP va por `src/api/http.ts` — sin instancias axios directas?
- [ ] ¿Los tipos están en `src/types/api.ts`?
- [ ] ¿La ruta tiene `meta: { requiresAuth: true }`?
- [ ] ¿Se muestran estados de loading?
- [ ] ¿Si hay feature flags relevantes, se consultan?

## Output Final

Entregar en este orden:
1. Adiciones a `src/types/api.ts`
2. Adiciones a `src/i18n/messages.ts` (los tres idiomas juntos)
3. `src/views/<Entity>.vue` — vista completa
4. Diff de `src/router/index.ts` — líneas a añadir

## Después de generar

Recordar al usuario:
- Si la vista necesita un endpoint nuevo → usar `/new-endpoint` primero
- Usar `code-doc-agent` si hay lógica compleja en el componente
