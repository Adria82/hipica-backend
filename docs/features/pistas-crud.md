# Feature: Gestión de Pistas (Tracks)

## Descripción

El módulo de pistas permite gestionar las instalaciones físicas (pistas, rutas) donde se celebran las clases de equitación. Sigue el mismo patrón CRUD que la vista de Boxes. Las pistas se asignan a clases en el momento de crearlas o editarlas, y aparecen en el calendario y en los informes.

## Flujo de Usuario

1. El usuario autenticado (rol `monitor`, `stable_admin` o `app_admin`) accede a `/tracks` desde la sección **Operativa** del menú lateral (visible cuando el feature flag `LESSONS` está activo).
2. La vista carga la lista de pistas mediante `GET /api/v1/tracks`.
3. Si el rol es `app_admin`, se carga también la lista de hípicas (`GET /api/v1/stables`).
4. El usuario puede filtrar la lista mediante el campo de búsqueda por nombre.
5. Al pulsar el botón "Nueva pista" (visible solo para `canManage`), se abre el diálogo de creación.
6. Al hacer clic en una fila de la tabla, se abre el diálogo de edición con los datos de la pista seleccionada.
7. Desde el diálogo de edición, el usuario puede eliminar la pista; se muestra un segundo diálogo de confirmación antes de ejecutar el borrado.
8. El resultado de cualquier operación (guardar, eliminar) se notifica mediante un `v-snackbar`.
9. El botón de exportación genera un fichero `.xlsx` con los datos visibles en la tabla (respeta el filtro de búsqueda activo).

## Modelo de Datos

```
Track
  id        : int (PK, autoincrement)
  name      : str
  stable_id : int (FK → stable.id, index)
  is_active : bool (default: true)
```

La entidad pertenece a una hípica (`stable_id`). El campo `is_active` permite desactivar una pista sin eliminarla; las pistas inactivas no aparecen en los selectores de creación de clases.

## Endpoints

| Método | Ruta | Roles | Descripción |
|--------|------|-------|-------------|
| `GET` | `/api/v1/tracks` | monitor, stable_admin, app_admin | Listar pistas. `app_admin` ve todas las hípicas; el resto solo las de su cuadra. |
| `POST` | `/api/v1/tracks/` | stable_admin, app_admin | Crear pista. El `stable_id` se fuerza al de la cuadra del usuario, excepto para `app_admin`. |
| `GET` | `/api/v1/tracks/{track_id}` | monitor, stable_admin, app_admin | Obtener pista por ID. Devuelve 403 si no pertenece a la cuadra del usuario. |
| `PUT` | `/api/v1/tracks/{track_id}` | stable_admin, app_admin | Actualizar nombre, estado activo/inactivo u otros campos. |
| `DELETE` | `/api/v1/tracks/{track_id}` | stable_admin, app_admin | Eliminar pista. Devuelve 404 si no existe, 403 si pertenece a otra cuadra. |

Archivo de implementación: `app/api/v1/endpoints/track.py`  
Schemas: `app/schemas/track.py` (`TrackCreate`, `TrackRead`, `TrackUpdate`)

## Componente Frontend

Archivo: `hipica-frontend/src/views/Tracks.vue`

| Elemento | Detalle |
|----------|---------|
| Tabla | `v-data-table` con columnas: ID, Nombre, Activo (icono), Hípica |
| Búsqueda | Campo de texto con filtrado local en tiempo real (`filteredTracks`) |
| Estado activo | Icono verde (`mdi-check-circle`) o rojo (`mdi-close-circle`) |
| Exportación | Botón `mdi-file-excel` que genera `.xlsx` vía la librería `xlsx` |
| Diálogo crear/editar | `v-dialog` con campos: nombre, estado activo (`v-switch`), selector de hípica (solo `app_admin`) |
| Confirmación eliminar | Segundo diálogo independiente antes de ejecutar el `DELETE` |
| Control de acceso | El botón "Nueva pista" y la opción de eliminar solo aparecen si `canManage` |

### Opciones de formulario

- **Nombre** — texto libre, requerido.
- **Activo** — `v-switch`, disponible solo en modo edición. Las nuevas pistas se crean activas por defecto.
- **Hípica** — `v-select` con las hípicas cargadas de `GET /api/v1/stables`. Visible y editable únicamente para `app_admin`.

## Datos del Seed

El script `app/seed.py` crea tres pistas para cada hípica de ejemplo:

| Nombre | Descripción |
|--------|-------------|
| Pista 1 | Pista de trabajo principal |
| Pista 2 | Pista secundaria |
| Ruta | Indica salida de excursión exterior |

## Integración con Otras Features

- **Clases (Lessons):** el campo `track_id` de `Lesson` referencia a `Track`. El selector de pista en el diálogo de clases muestra solo las pistas activas de la hípica.
- **Informes (Reports):** el informe agrega horas y número de clases por pista (`track_hours`). Desde la tabla de pistas del informe es posible hacer drill-down para ver el detalle de clases.
- **Calendario:** los chips de clase en la vista de calendario muestran el nombre de la pista entre paréntesis cuando está asignada.

## Consideraciones

- La eliminación de una pista no está protegida a nivel de aplicación frente a clases existentes que la referencian; la integridad referencial depende de la base de datos.
- El endpoint `GET /tracks` para `app_admin` devuelve pistas de todas las hípicas sin paginación. Si el volumen crece, puede ser necesario añadir filtrado por `stable_id` como parámetro de consulta.
