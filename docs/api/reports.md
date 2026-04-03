# API: Reports

Base URL: `/api/v1/reports`

Endpoints de informes agregados. Proporcionan datos estadisticos sobre la actividad de la hipica en un rango de fechas.

---

## Resumen de Endpoints

| Metodo | Path | Descripcion | Rol requerido |
|--------|------|-------------|---------------|
| GET | `/lessons` | Informe agregado de clases por rango de fechas | `monitor`, `stable_admin`, `app_admin` |

---

## Detalle de Endpoints

### GET /api/v1/reports/lessons

Devuelve un informe agregado de la actividad de clases en el rango de fechas indicado. Incluye horas de instructores y ayudantes, numero de clases por alumno y horas de trabajo por caballo.

Si no se indican fechas, el informe incluye todas las clases registradas de la hipica.

**Rol requerido:** `monitor`, `stable_admin`, `app_admin`

**Multi-tenant:** Los usuarios con rol `monitor` o `stable_admin` ven solo datos de su hipica. El `app_admin` ve datos de todas las hipicas.

**Query Parameters:**

| Parametro | Tipo | Requerido | Descripcion |
|-----------|------|-----------|-------------|
| `from_date` | date (`YYYY-MM-DD`) | No | Fecha de inicio del rango (inclusive) |
| `to_date` | date (`YYYY-MM-DD`) | No | Fecha de fin del rango (inclusive) |

**Response 200:**
```json
{
  "from_date": "2026-01-01",
  "to_date": "2026-03-31",
  "instructor_hours": [
    { "user_id": 2, "email": "monitor@hipica.com", "hours": 24.5 }
  ],
  "helper_hours": [
    { "user_id": 3, "email": "ayudante@hipica.com", "hours": 8.0 }
  ],
  "student_classes": [
    { "client_id": 1, "name": "Anna Garcia", "class_count": 12 }
  ],
  "horse_hours": [
    { "horse_id": 1, "name": "Trueno", "hours": 18.0 }
  ]
}
```

#### Estructura de la respuesta

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `from_date` | string \| null | Fecha de inicio aplicada al filtro |
| `to_date` | string \| null | Fecha de fin aplicada al filtro |
| `instructor_hours` | array | Horas impartidas por cada instructor, ordenadas desc |
| `helper_hours` | array | Horas como ayudante por cada usuario, ordenadas desc |
| `student_classes` | array | Numero de clases asistidas por cada alumno, ordenadas desc |
| `horse_hours` | array | Horas de trabajo por cada caballo, ordenadas desc |

#### Subtipos

**InstructorHours / HelperHours:**

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `user_id` | integer | ID del usuario |
| `email` | string | Email del usuario |
| `hours` | float | Horas totales (redondeadas a 2 decimales) |

**StudentClasses:**

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `client_id` | integer | ID del cliente |
| `name` | string | Nombre del cliente |
| `class_count` | integer | Numero de clases en el rango |

**HorseHours:**

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `horse_id` | integer | ID del caballo |
| `name` | string | Nombre del caballo |
| `hours` | float | Horas totales trabajadas (redondeadas a 2 decimales) |

#### Calculo de duracion

La duracion de cada clase se calcula como `end_time - date_time`. Si la clase no tiene `end_time` definido, se asume **1 hora** por defecto.

**Errores posibles:**

| Codigo | Causa |
|--------|-------|
| 401 | Token ausente o invalido |
| 403 | Rol insuficiente |
| 422 | Formato de fecha invalido |

---

## Notas de Uso

- El informe se genera bajo demanda; no hay datos precalculados ni caches.
- La vista `Reports.vue` en el frontend es la unica consumidora de este endpoint y solo es accesible para `app_admin`.
- Si se envia `from_date` sin `to_date` (o viceversa), el filtro se aplica unilateralmente (abierto por un extremo).
