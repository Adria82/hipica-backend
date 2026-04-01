# Sistema de Agentes y Skills — Hipica

Documentación de referencia del sistema de agentes Claude y skills del proyecto Hipica.

---

## Índice

### Agentes
- [backend-dev](#backend-dev) — Experto FastAPI / backend
- [frontend-dev](#frontend-dev) — Experto Vue 3 / frontend
- [fullstack-dev](#fullstack-dev) — Coordinador features full-stack
- [db-agent](#db-agent) — Base de datos y esquemas
- [test-agent](#test-agent) — Tests de integración
- [doc-agent](#doc-agent) — Documentación de features y arquitectura
- [code-doc-agent](#code-doc-agent) — Docstrings y comentarios de código
- [api-doc-agent](#api-doc-agent) — Documentación de endpoints
- [agent-maintainer](#agent-maintainer) — Sincronización del sistema de agentes
- [git-agent](#git-agent) — Commits, push y Pull Requests a GitHub

### Skills (Slash Commands)
- [/new-endpoint](#new-endpoint) — Scaffolding endpoint FastAPI
- [/new-view](#new-view) — Scaffolding vista Vue 3
- [/run-tests](#run-tests) — Ejecutar suite de tests
- [/docker](#docker) — Gestión entorno Docker

---

## Mapa de Colaboración

```
                        ┌─────────────────┐
                        │  fullstack-dev  │
                        │ (coordinador)   │
                        └────────┬────────┘
                    ┌────────────┴────────────┐
                    ▼                         ▼
           ┌──────────────┐         ┌──────────────────┐
           │ backend-dev  │         │  frontend-dev    │
           │  (FastAPI)   │         │   (Vue 3 / TS)   │
           └──────┬───────┘         └────────┬─────────┘
                  │                          │
           ┌──────▼───────┐                  │
           │   db-agent   │                  │
           │ (PostgreSQL) │                  │
           └──────────────┘                  │
                                             │
        ┌────────────────────────────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────────────┐
  │                  Agentes de Documentación            │
  │  doc-agent │ code-doc-agent │ api-doc-agent          │
  └──────────────────────────────────────────────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────────────┐
  │                  agent-maintainer                    │
  │   (mantiene el sistema de agentes sincronizado)      │
  └──────────────────────────────────────────────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────────────┐
  │                    git-agent                         │
  │   (commits semánticos, push y Pull Requests)         │
  └──────────────────────────────────────────────────────┘
```

---

## Cuándo usar cada agente — Guía rápida

| Situación | Agente a usar |
|-----------|--------------|
| Nuevo endpoint solo backend | `backend-dev` + `/new-endpoint` |
| Nueva vista solo frontend | `frontend-dev` + `/new-view` |
| Feature que cruza back y front | `fullstack-dev` |
| Cambio de esquema DB | `db-agent` |
| Escribir o ejecutar tests | `test-agent` + `/run-tests` |
| Documentar una feature completa | `doc-agent` |
| Añadir docstrings a código | `code-doc-agent` |
| Documentar endpoints API | `api-doc-agent` |
| Agentes con info obsoleta | `agent-maintainer` |
| Subir cambios a GitHub / abrir PR | `git-agent` |
| Gestionar contenedores Docker | `/docker` |

---

## Reglas de Calidad — No Negociables

Estas reglas aplican a todo el equipo y todos los agentes:

1. Toda feature nueva → documentada con `doc-agent`
2. Todo endpoint nuevo → documentado con `api-doc-agent`
3. Todo modelo o lógica compleja → docstrings con `code-doc-agent`
4. Tests de integración tras cada endpoint nuevo (`test-agent`)
5. Sin texto hardcodeado en frontend (i18n siempre — ca/es/en)
6. Sin filtros que ignoren `stable_id` (multi-tenant siempre)
7. Tras cada sprint o bloque de cambios estructurales → ejecutar `agent-maintainer`

---

# Agentes

---

## backend-dev

**Archivo:** [`.claude/agents/backend-dev.md`](../.claude/agents/backend-dev.md)

**Especialidad:** FastAPI, SQLModel, PostgreSQL, JWT, autenticación y autorización.

**Cuándo usarlo:** Implementar endpoints, modelos ORM, schemas Pydantic, lógica de negocio, seguridad.

### Stack

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| FastAPI | 0.128 | Routers, dependencies, response_model |
| SQLModel / SQLAlchemy | 2.0 | ORM, relaciones, sesiones |
| PostgreSQL | 15 | Base de datos principal |
| python-jose + bcrypt | — | JWT HS256, hashing contraseñas |
| pytest | 9 | Tests integración SQLite in-memory |

### Archivos clave

```
app/
├── api/v1/api.py           # Registro de routers
├── api/v1/endpoints/       # Un archivo .py por entidad
├── models/                 # SQLModel ORM — solo mapeo tabla
├── schemas/                # Pydantic — solo request/response
├── dependencies.py         # get_current_user, require_role, SessionDep
├── security.py             # create_access_token, verify_password
├── core/config.py          # Settings desde .env
└── db/session.py           # get_session → SessionDep
```

### Guardrails obligatorios

| # | Guardrail | Descripción |
|---|-----------|-------------|
| 1 | Separación ORM/Schema | `models/` solo ORM, `schemas/` solo Pydantic. Nunca exponer el modelo ORM directamente |
| 2 | `response_model` siempre | Todo endpoint debe declarar `response_model` explícitamente |
| 3 | Inyección de dependencias | Usar `SessionDep` y `CurrentUser` via `Depends` |
| 4 | `require_role(...)` | Todo endpoint de escritura requiere control de acceso explícito |
| 5 | Multi-tenant `stable_id` | Crear: forzar desde `current_user.stable_id`. Listar: filtrar. Leer/editar: verificar propiedad |
| 6 | Manejo errores HTTP | `404` si no existe, `403` si no pertenece a la cuadra |
| 7 | Prefijo `/api/v1/` | Registrar router en `app/api/v1/api.py` |

### Roles del sistema

| Rol | Permisos |
|-----|----------|
| `app_admin` | Acceso total, gestión de cuadras |
| `stable_admin` | CRUD completo dentro de su cuadra |
| `monitor` | Lectura + gestión de clases |
| `client` | Solo lectura de sus propias clases |

### Colaboración

- Tras crear endpoint → `api-doc-agent`
- Lógica compleja → `code-doc-agent`
- Feature completa → `doc-agent`
- Cambios en frontend → `fullstack-dev` o `frontend-dev`
- Tests → `/run-tests` o `test-agent`
- Nuevos modelos/endpoints → `agent-maintainer`

---

## frontend-dev

**Archivo:** [`.claude/agents/frontend-dev.md`](../.claude/agents/frontend-dev.md)

**Especialidad:** Vue 3, TypeScript, Vuetify 3, Axios, Vue Router, vue-i18n.

**Cuándo usarlo:** Nuevas vistas, componentes, routing, gestión de tokens, feature flags, i18n.

### Stack

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Vue 3 | 3.5 | Composition API, `<script setup>`, SFC |
| TypeScript | 5.9 | Tipos estrictos |
| Vuetify | 3.11 | Componentes Material Design |
| Vue Router | 4.6 | Rutas + guards de autenticación |
| Axios | 1.13 | HTTP client centralizado |
| vue-i18n | 11.2 | Internacionalización (ca/es/en) |

### Archivos clave

```
hipica-frontend/src/
├── api/http.ts              # Axios — ÚNICO punto de HTTP
├── auth/tokens.ts           # getAccessToken, setTokens, clearTokens, isLoggedIn
├── features/features.ts     # Feature flags reactivos
├── features/filter.ts       # Helpers para filtrar por feature
├── router/index.ts          # Rutas + guard global requiresAuth
├── types/api.ts             # Interfaces TypeScript de la API
├── i18n/messages.ts         # Traducciones ca/es/en
├── layouts/MainLayout.vue   # Wrapper rutas protegidas
├── views/                   # Páginas (una por entidad/feature)
└── components/              # Componentes reutilizables
```

### Guardrails obligatorios

| # | Guardrail | Descripción |
|---|-----------|-------------|
| 1 | i18n siempre | Nunca texto hardcodeado — usar `$t('key')` y añadir en `messages.ts` (ca/es/en) |
| 2 | HTTP por `http.ts` | No crear instancias Axios directas — siempre `import http from '@/api/http'` |
| 3 | Tipos en `api.ts` | Toda interfaz de API declarada en `src/types/api.ts` |
| 4 | `meta.requiresAuth` | Toda ruta protegida lleva `meta: { requiresAuth: true }` |
| 5 | Feature flags | Consultar `features.value` antes de renderizar funcionalidades opcionales |
| 6 | `<script setup>` | Usar siempre Composition API con `<script setup lang="ts">` |

### Colaboración

- Vista requiere endpoint nuevo → `backend-dev` o `fullstack-dev`
- Vista compleja → `code-doc-agent`
- Feature back+front → `fullstack-dev`
- Nuevas vistas/carpetas → `agent-maintainer`

---

## fullstack-dev

**Archivo:** [`.claude/agents/fullstack-dev.md`](../.claude/agents/fullstack-dev.md)

**Especialidad:** Coordinación de features que cruzan backend FastAPI y frontend Vue 3. Coherencia API ↔ TypeScript.

**Cuándo usarlo:** Features que requieren endpoint(s) + vista(s), cambios en modelos que afectan tipos TS, refactorizaciones que cruzan la frontera API.

### Flujo de trabajo

```
1. DISEÑO DEL CONTRATO API
   Definir schema Pydantic + interfaz TypeScript equivalente antes de implementar

2. BACKEND
   Modelo ORM → Schema Pydantic → Endpoint → Registro en api.py

3. FRONTEND
   Tipos TS → Traducciones (ca/es/en) → Vista → Ruta

4. VERIFICACIÓN (checklist)
   ¿stable_id filtrado? ¿require_role? ¿meta.requiresAuth? ¿$t()? ¿Tipos coinciden? ¿Tests?

5. DOCUMENTACIÓN Y SINCRONIZACIÓN
   api-doc-agent → code-doc-agent → doc-agent → agent-maintainer
```

### Tabla de coherencia Python ↔ TypeScript

| Python | TypeScript |
|--------|-----------|
| `int` | `number` |
| `str` | `string` |
| `bool` | `boolean` |
| `datetime` | `string` (ISO 8601) |
| `Optional[X]` | `X \| null` |
| `list[X]` | `X[]` |

### Colaboración

- Solo backend → `backend-dev`
- Solo frontend → `frontend-dev`
- Solo DB → `db-agent`
- Tests → `test-agent` / `/run-tests`
- Documentación → `doc-agent`, `api-doc-agent`, `code-doc-agent`
- Tras completar feature → `agent-maintainer`

---

## db-agent

**Archivo:** [`.claude/agents/db-agent.md`](../.claude/agents/db-agent.md)

**Especialidad:** PostgreSQL 15, SQLModel/SQLAlchemy 2.0, seeds, consultas SQL, diseño de esquemas.

**Cuándo usarlo:** Diseñar tablas, escribir consultas complejas, mantener seeds, analizar estado de la DB.

**Herramienta MCP disponible:** `mcp__postgres__query` — consultas SQL de solo lectura directas a PostgreSQL.

### Archivos clave

```
app/
├── models/          # Fuente de verdad del esquema
├── db/session.py    # engine, get_session
├── db/base.py       # init_db() — crea tablas al arrancar
└── seed.py          # Datos iniciales
```

### Diagrama de relaciones

```
stable
  ├── user (stable_id FK)
  ├── horse (stable_id FK)
  │     └── horselevellink → level
  ├── client (stable_id FK)
  └── lesson (stable_id FK)
        ├── lessonhorselink → horse
        ├── lessonclientlink → client
        └── instructor_id FK → user
```

### Convenciones de modelos

- `stable_id` con FK e índice en todo modelo de entidad operacional
- `id` autoincremental como primary key
- `is_active: bool = Field(default=True)` para soft-delete
- Tablas N:N como `XxxYyyLink` con dos PKs compuestas

### Nota sobre migraciones

El proyecto usa `init_db()` con `create_all()` — solo crea tablas nuevas, no altera existentes. Para cambios en tablas existentes en desarrollo: `docker-compose down -v && docker-compose up --build`. El proyecto aún no tiene Alembic.

### Colaboración

- Cambio afecta endpoints → `backend-dev`
- Cambio afecta tipos TS → `frontend-dev`
- Cambio en back+front → `fullstack-dev`
- Tras cambios de esquema → `agent-maintainer`

---

## test-agent

**Archivo:** [`.claude/agents/test-agent.md`](../.claude/agents/test-agent.md)

**Especialidad:** pytest, TestClient FastAPI, SQLite in-memory, fixtures, tests de integración.

**Cuándo usarlo:** Escribir tests para nuevos endpoints, ejecutar la suite completa, cubrir casos de seguridad y multi-tenant.

### Arquitectura de tests

| Aspecto | Detalle |
|---------|---------|
| Base de datos | SQLite in-memory — aislada por test, sin PostgreSQL |
| Cliente HTTP | `TestClient` de FastAPI (síncrono) |
| Autenticación | Login real con `/api/v1/auth/login` — sin mocks de JWT |
| Fixtures | `client` fixture en `conftest.py` o inicio del archivo |

### Comando de ejecución

```bash
PYTHONPATH=. python -m pytest -v
PYTHONPATH=. python -m pytest -v -k "test_horse"     # filtrar
PYTHONPATH=. python -m pytest -v --tb=short           # traceback corto
```

### Casos obligatorios por endpoint

| Categoría | Tests requeridos |
|-----------|-----------------|
| Positivos | list (autenticado), create (rol correcto), get by id, update, delete |
| Seguridad | sin token → 401, rol incorrecto → 403, multi-tenant → lista vacía o 403 |
| Edge | ID inexistente → 404, datos inválidos → 422 |

### Convenciones

- Nombres descriptivos: `test_create_horse_requires_stable_admin_role`
- Sin mocks de DB — SQLite in-memory real
- Sin mocks de JWT — login real
- Fixtures pequeñas y composables

### Colaboración

- Test falla por bug → `backend-dev`
- Falta endpoint para testear → `backend-dev`

---

## doc-agent

**Archivo:** [`.claude/agents/doc-agent.md`](../.claude/agents/doc-agent.md)

**Especialidad:** Documentación de features, arquitectura del sistema, ADRs (Architecture Decision Records).

**Cuándo usarlo:** Tras crear features importantes, al tomar decisiones arquitectónicas, para onboarding de nuevos miembros.

**Importante:** Solo lee e interpreta código. No genera código funcional.

### Tipos de documentación que genera

| Tipo | Destino | Contenido |
|------|---------|-----------|
| Feature doc | `docs/features/<feature>.md` | Descripción, flujo, endpoints, modelos involucrados |
| Architecture doc | `docs/architecture/<topic>.md` | Componentes, flujos, decisiones técnicas |
| ADR | `docs/adr/ADR-XXX-titulo.md` | Contexto, decisión, consecuencias |

### Convenciones

- Idioma: español
- Diagramas: preferir Mermaid (` ```mermaid `)
- Nivel de detalle: suficiente para que alguien nuevo entienda sin leer código

### Regla de oro

**Toda feature nueva en producción debe tener su documento antes de considerarse completada.**

---

## code-doc-agent

**Archivo:** [`.claude/agents/code-doc-agent.md`](../.claude/agents/code-doc-agent.md)

**Especialidad:** Docstrings Google-style en Python, JSDoc en TypeScript, comentarios de lógica compleja.

**Cuándo usarlo:** Tras generar código con `/new-endpoint` o `/new-view`, tras refactorizaciones, en modelos con lógica de negocio no obvia.

**Importante:** Solo añade documentación. No modifica lógica, imports ni estructura de código.

### Estilo Python — Google Docstrings

```python
def create_lesson(lesson_in: LessonCreate, session: SessionDep, current_user: CurrentUser):
    """Crea una nueva clase de equitación.

    Args:
        lesson_in: Datos de la clase (datetime, horse_ids, client_ids).
        session: Sesión de base de datos inyectada.
        current_user: Usuario autenticado (rol monitor o superior).

    Returns:
        La clase creada con sus relaciones cargadas.

    Raises:
        HTTPException(404): Si algún caballo o alumno no existe.
        HTTPException(403): Si el usuario no tiene rol suficiente.
    """
```

### Reglas de obligatoriedad

| Situación | ¿Docstring obligatorio? |
|-----------|------------------------|
| Modelos con relaciones complejas o reglas de negocio | ✅ Sí |
| Funciones de autenticación y seguridad | ✅ Sí |
| Endpoints con lógica multi-tenant no trivial | ✅ Sí |
| Funciones TS de gestión de estado o tokens | ✅ Sí |
| CRUD estándar simple | Recomendado |
| Funciones autoexplicativas sin parámetros complejos | ❌ No necesario |

---

## api-doc-agent

**Archivo:** [`.claude/agents/api-doc-agent.md`](../.claude/agents/api-doc-agent.md)

**Especialidad:** Documentación de endpoints REST: inputs, outputs, roles requeridos, ejemplos. También mejora docstrings FastAPI para OpenAPI.

**Cuándo usarlo:** Tras crear o modificar un endpoint, para auditar la API, para revisar coherencia de roles.

**Importante:** Solo lee e interpreta código. No genera código funcional.

### Tipos de output

1. **Markdown** — `docs/api/<recurso>.md` con tabla de endpoints, detalle de cada uno, ejemplos JSON
2. **OpenAPI** — docstrings `summary`/`description`/`response_description` en los decoradores FastAPI

### Checklist de auditoría de endpoints

- [ ] ¿Tiene `response_model`?
- [ ] ¿Tiene `require_role` explícito o está documentado que es público?
- [ ] ¿Filtra por `stable_id`?
- [ ] ¿Los errores 401, 403, 404, 422 están cubiertos?
- [ ] ¿El schema está en `app/schemas/`?

### Tabla de roles por operación

| Operación | Rol mínimo típico |
|-----------|-------------------|
| Listar / Leer | `monitor` |
| Crear / Actualizar | `stable_admin` |
| Eliminar | `stable_admin` |
| Gestión de usuarios | `app_admin` |
| Ver perfil propio | `client` |

### Estructura de docs que genera

```
docs/api/
├── auth.md
├── horses.md
├── clients.md
├── lessons.md
├── users.md
├── levels.md
└── stables.md
```

---

## agent-maintainer

**Archivo:** [`.claude/agents/agent-maintainer.md`](../.claude/agents/agent-maintainer.md)

**Especialidad:** Sincronización de archivos de contexto del sistema de agentes con el estado real del repositorio. Ediciones quirúrgicas, no reescrituras.

**Cuándo usarlo:** Tras sprints con cambios estructurales, cuando agentes cometan errores por contexto obsoleto, como tarea periódica de mantenimiento.

**Importante:** No reescribe archivos completos. No genera código funcional. Solo edita las secciones desactualizadas.

### Fuentes de verdad que monitoriza

| Qué cambia | Dónde mirarlo |
|-----------|--------------|
| Modelos ORM | `app/models/*.py` |
| Endpoints | `app/api/v1/endpoints/*.py` |
| Schemas | `app/schemas/*.py` |
| Vistas Vue | `hipica-frontend/src/views/*.vue` |
| Rutas frontend | `hipica-frontend/src/router/index.ts` |
| Tipos TypeScript | `hipica-frontend/src/types/api.ts` |
| Dependencias Python | `requirements.txt` |
| Dependencias JS | `hipica-frontend/package.json` |

### Tabla de impacto cambio → contexto

| Tipo de cambio | Archivos de contexto afectados |
|---------------|-------------------------------|
| Nuevo modelo | `CLAUDE.md` (diagrama), `db-agent.md` (relaciones) |
| Nuevo endpoint | `CLAUDE.md` (estructura), `backend-dev.md` (archivos clave) |
| Nueva vista | `CLAUDE.md` (estructura), `frontend-dev.md` (archivos clave) |
| Nueva carpeta src | `CLAUDE.md` (estructura), `frontend-dev.md` (archivos clave) |
| Nuevo agente | `CLAUDE.md` (tabla de agentes) |
| Nueva skill | `CLAUDE.md` (tabla de skills) |
| Dependencia mayor | `CLAUDE.md` (stack) |

### Señales de alerta — degradación del sistema

El agent-maintainer reportará como alerta si detecta:
- Referencia a archivo que ya no existe en ningún agente
- Diagrama de modelos con entidades ausentes en `app/models/`
- Vista listada en `frontend-dev.md` que no existe en `src/views/`
- Agente en `CLAUDE.md` sin su archivo `.md` correspondiente
- Skill en `CLAUDE.md` sin su archivo en `.claude/commands/`

---

## git-agent

**Archivo:** [`.claude/agents/git-agent.md`](../.claude/agents/git-agent.md)

**Especialidad:** Commits Conventional Commits, push a GitHub, creación de Pull Requests con `gh`. Conoce el flujo de ramas del proyecto.

**Cuándo usarlo:** Al finalizar una feature o bugfix, para subir cambios al repositorio remoto, para abrir un PR hacia `develop`.

**Importante:** Nunca hace push a `main`/`master` ni operaciones destructivas sin confirmación explícita del usuario.

### Flujo de ramas

```
master     ← producción (solo via PR revisado)
  └── develop     ← integración (rama base para PRs)
        ├── feature/<nombre>
        ├── fix/<nombre>
        └── chore/<nombre>
```

### Convención de commits — Conventional Commits

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Solo documentación |
| `refactor` | Refactorización sin cambio de comportamiento |
| `test` | Añadir o modificar tests |
| `chore` | Mantenimiento, deps, config |

**Ejemplos:**
```
feat(horses): añadir endpoint CRUD completo con multi-tenant
fix(auth): corregir expiración de refresh token
docs(api): documentar endpoints de lessons
test(clients): añadir casos de aislamiento multi-tenant
```

### Proceso que sigue

1. `git status` + `git diff --stat` — revisar estado
2. Staging selectivo de archivos (nunca `.env`)
3. Commit con mensaje semántico + `Co-Authored-By`
4. `git push` a la rama de trabajo
5. `gh pr create --base develop` si el usuario lo pide

### Guardrails de seguridad

| Restricción | Motivo |
|-------------|--------|
| No push a `main`/`master` sin confirmación | Rama de producción |
| No `--force` sin confirmación | Puede destruir historial remoto |
| No `git reset --hard` sin confirmación | Pérdida irreversible de trabajo |
| No commit de `.env` | Contiene secretos |
| No `--no-verify` | No saltarse hooks pre-commit |

### Verificación pre-commit

- [ ] Tests pasan (`/run-tests`)
- [ ] `.env` no incluido en staging
- [ ] Mensaje sigue Conventional Commits
- [ ] Estamos en la rama correcta (no `main`/`master`)

### Colaboración

- Antes de commit → verificar que `api-doc-agent` documentó el endpoint
- Si tests fallan → `backend-dev` o `test-agent` antes de hacer commit
- Tras merge del PR → `agent-maintainer` si hubo cambios estructurales

---

# Skills (Slash Commands)

---

## /new-endpoint

**Archivo:** [`.claude/commands/new-endpoint.md`](../.claude/commands/new-endpoint.md)

**Uso:** `/new-endpoint`

**Qué hace:** Genera el scaffolding completo y opinionado de un nuevo endpoint FastAPI. Aplica todos los guardrails arquitectónicos desde el inicio para evitar deuda técnica.

### Entrada requerida

Antes de generar, el skill preguntará por:
- Nombre de la entidad (ej. `payment`)
- Operaciones CRUD a implementar
- Rol requerido por operación
- Campos del modelo con sus tipos

### Lo que genera

| Archivo | Contenido |
|---------|-----------|
| `app/models/<entity>.py` | Modelo SQLModel con `stable_id`, `id`, `is_active` |
| `app/schemas/<entity>.py` | `<Entity>Base`, `<Entity>Create`, `<Entity>Read`, `<Entity>Update` |
| `app/api/v1/endpoints/<entity>.py` | Endpoint completo con todos los guardrails |
| Diff `app/api/v1/api.py` | Líneas para registrar el router |

### Checklist de verificación (9 puntos)

- [ ] Modelo tiene `stable_id` con FK e índice
- [ ] Schema `Create` sin `stable_id` ni `id`
- [ ] Schema `Read` con `id` y `stable_id`
- [ ] Todos los endpoints con `response_model`
- [ ] Endpoints de escritura con `require_role`
- [ ] GET list filtra por `stable_id`
- [ ] GET/PATCH/DELETE verifican propiedad
- [ ] Router registrado en `api.py`
- [ ] Prefijo plural `/api/v1/<entities>`

### Después de usar

Recordar ejecutar:
1. `/run-tests` — verificar regresiones
2. `api-doc-agent` — documentar el endpoint
3. `code-doc-agent` — si la lógica es compleja

---

## /new-view

**Archivo:** [`.claude/commands/new-view.md`](../.claude/commands/new-view.md)

**Uso:** `/new-view`

**Qué hace:** Genera el scaffolding completo y opinionado de una nueva vista Vue 3. Aplica todos los guardrails frontend desde el inicio.

### Entrada requerida

Antes de generar, el skill preguntará por:
- Entidad/feature que gestiona la vista
- Ruta (path)
- Funcionalidad (listar, crear, editar, eliminar)
- Roles que pueden acceder
- Endpoints de backend que consume

### Lo que genera

| Archivo | Contenido |
|---------|-----------|
| Adiciones `src/types/api.ts` | Interfaces TypeScript coherentes con `response_model` |
| Adiciones `src/i18n/messages.ts` | Claves en ca, es, en |
| `src/views/<Entity>.vue` | Vista Vuetify con Composition API, loading, i18n |
| Diff `src/router/index.ts` | Ruta con `meta.requiresAuth: true` |

### Tabla de coherencia de tipos que aplica

| Python | TypeScript generado |
|--------|---------------------|
| `int` | `number` |
| `bool` | `boolean` |
| `datetime` | `string` |
| `Optional[X]` | `X \| null` |
| `list[X]` | `X[]` |

### Checklist de verificación (8 puntos)

- [ ] Tipos TS coinciden con `response_model`
- [ ] Sin texto hardcodeado — todo `$t('key')`
- [ ] Claves i18n en los 3 idiomas
- [ ] HTTP por `src/api/http.ts`
- [ ] Tipos en `src/types/api.ts`
- [ ] Ruta con `meta.requiresAuth: true`
- [ ] Estado de loading visible
- [ ] Feature flags consultados si aplica

---

## /run-tests

**Archivo:** [`.claude/commands/run-tests.md`](../.claude/commands/run-tests.md)

**Uso:** `/run-tests`

**Qué hace:** Ejecuta la suite de tests de integración del backend y devuelve un informe estructurado con estado ✅/❌, diagnóstico de fallos y próximos pasos.

### Comandos que ejecuta

```bash
# Ejecución completa
PYTHONPATH=. python -m pytest -v --tb=short

# Filtrar por entidad
PYTHONPATH=. python -m pytest -v -k "horse" --tb=short

# Solo tests fallidos previos
PYTHONPATH=. python -m pytest -v --last-failed --tb=short
```

### Formato del informe

```
## Resultado de Tests

✅ Pasados:  XX
❌ Fallidos: XX
⚠️  Omitidos: XX
⏱  Tiempo:   X.XXs

### Tests fallidos (si los hay)
[nombre del test, archivo:línea, error, causa probable]

### Próximos pasos sugeridos
[acciones concretas]
```

### Diagnóstico de errores comunes

| Error | Causa probable |
|-------|---------------|
| `ImportError` | PYTHONPATH incorrecto o archivo inexistente |
| `fixture 'client' not found` | Fixture no definida en conftest.py |
| `422 Unprocessable Entity` | Schema de request cambiado — actualizar datos del test |
| `401 unexpected` | Test sin auth headers en endpoint protegido |

---

## /docker

**Archivo:** [`.claude/commands/docker.md`](../.claude/commands/docker.md)

**Uso:** `/docker <acción>`

**Qué hace:** Gestiona el entorno Docker del proyecto de forma segura y acotada. Siempre usa el `docker-compose.yml` local. Nunca ejecuta comandos docker arbitrarios.

### Acciones disponibles

| Acción | Comando ejecutado | Descripción |
|--------|-------------------|-------------|
| `up` | `docker-compose up -d` | Levanta api + db en background |
| `down` | `docker-compose down` | Para contenedores (preserva volumen de datos) |
| `rebuild` | `docker-compose down && up --build -d` | Reconstruye imágenes |
| `logs` | `docker-compose logs --tail=50` | Logs de todos los servicios |
| `logs api` | `docker-compose logs --tail=50 api` | Solo logs del backend |
| `logs db` | `docker-compose logs --tail=50 db` | Solo logs de PostgreSQL |
| `ps` | `docker-compose ps` | Estado de los contenedores |

### Guardrails de seguridad

- No ejecuta `down -v` sin confirmación explícita (borra datos PostgreSQL)
- No ejecuta `docker system prune` ni variantes destructivas
- Solo los comandos de la tabla anterior — no comandos docker arbitrarios
- Contexto siempre limitado al `docker-compose.yml` del proyecto

### Formato de estado al finalizar

```
## Estado Docker — Hipica

✔  api   running   0.0.0.0:8000->8000/tcp
✔  db    running   0.0.0.0:5432->5432/tcp
```

### Errores comunes

| Síntoma | Causa probable |
|---------|---------------|
| `api` exit 1 | Error Python en `app/main.py` o import fallido |
| `connection refused` en `db` | PostgreSQL tardando en arrancar |
| Puerto 5432 ocupado | PostgreSQL local en el host |
| Imagen obsoleta | Cambios en Dockerfile sin `--build` → usar `rebuild` |

### Agentes que lo invocan

`backend-dev`, `db-agent` y `test-agent` pueden invocar este skill para verificar el estado del entorno antes de ejecutar operaciones.
