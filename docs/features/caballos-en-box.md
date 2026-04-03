# Feature: Caballos Asignados en el Dialogo de Box

## Descripcion

Al abrir el dialogo de edicion de un box en la vista Boxes, se muestran los nombres de los caballos actualmente asignados a ese box, en forma de chips, entre el campo de capacidad y el switch de estado activo.

---

## Backend

### Schema `BoxRead` (`app/schemas/box.py`)

Se añadio el campo `horse_names`:

```python
class BoxRead(SQLModel):
    id: int
    name: str
    capacity: int
    stable_id: int
    stable_name: Optional[str] = None
    is_active: bool
    horses_count: int
    horse_names: list[str] = []  # Nombres de los caballos asignados
```

### Endpoint (`app/api/v1/endpoints/box.py`)

La funcion `_box_to_read` calcula `horse_names` a partir de la relacion ORM `box.horses`:

```python
horse_names=[h.name for h in box.horses]
```

No requiere consultas adicionales; la relacion ya esta cargada al acceder a `box.horses` (que se usa tambien para `horses_count`).

---

## Frontend

### Tipo `Box` (`src/types/api.ts`)

```typescript
export type Box = {
  ...
  horses_count: number;
  horse_names: string[];
};
```

### `Boxes.vue`

- Se añade el ref `editingHorseNames` que se rellena en `openEditDialog`:
  ```typescript
  editingHorseNames.value = box.horse_names ?? [];
  ```
- En el dialogo, entre capacidad y el switch activo, aparece la seccion de chips:
  ```html
  <v-col v-if="editingId && editingHorseNames.length" cols="12">
    <div class="text-caption ...">{{ t('boxes.dialog.assignedHorses') }}</div>
    <v-chip v-for="horseName in editingHorseNames" ...>{{ horseName }}</v-chip>
  </v-col>
  ```
- La seccion es invisible al crear un box nuevo y cuando el box no tiene caballos.

---

## Claves i18n

| Clave | es | ca | en |
|-------|----|----|-----|
| `boxes.dialog.assignedHorses` | Caballos en este box | Cavalls en aquest box | Horses in this box |
