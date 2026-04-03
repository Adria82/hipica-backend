# Feature: Niveles de Equitacion como Texto Libre

## Descripcion

Los niveles de equitacion dejaron de estar restringidos a un enum fijo (`principiante`, `iniciado`, `experto`) para pasar a ser cadenas de texto libres gestionadas por el administrador. Esto permite que cada instalacion defina su propia nomenclatura de niveles sin requerir cambios en el codigo.

## Motivacion del Cambio

El enum anterior obligaba a que todas las hipicas usasen la misma terminologia. En la practica cada cliente tiene su propia escala (p. ej. "Nivel 1 / Nivel 2 / Nivel 3", o "Basico / Avanzado / Competicion"). Liberar el campo elimina esa rigidez.

## Cambios en el Backend

### Modelo `Level`

- Se elimina la referencia al enum `NivelEquitacion`.
- `Level.name` es ahora un `str` simple con restriccion `unique=True`.

```
Level
  id   : int (PK)
  name : str (unique, index)
```

### Endpoint nuevo: `PUT /api/v1/levels/{level_id}`

Permite renombrar un nivel existente. Comprueba unicidad del nuevo nombre excluyendo el propio registro.

| Campo | Detalle |
|-------|---------|
| Metodo | `PUT` |
| Path | `/api/v1/levels/{level_id}` |
| Rol requerido | `app_admin` |
| Body | `{ "name": "Nuevo nombre" }` |
| Response 200 | `{ "id": 1, "name": "Nuevo nombre" }` |
| Error 400 | Ya existe otro nivel con ese nombre |
| Error 404 | Nivel no encontrado |

## Cambios en el Frontend

### `Levels.vue` — reescritura completa

La vista adopta el mismo patron de interaccion que `Horses.vue`:

- **Crear nivel:** campo de texto libre + boton "Crear". Ya no hay selector de enum.
- **Editar nivel:** click en una fila de la tabla abre un dialogo de edicion/eliminacion.
- **Eliminar nivel:** desde el mismo dialogo. El backend rechaza la eliminacion si el nivel tiene caballos asociados.

## Consideraciones

- La unicidad del nombre se valida en backend; el frontend muestra el mensaje de error devuelto por la API.
- No hay migracion de datos previa: los registros existentes en `level` ya tenian `name` como string; solo se elimina la validacion de enum a nivel de aplicacion.
- El endpoint `GET /api/v1/levels/` no requiere autenticacion y sigue funcionando igual.
