# Feature: Nombre de Hipica en Tablas de Caballos, Boxes y Clientes

## Descripcion

Las vistas de Caballos, Boxes y Clientes muestran ahora el nombre legible de la hipica a la que pertenece cada registro. Anteriormente solo se almacenaba y mostraba el `stable_id` numerico, lo que obligaba al usuario a memorizar los identificadores.

## Motivacion

El `app_admin` gestiona multiples hipicas y necesita distinguir rapidamente a que cuadra pertenece cada entidad cuando navega por las listas. Mostrar el nombre de la hipica elimina esa ambiguedad sin anadir llamadas adicionales desde el frontend.

## Implementacion

### Backend — schemas de respuesta

Los schemas `HorseRead`, `BoxRead` y `ClientRead` incluyen el campo adicional:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `stable_name` | `str \| null` | Nombre de la hipica. `null` si no se encuentra el registro. |

### Backend — funciones convertidoras

Cada endpoint de listado/detalle delega la conversion ORM → schema en una funcion interna (`_horse_to_read`, `_box_to_read`, `_client_to_read`). Estas funciones realizan un lookup adicional:

```
session.get(Stable, entity.stable_id) → stable.name
```

El campo se incluye aunque el usuario no sea `app_admin`; simplemente tendra el nombre de su propia hipica en todos los registros.

### Frontend — columna "Hipica"

Las tablas en `Horses.vue`, `Boxes.vue` y `Clients.vue` incluyen una columna adicional que muestra `stable_name`. La columna es visible para todos los roles pero resulta especialmente util para `app_admin`.

## Consideraciones

- El lookup de nombre se realiza en cada conversion individual, no en bulk. Para listados grandes esto supone N consultas adicionales. Si el volumen crece, considerar un JOIN explicito o un cache de nombres de hipica.
- Si la hipica asociada se elimina de BD (caso improbable por integridad referencial), `stable_name` devuelve `null`.
- No hay migracion de datos; el campo es calculado en tiempo de respuesta, no persistido.
