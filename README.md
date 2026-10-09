# Hípica — Gestión de hípicas

Aplicación web multi-hípica para gestionar caballos, boxes, pistas, clases, reservas, usuarios e informes.
Cada hípica tiene sus propios datos, su propia imagen de marca y las funcionalidades que tenga contratadas.
La interfaz está disponible en catalán, castellano e inglés.

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.10, FastAPI, SQLModel / SQLAlchemy 2.0 |
| Base de datos | PostgreSQL 15 |
| Autenticación | JWT (access token 15 min + refresh token 7 días) |
| Frontend | Vue 3 + TypeScript, Vuetify 3, Vite |
| Infraestructura | Docker + docker-compose |

---

## 🌐 Acceso público — Versión de evaluación

La aplicación **Gestión de Hípicas** está desplegada en la nube y disponible para su evaluación sin necesidad de instalar Docker, PostgreSQL, Python ni Node.js.

### Acceso a la aplicación

| Servicio | URL |
|---|---|
| **Aplicación web** | https://hipica-bigschool.web.app |
| **API REST** | https://hipica-backend.onrender.com |
| **Documentación API (Swagger)** | https://hipica-backend.onrender.com/docs |
| **Estado de la base de datos** | https://hipica-backend.onrender.com/health/db |

La aplicación puede utilizarse desde un navegador web de escritorio, tableta o móvil.

### ⚠️ Importante: primer acceso

Esta versión utiliza servicios de alojamiento gratuitos para facilitar su evaluación académica.

El backend está desplegado en **Render (plan gratuito)**, que suspende automáticamente el servicio después de aproximadamente **15 minutos de inactividad**.

Por este motivo:

- **El primer acceso puede tardar alrededor de un minuto** mientras el servidor vuelve a arrancar.
- Durante este tiempo, la pantalla de inicio de sesión puede tardar en responder o mostrar temporalmente un error de conexión.
- Una vez activado el servidor, la aplicación funciona normalmente.
- Si el primer intento no responde, se recomienda esperar aproximadamente un minuto y volver a intentarlo.

Este comportamiento es una limitación del alojamiento gratuito, no de las funcionalidades de la aplicación.

### Usuarios de demostración

