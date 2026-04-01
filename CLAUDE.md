# Hipica — Contexto del Proyecto para Claude Code

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.10, FastAPI 0.128, SQLModel/SQLAlchemy 2.0 |
| Base de datos | PostgreSQL 15 (Docker) |
| Auth | JWT HS256 — access token 15min, refresh token 7 días |
| Frontend | Vue 3 + TypeScript, Vuetify 3, Axios, vue-i18n |
| Build frontend | Vite 7, vue-tsc |
| Contenedores | Docker + docker-compose.yml (servicios: `api`, `db`) |
| Tests | pytest 9, SQLite in-memory, TestClient FastAPI |
| MCP | `postgres` (consulta directa DB) + `hipica` (API tools) |

---

## Estructura de Carpetas Clave

```
hipica-backend/
├── app/
│   ├── api/v1/
│   │   ├── api.py                  # Agrega todos los routers
│   │   └── endpoints/              # Un archivo por entidad
│   ├── core/config.py              # Config desde .env
│   ├── db/session.py               # SessionDep (get_session)
│   ├── models/                     # SQLModel ORM (tabla real)
│   ├── schemas/                    # Pydantic (request/response)
│   ├── dependencies.py             # get_current_user, require_role
│   ├── security.py                 # JWT, bcrypt
│   ├── seed.py                     # Datos iniciales
│   └── test/test_endpoints.py      # Tests de integración
├── hipica_mcp/server.py            # FastMCP tools para Claude
├── hipica-frontend/
│   └── src/
│       ├── api/http.ts             # Axios con interceptors (auth + i18n)
│       ├── auth/tokens.ts          # localStorage token management
│       ├── features/features.ts    # Feature flags reactivos
│       ├── router/index.ts         # Rutas + guards
│       ├── types/api.ts            # Interfaces TypeScript
│       ├── views/                  # Páginas Vue (una por entidad/feature)
│       ├── components/             # Componentes reutilizables
│       └── i18n/messages.ts        # Traducciones (ca/es/en)
├── docker-compose.yml
├── .env
└── .mcp.json
```

---

## Comandos Frecuentes

```bash
# Backend
docker-compose up --build           # Levantar entorno completo
docker-compose up -d                # Levantar en background
docker-compose down                 # Parar contenedores
docker-compose logs -f api          # Logs del backend
PYTHONPATH=. python -m pytest -v    # Ejecutar tests
PYTHONPATH=. python app/seed.py     # Cargar datos iniciales

# Frontend
cd hipica-frontend
npm install
npm run dev                         # Dev server en localhost:5173
npm run build                       # Build producción (incluye tsc)
```

---

## Convenciones Arquitectónicas — OBLIGATORIO

### Backend

1. **Separación ORM/Schema estricta**
   - `app/models/` → solo entidades SQLModel (mapeo DB)
   - `app/schemas/` → solo Pydantic para request/response
   - Nunca exponer el modelo ORM directamente en un endpoint

2. **Todo endpoint usa `response_model`**
   ```python
   @router.get("/{id}", response_model=HorseRead)
   ```

3. **Inyección de dependencias siempre**
   ```python
   def get_horse(id: int, session: SessionDep, current_user: CurrentUser):
   ```

4. **Control de acceso con `require_role`**
   ```python
   current_user: CurrentUser = Depends(require_role("stable_admin"))
   ```
   Roles disponibles: `app_admin` | `stable_admin` | `monitor` | `client`

5. **Multi-tenant obligatorio**: Toda entidad perteneciente a una cuadra debe incluir `stable_id` y los endpoints deben filtrar siempre por el `stable_id` del usuario autenticado.

6. **Prefijo de rutas**: Siempre bajo `/api/v1/`

7. **Registro en `api.py`**: Todo nuevo router debe registrarse en `app/api/v1/api.py`

### Frontend

1. **i18n obligatorio** — ningún texto hardcodeado en templates; usar `$t('key')` y añadir clave en `src/i18n/messages.ts` para ca/es/en

2. **HTTP siempre por `src/api/http.ts`** — no crear instancias Axios directas

3. **Tipos en `src/types/api.ts`** — toda interfaz de API documentada aquí

4. **Rutas protegidas** con `meta: { requiresAuth: true }` y el guard en `router/index.ts`

5. **Features flags** consultados en `src/features/features.ts` antes de renderizar funcionalidades condicionales

---

## Modelo de Datos (Diagrama simplificado)

```
Stable (1) ──< User
Stable (1) ──< Horse ──< HorseLevelLink >── Level
Stable (1) ──< Client
Stable (1) ──< Lesson ──< LessonHorseLink >── Horse
                       ──< LessonClientLink >── Client
Lesson.instructor_id → User
```

---

## Agentes Disponibles

| Agente | Especialidad | Cuándo usarlo |
|--------|-------------|---------------|
| `backend-dev` | FastAPI, SQLModel, JWT, lógica de negocio | Endpoints, modelos, autenticación |
| `frontend-dev` | Vue 3, TypeScript, Vuetify, Axios | Vistas, componentes, routing |
| `fullstack-dev` | Backend + Frontend coordinados | Features que cruzan ambas capas |
| `db-agent` | PostgreSQL, SQLAlchemy, migraciones, seeds | Esquemas, consultas, datos |
| `test-agent` | pytest, TestClient, fixtures | Escribir y ejecutar tests |
| `doc-agent` | Documentación de features y arquitectura | Después de cada feature importante |
| `code-doc-agent` | Docstrings, comentarios de código | Tras generar o refactorizar código |
| `api-doc-agent` | Documentación de endpoints (roles, I/O) | Tras crear o modificar endpoints |
| `agent-maintainer` | Sincroniza archivos de contexto con el repo | Tras sprints, features o cambios estructurales |
| `git-agent` | Commits semánticos, push y PRs a GitHub | Al finalizar una feature o bugfix listo para subir |

---

## Skills (Slash Commands) Disponibles

| Skill | Acción |
|-------|--------|
| `/new-endpoint` | Scaffolding opinionado de endpoint FastAPI completo |
| `/new-view` | Scaffolding opinionado de vista Vue 3 completa |
| `/run-tests` | Ejecutar suite de tests con salida estructurada |
| `/docker` | Gestión segura del entorno Docker del proyecto |

---

## Reglas de Calidad — No Negociables

- Toda feature nueva → documentada con `doc-agent`
- Todo endpoint nuevo → documentado con `api-doc-agent`
- Todo modelo o lógica compleja → docstrings con `code-doc-agent`
- Tests de integración tras cada endpoint nuevo
- Sin texto hardcodeado en frontend (i18n siempre)
- Sin filtros que ignoren `stable_id` (multi-tenant siempre)
- Tras cada sprint o bloque de cambios estructurales → ejecutar `agent-maintainer`

---

## MCP Configurado

- **`mcp__postgres__query`**: Consultas SQL directas (solo lectura) a PostgreSQL
- **`mcp__hipica__*`**: Tools de la API Hipica (login, CRUD completo) — requiere autenticación previa con `mcp__hipica__login`
