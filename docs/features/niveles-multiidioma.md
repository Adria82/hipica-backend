# Feature: Niveles de Equitacion Multiidioma

## Descripcion

Los niveles de equitacion soportan nombres en tres idiomas (`es`, `en`, `ca`) mediante una columna JSON en la tabla `level`. El nombre mostrado en cada vista se selecciona automaticamente segun el idioma activo del usuario, sin recargar datos.

Sustituye al sistema anterior de texto libre unico (`name: str`) documentado en `niveles-libres.md`.

---

## Motivacion

Con texto libre unico, cambiar de idioma en el frontend mostraba siempre el mismo nombre (el introducido al crear el nivel). Para que la interfaz sea coherente con el resto de traducciones, los niveles necesitan un nombre por cada locale soportado.

---

## Modelo de Datos

### Antes
```
Level
  id   : int (PK)
  name : str (unique, index)
```

### Ahora
```
Level
  id    : int (PK)
  names : JSON  -- {"es": "Principiante", "en": "Beginner", "ca": "Principiant"}
```

La columna `names` es un dict sin restriccion de unicidad (la unicidad se gestiona a nivel de negocio si se requiere).

---

## Migracion Alembic

Revision: `a1b2c3d4e5f6` — `level_name_to_names_json`

**Upgrade:**
1. Añade columna `names` (JSON, nullable)
2. Migra datos existentes: `names = json_build_object('es', name, 'en', name, 'ca', name)`
3. Hace `names` NOT NULL
4. Elimina columna `name` y su indice unico

**Downgrade:**
1. Restaura columna `name` con el valor `names->>'es'` como fallback
2. Elimina columna `names`

---

## Backend

### Schemas (`app/schemas/level.py`)

```python
class LevelBase(SQLModel):
    names: dict[str, str]  # {"es": ..., "en": ..., "ca": ...}

class LevelCreate(LevelBase): pass
class LevelUpdate(SQLModel):
    names: Optional[dict[str, str]] = None
class LevelRead(LevelBase):
    id: int
```

### Endpoints (`app/api/v1/endpoints/level.py`)

- `POST /levels/` — crea nivel con `names` dict
- `PUT /levels/{id}` — actualiza `names` dict; sin comprobacion de unicidad por nombre
- `GET /levels/` y `GET /levels/{id}` — devuelven `LevelRead` con `names`
- `DELETE /levels/{id}` — igual que antes; rechaza si hay caballos asociados

### HorseRead con niveles localizados

`HorseRead` expone dos campos relacionados con niveles:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `levels` | `List[str]` | Nombres localizados segun `Accept-Language` de la request |
| `level_ids` | `List[int]` | IDs de los niveles asignados (para formularios) |

La funcion `_horse_to_read(horse, session, lang)` en `horse.py` resuelve el nombre con fallback:
```
names.get(lang) → names.get("es") → names.get("ca") → str(level.id)
```

`HorseUpdate.levels` y `PUT /{id}/levels` aceptan **lista de IDs** (antes aceptaban nombres de texto).

---

## Frontend

### Tipo `Level` (`src/types/api.ts`)
```typescript
export type Level = {
  id: number;
  names: { es: string; en: string; ca: string };
};
```

### Tipo `Horse` — campo nuevo
```typescript
level_ids: number[];  // IDs para formularios de edicion
```

### `Levels.vue`

El dialogo de crear/editar muestra tres campos de texto (uno por locale):
- Nombre en español
- Nombre en inglés
- Nom en català

La tabla muestra el nombre en el locale activo mediante la funcion `localeName(level)`.

### `Horses.vue` — reactividad al cambio de locale

Los chips de niveles usan `level_ids` (IDs que no cambian) y calculan el nombre con:

```typescript
function levelName(id: number): string {
  const level = levels.value.find((l) => l.id === id);
  // fallback: lang → es → ca → en
}
```

Al cambiar de idioma, Vue recomputa los chips automaticamente sin recargar la vista.

---

## Seed (`app/seed.py`)

Los niveles iniciales incluyen traducciones reales:

```python
{"es": "Principiante", "en": "Beginner",    "ca": "Principiant"}
{"es": "Iniciado",     "en": "Novice",       "ca": "Iniciat"}
{"es": "Intermedio",   "en": "Intermediate", "ca": "Intermedi"}
{"es": "Avanzado",     "en": "Advanced",     "ca": "Avançat"}
{"es": "Experto",      "en": "Expert",       "ca": "Expert"}
```