Los usuarios y contraseñas para evaluar los diferentes roles de la aplicación están documentados en el apartado [Usuarios de acceso](#usuarios-de-acceso).

Para acceder a la versión pública, deben utilizarse las siguientes direcciones:

- **Superadministrador:** https://hipica-bigschool.web.app/

La aplicación incluye datos ficticios de demostración para probar sus funcionalidades.

### Arquitectura del despliegue

| Componente | Tecnología | Plataforma |
|---|---|---|
| Frontend | Vue 3 + TypeScript + Vuetify | Firebase Hosting |
| Backend | Python + FastAPI + Docker | Render |
| Base de datos | PostgreSQL | Neon |
| Código fuente | Git | GitHub, rama `bigschool` |

El frontend se comunica mediante HTTPS con la API REST alojada en Render, que a su vez accede a la base de datos PostgreSQL de Neon.

### Consideraciones de la versión de evaluación

- El acceso público está pensado para fines académicos y demostrativos.
- La disponibilidad está sujeta a los límites de los planes gratuitos de alojamiento.
- Los datos almacenados son de demostración y pueden restablecerse durante el periodo de evaluación.
- El backend puede experimentar tiempos de respuesta superiores tras periodos de inactividad.
- La aplicación también puede ejecutarse localmente siguiendo las instrucciones que se detallan a continuación.

---

## Requisitos Despliegue en local

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js](https://nodejs.org/) 20 o superior (para el frontend)

---

## Puesta en marcha

Hacen falta dos ficheros `.env`, que se entregan con el proyecto:

| Fichero | Contenido |
|---------|-----------|
| `.env` (en la raíz) | Credenciales de PostgreSQL y configuración JWT |
| `hipica-frontend/.env` | `VITE_API_BASE_URL`: URL de la API |

### 1. Backend + base de datos

Desde la carpeta raíz del proyecto:

```bash
docker-compose up --build
```

La primera vez que arranca con la base de datos vacía, crea las tablas y carga automáticamente los **datos de prueba**.
En los siguientes arranques detecta que ya hay datos y no los vuelve a cargar.

### 2. Frontend

En otra terminal:

```bash
cd hipica-frontend
npm install
npm run dev
```

### 3. URLs

| Servicio | URL |
|----------|-----|
| Aplicación (marca por defecto) | http://localhost:5173/ |
| Aplicación (marca Hípica Can Valls) | http://localhost:5173/?client=canValls |
| API | http://localhost:8000 |
| Documentación de la API (Swagger) | http://localhost:8000/docs |
| Estado de la base de datos | http://localhost:8000/health/db |

---

## Usuarios de acceso

### Superadministrador (todas las hípicas)

| | |
|---|---|
| **URL** | http://localhost:5173/ |
| **Email** | `abe@hipica.com` |
| **Contraseña** | `qwerty` |
| **Rol** | `app_admin` |

Gestiona todas las hípicas del sistema, sus funcionalidades contratadas, los niveles y los usuarios de cualquier hípica.

### Administrador de la hípica (Hípica Can Valls)

| | |
|---|---|
| **URL** | http://localhost:5173/?client=canValls |
| **Email** | `toni@canvalls.es` |
| **Contraseña** | `admin123` |
| **Rol** | `stable_admin` |

Gestiona su hípica: caballos, boxes, pistas, clases, reservas, usuarios e informes.
El parámetro `?client=canValls` carga la imagen de marca de la hípica.


## Datos de prueba

Los datos se definen en [app/seed.py](app/seed.py): una hípica (Can Valls), usuarios de todos los roles, niveles, caballos, boxes, pistas y clases.

- **Carga automática:** al arrancar Docker, solo si la base de datos está vacía.
- **Volver a los datos iniciales:**
  ```bash
  docker-compose down -v      # borra el volumen de la base de datos
  docker-compose up --build   # vuelve a crear las tablas y cargar el seed
  ```

> ⚠️ Ejecutar `python app/seed.py` a mano **borra todas las tablas** y las vuelve a crear con los datos de prueba.

---

## Desarrollo

### Tests

```bash
PYTHONPATH=. python -m pytest -v
```

Los tests usan SQLite en memoria y no tocan la base de datos de Docker.

### Shell dentro de los contenedores

```bash
docker-compose exec api bash   # contenedor de la API
docker-compose exec db bash    # contenedor de PostgreSQL
```

### PostgreSQL (psql)

```bash
docker-compose exec db psql -U hipica -d hipica
```

| Comando | Acción |
|---------|--------|
| `\dt` | Listar tablas |
| `\d <tabla>` | Ver la estructura de una tabla |
| `\q` | Salir |

### Migraciones (Alembic)

Dentro del contenedor (la URL de la base de datos se lee del `.env`):

```bash
docker-compose exec api python -m alembic current                          # estado actual
docker-compose exec api python -m alembic upgrade head                     # aplicar migraciones
docker-compose exec api python -m alembic revision --autogenerate -m "..." # nueva migración
docker-compose exec api python -m alembic downgrade -1                     # revertir la última
```

---

## Estructura del proyecto

```
hipica-backend/
├── app/
│   ├── api/v1/endpoints/   # Endpoints REST (uno por entidad)
│   ├── models/             # Entidades ORM (SQLModel)
│   ├── schemas/            # Esquemas de entrada/salida (Pydantic)
│   ├── core/               # Configuración e i18n
│   ├── db/                 # Sesión y creación de tablas
│   ├── test/               # Tests de integración
│   └── seed.py             # Datos de prueba
├── alembic/                # Migraciones de base de datos
├── hipica-frontend/        # Aplicación Vue 3
│   ├── public/branding/    # Imagen de marca por hípica
│   └── src/                # Vistas, componentes, router, i18n...
├── docs/                   # Documentación técnica
├── Docu/                   # Notas de diseño del proyecto
├── Dockerfile
└── docker-compose.yml
```

---

## Documentación

- [docs/api/](docs/api/): endpoints de la API (entradas, salidas y roles necesarios)
- [docs/features/](docs/features/): funcionalidades (autenticación, reservas, informes, licencias, branding...)
- [Docu/](Docu/): notas de diseño (i18n, Vuetify, layouts, branding, menú por licencia, servidor MCP)
