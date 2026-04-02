# API: Me

Base URL: `/api/v1/me`

Endpoints relacionados con el usuario autenticado. Permiten al frontend obtener informacion de contexto del usuario actual, como las funcionalidades activas para su hipica.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| GET | `/features` | Listar funcionalidades activas de la hipica del usuario | Cualquier usuario autenticado |

---

## Detalle de Endpoints

### GET /api/v1/me/features

Devuelve la lista de codigos de funcionalidad (`FeatureCode`) activados para la hipica del usuario autenticado.

El flujo interno es:
1. Se obtiene el usuario desde el JWT.
2. Se identifica su `stable_id`.
3. Se consulta la tabla `StableFeature` para esa hipica.
4. Se devuelve la lista de codigos de funcionalidad activos.

**Caso especial:** Si el usuario es `app_admin` y no pertenece a ninguna hipica (`stable_id` es `null`), se devuelven **todas** las funcionalidades disponibles en el sistema.

**Autenticacion requerida:** Si. Token Bearer en la cabecera `Authorization`.

**Rol requerido:** Cualquier usuario autenticado (no hay restriccion de rol adicional).

**Response 200:**
```json
{
  "features": ["HORSES", "CLIENTS", "LESSONS"]
}
```

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| features | array[string] | Lista de codigos de funcionalidad activos para la hipica |

**Ejemplo — usuario app_admin sin hipica asignada (acceso total):**
```json
{
  "features": ["HORSES", "CLIENTS", "LESSONS", "LEVELS", "USERS"]
}
```

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente, invalido o expirado |

---

## Notas de Uso

Este endpoint es el mecanismo principal por el que el frontend decide que secciones del menu lateral mostrar. Se consulta tras el login y se almacena en el store reactivo de features (`src/features/features.ts`).

El catalogo de codigos posibles (`FeatureCode`) esta definido en `app/models/feature.py`.
