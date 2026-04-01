Ejecuta la suite de tests de integración del backend Hipica y devuelve un informe estructurado.

## Comando de ejecución

```bash
cd c:/abe/Hipica/app/hipica-backend && PYTHONPATH=. python -m pytest -v --tb=short 2>&1
```

## Opciones adicionales según el contexto

- Filtrar por entidad: `PYTHONPATH=. python -m pytest -v -k "horse" --tb=short`
- Solo fallidos: `PYTHONPATH=. python -m pytest -v --last-failed --tb=short`
- Con cobertura (si está instalado): `PYTHONPATH=. python -m pytest -v --cov=app --cov-report=term-missing`

## Formato del informe de resultados

Después de ejecutar, presentar siempre en este formato:

```
## Resultado de Tests

✅ Pasados:  XX
❌ Fallidos: XX
⚠️  Omitidos: XX
⏱  Tiempo:   X.XXs

### Tests fallidos (si los hay)

**test_create_horse_requires_auth**
app/test/test_endpoints.py:45
AssertionError: assert 401 == 200
→ El endpoint no devuelve 401 cuando no hay token

### Próximos pasos sugeridos
- [ ] Corregir test_create_horse_requires_auth → revisar dependencia require_role
```

## Diagnóstico de errores comunes

| Error | Causa probable | Acción |
|-------|---------------|--------|
| `ImportError` | Módulo no encontrado | Verificar PYTHONPATH=. y que el archivo existe |
| `fixture 'client' not found` | Fixture no definida | Verificar conftest.py o fixture en test file |
| `Engine not found / DB error` | Configuración de SQLite | Verificar fixture usa `create_engine("sqlite://")` |
| `422 Unprocessable Entity` | Schema de request cambiado | Actualizar datos del test |
| `401 unexpected` | `require_role` activo pero test sin auth | Añadir headers de auth al test |

## Cuándo actuar tras los tests

- **Todos pasan** → informar resultado y sugerir `api-doc-agent` si hay endpoints nuevos sin documentar
- **Hay fallos** → analizar causa, proponer fix concreto, o delegar a `test-agent` si hay que reescribir tests
- **Error de importación** → verificar que se ejecuta desde el directorio correcto y con `PYTHONPATH=.`
