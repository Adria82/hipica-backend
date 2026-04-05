# Feature: Nombres Completos (apellidos y DNI en User)

## Descripcion

El modelo `User` incorpora los campos `apellidos` y `dni` para completar la identificacion de los usuarios de la aplicacion. Estos campos se muestran y editan en la vista de perfil propio y en la gestion de usuarios por parte de los administradores, y aparecen concatenados en todos los desplegables de seleccion de usuarios de la aplicacion.

## Motivacion

Hasta esta version, el campo `name` del usuario contenia el nombre completo ("Juan Garcia"). Esto dificultaba el ordenado alfabetico por apellido y la identificacion inequivoca de usuarios con el mismo nombre. Con la separacion en `name` y `apellidos` se gana precision en la identificacion y se puede mostrar el nombre completo ordenado correctamente.

El campo `dni` permite la identificacion oficial del usuario, necesaria para contratos, fichas de alumno o cualquier documento administrativo de la hipica.

## Cambios en el Modelo

**Archivo:** `app/models/user.py`

```python
class User(SQLModel, table=True):
    name: str           # Solo el nombre de pila (ej. "Juan")
    apellidos: Optional[str]  # Apellidos (ej. "Garcia Lopez")
    dni: Optional[str]        # DNI/NIF (ej. "12345678A")
    ...
```

**Migracion:** `alembic/versions/b2c3d4e5f6a7_add_surnames_and_dni_to_user.py`

```python
def upgrade():
    op.add_column("user", sa.Column("apellidos", sa.String(), nullable=True))
    op.add_column("user", sa.Column("dni", sa.String(), nullable=True))
```

## Propagacion a Endpoints

### GET y PUT /api/v1/me/profile

Los campos `apellidos` y `dni` se incluyen en la respuesta y en el payload de actualizacion:

```json
{
  "name": "Juan",
  "apellidos": "Garcia",
  "dni": "12345678A",
  "email": "juan@hipica.com",
  "phone": "600100200"
}
```

### GET /api/v1/users y GET /api/v1/users/{id}

El schema `UserRead` incluye `apellidos` y `dni`.

### Informes (`/api/v1/reports/lessons`)

Los schemas `InstructorHours`, `HelperHours` y `StudentClasses` incluyen el campo `apellidos` para mostrar el nombre completo en tablas y graficos.

## Nombre Completo en Listas Desplegables

Todos los desplegables de seleccion de usuarios muestran "Nombre Apellidos":

**Lessons.vue:**
- Selector de instructor → `instructorOptions` con propiedad `fullName`
- Selector de ayudante → `helperOptions` con propiedad `fullName`
- Selector de alumnos → `studentOptions` con propiedad `fullName`
- Fila de asignacion caballo-alumno → muestra `fullName` del alumno

**Reports.vue:**
- Tablas de horas por instructor, ayudante y clases por alumno → columna `fullName`
- Grafico de barras de monitores/ayudantes → etiquetas con nombre completo
- Selector de filtro por dia de la semana → opciones con nombre completo para tipos `student`, `instructor` y `helper`

**Helper reutilizable:**

```typescript
// Lessons.vue
function fullName(user: { name: string; apellidos?: string | null }): string {
  return user.apellidos ? `${user.name} ${user.apellidos}` : user.name;
}

// Reports.vue
function userFullName(u: { name: string; apellidos?: string | null }): string {
  return u.apellidos ? `${u.name} ${u.apellidos}` : u.name;
}
```

Ambas funciones son defensivas: si `apellidos` es `null` o `undefined`, devuelven solo el nombre.

## ClientProfile y apellidos

El campo `apellidos` reside unicamente en `User`. La tabla `clientprofile` no tiene campo `apellidos` propio (fue eliminado en la migracion `0b4c25361aa2`). Anteriormente existia una funcion `_sync_client_surname` que sincronizaba ambos campos; al unificarlos en `User` esta funcion fue eliminada.

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `app/models/user.py` | Campos `apellidos` y `dni` |
| `app/schemas/user.py` | `UserRead` incluye `apellidos` y `dni` |
| `app/api/v1/endpoints/me.py` | `ProfileUpdate` y respuestas incluyen `apellidos`, `dni`, `phone` |
| `app/api/v1/endpoints/reports.py` | Schemas de informe incluyen `apellidos` |
| `app/models/client_profile.py` | Eliminado campo `apellidos` |
| `app/schemas/profile.py` | `ClientProfileRead/Update` sin `apellidos` |
| `app/seed.py` | Datos de ejemplo con `name` y `apellidos` separados |
| `alembic/versions/b2c3d4e5f6a7_*` | Migracion: columnas en `user` |
| `alembic/versions/0b4c25361aa2_*` | Migracion: eliminar `apellidos` de `clientprofile` |
| `hipica-frontend/src/types/api.ts` | `UserProfile` y `UserRead` con `apellidos` y `dni` |
| `hipica-frontend/src/views/Lessons.vue` | Desplegables con nombre completo |
| `hipica-frontend/src/views/Reports.vue` | Tablas y graficos con nombre completo |
| `hipica-frontend/src/i18n/messages.ts` | Claves `profile.apellidos`, `profile.dni` en es/ca/en |
