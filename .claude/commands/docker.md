Gestiona el entorno Docker del proyecto Hipica de forma segura usando el `docker-compose.yml` local.

## Acciones disponibles

El usuario debe indicar una de estas acciones:
- `up` — levantar los contenedores
- `down` — parar y eliminar los contenedores
- `rebuild` — reconstruir las imágenes y levantar
- `logs` — ver logs (opcionalmente filtrar por servicio: `api` o `db`)
- `ps` — ver estado actual de los contenedores

Si no se indica ninguna acción, pedir al usuario que especifique una.

## Comandos por acción

**Siempre ejecutar desde el directorio del proyecto:**
```
c:/abe/Hipica/app/hipica-backend
```

### up
```bash
docker-compose up -d
```
Levanta los servicios `api` y `db` en background.

### down
```bash
docker-compose down
```
Para y elimina los contenedores. **No elimina los volúmenes** (`postgres_data` se preserva).

### rebuild
```bash
docker-compose down && docker-compose up --build -d
```
Reconstruye las imágenes (útil tras cambios en `requirements.txt` o `Dockerfile`).

### logs (sin filtro)
```bash
docker-compose logs --tail=50
```

### logs api
```bash
docker-compose logs --tail=50 api
```

### logs db
```bash
docker-compose logs --tail=50 db
```

### ps
```bash
docker-compose ps
```

## Guardrails — Restricciones de Seguridad

- **Solo** se usan los comandos listados arriba
- **No** se ejecutan comandos docker arbitrarios del usuario
- **No** se usa `down -v` (borraría los datos de PostgreSQL) sin confirmación explícita del usuario
- **No** se ejecuta `docker system prune` ni variantes
- El contexto es **siempre** el `docker-compose.yml` del proyecto

## Formato de estado al finalizar

Siempre presentar el estado resultante tras la acción:

```
## Estado Docker — Hipica

✔  api   running   0.0.0.0:8000->8000/tcp
✔  db    running   0.0.0.0:5432->5432/tcp
```

Si hay errores:
```
## Estado Docker — Hipica

✔  db    running   0.0.0.0:5432->5432/tcp
✖  api   error     Exit code 1

### Error detectado
[extracto relevante del log de error]

### Causa probable
- Error de importación Python → revisar requirements.txt o código
- Puerto 8000 ocupado → otro proceso usa ese puerto
- Variables .env faltantes → verificar .env existe y tiene DATABASE_URL
```

## Errores comunes y diagnóstico

| Síntoma | Causa probable |
|---------|---------------|
| `api` no arranca, exit 1 | Error Python en `app/main.py` o import fallido |
| `connection refused` en `db` | PostgreSQL tardando en arrancar — esperar y reintentar |
| Puerto 5432 ocupado | PostgreSQL local en el host — parar el servicio local |
| `no such service` | Nombre de servicio incorrecto — solo existen `api` y `db` |
| Imagen obsoleta | Cambios en Dockerfile sin `--build` — usar `rebuild` |

## Uso por otros agentes

Este skill puede ser invocado por `backend-dev`, `db-agent` y `test-agent` para:
- Verificar que los servicios están corriendo antes de ejecutar tests o seeds
- Reiniciar el backend tras cambios en configuración
- Consultar logs cuando hay errores en endpoints
