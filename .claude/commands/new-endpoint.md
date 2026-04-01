Genera el scaffolding completo y opinionado de un nuevo endpoint FastAPI para el proyecto Hipica.

## Entrada esperada del usuario

El usuario debe indicar:
- **Entidad**: nombre del recurso (ej. "payment", "document")
- **Operaciones**: cuáles de CRUD implementar
- **Rol requerido**: qué rol necesita cada operación
- **Campos del modelo**: atributos con tipos

Si falta algún dato, pregúntalo antes de generar.

## Pasos a ejecutar

### 1. Modelo ORM — `app/models/<entity>.py`

Crear con SQLModel incluyendo:
- `id: int | None = Field(default=None, primary_key=True)`
- `stable_id: int = Field(foreign_key="stable.id", index=True)` — **siempre, sin excepción**
- `is_active: bool = Field(default=True)`
- Índice en campos que se van a filtrar frecuentemente

### 2. Schema Pydantic — `app/schemas/<entity>.py`

Crear tres clases separadas:
- `<Entity>Base` — campos comunes
- `<Entity>Create(EntityBase)` — campos para crear (sin id, sin stable_id)
- `<Entity>Read(EntityBase)` — campos de respuesta (con id, stable_id)
- `<Entity>Update` — campos opcionales para PATCH (todos Optional)

### 3. Endpoint — `app/api/v1/endpoints/<entity>.py`

Implementar con estos guardrails **obligatorios**:

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from sqlmodel import Session, select
from app.db.session import get_session
from app.dependencies import get_current_user, require_role
from app.models.<entity> import <Entity>
from app.schemas.<entity> import <Entity>Create, <Entity>Read, <Entity>Update
from app.models.user import User

router = APIRouter(prefix="/<entities>", tags=["<entities>"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

Cada operación debe:
- **GET (list):** filtrar por `stable_id == current_user.stable_id`
- **GET (detail):** verificar `entity.stable_id == current_user.stable_id` → 403 si no coincide
- **POST:** asignar `stable_id = current_user.stable_id` (nunca del body)
- **PATCH:** verificar propiedad antes de modificar
- **DELETE:** verificar propiedad antes de eliminar
- **Todos:** usar `response_model` explícito
- **Escritura:** usar `require_role(...)` apropiado

### 4. Registro — `app/api/v1/api.py`

Añadir:
```python
from app.api.v1.endpoints.<entity> import router as <entity>_router
api_router.include_router(<entity>_router)
```

## Guardrails de Verificación

Antes de entregar el código generado, verificar:

- [ ] ¿El modelo tiene `stable_id` con FK e índice?
- [ ] ¿El schema Create NO incluye `stable_id` ni `id`?
- [ ] ¿El schema Read SÍ incluye `id` y `stable_id`?
- [ ] ¿Todos los endpoints tienen `response_model`?
- [ ] ¿Los endpoints de escritura tienen `require_role`?
- [ ] ¿GET list filtra por `stable_id`?
- [ ] ¿GET/PATCH/DELETE verifican propiedad (`entity.stable_id == current_user.stable_id`)?
- [ ] ¿El router está registrado en `api.py`?
- [ ] ¿El prefijo sigue el patrón `/api/v1/<entities>` (plural)?

## Output Final

Entregar en este orden:
1. `app/models/<entity>.py` — modelo completo
2. `app/schemas/<entity>.py` — schemas completos
3. `app/api/v1/endpoints/<entity>.py` — endpoint completo
4. Diff de `app/api/v1/api.py` — líneas a añadir

## Después de generar

Recordar al usuario:
- Ejecutar `/run-tests` para verificar que no hay regresiones
- Usar `api-doc-agent` para documentar el endpoint
- Usar `code-doc-agent` para añadir docstrings si la lógica es compleja
