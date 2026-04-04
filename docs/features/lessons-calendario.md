# Feature: Lessons con Calendario Semanal y Tracks

## Descripcion

La feature de Lessons (clases de equitacion) se expande con nuevos campos en el modelo, una nueva entidad `Track` (pista), una vista de calendario semanal en el frontend y un modulo de informes agregados.

## Nuevos Campos en `Lesson`

| Campo | Tipo | Default | Descripcion |
|-------|------|---------|-------------|
| `end_time` | `datetime \| null` | `null` | Hora de fin de la clase. Si no se indica, se asume 1 hora de duracion en los calculos de informes. |
| `helper_id` | `int \| null` | `null` | FK a `user.id`. Monitor ayudante (secundario) de la clase. |
| `track_id` | `int \| null` | `null` | FK a `track.id`. Pista donde se celebra la clase. |
| `description` | `str \| null` | `null` | Notas adicionales sobre la clase. |

## Nueva Entidad: Track (Pista)

Representa una pista fisica dentro de una hipica.

```
Track
  id        : int (PK)
  name      : str
  stable_id : int (FK → stable.id, index)
  is_active : bool (default: true)
```

El CRUD completo se expone bajo `/api/v1/tracks`. Ver `docs/api/tracks.md` para detalle de endpoints.

## Schema `LessonRead` Desnormalizado

La respuesta de los endpoints de Lesson incluye datos resueltos para evitar multiples llamadas desde el frontend:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `instructor_email` | `str` | Email del instructor principal |
| `helper_email` | `str \| null` | Email del ayudante (si existe) |
| `track_name` | `str \| null` | Nombre de la pista (si asignada) |
| `horse_names` | `list[str]` | Nombres de los caballos asignados |
| `client_names` | `list[str]` | Nombres de los alumnos participantes |

## Frontend: Calendario (`Lessons.vue`)

La vista adopta un calendario con dos modos de visualizacion intercambiables mediante un toggle:

### Toggle semana / mes

Boton `v-btn-toggle` en el header derecho con opciones `week` y `month`. El estado se guarda en `viewMode` (ref).

### Vista semanal

- **Navegacion:** botones "Semana anterior" / "Hoy" / "Semana siguiente".
- **Grid semanal:** 7 columnas (lun–dom). El dia actual se resalta.
- **Chips de clase:** hora de inicio, pista (si existe), email instructor.
- **Crear clase:** click en celda vacia abre el dialogo con la fecha preseleccionada.

### Vista mensual

- **Navegacion:** botones "Mes anterior" / "Hoy" / "Mes siguiente" (los mismos botones del centro cambian dinamicamente segun `viewMode`).
- **Grid mensual:** `month-grid` con `grid-template-columns: repeat(7, 1fr)`. Incluye dias del mes anterior/siguiente para completar filas de 7; esos dias se renderizan con `opacity: 0.4`.
- **Cabecera:** dias de la semana abreviados (lun, mar, ...) derivados de una semana de referencia con `toLocaleDateString`.
- **Chips de clase:** identicos a la vista semanal.

Computed relevantes:
- `monthDays`: array de `{ iso, dayNum, isToday, isCurrentMonth }` con todos los dias del grid mensual.
- `monthWeekHeaders`: array con los 7 nombres abreviados de dia de la semana (Lun–Dom).

### Dialogo de creacion/edicion

| Campo | Control | Notas |
|-------|---------|-------|
| **Hipica** | `v-select` | Solo visible para `app_admin`. Requerido al crear. |
| Fecha y hora inicio | `datetime-local` | Requerido |
| Fecha y hora fin | `datetime-local` | Opcional |
| Instructor | `v-select` | Usuarios de la hipica |
| Ayudante | `v-select` | Usuarios + opcion limpia |
| Pista | `v-select` | Tracks activos + opcion limpia |
| Caballos | `v-select` multiple | Chips |
| Alumnos | `v-select` multiple | Chips |
| Descripcion | `v-textarea` | Notas adicionales |

El campo **Hipica** es necesario porque `app_admin` no tiene `stable_id` propio. Para otros roles, el backend fuerza `stable_id = current_user.stable_id` y el campo no se muestra.

## Frontend: Informes (`Reports.vue`)

Vista nueva en el area de Administracion. Consume `GET /api/v1/reports/lessons` y presenta los resultados en cuatro tablas:

| Tabla | Datos mostrados |
|-------|----------------|
| Horas de instructor | Email + horas impartidas, ordenado desc |
| Horas de ayudante | Email + horas como ayudante, ordenado desc |
| Clases de alumnos | Nombre de cliente + numero de clases, ordenado desc |
| Horas de caballos | Nombre de caballo + horas trabajadas, ordenado desc |

El usuario selecciona un rango de fechas (`from_date` / `to_date`) y pulsa "Buscar" para cargar el informe. Si no se indican fechas se devuelven todas las clases de la hipica.

### Acceso a la vista de informes

- Ruta: `/reports`
- Visible solo para `app_admin` en el menu lateral (`ADMIN_ITEMS` de `MainLayout.vue`).
- La ruta tiene `meta: { requiresAuth: true }`.

## Flujo de Datos — Crear Clase

```mermaid
sequenceDiagram
    participant Monitor
    participant Lessons.vue
    participant API
    participant DB

    Monitor->>Lessons.vue: Click en dia del calendario
    Lessons.vue->>Lessons.vue: openCreateDialog(fecha)
    Monitor->>Lessons.vue: Rellena formulario y guarda
    Lessons.vue->>API: POST /api/v1/lessons/ { date_time, end_time, instructor_id, helper_id, track_id, horse_ids, student_ids, description, stable_id? }
    API->>DB: INSERT lesson + LessonHorseLink + LessonUserLink
    DB-->>API: Lesson creada
    API-->>Lessons.vue: LessonRead desnormalizado
    Lessons.vue->>Lessons.vue: Refresca lista y muestra chip en calendario
```

## Consideraciones

- La duracion de una clase se calcula como `end_time - date_time`. Si `end_time` es `null`, los informes asumen 1 hora por defecto.
- El `instructor_id` se puede especificar libremente en el body (no se fuerza al usuario autenticado), lo que permite que un `stable_admin` asigne clases a otros monitores.
- `track_id` se valida por integridad referencial en BD; el endpoint no comprueba que la pista pertenezca a la misma hipica que la clase (pendiente de reforzar).
- Los informes filtran por `stable_id` del usuario autenticado, excepto `app_admin` que ve datos de todas las hipicas.
